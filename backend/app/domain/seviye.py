"""Doluluk oranı ve seviye eşikleme — saf fonksiyonlar (plan Bölüm 8.2).

Eşik değerleri ayarlardan gelir; burada yalnızca kural vardır, yapılandırma yoktur.
"""

SEVIYE_SEYREK = "seyrek"
SEVIYE_ORTA = "orta"
SEVIYE_YOGUN = "yogun"


def doluluk_orani_hesapla(kisi_sayisi: int, kapasite: int) -> float:
    """Oran 1.0'a kırpılmaz — aşırı doluluk görünür kalmalı."""
    return kisi_sayisi / kapasite


def seviye_belirle(doluluk_orani: float, seyrek_ust: float, orta_ust: float) -> str:
    if doluluk_orani < seyrek_ust:
        return SEVIYE_SEYREK
    if doluluk_orani <= orta_ust:
        return SEVIYE_ORTA
    return SEVIYE_YOGUN
