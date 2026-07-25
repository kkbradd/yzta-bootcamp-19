"""
CSRNet Model Ağırlıkları Otomatik İndirme Scripti
==================================================
Bu script, Google Drive klasörü üzerinden önceden eğitilmiş CSRNet model ağırlıklarını
(.pth.tar) otomatik olarak kontrol eder ve eksikse indirir.

Paylaşılan Google Drive Klasör Linki:
  https://drive.google.com/drive/folders/1Ak4ef-kgtZT9avwjbBETAjZ8q5PZZIxP

Desteklenen Çevre Değişkenleri (Environment Variables):
  - DRIVE_FOLDER_URL : Google Drive paylaşılan klasör URL'si
  - PART_A_DRIVE_ID  : Part A modeli için Google Drive ID
  - PART_B_DRIVE_ID  : Part B modeli için Google Drive ID

Kullanım:
    python download_weights.py
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("WeightDownloader")

# Ekibin paylaşılan Google Drive klasör URL'si
DEFAULT_DRIVE_FOLDER_URL = os.environ.get(
    "DRIVE_FOLDER_URL", 
    "https://drive.google.com/drive/folders/1Ak4ef-kgtZT9avwjbBETAjZ8q5PZZIxP"
)

# Tekil Google Drive ID'leri (Yedek/Opsiyonel)
DEFAULT_DRIVE_IDS = {
    "PartAmodel_best.pth.tar": os.environ.get("PART_A_DRIVE_ID", "1Z-atzS5Y2pOd-nEWqZRVBDMYJDreGWHH"),
    "partBmodel_best.pth.tar": os.environ.get("PART_B_DRIVE_ID", "1zKn6YlLW3Z9ocgPbP99oz7r2nC7_TBXK"),
}


def download_from_folder(target_dir: str = None) -> bool:
    """
    Paylaşılan Google Drive klasöründen eksik ağırlık dosyalarını indirir.
    """
    if target_dir is None:
        target_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        import gdown
    except ImportError:
        logger.error("❌ 'gdown' kütüphanesi yüklü değil. Lütfen 'pip install gdown' komutu ile kurun.")
        return False

    logger.info(f"⏳ Google Drive klasöründen model ağırlıkları indiriliyor: {DEFAULT_DRIVE_FOLDER_URL}")
    try:
        gdown.download_folder(url=DEFAULT_DRIVE_FOLDER_URL, output=target_dir, quiet=False)
        logger.info("🎉 Google Drive klasör indirme işlemi tamamlandı.")
        return True
    except Exception as e:
        logger.error(f"❌ Klasör indirilirken hata oluştu: {str(e)}")
        return False


def download_weight_file(filename: str, target_dir: str = None) -> bool:
    """
    Belirtilen ağırlık dosyasını kontrol eder, eksikse indirir.
    """
    if target_dir is None:
        target_dir = os.path.dirname(os.path.abspath(__file__))

    filepath = os.path.join(target_dir, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        logger.info(f"✅ Model ağırlık dosyası mevcut: {filename} ({os.path.getsize(filepath) / (1024*1024):.1f} MB)")
        return True

    logger.info(f"⏳ '{filename}' eksik. Google Drive klasöründen indirme başlatılıyor...")
    
    # Önce klasörden indirmeyi dene
    if download_from_folder(target_dir) and os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return True

    # Klasör başarısız olursa tekil ID ile dene
    logger.info(f"⚠️ Klasör indirmesi sonrasında '{filename}' bulunamadı. Tekil ID ile deneniyor...")
    try:
        import gdown
        drive_id = DEFAULT_DRIVE_IDS.get(filename)
        if drive_id:
            output = gdown.download(id=drive_id, output=filepath, quiet=False, fuzzy=True)
            if output and os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                logger.info(f"🎉 {filename} tekil ID ile başarıyla indirildi! ({os.path.getsize(filepath) / (1024*1024):.1f} MB)")
                return True
    except Exception as e:
        logger.error(f"❌ Tekil indirme hatası ({filename}): {str(e)}")

    return False


def ensure_all_weights(target_dir: str = None):
    """
    Tüm model ağırlıklarının (Part A ve Part B) mevcut olmasını sağlar.
    """
    if target_dir is None:
        target_dir = os.path.dirname(os.path.abspath(__file__))

    missing = []
    for fname in ["PartAmodel_best.pth.tar", "partBmodel_best.pth.tar"]:
        fpath = os.path.join(target_dir, fname)
        if not (os.path.exists(fpath) and os.path.getsize(fpath) > 0):
            missing.append(fname)

    if not missing:
        logger.info("✅ Tüm model ağırlık dosyaları (Part A ve Part B) mevcut ve hazır.")
        return True

    logger.info(f"⚠️ Eksik model ağırlıkları tespit edildi: {missing}")
    download_from_folder(target_dir)

    all_exist = True
    for fname in ["PartAmodel_best.pth.tar", "partBmodel_best.pth.tar"]:
        fpath = os.path.join(target_dir, fname)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            logger.info(f"✅ {fname} doğrulandı ({os.path.getsize(fpath) / (1024*1024):.1f} MB).")
        else:
            logger.error(f"❌ {fname} indirilemedi!")
            all_exist = False

    return all_exist


if __name__ == "__main__":
    logger.info("CSRNet Model Ağırlıkları Kontrol Ediliyor...")
    ensure_all_weights()
