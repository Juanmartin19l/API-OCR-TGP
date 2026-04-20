FROM ghcr.io/astral-sh/uv:python3.12-trixie

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --index-strategy unsafe-best-match

COPY app/ ./app/

ENV UV_COMPILE_BYTECODE=1
ENV DISABLE_MODEL_SOURCE_CHECK=1

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
