FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.10.10 /uv /uvx /bin/

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
