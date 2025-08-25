# syntax=docker/dockerfile:1.2
FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip && pip install uv

# # NOTE: this presumes we're building from the repo root
COPY lib/ /app/lib/
COPY /src /app/power-tariffs/
COPY plugin_manifest.yaml /app/power-tariffs/plugin_manifest.yaml
COPY alembic.ini /app/power-tariffs/alembic.ini
COPY /static /app/power-tariffs/static
COPY uv.lock /app/power-tariffs/uv.lock

WORKDIR /app/power-tariffs

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system .

CMD ["power-tariffs", "run"]
