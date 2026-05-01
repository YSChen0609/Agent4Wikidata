# Docker Workflow (ASK-WIKIDATA)

This project is set up to use `pyproject.toml` + `uv.lock` as the source of truth for dependencies.

## Current status

- `uv.lock` already exists and matches the current `pyproject.toml`.
- Docker installs with `uv sync --frozen`, so image builds are deterministic.

## When you change dependencies

If you add or update packages in `[project].dependencies`, refresh the lockfile before rebuilding.

### Option A: Update lockfile with local `uv`

```powershell
cd "<project_dir>"
uv lock --python 3.12
```

### Option B: Update lockfile in a container (no local `uv` required)

```powershell
cd "<project_dir>"
docker build -t ask-wikidata:latest .
docker run --rm `
  -v "${PWD}:/app" `
  -w /app `
  --entrypoint uv `
  ask-wikidata:latest `
  lock --python 3.12
```

If you previously mounted a Linux-created `.venv` into Windows and see interpreter-link warnings, remove the host `.venv` and run the command again.

Then rebuild:

```powershell
docker build -t ask-wikidata:latest .
```

## Development mode (mount source)

Use a bind mount so local code changes are reflected immediately in the container.

```powershell
cd "<project_dir>"
docker run --rm -it `
  -v "${PWD}:/app" `
  -w /app `
  --entrypoint /bin/bash `
  ask-wikidata:latest
```

Inside the container shell:

```sh
uv sync --frozen
ask-wikidata --help
ask-wikidata hello Dev
```

Notes:
- This is best for iterative development and debugging.
- If dependencies changed but image was not rebuilt, run `uv sync --frozen` in the mounted container.
- You can skip `uv sync --frozen` only if all are true: you just rebuilt the image, you did not change dependency files since build, and you are not overriding the environment path.
- Keep `uv sync --frozen` as the default in dev shells; it quickly verifies lockfile consistency and prevents drift.
- Prefer `/bin/bash` over `/bin/sh` for interactive use (arrow keys and tab behavior are better).

### Optional: Typer tab-completion in the dev shell

After entering the container with `bash`, run:

```bash
eval "$(_ASK_WIKIDATA_COMPLETE=bash_source ask-wikidata)"
```

This enables shell completion for the current session. Add the same line to `~/.bashrc` in the container if you want it auto-enabled in that shell environment.

## Working with Ollama (from Docker)

When `LLM_PROVIDER=ollama`, the app in container must reach the Ollama server running on your host machine.

### 1) Start Ollama on host

On your host, make sure Ollama is running and has the model you want:

```powershell
ollama serve
ollama list
```

### 2) Run container with host mapping + Ollama URL

Use `host.docker.internal` so the container can connect to host Ollama:

```powershell
cd "<project_dir>"
docker run --rm -it `
  --add-host=host.docker.internal:host-gateway `
  -e LLM_PROVIDER=ollama `
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 `
  -v "${PWD}:/app" `
  -w /app `
  --entrypoint /bin/bash `
  ask-wikidata:latest
```

Inside the container shell:

```bash
uv sync --frozen
python ask_wikidata/sparql_query_graph.py
```

### 3) Quick connectivity check (optional)

If you see connection errors, verify Ollama endpoint from inside the container:

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://host.docker.internal:11434/api/tags', timeout=5).status)"
```

Expected output is `200`.

Notes:
- `localhost` inside container points to the container itself, not your host.
- If `Network is unreachable` appears, check `OLLAMA_BASE_URL` and ensure Docker can resolve `host.docker.internal`.
- This only solves LLM connectivity; Wikidata tool calls still need normal outbound internet access.

## Production-style mode (direct run, no source mount)

Build once, then run immutable image commands:

```powershell
cd "<project_dir>"
docker build -t ask-wikidata:latest .
docker run --rm ask-wikidata:latest --help
docker run --rm ask-wikidata:latest hello Prod
```

Notes:
- No local files are mounted.
- Behavior depends only on image contents (`pyproject.toml`, `uv.lock`, code copied at build time).

## Performance notes

- First runs are slower due to cold image/container startup and initial dependency installation.
- For code-only changes, prefer `docker run` on an existing image; rebuild only when dependencies or Dockerfile inputs change.
- In development, `uv sync --frozen` is a consistency check; skip it only when you are sure lockfile and environment have not changed.

## Why `.venv` is still referenced

- The container uses `/app/.venv` as its internal environment path.
- Your host `.venv` is not required and is excluded by `.dockerignore`.
- You can stay fully Docker-first and never create a host `.venv`.
