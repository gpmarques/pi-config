#!/usr/bin/env python3
"""Focused integration tests for scripts/start-lab using real fzf and a fake gh."""

from __future__ import annotations

import fcntl
import os
from pathlib import Path
import pty
import select
import shutil
import struct
import tempfile
import termios
import time

ROOT = Path(__file__).resolve().parents[1]
START_LAB = ROOT / "scripts" / "start-lab"
TEMPLATE = ROOT / "templates" / "workspace" / "AGENTS.md"

FAKE_GH = r"""#!/bin/sh
set -eu
command=${1-}
case "$command" in
  auth)
    printf 'auth\0' >> "$GH_LOG"
    [ "${GH_AUTH_FAIL:-0}" != 1 ]
    ;;
  search)
    shift 2
    query=''
    for argument do query=$argument; done
    printf 'search:%s\0' "$query" >> "$GH_LOG"
    case "$query" in
      alpha) printf 'Acme/One\tPUBLIC\tfirst repository\n' ;;
      beta) printf 'Acme/Two\tPRIVATE\tsecond repository\n' ;;
      duplicate-one) printf 'Acme/Same\tPUBLIC\tone\n' ;;
      duplicate-two) printf 'Other/same\tPRIVATE\ttwo\n' ;;
      mixed)
        printf 'Acme/Good\tPUBLIC\tworks\n'
        printf 'Acme/Fail\tPRIVATE\tfails\n'
        ;;
      empty) : ;;
      slow) sleep 2; printf 'Acme/Stale\tPUBLIC\tstale result\n' ;;
      error) printf 'simulated API error\n' >&2; exit 1 ;;
      *) printf 'Acme/Quoted\tPUBLIC\tquoted query\n' ;;
    esac
    ;;
  repo)
    [ "${2-}" = clone ]
    repository=$3
    destination=$4
    printf 'clone:%s:%s\0' "$repository" "$destination" >> "$GH_LOG"
    case "$repository" in
      */Fail) exit 1 ;;
    esac
    mkdir "$destination"
    printf '%s\n' "$repository" > "$destination/CLONED"
    ;;
  *) exit 2 ;;
esac
"""


class PtyRun:
    def __init__(self, command: Path, cwd: Path, env: dict[str, str]):
        pid, fd = pty.fork()
        if pid == 0:
            os.chdir(cwd)
            os.execve(str(command), [str(command)], env)
        self.pid = pid
        self.fd = fd
        self.output = bytearray()
        self.status: int | None = None
        os.set_blocking(fd, False)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 160, 0, 0))

    def send(self, data: bytes) -> None:
        os.write(self.fd, data)

    def wait_for(self, text: str, timeout: float = 5.0, after: int = 0) -> None:
        needle = text.encode()
        deadline = time.monotonic() + timeout
        while needle not in self.output[after:] and time.monotonic() < deadline:
            ready, _, _ = select.select([self.fd], [], [], 0.05)
            if ready:
                try:
                    self.output.extend(os.read(self.fd, 65536))
                except (BlockingIOError, OSError):
                    pass
        if needle not in self.output[after:]:
            raise AssertionError(f"timed out waiting for {text!r}\n{self.text}")

    def pump(self, duration: float) -> None:
        """Drain terminal output while waiting, so the PTY cannot block fzf."""
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            ready, _, _ = select.select([self.fd], [], [], 0.02)
            if ready:
                try:
                    chunk = os.read(self.fd, 65536)
                    if not chunk:
                        break
                    self.output.extend(chunk)
                except (BlockingIOError, OSError):
                    break

    def finish(self, timeout: float = 8.0) -> tuple[int, str]:
        deadline = time.monotonic() + timeout
        while self.status is None and time.monotonic() < deadline:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
            if pid:
                self.status = status
                break
            ready, _, _ = select.select([self.fd], [], [], 0.05)
            if ready:
                try:
                    self.output.extend(os.read(self.fd, 65536))
                except (BlockingIOError, OSError):
                    pass
        if self.status is None:
            os.kill(self.pid, 9)
            os.waitpid(self.pid, 0)
            raise AssertionError(f"process did not exit\n{self.text}")
        while True:
            ready, _, _ = select.select([self.fd], [], [], 0)
            if not ready:
                break
            try:
                chunk = os.read(self.fd, 65536)
                if not chunk:
                    break
                self.output.extend(chunk)
            except (BlockingIOError, OSError):
                break
        return os.waitstatus_to_exitcode(self.status), self.text

    @property
    def text(self) -> str:
        return self.output.decode(errors="replace")


def fixture() -> tuple[tempfile.TemporaryDirectory[str], Path, dict[str, str], Path]:
    temporary = tempfile.TemporaryDirectory(prefix="start-lab-test.")
    root = Path(temporary.name)
    fake_bin = root / "bin"
    fake_bin.mkdir()
    gh = fake_bin / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(0o755)
    log = root / "gh.log"
    log.touch()
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{fake_bin}:{env['PATH']}",
            "GH_LOG": str(log),
            "TERM": "xterm-256color",
            "LC_ALL": "C",
        }
    )
    return temporary, root, env, log


def begin(run: PtyRun, name: str) -> None:
    run.wait_for("Lab directory name:")
    run.send(name.encode() + b"\n")


def search_and_save(run: PtyRun, query: str, expected: str, marks: int = 1) -> None:
    run.wait_for("GitHub query>")
    run.send(query.encode())  # Search updates without Enter.
    run.wait_for(expected)
    for _ in range(marks):
        run.send(b"\t")  # Toggle and persist, then move down.
        time.sleep(0.1)


def finish_and_confirm(run: PtyRun, answer: str = "y") -> tuple[int, str]:
    run.send(b"\x04")  # Ctrl-D
    run.wait_for("Create this lab? [y/N]")
    run.send(answer.encode() + b"\n")
    return run.finish()


def calls(log: Path) -> list[str]:
    return [part.decode() for part in log.read_bytes().split(b"\0") if part]


def test_multi_query_retention_quoting_layout_and_symlink() -> None:
    temporary, root, env, log = fixture()
    try:
        caller = root / "caller"
        caller.mkdir()
        launcher = root / "start-lab-link"
        launcher.symlink_to(START_LAB)
        run = PtyRun(launcher, caller, env)
        begin(run, "demo")
        search_and_save(run, "alpha", "Acme/One")
        run.send(b"\x15beta")  # Ctrl-U replaces the first query.
        run.wait_for("Acme/Two")
        run.send(b"\t")
        time.sleep(0.15)
        quoted = "odd ' \" $;$(touch SHOULD_NOT_EXIST)"
        run.send(b"\x15" + quoted.encode())
        run.wait_for("Acme/Quoted")
        run.send(b"\t")
        time.sleep(0.15)
        status, output = finish_and_confirm(run)
        target = caller / "demo"
        assert status == 0, output
        assert (target / "data").is_dir()
        assert (target / "docs").is_dir()
        assert (target / "projects" / "One" / "CLONED").read_text().strip() == "Acme/One"
        assert (target / "projects" / "Two" / "CLONED").read_text().strip() == "Acme/Two"
        assert (target / "projects" / "Quoted" / "CLONED").read_text().strip() == "Acme/Quoted"
        expected_agents = TEMPLATE.read_text().replace("{{WORKSPACE_NAME}}", "demo")
        assert (target / "AGENTS.md").read_text() == expected_agents
        assert not (caller / "SHOULD_NOT_EXIST").exists()
        history = calls(log)
        assert history.count("search:alpha") == 1
        assert history.count("search:beta") == 1
        assert history.count(f"search:{quoted}") == 1
        assert "Clone summary:" in output and "Lab created successfully:" in output
    finally:
        temporary.cleanup()


def test_escape_and_empty_query_create_nothing() -> None:
    temporary, root, env, log = fixture()
    try:
        run = PtyRun(START_LAB, root, env)
        begin(run, "cancelled")
        run.wait_for("GitHub query>")
        run.send(b"\r")
        time.sleep(0.1)
        run.send(b"\x1b")
        status, output = run.finish()
        assert status == 0, output
        assert not (root / "cancelled").exists()
        assert not any(call.startswith("search:") for call in calls(log))

        run = PtyRun(START_LAB, root, env)
        begin(run, "empty-selection")
        run.wait_for("GitHub query>")
        run.send(b"\x04")
        run.wait_for("Select at least one repository")
        run.send(b"\x1b")
        status, output = run.finish()
        assert status == 0, output
        assert "No repositories were saved" not in output
        assert not (root / "empty-selection").exists()
    finally:
        temporary.cleanup()


def test_ctrl_d_reviews_marked_repositories() -> None:
    temporary, root, env, _ = fixture()
    run = None
    try:
        run = PtyRun(START_LAB, root, env)
        begin(run, "marked-selection")
        run.wait_for("GitHub query>")
        run.send(b"alpha")
        run.wait_for("Acme/One")
        run.send(b"\t")
        time.sleep(0.1)
        run.send(b"\x04")  # Review must not require a separate Ctrl-A save.
        run.wait_for("Create this lab? [y/N]")
        run.send(b"n\n")
        status, output = run.finish()
        assert status == 0, output
        assert "  - Acme/One" in output
        assert "No repositories were saved" not in output
        assert not (root / "marked-selection").exists()
    finally:
        if run is not None and run.status is None:
            try:
                run.send(b"\x03")
            except OSError:
                pass  # The failing picker may already have exited.
            run.finish()
        temporary.cleanup()


def test_selection_survives_empty_error_and_revisit_then_can_be_removed() -> None:
    temporary, root, env, log = fixture()
    try:
        run = PtyRun(START_LAB, root, env)
        begin(run, "persistent")
        search_and_save(run, "alpha", "Acme/One")
        run.wait_for("1 selected")
        run.send(b"\x15empty")
        run.wait_for("No repositories found")
        run.send(b"\t")  # An informational row cannot be selected.
        run.wait_for("Choose a repository result first")
        run.send(b"\x15error")
        run.wait_for("SEARCH FAILED")
        run.send(b"\t")  # Nor can an API error row.
        time.sleep(0.1)
        offset = len(run.output)
        run.send(b"\x15alpha")
        run.wait_for("GitHub results", after=offset)
        run.send(b"\t")  # Revisiting and toggling removes the saved repo.
        run.wait_for("0 selected", after=offset)
        run.send(b"\r")
        run.wait_for("Select at least one repository")
        run.send(b"\t")
        run.wait_for("1 selected", after=offset)
        run.send(b"\r")  # Enter reviews; it no longer searches.
        run.wait_for("Create this lab? [y/N]")
        run.send(b"y\n")
        status, output = run.finish()
        assert status == 0, output
        clones = [call for call in calls(log) if call.startswith("clone:")]
        assert clones == [f"clone:Acme/One:{root.resolve()}/persistent/projects/One"], clones
    finally:
        temporary.cleanup()


def test_typing_is_debounced_and_empty_query_does_not_search() -> None:
    temporary, root, env, log = fixture()
    try:
        run = PtyRun(START_LAB, root, env)
        begin(run, "debounced")
        run.wait_for("GitHub query>")
        for letter in b"alpha":
            run.send(bytes([letter]))
            time.sleep(0.03)
        run.wait_for("Acme/One")
        offset = len(run.output)
        run.send(b"\x15")
        run.wait_for("Type to search GitHub", after=offset)
        run.send(b"\x1b")
        status, output = run.finish()
        assert status == 0, output
        assert [call for call in calls(log) if call.startswith("search:")] == ["search:alpha"]
        assert not (root / "debounced").exists()
    finally:
        temporary.cleanup()


def test_pending_search_does_not_block_toggling_or_replace_newer_results() -> None:
    temporary, root, env, log = fixture()
    try:
        run = PtyRun(START_LAB, root, env)
        begin(run, "responsive")
        run.wait_for("GitHub query>")
        run.send(b"alpha")
        run.wait_for("Acme/One")
        run.send(b"\x15slow")
        deadline = time.monotonic() + 3
        while "search:slow" not in calls(log) and time.monotonic() < deadline:
            run.pump(0.02)
        assert "search:slow" in calls(log), calls(log)
        run.send(b"\t")  # Select the still-visible result while GitHub is busy.
        run.wait_for("1 selected", timeout=1)
        run.send(b"\x15beta")
        run.wait_for("Acme/Two", timeout=1.5)  # Before the 2-second slow request.
        run.send(b"\t")
        run.wait_for("2 selected")
        run.pump(2.1)  # A late response must not replace these newer results.
        status, output = finish_and_confirm(run)
        assert status == 0, output
        assert "Acme/Stale" not in output
        assert (root / "responsive/projects/One/CLONED").exists()
        assert (root / "responsive/projects/Two/CLONED").exists()
        assert not (root / "responsive/projects/Stale").exists()
    finally:
        temporary.cleanup()


def test_no_confirmation_create_nothing() -> None:
    temporary, root, env, _ = fixture()
    try:
        run = PtyRun(START_LAB, root, env)
        begin(run, "declined")
        search_and_save(run, "alpha", "Acme/One")
        status, output = finish_and_confirm(run, "n")
        assert status == 0, output
        assert not (root / "declined").exists()
    finally:
        temporary.cleanup()


def test_name_existing_and_dangling_symlink_rejection() -> None:
    for name, setup in [
        ("", lambda root: None),
        (".", lambda root: None),
        ("..", lambda root: None),
        ("slash/name", lambda root: None),
        ("unsafe name", lambda root: None),
        ("-option", lambda root: None),
        ("existing", lambda root: (root / "existing").mkdir()),
        ("dangling", lambda root: (root / "dangling").symlink_to(root / "missing")),
    ]:
        temporary, root, env, _ = fixture()
        try:
            setup(root)
            run = PtyRun(START_LAB, root, env)
            begin(run, name)
            status, output = run.finish()
            assert status != 0, output
            assert "Error:" in output
            if name == "slash/name":
                assert not (root / "slash").exists()
        finally:
            temporary.cleanup()


def test_case_insensitive_basename_collision() -> None:
    temporary, root, env, _ = fixture()
    try:
        run = PtyRun(START_LAB, root, env)
        begin(run, "collision")
        search_and_save(run, "duplicate-one", "Acme/Same")
        run.send(b"\x15duplicate-two")
        run.wait_for("Other/same")
        run.send(b"\t")
        time.sleep(0.15)
        run.send(b"\x04")
        status, output = run.finish()
        assert status != 0, output
        assert "duplicate repository basename" in output
        assert not (root / "collision").exists()
    finally:
        temporary.cleanup()


def test_partial_clone_failure_preserves_success_and_is_nonzero() -> None:
    temporary, root, env, _ = fixture()
    try:
        run = PtyRun(START_LAB, root, env)
        begin(run, "partial")
        search_and_save(run, "mixed", "Acme/Good", marks=2)
        status, output = finish_and_confirm(run)
        target = root / "partial"
        assert status != 0, output
        assert (target / "projects" / "Good" / "CLONED").exists()
        assert not (target / "projects" / "Fail").exists()
        assert "OK     Acme/Good" in output
        assert "FAILED Acme/Fail" in output
    finally:
        temporary.cleanup()


def test_auth_failure_is_actionable() -> None:
    temporary, root, env, _ = fixture()
    try:
        env["GH_AUTH_FAIL"] = "1"
        run = PtyRun(START_LAB, root, env)
        status, output = run.finish()
        assert status != 0, output
        assert "gh auth login" in output
        assert "SSO" in output
    finally:
        temporary.cleanup()


def test_search_error_is_visible() -> None:
    temporary, root, env, _ = fixture()
    try:
        run = PtyRun(START_LAB, root, env)
        begin(run, "error-case")
        run.wait_for("GitHub query>")
        run.send(b"error")
        run.wait_for("SEARCH FAILED")
        run.send(b"\x1b")
        status, output = run.finish()
        assert status == 0, output
        assert "simulated API error" in output
        assert not (root / "error-case").exists()
    finally:
        temporary.cleanup()


def main() -> None:
    if shutil.which("fzf") is None:
        raise SystemExit("fzf is required to run these tests")
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    for test in sorted(tests, key=lambda item: item.__name__):
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(tests)} tests")


if __name__ == "__main__":
    main()
