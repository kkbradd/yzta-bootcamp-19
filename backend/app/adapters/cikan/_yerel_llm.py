"""Yerel LLM çağrısı (OpenJarvis SimpleAgent + Ollama) — öneri ve uyarı ortak.

Yerel modeller şemayı API düzeyinde zorlayamaz (Ollama yalnız ``format: json``
destekler), bu yüzden şema ve "yalnız saf JSON" talimatı sistem promptuna eklenir;
sıcaklık 0'a çekilir. Canlı doğrulandı: bu talimat olmadan gemma-9b markdown düz
metne kaçıyor ve hiç sonuç üretilemiyordu.
"""

import json
from typing import Any

from openjarvis.agents._stubs import AgentContext
from openjarvis.agents.simple import SimpleAgent
from openjarvis.core.types import Conversation, Message, Role
from openjarvis.engine._stubs import ResponseFormat

_JSON_TALIMATI_BASI = (
    "\n\nÇıktıyı YALNIZCA saf JSON olarak ver — markdown, ```json bloğu veya "
    "açıklama metni EKLEME. Tam olarak şu şema: "
)


def json_talimati(sema_ornegi: str) -> str:
    """Şema örneğini 'yalnız saf JSON ver' talimatına sarar."""
    return _JSON_TALIMATI_BASI + sema_ornegi


def yerel_calistir(motor: Any, model: str, sistem_prompt: str, ozet_veri: list[dict]) -> str:
    """Özet veriyi yerel modele gönderir, ham metin yanıtı döndürür."""
    vekil = SimpleAgent(motor, model)
    girdi = "Aşağıdaki özet veriyi analiz et:\n\n" + json.dumps(ozet_veri, default=str)
    sonuc = vekil.run(
        girdi,
        context=_baglam(sistem_prompt),
        response_format=ResponseFormat(type="json_object"),
        temperature=0.0,
    )
    return sonuc.content


def _baglam(sistem_prompt: str) -> AgentContext:
    sistem = Message(role=Role.SYSTEM, content=sistem_prompt)
    return AgentContext(conversation=Conversation(messages=[sistem]))
