"""Asistan çekirdeği — OrchestratorAgent'ı doğrulanmış reçeteyle kurar.

Reçete (bkz. README): OrchestratorAgent'ın ``system_prompt`` parametresi
function_calling modunda yok sayıldığı için sistem promptu AgentContext'in
konuşmasına SYSTEM mesajı olarak konur; temperature=0.0 tool çağırmayı
kararlı kılar (qwen3.5:0.8b ile 4/4 doğrulandı).
"""

import os
from dataclasses import dataclass
from typing import Any, Protocol

from openjarvis.agents._stubs import AgentContext
from openjarvis.agents.orchestrator import OrchestratorAgent
from openjarvis.core.types import Conversation, Message, Role
from openjarvis.tools._stubs import BaseTool

from app.araclar import YotayVeriKaynagi, varsayilan_araclar
from app.ayarlar import AZAMI_TOKEN, AZAMI_TUR, SICAKLIK, Ayarlar

# DİKKAT: qwen3.5:0.8b prompt uzunluğuna aşırı duyarlı — tek fazla cümle bile tool
# çağırmayı bozuyor (canlı tarama: kısa-sert prompt 2/2 çağırdı, +1 cümlesi 0/2).
# Genişletmeden önce docs'taki varyant testini tekrarla.
SISTEM_PROMPTU = (
    "Sen YOTAY asistanısın. Yoğunluk/hat/araç sorularında MUTLAKA önce uygun tool'u çağır "
    "(hat_yogunluklari, hat_anlik_durum, hat_trend). Tool sonucu olmadan cevap verme."
)


@dataclass(slots=True)
class AsistanCevabi:
    cevap: str
    tur_sayisi: int
    arac_cagrilari: list[str]


class Ureten(Protocol):
    """Asistanın çıkarım motorundan beklediği asgari sözleşme."""

    def generate(self, messages: list[Any], **kwargs: Any) -> dict[str, Any]: ...


class Soran(Protocol):
    """HTTP katmanının asistandan beklediği sözleşme."""

    def sor(self, mesaj: str) -> AsistanCevabi: ...


def _sistem_baglami() -> AgentContext:
    sistem_mesaji = Message(role=Role.SYSTEM, content=SISTEM_PROMPTU)
    return AgentContext(conversation=Conversation(messages=[sistem_mesaji]))


def _gemini_ortamini_hazirla(ayarlar: Ayarlar) -> None:
    """Anahtarı OpenJarvis'in okuduğu yere koyar.

    ``CloudEngine._init_clients`` anahtarı yalnız ``os.environ``'dan okur ve
    ``EngineConfig``'de karşılığı yoktur; config üzerinden geçirmenin yolu yok.
    (pyproject'te sabitlenmiş OpenJarvis sürümüne karşı doğrulandı.)
    """
    if ayarlar.gemini_mi and ayarlar.gemini_anahtari:
        os.environ["GEMINI_API_KEY"] = ayarlar.gemini_anahtari


def _motor_kur(ayarlar: Ayarlar) -> Ureten:
    from openjarvis.core.config import load_config
    from openjarvis.engine import get_engine

    _gemini_ortamini_hazirla(ayarlar)
    config = load_config()
    # Gizlilik şartı: OpenJarvis'in anonim kullanım analitiği (PostHog) bizim kod
    # yolumuzda zaten başlatılmıyor; ileride değişmesin diye açıkça kapatıyoruz.
    config.analytics.enabled = False
    config.engine.ollama.host = ayarlar.ollama_adresi
    config.engine.default = ayarlar.motor
    _, motor = get_engine(config, engine_key=ayarlar.motor)
    return motor


class YotayAsistani:
    """Her soruda taze bir OrchestratorAgent kurar; üretim kablolaması `ayarlardan`'da."""

    def __init__(self, ayarlar: Ayarlar, motor: Ureten, araclar: list[BaseTool]) -> None:
        self._ayarlar = ayarlar
        self._motor = motor
        self._araclar = araclar

    @classmethod
    def ayarlardan(cls, ayarlar: Ayarlar) -> "YotayAsistani":
        kaynak = YotayVeriKaynagi.adresten(ayarlar.yotay_api_adresi)
        return cls(ayarlar, motor=_motor_kur(ayarlar), araclar=varsayilan_araclar(kaynak))

    def sor(self, mesaj: str) -> AsistanCevabi:
        vekil = OrchestratorAgent(
            self._motor,
            self._ayarlar.model,
            tools=self._araclar,
            max_turns=AZAMI_TUR,
            temperature=SICAKLIK,
            max_tokens=AZAMI_TOKEN,
        )
        sonuc = vekil.run(mesaj, context=_sistem_baglami())
        return AsistanCevabi(
            cevap=sonuc.content,
            tur_sayisi=sonuc.turns,
            arac_cagrilari=[arac.tool_name for arac in sonuc.tool_results],
        )
