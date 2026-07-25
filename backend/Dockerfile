FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.10.10 /uv /uvx /bin/

# OpenJarvis (AI_MOTOR=local yolu) PyPI'da olmadığı için SHA-pinli git
# bağımlılığıdır; kurulum git ister.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /uygulama

# Önce yalnız bağımlılıklar: kod değişikliği bu katmanı bozmaz,
# --frozen kilit dosyasıyla birebir aynı sürümleri kurar.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app
RUN uv sync --frozen --no-dev

ENV PATH="/uygulama/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:uygulama", "--host", "0.0.0.0", "--port", "8000"]
