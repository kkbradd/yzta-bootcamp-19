"""Ollama'da modelin hazır olmasını sağlar — konteyner girişinde çalışır.

Model zaten çekilmişse hiçbir şey yapmaz; yoksa Ollama'nın ``/api/pull``
ucuyla indirir (ilk açılışta ~1 GB sürebilir, bkz. README).
"""

import logging

import httpx

from app.ayarlar import Ayarlar

logger = logging.getLogger(__name__)

CEKME_ZAMAN_ASIMI_SN = 1800.0


def _mevcut_modeller(istemci: httpx.Client) -> list[str]:
    yanit = istemci.get("/api/tags")
    yanit.raise_for_status()
    return [model["name"] for model in yanit.json().get("models", [])]


def model_hazirla(model: str, istemci: httpx.Client) -> None:
    if model in _mevcut_modeller(istemci):
        logger.info("Model zaten hazır: %s", model)
        return
    logger.info("Model çekiliyor (ilk açılışta uzun sürebilir): %s", model)
    yanit = istemci.post(
        "/api/pull",
        json={"name": model, "stream": False},
        timeout=CEKME_ZAMAN_ASIMI_SN,
    )
    yanit.raise_for_status()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    ayarlar = Ayarlar.ortamdan()
    with httpx.Client(base_url=ayarlar.ollama_adresi) as istemci:
        model_hazirla(ayarlar.model, istemci=istemci)


if __name__ == "__main__":
    main()
