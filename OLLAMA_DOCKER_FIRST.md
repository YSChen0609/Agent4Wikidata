# Ollama Docker-First Guide (No docker-compose)

This guide shows how to run Ollama and your app with plain `docker run` commands only.

Verified against:
- Ollama Docker docs: <https://docs.ollama.com/docker>
- Ollama API (`/api/tags`): <https://docs.ollama.com/api/tags>
- Qwen2.5-Coder library/tags: <https://ollama.com/library/qwen2.5-coder>

## 1) Start Ollama in Docker

```powershell
docker volume create ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

Notes:
- Image name is `ollama/ollama` (official).
- API listens on port `11434`.

## 2) Pull a model (verified model names)

Recommended for this project (NL -> SPARQL):

```powershell
docker exec -it ollama ollama pull qwen2.5-coder:14b
```

Other valid options:

```powershell
docker exec -it ollama ollama pull qwen2.5-coder:7b
docker exec -it ollama ollama pull qwen2.5-coder:32b
```

All tags above are valid in Ollama's model library.

## 3) Verify local models in Ollama

```powershell
curl http://localhost:11434/api/tags
```

You should see your pulled model in the `models` array.

## 4) Run your app container (no compose)

From `<project_dir>`, build your app image if needed:

```powershell
cd "<project_dir>"
docker build -t ask-wikidata:latest .
```

Option A (inline env vars):

```powershell
docker run --rm -it `
  -e LLM_PROVIDER=ollama `
  -e LLM_MODEL=qwen2.5-coder:14b `
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 `
  ask-wikidata:latest
```

Option B (simpler, use `.env`):

```powershell
docker run --rm -it `
  --env-file ".\ask_wikidata\.env" `
  ask-wikidata:latest
```

Why `host.docker.internal`:
- It is the easiest way for one container (your app) to reach another service exposed on your host (`localhost:11434`) in Docker Desktop.

## 5) Put env in your project `.env` (recommended)

In `ask_wikidata/.env`:

```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:14b
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Then your Docker run command stays short:

```powershell
docker run --rm -it --env-file ".\ask_wikidata\.env" ask-wikidata:latest
```

Note on Docker env loading:
- `--env-file` injects variables directly into the container process and is the most reliable way in Docker runs.
- `python-dotenv` reads files from inside the container filesystem, so `--env-file` should remain your default for container execution.

Your code now also supports fallback variables:

```env
LLM_FALLBACK_PROVIDER=ollama
LLM_FALLBACK_MODEL=qwen2.5-coder:7b
```

## 6) Recommended model choice for this repo

- Start with `qwen2.5-coder:14b` (best quality/speed balance for NL-to-query tasks).
- Use `qwen2.5-coder:7b` if machine resources are tight.
- Move to `qwen2.5-coder:32b` if you need more robust query generation and have enough RAM/VRAM.

## 7) Quick troubleshooting

- `connection refused` from app container:
  - Confirm Ollama container is running: `docker ps`
  - Confirm API responds: `curl http://localhost:11434/api/tags`
  - Confirm `OLLAMA_BASE_URL=http://host.docker.internal:11434`

- Model not found:
  - Pull it first: `docker exec -it ollama ollama pull qwen2.5-coder:14b`
  - Recheck tags: `curl http://localhost:11434/api/tags`

- Port conflict on `11434`:
  - Run Ollama on another host port, e.g. `-p 11435:11434`
  - Update app env: `OLLAMA_BASE_URL=http://host.docker.internal:11435`

