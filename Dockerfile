# syntax=docker/dockerfile:1.2
FROM python:3.11-slim

WORKDIR /power-tariffs

RUN pip install --upgrade pip && pip install uv

# # NOTE: this presumes we're building from the repo root
COPY /src ./src
COPY plugin_manifest.yaml ./plugin_manifest.yaml
COPY /static ./static
COPY /data ./data

COPY pyproject.toml .
COPY uv.lock .

COPY alembic.ini .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system .

CMD ["power-tariffs", "run"]
