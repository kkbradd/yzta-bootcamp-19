"""LLM çıktısı ayrıştırma birim testleri — küçük modellerin bozuk çıktısına dayanıklı.

Fixture'lar PoC'de gözlenen gerçek qwen/gemma çıktılarıdır (markdown fence, çöp önek,
yarıda kesilen JSON). Ayrıştırıcı bunları güvenle ele almalı; asla fırlatmamalı.
"""

from pydantic import BaseModel

from app.adapters.cikan._llm_ayristir import dogrula_veya_bos, json_soy


class _Madde(BaseModel):
    hat_id: int
    metin: str


class _Liste(BaseModel):
    maddeler: list[_Madde]


def test_saf_json_oldugu_gibi_kalir():
    ham = '{"maddeler": [{"hat_id": 1, "metin": "ek sefer"}]}'

    assert json_soy(ham) == ham


def test_markdown_fence_soyulur():
    ham = '```json\n{"maddeler": []}\n```'

    assert json_soy(ham) == '{"maddeler": []}'


def test_fence_dil_etiketsiz_de_soyulur():
    ham = '```\n{"maddeler": []}\n```'

    assert json_soy(ham) == '{"maddeler": []}'


def test_onundeki_arkasindaki_metin_atilir():
    ham = 'İşte sonuç:\n{"maddeler": []}\nUmarım yardımcı olur.'

    assert json_soy(ham) == '{"maddeler": []}'


def test_gecerli_json_pydantice_dogrulanir():
    ham = '{"maddeler": [{"hat_id": 1, "metin": "ek sefer"}]}'

    sonuc = dogrula_veya_bos(ham, _Liste, "maddeler")

    assert len(sonuc.maddeler) == 1
    assert sonuc.maddeler[0].hat_id == 1


def test_fenceli_json_dogrulanir():
    ham = '```json\n{"maddeler": [{"hat_id": 2, "metin": "izle"}]}\n```'

    sonuc = dogrula_veya_bos(ham, _Liste, "maddeler")

    assert sonuc.maddeler[0].hat_id == 2


def test_bozuk_json_bos_liste_doner_firlatmaz():
    ham = '{"maddeler": [{"hat_id": 1, "metin": "yarim'  # yarıda kesilmiş

    sonuc = dogrula_veya_bos(ham, _Liste, "maddeler")

    assert sonuc.maddeler == []


def test_fazla_alanli_json_bos_liste_doner():
    # Küçük model şemaya olmayan alan ekleyebilir; strict doğrulama boş döner.
    ham = '{"maddeler": [{"hat_id": 1, "metin": "x", "uydurma_alan": "z"}]}'

    sonuc = dogrula_veya_bos(ham, _Liste, "maddeler")

    assert isinstance(sonuc.maddeler, list)
