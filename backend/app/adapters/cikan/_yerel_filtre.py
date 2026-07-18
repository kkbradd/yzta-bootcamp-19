"""Yerel modele gönderilecek özet satırlarını daraltır.

Gerçek veride haftalık örüntü özeti 168 satıra / ~25 bin karaktere çıkabiliyor;
bu boyutta yerel model (gemma-9b) talimatı kaybedip düz metne kaçıyor ve hiç
sonuç üretilemiyor (canlı doğrulandı). Bulut modelinde şema API düzeyinde
zorlandığı için bu sorun yok — filtre yalnız yerel yolda uygulanır.

Elemenin anlamı promptla aynı: "yalnız diğer günlere göre belirgin sapma
gösteren örüntüler" zaten öneriye değer; gerisi gürültü.
"""

BELIRGIN_SAPMA_ESIGI = 0.15  # doluluk oranı farkı (0-1 ölçeğinde)
AZAMI_SATIR = 12


def _sapma(satir: dict) -> float | None:
    karsilastirma = satir.get("karsilastirma_ortalama_doluluk")
    if karsilastirma is None:
        return None
    return abs(satir["ortalama_doluluk"] - karsilastirma)


def belirgin_sapmalar(ozet_veri: list[dict], azami: int = AZAMI_SATIR) -> list[dict]:
    """Karşılaştırmasına göre belirgin sapan satırları, sapma büyüklüğüne göre döndürür."""
    sapmali = []
    for satir in ozet_veri:
        sapma = _sapma(satir)
        if sapma is not None and sapma >= BELIRGIN_SAPMA_ESIGI:
            sapmali.append((sapma, satir))
    sapmali.sort(key=lambda ikili: ikili[0], reverse=True)
    return [satir for _, satir in sapmali[:azami]]
