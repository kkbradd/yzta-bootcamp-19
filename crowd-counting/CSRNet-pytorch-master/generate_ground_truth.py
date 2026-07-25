"""
Ground Truth Density Map Üretici — ShanghaiTech Dataset
=========================================================
Bu script, ShanghaiTech veri setindeki .mat annotation dosyalarından
gaussian density map (.h5) dosyaları oluşturur.

CSRNet'in inference sırasında MAE hesaplaması için gereklidir.

Kullanım:
    py generate_ground_truth.py --dataset-root ../ShanghaiTech_Crowd_Counting_Dataset --part A
    py generate_ground_truth.py --dataset-root ../ShanghaiTech_Crowd_Counting_Dataset --part B
    py generate_ground_truth.py --dataset-root ../ShanghaiTech_Crowd_Counting_Dataset --part both
"""

import os
import sys
import glob
import argparse

import numpy as np
import scipy.io as io
import scipy.spatial
import scipy.ndimage
from PIL import Image
import h5py


def gaussian_filter_density(gt):
    """
    Adaptive Gaussian kernel ile density map oluşturur.
    
    Her bir annotation noktası için, en yakın 3 komşuya olan
    mesafenin ortalamasının %10'u sigma olarak kullanılır.
    Bu yöntem, kalabalık bölgelerde daha dar, seyrek bölgelerde
    daha geniş Gaussian kernel uygular (geometry-adaptive).
    
    Args:
        gt: 2D numpy array, annotation noktalarında 1, diğer yerlerde 0
    
    Returns:
        density: float32 density map, toplam = kişi sayısı
    """
    density = np.zeros(gt.shape, dtype=np.float32)
    gt_count = np.count_nonzero(gt)
    
    if gt_count == 0:
        return density

    # Annotation noktalarının (x, y) koordinatları
    pts = np.array(list(zip(np.nonzero(gt)[1], np.nonzero(gt)[0])))
    leafsize = 2048
    
    # KD-Tree ile en yakın komşu hesabı
    tree = scipy.spatial.KDTree(pts.copy(), leafsize=leafsize)
    distances, locations = tree.query(pts, k=4)

    for i, pt in enumerate(pts):
        pt2d = np.zeros(gt.shape, dtype=np.float32)
        pt2d[pt[1], pt[0]] = 1.
        if gt_count > 1:
            # Adaptive sigma: en yakın 3 komşunun mesafe ortalamasının %10'u
            sigma = (distances[i][1] + distances[i][2] + distances[i][3]) * 0.1
        else:
            # Tek nokta durumu
            sigma = np.average(np.array(gt.shape)) / 2. / 2.
        density += scipy.ndimage.gaussian_filter(pt2d, sigma, mode='constant')
    
    return density


def generate_h5_files(dataset_root, part='A', splits=None):
    """
    Belirtilen part ve split için ground truth .h5 dosyaları oluşturur.
    
    Args:
        dataset_root: ShanghaiTech veri setinin kök dizini
        part: 'A' veya 'B'
        splits: İşlenecek split'ler listesi, varsayılan ['train_data', 'test_data']
    """
    if splits is None:
        splits = ['train_data', 'test_data']
    
    for split in splits:
        images_dir = os.path.join(dataset_root, f'part_{part}_final', split, 'images')
        gt_dir = os.path.join(dataset_root, f'part_{part}_final', split, 'ground_truth')
        
        if not os.path.exists(images_dir):
            print(f"[UYARI] Dizin bulunamadı: {images_dir}")
            continue
        
        img_paths = sorted(glob.glob(os.path.join(images_dir, '*.jpg')))
        
        if not img_paths:
            print(f"[UYARI] {images_dir} içinde .jpg dosyası bulunamadı")
            continue
        
        print(f"\n{'='*60}")
        print(f"Part {part} — {split} ({len(img_paths)} görüntü)")
        print(f"{'='*60}")
        
        skipped = 0
        processed = 0
        
        for idx, img_path in enumerate(img_paths):
            img_name = os.path.basename(img_path)
            h5_path = img_path.replace('.jpg', '.h5').replace('images', 'ground_truth')
            
            # Zaten varsa atla
            if os.path.exists(h5_path):
                skipped += 1
                continue
            
            # .mat dosya yolu
            mat_name = img_name.replace('IMG_', 'GT_IMG_').replace('.jpg', '.mat')
            mat_path = os.path.join(gt_dir, mat_name)
            
            if not os.path.exists(mat_path):
                print(f"  [HATA] .mat dosyası bulunamadı: {mat_path}")
                continue
            
            # Görüntüyü oku (boyut bilgisi için)
            img = np.array(Image.open(img_path))
            
            # .mat annotation'ı oku
            mat = io.loadmat(mat_path)
            gt_points = mat["image_info"][0, 0][0, 0][0]  # Nx2 array: [x, y]
            
            # Annotation haritası oluştur
            k = np.zeros((img.shape[0], img.shape[1]))
            for point in gt_points:
                x, y = int(point[0]), int(point[1])
                if y < img.shape[0] and x < img.shape[1]:
                    k[y, x] = 1
            
            # Part B için sabit sigma (15), Part A için adaptive sigma
            if part == 'B':
                density = scipy.ndimage.gaussian_filter(k, 15, mode='constant')
            else:
                density = gaussian_filter_density(k)
            
            # .h5 dosyası olarak kaydet
            with h5py.File(h5_path, 'w') as hf:
                hf['density'] = density
            
            processed += 1
            gt_count = len(gt_points)
            density_sum = density.sum()
            
            print(f"  [{idx+1:3d}/{len(img_paths)}] {img_name}: "
                  f"GT={gt_count} kişi, Density sum={density_sum:.1f}, "
                  f"Shape={img.shape[:2]}")
        
        print(f"\n  Özet: {processed} işlendi, {skipped} atlandı (zaten mevcut)")


def main():
    parser = argparse.ArgumentParser(
        description='ShanghaiTech Ground Truth Density Map Üretici')
    parser.add_argument('--dataset-root', type=str, required=True,
                        help='ShanghaiTech veri seti kök dizini')
    parser.add_argument('--part', type=str, default='A', choices=['A', 'B', 'both'],
                        help='İşlenecek part: A, B veya both (varsayılan: A)')
    parser.add_argument('--split', type=str, default='both',
                        choices=['train_data', 'test_data', 'both'],
                        help='İşlenecek split (varsayılan: both)')
    args = parser.parse_args()
    
    splits = ['train_data', 'test_data'] if args.split == 'both' else [args.split]
    parts = ['A', 'B'] if args.part == 'both' else [args.part]
    
    for part in parts:
        generate_h5_files(args.dataset_root, part=part, splits=splits)
    
    print("\n✅ Ground truth oluşturma tamamlandı!")


if __name__ == '__main__':
    main()
