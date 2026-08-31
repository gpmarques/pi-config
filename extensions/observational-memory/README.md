# Observational memory

This is a documentation-only external stub for **[elpapi42/pi-observational-memory](https://github.com/elpapi42/pi-observational-memory)**. It contains no extension entry point and must not be copied as an implementation.

## Pinned installation

Install the reviewed published package, not the repository's moving `master` branch:

```bash
pi install npm:pi-observational-memory@3.0.4
```

Pi records the exact source string `npm:pi-observational-memory@3.0.4` in global `settings.json`; versioned npm package sources are skipped by package updates. The npm working directory may express the dependency as `^3.0.4`, but the Pi package source is the controlling pin. Published 3.0.4 identifies the upstream repository as `elpapi42/pi-observational-memory` and npm git head `e07d2b2451496a69dec5bbd2109d2fbe96900880`. Upstream explicitly describes `master` as active, potentially unreleased development, so do not replace this install with git `master` without a new review.

V3 is incompatible with V2 settings and memory records. Upgrade into a new clean Pi session and use only the V3 keys shown below.

## V3 architecture and surfaces

Published 3.0.4 does not use parallel observer subprocesses. It runs one branch-local consolidation pipeline per extension runtime:

1. An observer converts newly covered source entries into observations.
2. A reflector derives durable reflections after its token threshold.
3. A dropper can tombstone active observations after a successful reflection when the active pool exceeds its target.
4. `session_before_compact` folds the prepared ledger into a deterministic summary without another model call.

The append-only V3 ledger lives in the Pi session JSONL as custom entries (`om.observations.recorded`, `om.reflections.recorded`, and `om.observations.dropped`). Compaction projections are stored in `om.folded` compaction details. Folding and recall follow the current session branch; there is no vendored implementation, global topic database, or hidden project-level topic store in this project.

Registered surfaces:

- `/om:status` — counts, worker state/errors, pool pressure, and token clocks.
- `/om:view` and `/om:view full` — visible or full branch memory; also attempt to copy it to the system clipboard.
- `recall` — agent tool for source evidence behind a known 12-character observation/reflection ID; it is not semantic search.

## Verified local worker configuration

The global namespace used on this machine is:

```json
{
  "observational-memory": {
    "observerChunkMaxTokens": 6000,
    "model": {
      "provider": "llama-local",
      "id": "qwen3.8-27b-q4km-om",
      "thinking": "off"
    }
  }
}
```

`llama-local/qwen3.8-27b-q4km-om` is a text-only OpenAI Chat Completions model with a 32,768-token context window, 4,096 maximum output tokens, zero local costs, and Qwen chat-template thinking controls. The explicit model block prevents normal operation from depending on the active session model. A 6,000-token observer chunk cap is conservative for the 32K context because it leaves room for the worker system prompt, existing memory, tool schema, and response.

### Exact command verified on this machine

The model is the official [`ggml-org/Qwen3.8-27B-GGUF`](https://huggingface.co/ggml-org/Qwen3.8-27B-GGUF) Q4_K_M file. Its verified SHA-256 is:

```text
31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34
```

Start the server manually in its own terminal:

```bash
MODEL="$HOME/Models/hf-hub/models--ggml-org--Qwen3.8-27B-GGUF/snapshots/0669b98607d47046c7c2b3f801011d54a08cfccf/Qwen3.8-27B-Q4_K_M.gguf"

llama-server \
  --model "$MODEL" \
  --alias qwen3.8-27b-q4km-om \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 32768 \
  --n-gpu-layers all \
  --flash-attn on \
  --parallel 1 \
  --jinja \
  --reasoning off \
  --no-mmproj \
  --offline \
  --no-ui
```

This uses Metal offload, disables vision-projector discovery, prevents remote model loading, enables the Jinja tool-calling template with server-side reasoning disabled, disables the web UI, and binds only to loopback. `--parallel 1` is intentional: this V3 implementation serializes observer → reflector → dropper behind one `consolidationInFlight` guard, and its nested agent tools execute sequentially. It does not need the four slots associated with the other implementation.

There is deliberately no LaunchAgent, daemon, login item, shell-profile hook, or auto-start. Stop the foreground server with `Ctrl+C`; verify release with `lsof -nP -iTCP:8080 -sTCP:LISTEN`.

Basic local checks after startup:

```bash
curl -fsS http://127.0.0.1:8080/v1/models
pi --offline --list-models qwen3.8-27b-q4km-om
```

## Storage, privacy, and accepted 3.0.4 caveats

- Source conversation excerpts, observations, and reflections are sent to the configured worker model. With the command above they stay on a loopback-only local server; the model file loads offline.
- Memory records and their source IDs persist inside normal Pi session files. Anyone who can read those sessions can read or recall that material. `/om:view` also writes rendered memory to the OS clipboard when clipboard support succeeds.
- `debugLog` remains false, so this setup does not create observational-memory NDJSON debug logs.
- Published 3.0.4 falls back to the session model if the configured provider/model ID cannot be found (the warning is UI-only). That fallback could be remote. Keep the exact alias in `models.json`, verify it with `pi --list-models`, and treat a missing alias as a stop condition rather than relying on fallback. A stopped local server instead produces a worker stream failure; it does not justify switching the configuration to a remote model.
- Published 3.0.4 has no `session_shutdown` handler to cancel or await a worker already in flight. Avoid reloading, replacing sessions, or exiting while `/om:status` reports consolidation in flight.
- Its compaction hook always supplies its own result. If no prepared observations/reflections are available, that result can be an empty summary instead of falling back to Pi's normal model summarizer. Do not force early compaction in a fresh session expecting the native summarizer.
- V3 observations are model-generated compression, not ground truth. Use `recall` when exact wording or provenance materially affects the next action.

These lifecycle and empty-compaction behaviors are known limitations accepted for the pinned npm 3.0.4 setup; installing newer git code implicitly is not the remedy.
