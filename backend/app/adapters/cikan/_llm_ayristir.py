"""Küçük yerel modellerin çıktısını güvenle JSON'a çevirme yardımcıları.

Yerel modeller (qwen3.5, gemma) çıktıyı ```json fence'iyle sarabilir, önüne/arkasına
açıklama metni koyabilir veya JSON'u yarıda kesebilir. Bu yardımcılar bu durumları
ele alır; doğrulama başarısızsa istisna yerine boş sonuç döner (üretim akışı,
boş sonuçta zaten depoya yazmaz).
"""

import logging
import re

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

_FENCE = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.DOTALL)


def json_soy(ham: str) -> str:
    """Markdown fence'i ve çevresindeki metni soyarak ilk {...} bloğunu döndürür."""
    eslesme = _FENCE.search(ham)
    if eslesme:
        ham = eslesme.group(1)
    baslangic = ham.find("{")
    bitis = ham.rfind("}")
    if baslangic == -1 or bitis == -1 or bitis < baslangic:
        return ham
    return ham[baslangic : bitis + 1]


def dogrula_veya_bos[TModel: BaseModel](ham: str, model: type[TModel], liste_alani: str) -> TModel:
    """Ham LLM çıktısını doğrular; başarısızsa `liste_alani` boş olan bir örnek döner."""
    try:
        return model.model_validate_json(json_soy(ham))
    except ValidationError as hata:
        logger.warning("LLM çıktısı doğrulanamadı, boş sonuç dönülüyor: %s", hata)
        return model.model_validate({liste_alani: []})
