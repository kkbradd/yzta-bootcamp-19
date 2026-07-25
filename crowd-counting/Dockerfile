# Resmi PyTorch CUDA 12.4 imajını taban alıyoruz
FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime

# Etkileşimsiz kurulum ve Python optimizasyonları
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Çalışma dizinini ayarlıyoruz
WORKDIR /app

# OpenCV ve sistem kütüphaneleri için gerekli sistem bağımlılıklarını kuruyoruz
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılık dosyasını kopyalayıp python paketlerini kuruyoruz
# (İmaj içindeki CUDA destekli PyTorch ve Torchvision sürümlerini korumak için requirements'ta torch listelenmemiştir)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını çalışma dizinine kopyalıyoruz
COPY . .

# Çalışma dizinini CSRNet-pytorch-master olarak ayarlıyoruz
WORKDIR /app/CSRNet-pytorch-master

# FastAPI web API için varsayılan port
EXPOSE 8000

# Varsayılan komut: Uvicorn ile FastAPI uygulaması başlatılır
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
