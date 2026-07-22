"""REST istek/yanıt şemaları — alan adları plan sözleşmesiyle birebir (Bölüm 9)."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator


class HatOzeti(BaseModel):
    hat_id: int
    hat_no: str
    ad: str
    ortalama_doluluk: float | None
    seviye: str | None
    arac_sayisi: int
    durak_sayisi: int = 0


class AracAnlikDurumu(BaseModel):
    arac_id: int
    kisi_sayisi: int
    doluluk_orani: float
    seviye: str | None
    zaman: datetime


class TrendNoktasi(BaseModel):
    zaman: datetime
    ortalama_doluluk: float | None
    ortalama_kisi: float
    olcum_sayisi: int


class OlcumYaniti(BaseModel):
    sira_no: int
    kisi_sayisi: int
    doluluk_orani: float | None
    seviye: str | None
    olcum_zamani: datetime


class DurakYaniti(BaseModel):
    id: int
    ad: str
    enlem: float
    boylam: float
    hat_kodlari: list[str] = []


class HatGuzergahYaniti(BaseModel):
    duraklar: list[DurakYaniti]
    koordinatlar: list[tuple[float, float]]
    mesafe_metre: float | None
    sure_saniye: float | None


class CihazYaniti(BaseModel):
    id: str
    tip: str
    yazilim_surumu: str | None
    cevrimici: bool
    son_gorulme: datetime | None


# ---- Tanımlar ekranı: minimal CRUD istekleri ----


class HatOlustur(BaseModel):
    hat_no: str
    ad: str


class AracOlustur(BaseModel):
    plaka: str
    tip: str
    kapasite: int = Field(gt=0)


class DurakOlustur(BaseModel):
    ad: str
    enlem: float
    boylam: float


class CihazOlustur(BaseModel):
    id: str
    tip: Literal["arac", "durak"]
    yazilim_surumu: str | None = None


class HatAtamasiOlustur(BaseModel):
    tur: Literal["hat"]
    hat_id: int
    arac_id: int


class CihazAtamasiOlustur(BaseModel):
    tur: Literal["cihaz"]
    cihaz_id: str
    arac_id: int | None = None
    durak_id: int | None = None

    @model_validator(mode="after")
    def _hedef_tam_biri(self) -> "CihazAtamasiOlustur":
        if (self.arac_id is None) == (self.durak_id is None):
            raise ValueError("arac_id ile durak_id'den tam biri verilmelidir")
        return self


AtamaOlustur = Annotated[HatAtamasiOlustur | CihazAtamasiOlustur, Field(discriminator="tur")]


# ---- Oturum (giriş) ----


class OturumAcIstegi(BaseModel):
    eposta: str
    sifre: str


class OturumYaniti(BaseModel):
    erisim_tokeni: str
    token_tipi: Literal["bearer"] = "bearer"


# ---- Öneriler ----


class OneriYaniti(BaseModel):
    id: int | None
    hat_id: int
    gun_no: int
    saat_baslangic: int
    saat_bitis: int
    ortalama_doluluk: float
    karsilastirma_ortalama_doluluk: float | None
    oneri_metni: str
    gerekce: str
    olusturulma_zamani: datetime


# ---- Son Uyarılar ----


class UyariYaniti(BaseModel):
    id: int | None
    hat_id: int
    ortalama_doluluk: float
    ortalama_kisi: float
    uyari_metni: str
    gerekce: str
    olusturulma_zamani: datetime
