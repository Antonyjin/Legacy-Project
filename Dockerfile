# syntax=docker/dockerfile:1.7

# Builder: create Python venv with deps
FROM python:3.11-slim AS builder

ENV VIRTUAL_ENV=/opt/venv \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends build-essential curl ca-certificates; \
    python -m venv "$VIRTUAL_ENV"; \
    . "$VIRTUAL_ENV/bin/activate"; \
    pip install --upgrade pip

WORKDIR /tmp/app
COPY requirements.txt ./
RUN . "$VIRTUAL_ENV/bin/activate" && pip install -r requirements.txt

# Runtime: slim image with app and GeneWeb assets
FROM python:3.11-slim AS runtime

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    GW_DIR=/app/GeneWeb/gw \
    BASES_DIR=/app/GeneWeb/bases \
    BACKEND=ocaml \
    FLASK_PORT=23182 \
    OCAML_GWD_PORT=2317

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends tini ca-certificates curl; \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY python_app/ ./python_app/
COPY GeneWeb/ ./GeneWeb/
COPY docker/entrypoint.sh /entrypoint.sh

RUN set -eux; \
    addgroup --system geneweb && adduser --system --ingroup geneweb geneweb; \
    mkdir -p "$BASES_DIR/etc"; \
    chown -R geneweb:geneweb /app /entrypoint.sh; \
    chmod +x /entrypoint.sh

USER geneweb

EXPOSE 2317 23182

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD curl -fsS http://127.0.0.1:${FLASK_PORT}/health || exit 1

ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["/entrypoint.sh"]
