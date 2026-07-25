FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.10.10 /uv /uvx /bin/

WORKDIR /uygulama

# Önce yalnız bağımlılıklar: kod değişikliği bu katmanı bozmaz,
# --frozen kilit dosyasıyla birebir aynı sürümleri kurar.
# --extra csrnet: torch + OpenCV imaja dahil edilir. torch CPU tekerleği ayrı
# index'ten gelir; varsayılan PyPI sürümü CUDA kitaplıklarıyla ~1 GB daha büyük.
# opencv-python-headless bilinçli: düz opencv-python slim imajda libGL.so.1
# bulamayıp ImportError veriyor.
ENV UV_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra csrnet --no-install-project

COPY app ./app
RUN uv sync --frozen --no-dev --extra csrnet

ENV PATH="/uygulama/.venv/bin:$PATH"

# Model ağırlığı ve video imaja gömülmez; compose salt-okunur bağlar.
# Konteyner çalışırken ağa hiç çıkmaz: indirme adımı yoktur.
CMD ["python", "-m", "app.calistir"]
