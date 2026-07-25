"""
CSRNet Validasyon Scripti — ShanghaiTech Dataset
==================================================
Pretrained ağırlıkları yükleyerek ShanghaiTech test seti üzerinde
MAE (Mean Absolute Error) hesaplar.

Kullanım:
    py validate.py --weights ../PartAmodel_best.pth.tar --dataset-root ../ShanghaiTech_Crowd_Counting_Dataset --part A
    py validate.py --weights ../partBmodel_best.pth.tar --dataset-root ../ShanghaiTech_Crowd_Counting_Dataset --part B
"""

import os
import sys
import glob
import argparse

import numpy as np
import h5py
import torch
import torchvision.transforms.functional as F
from torchvision import transforms
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib import cm as CM

from model import CSRNet

# Model train.py'deki ile aynı normalizasyon — ImageNet mean/std
_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


def get_device():
    """Mevcut en iyi cihazı döndürür."""
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"🟢 GPU kullanılıyor: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device('cpu')
        print("🟡 CPU kullanılıyor (GPU bulunamadı)")
    return device


def load_model(weights_path, device):
    """
    CSRNet modelini yükler ve pretrained ağırlıkları uygular.
    
    Args:
        weights_path: .pth.tar ağırlık dosyasının yolu
        device: torch device
    
    Returns:
        Ağırlıkları yüklenmiş model (eval modunda)
    """
    # load_weights=True: VGG16 pretrained indirilmesin, biz kendi ağırlığımızı yükleyeceğiz
    model = CSRNet(load_weights=True)
    
    checkpoint = torch.load(weights_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['state_dict'])
    model.to(device)
    model.eval()
    
    epoch = checkpoint.get('epoch', 'N/A')
    best_mae = checkpoint.get('best_prec1', 'N/A')
    print(f"✅ Model yüklendi: {os.path.basename(weights_path)}")
    print(f"   Epoch: {epoch}, Kaydedilen en iyi MAE: {best_mae}")
    
    return model


def preprocess_image(img_path):
    """
    Görüntüyü CSRNet inference için ön işler.
    
    train.py ile aynı normalizasyon:
    - RGB'ye dönüştür
    - ToTensor ile [0, 1] aralığına ölçekle
    - ImageNet mean/std ile normalize et
    
    Args:
        img_path: Görüntü dosya yolu
    
    Returns:
        img_tensor: (1, 3, H, W) boyutunda tensor
    """
    img = Image.open(img_path).convert('RGB')
    img_tensor = _transform(img)
    
    return img_tensor.unsqueeze(0)  # Batch boyutu ekle


def validate(model, img_paths, device, show_samples=0, output_dir=None):
    """
    Test seti üzerinde MAE hesaplar.
    
    Args:
        model: Yüklenmiş CSRNet modeli
        img_paths: Test görüntü yolları listesi
        device: torch device
        show_samples: Kaç örnek görselleştirilsin (0=hiçbiri)
        output_dir: Görselleştirme kayıt dizini
    
    Returns:
        mae: Ortalama mutlak hata
    """
    mae = 0.0
    results = []
    
    print(f"\n{'='*60}")
    print(f"Validasyon başlatılıyor ({len(img_paths)} görüntü)")
    print(f"{'='*60}")
    
    with torch.no_grad():
        for i, img_path in enumerate(img_paths):
            # Görüntü ön işleme
            img_tensor = preprocess_image(img_path).to(device)
            
            # Model tahmini
            output = model(img_tensor)
            predicted_count = output.detach().cpu().sum().numpy()
            
            # Ground truth yükle
            gt_path = img_path.replace('.jpg', '.h5').replace('images', 'ground_truth')
            if not os.path.exists(gt_path):
                print(f"  [UYARI] GT dosyası yok, atlıyorum: {gt_path}")
                continue
                
            with h5py.File(gt_path, 'r') as gt_file:
                groundtruth = np.asarray(gt_file['density'])
            
            gt_count = np.sum(groundtruth)
            error = abs(predicted_count - gt_count)
            mae += error
            
            results.append({
                'image': os.path.basename(img_path),
                'predicted': float(predicted_count),
                'ground_truth': float(gt_count),
                'error': float(error)
            })
            
            if (i + 1) % 20 == 0 or i == 0:
                print(f"  [{i+1:3d}/{len(img_paths)}] "
                      f"Tahmin: {predicted_count:.1f}, GT: {gt_count:.1f}, "
                      f"Hata: {error:.1f}")
            
            # Örnek görselleştirme
            if show_samples > 0 and i < show_samples:
                _visualize_sample(img_path, output, groundtruth, 
                                  predicted_count, gt_count, i, output_dir)
    
    valid_count = len(results)
    if valid_count == 0:
        print("\n❌ Hiçbir görüntü doğrulanamadı! Ground truth dosyaları eksik olabilir.")
        return float('inf')
    
    mae = mae / valid_count
    
    # Detaylı istatistikler
    errors = [r['error'] for r in results]
    print(f"\n{'='*60}")
    print(f"📊 Validasyon Sonuçları")
    print(f"{'='*60}")
    print(f"  Toplam görüntü  : {valid_count}")
    print(f"  MAE             : {mae:.2f}")
    print(f"  Min hata        : {min(errors):.2f}")
    print(f"  Max hata        : {max(errors):.2f}")
    print(f"  Medyan hata     : {np.median(errors):.2f}")
    print(f"  Std hata        : {np.std(errors):.2f}")
    
    return mae


def _visualize_sample(img_path, output, groundtruth, predicted, gt_count, idx, output_dir):
    """Tek bir örnek için density map görselleştirmesi oluşturur."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Orijinal görüntü
    img = Image.open(img_path)
    axes[0].imshow(img)
    axes[0].set_title(f'Orijinal Görüntü\nGT: {gt_count:.0f} kişi', fontsize=12)
    axes[0].axis('off')
    
    # Model density map
    density = output.detach().cpu().squeeze().numpy()
    axes[1].imshow(density, cmap=CM.jet)
    axes[1].set_title(f'CSRNet Density Map\nTahmin: {predicted:.0f} kişi', fontsize=12)
    axes[1].axis('off')
    
    # Ground truth density map
    axes[2].imshow(groundtruth, cmap=CM.jet)
    axes[2].set_title(f'Ground Truth Density Map', fontsize=12)
    axes[2].axis('off')
    
    plt.suptitle(f'{os.path.basename(img_path)} — Hata: {abs(predicted - gt_count):.1f}',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f'validation_sample_{idx+1}.png')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  📷 Görselleştirme kaydedildi: {save_path}")
    
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='CSRNet Validasyon')
    parser.add_argument('--weights', type=str, required=True,
                        help='Pretrained ağırlık dosyası (.pth.tar)')
    parser.add_argument('--dataset-root', type=str, required=True,
                        help='ShanghaiTech veri seti kök dizini')
    parser.add_argument('--part', type=str, default='A', choices=['A', 'B'],
                        help='Veri seti parçası (varsayılan: A)')
    parser.add_argument('--show-samples', type=int, default=5,
                        help='Görselleştirilecek örnek sayısı (varsayılan: 5)')
    parser.add_argument('--output-dir', type=str, default='validation_results',
                        help='Görselleştirme kayıt dizini')
    args = parser.parse_args()
    
    # Cihaz tespiti
    device = get_device()
    
    # Model yükleme
    model = load_model(args.weights, device)
    
    # Test görüntü yolları
    test_images_dir = os.path.join(
        args.dataset_root, f'part_{args.part}_final', 'test_data', 'images')
    
    img_paths = sorted(glob.glob(os.path.join(test_images_dir, '*.jpg')))
    
    if not img_paths:
        print(f"❌ Test görüntüsü bulunamadı: {test_images_dir}")
        sys.exit(1)
    
    print(f"📂 {len(img_paths)} test görüntüsü bulundu")
    
    # Validasyon
    mae = validate(model, img_paths, device, 
                   show_samples=args.show_samples,
                   output_dir=args.output_dir)
    
    print(f"\n✅ Validasyon tamamlandı — MAE: {mae:.2f}")


if __name__ == '__main__':
    main()
