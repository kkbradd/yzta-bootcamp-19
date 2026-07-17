"""YotayAsistani birim testleri — SahteMotor ile, Ollama gerektirmez.

Reçetenin kalbi: sistem promptu konuşmanın İLK mesajı olarak SYSTEM rolüyle gitmeli
(OrchestratorAgent'ın system_prompt parametresi function_calling modunda yok sayılıyor)
ve motora temperature=0.0 iletilmeli.
"""

import dataclasses
import os
from typing import Any

import pytest
from openjarvis.core.types import Role, ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec

from app.ayarlar import Ayarlar
from app.cekirdek import (
    SISTEM_PROMPTU,
    MotorKurulamadi,
    YotayAsistani,
    _gemini_ortamini_hazirla,
    _motor_kur,
)

AYARLAR = Ayarlar(
    yotay_api_adresi="http://test",
    ollama_adresi="http://test:11434",
    model="test-model",
    motor="ollama",
)

GEMINI_AYARLARI = dataclasses.replace(
    AYARLAR, model="gemini-3-flash", motor="cloud", gemini_anahtari="gizli-anahtar"
)

BOS_KULLANIM = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def _final_yanit(icerik: str) -> dict[str, Any]:
    return {"content": icerik, "usage": dict(BOS_KULLANIM), "tool_calls": []}


def _tool_cagrisi_yaniti(arac_adi: str) -> dict[str, Any]:
    return {
        "content": "",
        "usage": dict(BOS_KULLANIM),
        "tool_calls": [{"id": "cagri_1", "name": arac_adi, "arguments": "{}"}],
    }


class SahteMotor:
    """generate çağrılarını kaydeder, sırayla hazır yanıtları döndürür."""

    def __init__(self, yanitlar: list[dict[str, Any]]) -> None:
        self._yanitlar = list(yanitlar)
        self.cagrilar: list[dict[str, Any]] = []

    def generate(self, messages: list[Any], **kwargs: Any) -> dict[str, Any]:
        self.cagrilar.append({"mesajlar": list(messages), **kwargs})
        return self._yanitlar.pop(0)


class SahteAraci(BaseTool):
    tool_id = "sahte_arac"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="sahte_arac",
            description="Test aracı.",
            parameters={"type": "object", "properties": {}, "required": []},
        )

    def execute(self, **params: Any) -> ToolResult:
        return ToolResult(tool_name="sahte_arac", content="sahte veri")


def test_sistem_promptu_ilk_mesaj_olarak_system_rolunde_gider():
    motor = SahteMotor([_final_yanit("merhaba")])
    asistan = YotayAsistani(AYARLAR, motor=motor, araclar=[SahteAraci()])

    asistan.sor("selam")

    ilk_mesaj = motor.cagrilar[0]["mesajlar"][0]
    assert ilk_mesaj.role == Role.SYSTEM
    assert ilk_mesaj.content == SISTEM_PROMPTU


def test_tool_cagrisi_calistirilir_ve_final_cevap_doner():
    motor = SahteMotor([_tool_cagrisi_yaniti("sahte_arac"), _final_yanit("34 hattı orta.")])
    asistan = YotayAsistani(AYARLAR, motor=motor, araclar=[SahteAraci()])

    cevap = asistan.sor("34 hattı nasıl?")

    assert cevap.cevap == "34 hattı orta."
    assert cevap.arac_cagrilari == ["sahte_arac"]
    assert cevap.tur_sayisi == 2


def test_motora_sifir_sicaklik_ve_model_iletilir():
    motor = SahteMotor([_final_yanit("tamam")])
    asistan = YotayAsistani(AYARLAR, motor=motor, araclar=[SahteAraci()])

    asistan.sor("selam")

    assert motor.cagrilar[0]["temperature"] == 0.0
    assert motor.cagrilar[0]["model"] == "test-model"


def test_arac_tanimlari_motora_gonderilir():
    motor = SahteMotor([_final_yanit("tamam")])
    asistan = YotayAsistani(AYARLAR, motor=motor, araclar=[SahteAraci()])

    asistan.sor("selam")

    gonderilen = motor.cagrilar[0]["tools"]
    assert gonderilen[0]["function"]["name"] == "sahte_arac"


# ---- Gemini ortamı ----
# CloudEngine anahtarı yalnız os.environ'dan okur; config'de alanı yok (bkz. cekirdek.py).


def _ortami_yalit(monkeypatch) -> None:
    # setenv değişkeni monkeypatch'e sahiplendirir (önceki değeri geri alma kaydına
    # yazar) — testin sonradan os.environ'a doğrudan yazdığı anahtar da böylece
    # temizlenir. Tek başına delenv, olmayan değişken için hiçbir kayıt tutmaz ve
    # anahtar sonraki testlere sızar. delenv ise testin gördüğü durumu "yok" yapar.
    monkeypatch.setenv("GEMINI_API_KEY", "yalitim-nobeti")
    monkeypatch.delenv("GEMINI_API_KEY")


def test_gemini_anahtari_ortama_yazilir(monkeypatch):
    _ortami_yalit(monkeypatch)

    _gemini_ortamini_hazirla(GEMINI_AYARLARI)

    assert os.environ["GEMINI_API_KEY"] == "gizli-anahtar"


def test_lokal_motorda_ortama_dokunulmaz(monkeypatch):
    _ortami_yalit(monkeypatch)

    _gemini_ortamini_hazirla(AYARLAR)

    assert "GEMINI_API_KEY" not in os.environ


def test_motor_bulunamazsa_aciklayici_hata_verilir(monkeypatch):
    # get_engine sağlıklı motor yoksa None döner; fonksiyon-içi import edildiği için
    # kaynak modülde değiştiriliyor (app.cekirdek'te bağlı bir isim yok).
    import openjarvis.engine

    monkeypatch.setattr(openjarvis.engine, "get_engine", lambda *a, **k: None)

    with pytest.raises(MotorKurulamadi) as hata:
        _motor_kur(AYARLAR)

    assert "ollama" in str(hata.value)
