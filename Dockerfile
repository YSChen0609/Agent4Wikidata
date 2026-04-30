# Reproducible install from pyproject.toml + uv.lock (frozen graph).
# See DOCKER_WORKFLOW.md for dev/prod run patterns and lockfile update commands.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY ask_wikidata ./ask_wikidata

RUN uv sync --frozen --no-cache

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["ask-wikidata"]
CMD ["--help"]
