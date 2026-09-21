# `start-lab`

`start-lab` creates a workspace in the directory where it is invoked and clones
selected GitHub repositories into `projects/`.

## Requirements

- An interactive terminal
- `gh`, authenticated with `gh auth login`
- `git`
- `fzf`

The command never installs dependencies or logs in for you. Repository search
and cloning are limited to repositories available to the authenticated GitHub
account, including any organization or SSO restrictions.

## Usage

From the directory that should contain the lab:

```sh
/path/to/pi-config/scripts/start-lab
```

Enter one safe directory name. The target must not already exist, including as
a dangling symlink.

The repository picker searches GitHub as you type. After typing stops for 250 ms,
the result list reloads with repository name, visibility, and description; an
empty query does not call GitHub. The details panel shows the highlighted
repository's details and a preview of every selected repository.

- **Tab / Shift-Tab** — immediately toggle the highlighted repository in the
  persistent selection and move to the next row
- **Enter / Ctrl-D** — review the full selection; these keys do not run a search
  or change the selection
- **Ctrl-R** — refresh the current query immediately
- **Ctrl-U** — clear the query
- **Ctrl-/** — show or hide the details and selection-preview panel
- **Esc** — cancel

Selections persist when the query changes, including across disjoint, empty, or
failed searches. Search for a selected repository again and toggle it to remove
it. Informational empty-query, no-results, and error rows cannot be selected. If
Enter or Ctrl-D is pressed with nothing selected, the picker stays open and asks
for at least one repository.

After a nonempty selection is submitted, the review shows the exact target and
repository identities before asking for confirmation. Cancellation or a declined
confirmation creates nothing.

After confirmation, the command uses `scripts/init-workspace.sh`, then clones
each repository's default branch into `projects/<repository-name>`. Clone
failures do not remove successful clones; the final summary reports each result
and the command exits nonzero if any clone failed.

## Tests

The focused tests use a fake `gh` and the real installed `fzf`; they do not make
network requests:

```sh
uv run tests/test-start-lab.py
```

## Deferred global installation

Do not install the global launcher until this repository has reached its final
location. After that move, create a symlink only if the destination is unused:

```sh
source=/absolute/final/path/to/pi-config/scripts/start-lab
destination="$HOME/.local/bin/start-lab"

if [ -e "$destination" ] || [ -L "$destination" ]; then
  printf 'Refusing to replace existing path: %s\n' "$destination" >&2
else
  ln -s "$source" "$destination"
fi
```

This does not edit shell configuration. `$HOME/.local/bin` must already be on
`PATH` to invoke `start-lab` by name. The script resolves symlinks, so its
initializer and template continue to resolve from the repository rather than
the caller's working directory.
