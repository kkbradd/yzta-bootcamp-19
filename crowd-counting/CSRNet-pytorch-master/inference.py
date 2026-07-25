"""
CSRNet Inference Modülü — Kalabalık Sayma Sistemi
====================================================
Herhangi bir kamera görüntüsünden insan yoğunluğu tahmini yapar.

Çıktılar:
    - Tahmini toplam insan sayısı
    - Yoğunluk haritası (Density Map) 
    - Orijinal görüntü üzerine overlay görselleştirme
    - JSON formatında sonuç raporu

Kullanım:
    # Tekil görüntü
    py inference.py --image foto.jpg --weights ../PartAmodel_best.pth.tar

    # Klasör bazlı toplu inference
    py inference.py --image-dir ./test_images/ --weights ../PartAmodel_best.pth.tar

    # TTA (Test-Time Augmentation) ile daha doğru tahmin
    py inference.py --image foto.jpg --weights ../PartAmodel_best.pth.tar --tta

    # Çıktı dizini belirtme
    py inference.py --image-dir ./test_images/ --weights ../PartAmodel_best.pth.tar --output-dir ./results/

    # Maksimum çözünürlük sınırlama (büyük görüntüler için)
    py inference.py --image foto.jpg --weights ../PartAmodel_best.pth.tar --max-size 1920
"""

import os
import sys
import glob
import json
import argparse
import time
from datetime import datetime

import numpy as np
import torch
import torchvision.transforms.functional as F
from torchvision import transforms
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib import cm as CM
import matplotlib.colors as mcolors

from model import CSRNet

# Model train.py'deki ile ayni normalizasyon — ImageNet mean/std
_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


# ──────────────────────────────────────────────────────────
#  Cihaz ve Model Yönetimi
# ──────────────────────────────────────────────────────────

def get_device():
    """Mevcut en iyi hesaplama cihazını tespit eder."""
    if torch.cuda.is_available():
        device = torch.device('cuda')
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"🟢 GPU: {gpu_name} ({gpu_mem:.1f} GB)")
    else:
        device = torch.device('cpu')
        print("🟡 CPU modu (GPU bulunamadı)")
    return device


def load_model(weights_path, device):
    """
    CSRNet modelini yükler ve pretrained ağırlıkları uygular.
    
    Args:
        weights_path: .pth.tar ağırlık dosyasının yolu
        device: torch.device
    
    Returns:
        model: Eval modunda CSRNet modeli
    """
    if not os.path.exists(weights_path):
        print(f"❌ Ağırlık dosyası bulunamadı: {weights_path}")
        sys.exit(1)
    
    model = CSRNet(load_weights=True)
    checkpoint = torch.load(weights_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['state_dict'])
    model.to(device)
    model.eval()
    
    file_size_mb = os.path.getsize(weights_path) / (1024 * 1024)
    print(f"✅ Model yüklendi: {os.path.basename(weights_path)} ({file_size_mb:.1f} MB)")
    
    return model


# ──────────────────────────────────────────────────────────
#  Ön İşleme (Preprocessing)
# ──────────────────────────────────────────────────────────

def preprocess_image(img_path, max_size=None):
    """
    Goruntuyu CSRNet inference icin on isler.
    
    Preprocessing adimlari:
    1. RGB'ye donusturme
    2. (Opsiyonel) Boyut sinlrlama — en-boy orani korunarak
    3. ImageNet mean/std normalizasyonu (train.py ile ayni)
    
    Args:
        img_path: Goruntu dosya yolu
        max_size: Maksimum boyut (piksel). None ise orijinal boyut korunur.
    
    Returns:
        img_tensor: (1, 3, H, W) tensor
        original_img: PIL Image (gorsellestirme icin)
        scale_factor: Uygulanan olcek faktoru
    """
    img = Image.open(img_path).convert('RGB')
    original_img = img.copy()
    scale_factor = 1.0
    
    # Buyuk goruntuleri sinirla (bellek korumasi, en-boy orani korunur)
    if max_size is not None:
        w, h = img.size
        max_dim = max(w, h)
        if max_dim > max_size:
            scale_factor = max_size / max_dim
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            # 8'in katina yuvarla (CSRNet 3 kez 2x downsampling yapar = 8x)
            new_w = (new_w // 8) * 8
            new_h = (new_h // 8) * 8
            img = img.resize((new_w, new_h), Image.LANCZOS)
            scale_factor = (new_w * new_h) / (w * h)
    
    # Boyutlari 8'in katina getir (gerekirse)
    w, h = img.size
    if w % 8 != 0 or h % 8 != 0:
        new_w = (w // 8) * 8
        new_h = (h // 8) * 8
        if new_w > 0 and new_h > 0:
            img = img.resize((new_w, new_h), Image.LANCZOS)
    
    # Standart ImageNet normalizasyonu (train.py ile ayni)
    img_tensor = _transform(img)
    
    return img_tensor.unsqueeze(0), original_img, scale_factor


# ──────────────────────────────────────────────────────────
#  Inference
# ──────────────────────────────────────────────────────────

def predict_single(model, img_path, device, max_size=None, use_tta=False):
    """
    Tek bir görüntü için kalabalık sayma tahmini yapar.
    
    Args:
        model: Yüklenmiş CSRNet modeli
        img_path: Görüntü dosya yolu
        device: torch.device
        max_size: Maksimum boyut sınırı
        use_tta: Test-Time Augmentation kullanılsın mı
    
    Returns:
        dict: {
            'count': float,           # Tahmini insan sayısı
            'density_map': np.array,  # Density map
            'original_img': PIL.Image,# Orijinal görüntü
            'processing_time': float  # İşlem süresi (ms)
        }
    """
    start_time = time.time()
    
    img_tensor, original_img, scale_factor = preprocess_image(img_path, max_size)
    img_tensor = img_tensor.to(device)
    
    with torch.no_grad():
        output = model(img_tensor)
        density_map = output.detach().cpu().squeeze().numpy()
        count = density_map.sum()
        
        if use_tta:
            # Horizontal flip augmentation
            img_flipped = torch.flip(img_tensor, dims=[3])
            output_flipped = model(img_flipped)
            density_flipped = output_flipped.detach().cpu().squeeze().numpy()
            
            # İki tahminin ortalaması
            density_map = (density_map + np.flip(density_flipped, axis=1)) / 2.0
            count = density_map.sum()
    
    # Ölçek düzeltmesi (görüntü küçültüldüyse)
    if scale_factor != 1.0:
        count = count / scale_factor
    
    processing_time = (time.time() - start_time) * 1000  # ms
    
    return {
        'count': float(count),
        'density_map': density_map,
        'original_img': original_img,
        'processing_time': processing_time
    }


# ──────────────────────────────────────────────────────────
#  Görselleştirme
# ──────────────────────────────────────────────────────────

def save_density_map(density_map, save_path):
    """Density map'i renkli görüntü olarak kaydeder."""
    plt.figure(figsize=(12, 8))
    plt.imshow(density_map, cmap=CM.jet)
    plt.colorbar(label='Yoğunluk', shrink=0.8)
    plt.title(f'Density Map — Toplam: {density_map.sum():.0f} kişi', fontsize=14)
    plt.axis('off')
    plt.savefig(save_path, dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close()


def save_overlay(original_img, density_map, count, save_path):
    """Orijinal görüntü üzerine density map overlay kaydeder."""
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    # 1. Orijinal görüntü
    axes[0].imshow(original_img)
    axes[0].set_title('Orijinal Görüntü', fontsize=13, fontweight='bold')
    axes[0].axis('off')
    
    # 2. Density map
    im = axes[1].imshow(density_map, cmap=CM.jet)
    axes[1].set_title(f'Yoğunluk Haritası', fontsize=13, fontweight='bold')
    axes[1].axis('off')
    plt.colorbar(im, ax=axes[1], shrink=0.8)
    
    # 3. Overlay
    # Density map'i orijinal görüntü boyutuna resize et
    from PIL import ImageFilter
    orig_w, orig_h = original_img.size
    
    # Density map'i normalize et ve orijinal boyuta resize et
    if density_map.max() > 0:
        density_normalized = density_map / density_map.max()
    else:
        density_normalized = density_map
    
    density_resized = np.array(
        Image.fromarray(density_normalized).resize((orig_w, orig_h), Image.BILINEAR)
    )
    
    # Overlay: orijinal görüntü + yarı-saydam heatmap
    axes[2].imshow(original_img)
    axes[2].imshow(density_resized, cmap=CM.jet, alpha=0.5)
    axes[2].set_title('Overlay', fontsize=13, fontweight='bold')
    axes[2].axis('off')
    
    plt.suptitle(f'Tahmini İnsan Sayısı: {count:.0f}',
                 fontsize=16, fontweight='bold', color='#2c3e50')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ──────────────────────────────────────────────────────────
#  Toplu İşlem ve Raporlama
# ──────────────────────────────────────────────────────────

def process_images(model, img_paths, device, output_dir, max_size=None, use_tta=False):
    """
    Birden fazla görüntüyü toplu işler.
    
    Args:
        model: CSRNet modeli
        img_paths: Görüntü yolları listesi
        device: torch.device
        output_dir: Çıktı dizini
        max_size: Maksimum boyut
        use_tta: TTA aktif mi
    
    Returns:
        results: Sonuç listesi
    """
    os.makedirs(output_dir, exist_ok=True)
    density_dir = os.path.join(output_dir, 'density_maps')
    overlay_dir = os.path.join(output_dir, 'overlays')
    os.makedirs(density_dir, exist_ok=True)
    os.makedirs(overlay_dir, exist_ok=True)
    
    results = []
    total_count = 0
    total_time = 0
    
    print(f"\n{'═'*60}")
    print(f"  CSRNet Kalabalık Sayma — {len(img_paths)} Görüntü")
    print(f"  TTA: {'Açık ✅' if use_tta else 'Kapalı'}")
    print(f"  Çıktı: {output_dir}")
    print(f"{'═'*60}\n")
    
    for i, img_path in enumerate(img_paths):
        img_name = os.path.splitext(os.path.basename(img_path))[0]
        
        try:
            result = predict_single(model, img_path, device, max_size, use_tta)
            
            # Density map kaydet
            density_path = os.path.join(density_dir, f'{img_name}_density.png')
            save_density_map(result['density_map'], density_path)
            
            # Overlay kaydet
            overlay_path = os.path.join(overlay_dir, f'{img_name}_overlay.png')
            save_overlay(result['original_img'], result['density_map'],
                         result['count'], overlay_path)
            
            total_count += result['count']
            total_time += result['processing_time']
            
            results.append({
                'image': os.path.basename(img_path),
                'image_path': os.path.abspath(img_path),
                'predicted_count': round(result['count'], 1),
                'processing_time_ms': round(result['processing_time'], 1),
                'density_map_path': os.path.abspath(density_path),
                'overlay_path': os.path.abspath(overlay_path)
            })
            
            print(f"  [{i+1:3d}/{len(img_paths)}] {os.path.basename(img_path):30s} "
                  f"→ {result['count']:7.1f} kişi  ({result['processing_time']:.0f} ms)")
            
        except Exception as e:
            print(f"  [{i+1:3d}/{len(img_paths)}] ❌ {os.path.basename(img_path)}: {str(e)}")
            results.append({
                'image': os.path.basename(img_path),
                'error': str(e)
            })
    
    # Özet rapor
    valid_results = [r for r in results if 'predicted_count' in r]
    counts = [r['predicted_count'] for r in valid_results]
    
    print(f"\n{'═'*60}")
    print(f"  📊 SONUÇ ÖZETİ")
    print(f"{'═'*60}")
    print(f"  İşlenen görüntü     : {len(valid_results)}/{len(img_paths)}")
    print(f"  Toplam tahmini kişi  : {total_count:.0f}")
    print(f"  Ortalama kişi/görüntü: {np.mean(counts):.1f}" if counts else "")
    print(f"  Min kişi sayısı      : {min(counts):.1f}" if counts else "")
    print(f"  Max kişi sayısı      : {max(counts):.1f}" if counts else "")
    print(f"  Toplam süre          : {total_time/1000:.1f} s")
    print(f"  Ortalama süre/görüntü: {total_time/len(valid_results):.0f} ms" if valid_results else "")
    
    # JSON rapor kaydet
    report = {
        'timestamp': datetime.now().isoformat(),
        'model_weights': os.path.basename(args.weights) if 'args' in dir() else 'N/A',
        'device': str(device),
        'tta_enabled': use_tta,
        'total_images': len(img_paths),
        'total_predicted_count': round(total_count, 1),
        'average_count': round(np.mean(counts), 1) if counts else 0,
        'total_processing_time_s': round(total_time / 1000, 2),
        'results': results
    }
    
    report_path = os.path.join(output_dir, 'inference_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n  📄 JSON rapor: {report_path}")
    print(f"  🖼️  Density map'ler: {density_dir}")
    print(f"  🎨 Overlay'ler: {overlay_dir}")
    
    return results


# ──────────────────────────────────────────────────────────
#  Ana Giriş Noktası
# ──────────────────────────────────────────────────────────

def main():
    global args
    
    parser = argparse.ArgumentParser(
        description='CSRNet Kalabalık Sayma — Inference Aracı',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Tekil görüntü
  py inference.py --image foto.jpg --weights ../PartAmodel_best.pth.tar

  # Klasör bazlı toplu inference
  py inference.py --image-dir ./test_images/ --weights ../PartAmodel_best.pth.tar

  # TTA ile daha doğru tahmin
  py inference.py --image foto.jpg --weights ../PartAmodel_best.pth.tar --tta

  # Büyük görüntüler için boyut sınırı
  py inference.py --image foto.jpg --weights ../PartAmodel_best.pth.tar --max-size 1920
        """)
    
    # Giriş kaynağı (biri zorunlu)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--image', type=str,
                             help='Tek bir görüntü dosyası yolu')
    input_group.add_argument('--image-dir', type=str,
                             help='Görüntü klasörü yolu (jpg, png, bmp)')
    
    # Model
    parser.add_argument('--weights', type=str, required=True,
                        help='Pretrained ağırlık dosyası (.pth.tar)')
    
    # Çıktı
    parser.add_argument('--output-dir', type=str, default='inference_results',
                        help='Çıktı dizini (varsayılan: inference_results)')
    
    # İyileştirmeler
    parser.add_argument('--tta', action='store_true',
                        help='Test-Time Augmentation (horizontal flip ortalaması)')
    parser.add_argument('--max-size', type=int, default=None,
                        help='Maksimum görüntü boyutu (piksel). Büyük görüntülerde bellek tasarrufu.')
    
    args = parser.parse_args()
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        CSRNet — Kalabalık Sayma Inference Aracı        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # Cihaz tespiti
    device = get_device()
    
    # Model yükleme
    model = load_model(args.weights, device)
    
    # Görüntü listesi oluşturma
    if args.image:
        if not os.path.exists(args.image):
            print(f"❌ Görüntü bulunamadı: {args.image}")
            sys.exit(1)
        img_paths = [args.image]
    else:
        if not os.path.isdir(args.image_dir):
            print(f"❌ Klasör bulunamadı: {args.image_dir}")
            sys.exit(1)
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
        img_paths = []
        for ext in extensions:
            img_paths.extend(glob.glob(os.path.join(args.image_dir, ext)))
            img_paths.extend(glob.glob(os.path.join(args.image_dir, ext.upper())))
        img_paths = sorted(list(set(img_paths)))
        
        if not img_paths:
            print(f"❌ Desteklenen formatta görüntü bulunamadı: {args.image_dir}")
            sys.exit(1)
    
    print(f"📂 {len(img_paths)} görüntü işlenecek")
    
    # Inference çalıştır
    process_images(model, img_paths, device, args.output_dir,
                   max_size=args.max_size, use_tta=args.tta)
    
    print(f"\n✅ Inference tamamlandı!")


if __name__ == '__main__':
    main()
