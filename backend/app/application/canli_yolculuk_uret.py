"""Sistem açıkken de yolculuk üretimi: her 15 dakikada bir TÜM hatlar aynı anda
tek bir ölçüm üretir ve gerçek `OlcumIsleyici` akışından (yaz → anlık durum →
canlı yayın) geçirir — böylece harita rengi, dashboard KPI'ları, trend, uyarı
ve öneri motoru donuk kalmaz, zaman ilerledikçe gerçekten güncellenir.

`gecmis_veri_yukle.py` yalnızca geçmişe dönük backfill yapar (tek seferlik job);
bu sınıf olmadan docker ayaktayken hiç yeni ölçüm oluşmazdı.

Tasarım (kullanıcı gereksinimi): her 15 dakikada bir TEK tetikleme olur. Her
turda önce turun genel PROFİLİ (sakin/dengeli/yoğun, bkz. _TUR_PROFILLERI)
rastgele seçilir, sonra her hatta o profile göre bir kategori atanır. Hattın
kendi HAT_DESENLERI penceresi bu atamayı hafifçe etkiler (yoğun pencerede
olan hat "yoğun" çıkma ihtimali biraz daha yüksektir) ama KESİN belirlemez.
Böylece hem hat-içi rotasyon (her turda hangi hat yeşil/sarı/kırmızı olduğu
değişir) hem de tur-içi toplam (bazı turlar sakin ~400-450, bazıları yoğun
~800-950) gerçekten dalgalanır — sabit bir oran/toplam zorlanmaz. Kategori
belirlendikten sonra o kategorinin sayı aralığında üçgen dağılımla kişi
sayısı üretilir (bkz. _kisi_sayisi_uret).

Önceki tasarımda her hat bağımsız rastgele periyotta (1.5-5dk) tetikleniyordu,
bu da bir kovaya bazen 2 bazen 19 ölçüm düşmesine ve SUM(kisi_sayisi)
toplamının öngörülemez şekilde şişmesine yol açıyordu — artık sabit periyotla
(15dk, tüm hatlar birlikte) bu sorun yok.
"""

import logging
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from app.application.olcum_isle import OlcumIsleyici
from app.gecmis_veri_yukle import HAT_DESENLERI, _desen_yogun_mu
from app.ports.sorgular import HatEslemeSorgusuPort

logger = logging.getLogger(__name__)

# Tüm hatlar duvar saatinin bu dakikalarında birlikte tetiklenir.
_CEYREK_SAAT_DAKIKALARI = (0, 15, 30, 45)


def _sonraki_ceyrek_saat(simdi: datetime) -> datetime:
    """simdi'den sonraki ilk :00/:15/:30/:45 anını döndürür (saniye/mikrosaniye
    sıfırlanır) — üretim gerçek duvar saatine hizalı olsun diye.
    """
    taban = simdi.replace(second=0, microsecond=0)
    for dakika in _CEYREK_SAAT_DAKIKALARI:
        aday = taban.replace(minute=dakika)
        if aday > simdi:
            return aday
    # Bu saatte uygun dakika kalmadıysa bir sonraki saatin :00'ına geç.
    return (taban + timedelta(hours=1)).replace(minute=0)


# Her turda hatlara dağıtılan kategori oranı sabit DEĞİLDİR: turlar arası
# TOPLAM yolcu sayısının 400-950 aralığında gerçekten seyretmesi için (sadece
# hat-içi rotasyon değil, tur-içi toplam da dalgalanmalı) her turda üç olası
# dağılım profilinden biri rastgele seçilir — "sakin tur" (toplam ~400-450'ye
# yakın), "dengeli tur" (~550-650), "yoğun tur" (~800-950'ye yakın).
SEYREK, ORTA, YOGUN = "seyrek", "orta", "yogun"
_TUR_PROFILLERI = [
    {SEYREK: 7, ORTA: 3, YOGUN: 1},  # sakin tur
    {SEYREK: 3, ORTA: 5, YOGUN: 3},  # dengeli tur
    {SEYREK: 0, ORTA: 2, YOGUN: 9},  # yoğun tur
]

# Her kategorinin kişi sayısı aralığı + üçgen dağılım modu (en olası değer).
_KATEGORI_ARALIKLARI = {
    SEYREK: (10, 40, 30),
    ORTA: (35, 65, 55),
    YOGUN: (65, 95, 88),
}


@dataclass(slots=True)
class _HatDurumu:
    hat_id: int
    cihaz_id: str
    hat_no: str
    sira_no: int


@dataclass(slots=True)
class CanliYolculukUret:
    sorgular: HatEslemeSorgusuPort
    olcum_isleyici: OlcumIsleyici
    _hatlar: list[_HatDurumu] = field(default_factory=list)
    _yuklendi: bool = False
    _sonraki_uretim: datetime | None = None

    async def _durumlari_yukle(self) -> None:
        eslemeler = await self.sorgular.hat_arac_cihaz_eslemelerini_al()
        simdi = datetime.now(UTC)
        for esleme in eslemeler:
            hat_no = esleme["hat_no"]
            if hat_no not in HAT_DESENLERI:
                continue
            self._hatlar.append(
                _HatDurumu(
                    hat_id=esleme["hat_id"],
                    cihaz_id=esleme["cihaz_id"],
                    hat_no=hat_no,
                    sira_no=int(simdi.timestamp()),
                )
            )
        self._yuklendi = True
        self._sonraki_uretim = _sonraki_ceyrek_saat(simdi)
        logger.info("canlı yolculuk üretimi başladı: %d hat izleniyor", len(self._hatlar))

    async def tetikle(self) -> None:
        """Duvar saatinin :00/:15/:30/:45 dakikalarında TÜM hatlar için tek
        turda birer ölçüm üretir — periyot backend'in ne zaman başladığına
        değil, gerçek saate hizalıdır.
        """
        if not self._yuklendi:
            await self._durumlari_yukle()

        simdi = datetime.now(UTC)
        if self._sonraki_uretim is None or simdi < self._sonraki_uretim:
            return
        self._sonraki_uretim = _sonraki_ceyrek_saat(simdi)

        kategoriler = self._kategorileri_dagit(simdi)

        for durum in self._hatlar:
            kategori = kategoriler[durum.hat_id]
            kisi_sayisi = self._kisi_sayisi_uret(kategori)
            durum.sira_no += 1
            await self.olcum_isleyici.isle(
                cihaz_id=durum.cihaz_id,
                sira_no=durum.sira_no,
                kisi_sayisi=kisi_sayisi,
                olcum_zamani=simdi,
            )

    def _kategorileri_dagit(self, simdi: datetime) -> dict[int, str]:
        """Bu turun profili (sakin/dengeli/yoğun) rastgele seçilir, o profilin
        oranına göre bir kategori havuzu oluşturulup hatlara dağıtılır. Kendi
        HAT_DESENLERI penceresindeki hatlar önce sıraya girer ve havuzun en
        yoğun kategorilerini alır (kesin değil, sadece öncelik) — böylece
        "yoğun saatte olan hat daha büyük ihtimalle yoğun çıkar" eğilimi
        korunurken, her turda hem hangi hattın hangi kategoriye düştüğü hem de
        turun genel profili (dolayısıyla toplamı) değişir.
        """
        profil = random.choice(_TUR_PROFILLERI)
        havuz: list[str] = []
        for kategori, adet in profil.items():
            havuz.extend([kategori] * adet)
        while len(havuz) < len(self._hatlar):
            havuz.extend(havuz)
        havuz = havuz[: len(self._hatlar)]
        # En yoğun kategoriler başta olsun ki desen-içi hatlar bunları önce alsın.
        siralama = {YOGUN: 0, ORTA: 1, SEYREK: 2}
        havuz.sort(key=lambda k: siralama[k])

        hatlar_sirali = sorted(
            self._hatlar,
            key=lambda d: (
                0 if _desen_yogun_mu(simdi, HAT_DESENLERI[d.hat_no]) else 1,
                random.random(),
            ),
        )
        return {durum.hat_id: havuz[i] for i, durum in enumerate(hatlar_sirali)}

    @staticmethod
    def _kisi_sayisi_uret(kategori: str) -> int:
        alt, ust, mod = _KATEGORI_ARALIKLARI[kategori]
        return round(random.triangular(alt, ust, mod))
