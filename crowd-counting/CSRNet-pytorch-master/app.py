"""
CSRNet FastAPI Web API Servisi
==============================
Bu servis, kalabalık sayma ve yoğunluk tahmini modelini HTTP API olarak sunar.
Admin panelleri veya dış sistemler için ideal entegrasyon aracıdır.

Endpoint'ler:
  - GET  /         : Sağlık kontrolü ve sistem bilgisi
  - POST /predict  : Görüntü yükleyip insan sayısı ve base64 yoğunluk görsellerini alma
"""

import os
import io
import base64
import time
import logging
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
import torch
from torchvision import transforms
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from matplotlib import pyplot as plt
from matplotlib import cm as CM

# model.py dosyasından CSRNet mimarisini içe aktarıyoruz
# app.py, CSRNet-pytorch-master altında olacağı için doğrudan import edebiliriz.
from model import CSRNet

# Log yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CSRNet-API")

# Küresel model önbelleği
models = {}
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Model train.py'deki ile aynı normalizasyon — ImageNet mean/std
_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


def load_cached_model(weights_filename: str):
    """Ağırlık dosyasını yükler ve modeli önbelleğe alır. Dosya eksikse Google Drive üzerinden otomatik indirir."""
    # Dosya yollarını dinamik olarak YOTAY kök dizininden çözüyoruz
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)  # c:\Users\bisol\Desktop\YOTAY
    weights_path = os.path.join(root_dir, weights_filename)
    
    # Dosya yoksa otomatik olarak Google Drive'dan indirmeyi dene
    if not os.path.exists(weights_path) or os.path.getsize(weights_path) == 0:
        logger.info(f"'{weights_filename}' eksik. Google Drive üzerinden indirilmeye çalışılıyor...")
        try:
            sys.path.insert(0, root_dir)
            from download_weights import download_weight_file
            download_weight_file(weights_filename, root_dir)
        except Exception as dl_err:
            logger.error(f"Otomatik model indirme hatası: {str(dl_err)}")

    if not os.path.exists(weights_path):
        logger.warning(f"Ağırlık dosyası bulunamadı: {weights_path}")
        return None
        
    try:
        model = CSRNet(load_weights=True)
        checkpoint = torch.load(weights_path, map_location=device, weights_only=False)
        model.load_state_dict(checkpoint['state_dict'])
        model.to(device)
        model.eval()
        logger.info(f"Model başarıyla belleğe yüklendi: {weights_filename} ({device})")
        return model
    except Exception as e:
        logger.error(f"Model yüklenirken hata oluştu ({weights_filename}): {str(e)}")
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama ömrü boyunca modelleri bellekte tutar."""
    logger.info("FastAPI uygulaması başlatılıyor. Modeller belleğe yükleniyor...")
    models['A'] = load_cached_model('PartAmodel_best.pth.tar')
    models['B'] = load_cached_model('partBmodel_best.pth.tar')
    yield
    logger.info("Uygulama kapatılıyor, kaynaklar temizleniyor...")
    models.clear()


app = FastAPI(
    title="CSRNet Kalabalık Yoğunluğu Ölçüm API'si",
    description="Güvenlik kameraları ve toplu taşıma araçları için insan yoğunluğu tahmini API'si.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS ayarları — Admin paneli farklı bir port veya domainden istek atabilir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def preprocess_image_data(img: Image.Image, max_size: Optional[int] = None):
    """Görüntüyü bellek üzerinde ön işler (In-memory preprocessing)."""
    img = img.convert('RGB')
    original_img = img.copy()
    scale_factor = 1.0
    
    # Büyük görüntüleri sınırla (OOM koruması)
    if max_size is not None:
        w, h = img.size
        max_dim = max(w, h)
        if max_dim > max_size:
            scale_factor = max_size / max_dim
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            # 8'in katına yuvarla
            new_w = (new_w // 8) * 8
            new_h = (new_h // 8) * 8
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            scale_factor = (new_w * new_h) / (w * h)
            
    # Boyutları 8'in katına getir
    w, h = img.size
    if w % 8 != 0 or h % 8 != 0:
        new_w = (w // 8) * 8
        new_h = (h // 8) * 8
        if new_w > 0 and new_h > 0:
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
    # Normalizasyon
    img_tensor = _transform(img)
    return img_tensor.unsqueeze(0), original_img, scale_factor


def convert_fig_to_base64(fig):
    """Matplotlib figürünü diske yazmadan Base64 formatına çevirir."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    base64_data = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{base64_data}"


@app.get("/")
def read_root():
    """Sağlık kontrolü ve sistem bilgisi döner."""
    return {
        "status": "active",
        "device": str(device),
        "cuda_available": torch.cuda.is_available(),
        "loaded_models": {
            "PartA (Yüksek Yoğunluk)": "Yüklendi ✅" if models.get('A') else "Eksik ❌",
            "PartB (Düşük Yoğunluk)": "Yüklendi ✅" if models.get('B') else "Eksik ❌"
        }
    }


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    model_type: str = Query('A', enum=['A', 'B'], description="A: PartA (Yüksek yoğunluk), B: PartB (Düşük yoğunluk)"),
    tta: bool = Query(False, description="Test-Time Augmentation (Horizontal Flip) uygulansın mı?"),
    max_size: Optional[int] = Query(None, description="Maksimum resim çözünürlük sınırı (Örn: 1920)")
):
    """
    Görüntü dosyası üzerinde kalabalık analizi yapar.
    Sayısal değeri ve base64 formatındaki density map ve overlay görsellerini döner.
    """
    # İlgili model yüklü mü kontrol et
    model = models.get(model_type)
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail=f"İstenen model ({model_type}) sunucu üzerinde yüklü/aktif değil."
        )

    # Dosya tipini kontrol et
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Lütfen geçerli bir resim dosyası yükleyin.")

    start_time = time.time()
    
    try:
        # Resmi belleğe oku
        file_bytes = await file.read()
        image = Image.open(io.BytesIO(file_bytes))
        
        # Ön işleme yap
        img_tensor, original_img, scale_factor = preprocess_image_data(image, max_size)
        img_tensor = img_tensor.to(device)
        
        # Inference çalıştır
        with torch.no_grad():
            output = model(img_tensor)
            density_map = output.detach().cpu().squeeze().numpy()
            count = density_map.sum()
            
            if tta:
                # Horizontal flip ile TTA
                img_flipped = torch.flip(img_tensor, dims=[3])
                output_flipped = model(img_flipped)
                density_flipped = output_flipped.detach().cpu().squeeze().numpy()
                
                # İki tahminin ortalaması
                density_map = (density_map + np.flip(density_flipped, axis=1)) / 2.0
                count = density_map.sum()

        # Ölçek faktörü düzeltmesi
        if scale_factor != 1.0:
            count = count / scale_factor

        # Görselleştirme oluşturma (Diski yormadan in-memory)
        # 1. Density Map görseli
        fig1 = plt.figure(figsize=(8, 6))
        plt.imshow(density_map, cmap=CM.jet)
        plt.axis('off')
        density_base64 = convert_fig_to_base64(fig1)

        # 2. Overlay görseli
        fig2 = plt.figure(figsize=(10, 8))
        orig_w, orig_h = original_img.size
        
        if density_map.max() > 0:
            density_normalized = density_map / density_map.max()
        else:
            density_normalized = density_map
            
        density_resized = np.array(
            Image.fromarray(density_normalized).resize((orig_w, orig_h), Image.Resampling.BILINEAR)
        )
        
        plt.imshow(original_img)
        plt.imshow(density_resized, cmap=CM.jet, alpha=0.5)
        plt.axis('off')
        overlay_base64 = convert_fig_to_base64(fig2)

        processing_time = (time.time() - start_time) * 1000  # ms

        return {
            "status": "success",
            "model_type": model_type,
            "predicted_count": round(float(count), 1),
            "processing_time_ms": round(processing_time, 1),
            "density_map_base64": density_base64,
            "overlay_base64": overlay_base64
        }

    except Exception as e:
        logger.error(f"Inference sırasında hata oluştu: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Resim işlenirken sunucu hatası oluştu: {str(e)}"
        )
