"""
Ātmanepada paradigm tables for Q4-C v1.

Merged into _tinanta.PARADIGMS at import time. Separate file so Q4-B
parasmaipada data in _tinanta_data.py stays untouched.

Verified paradigms (189 cells):
  - kṛ   (gaṇa 8, ubhayapada)   — lṛṭ, loṭ (laṭ, laṅ already in _tinanta_data.py)
  - labh (gaṇa 1, ātmanepada)   — laṭ, laṅ, lṛṭ, loṭ
  - cur  (gaṇa 10, ubhayapada)  — laṭ, laṅ, lṛṭ, loṭ   [usage_note: rare]
  - vah  (gaṇa 1, ubhayapada)   — laṭ, laṅ, lṛṭ, loṭ   [usage_note: semantic]
  - jñā  (gaṇa 9, ubhayapada)   — laṭ, laṅ, lṛṭ, loṭ
  - dā   (gaṇa 3, ubhayapada)   — laṭ, laṅ, lṛṭ        [loṭ NOT yet verified]

Sources: M.R. Kale (Higher Sanskrit Grammar), Siddhāntakaumudī, Whitney.
"""

ATMANEPADA_USAGE_NOTES = {
    "cur": "ātmanepada_rare: cur (gaṇa 10) is grammatically ubhayapada, but classical Sanskrit strongly prefers parasmaipada (corayati).",
    "vah": "ātmanepada_semantic: vah (gaṇa 1) uses parasmaipada (vahati) for 'to carry' and ātmanepada (vahate) specifically in the sense 'to marry'.",
    "dā":  "ātmanepada_loṭ_unverified: dā loṭ (imperative) ātmanepada paradigm is not yet verified against primary sources. laṭ / laṅ / lṛṭ are fully verified.",
}

# Roots for which a specific lakāra's ātmanepada paradigm is explicitly
# not yet verified. When conjugate() falls through to generation for one
# of these, it returns source="unsupported" instead of a guessed form.
ATMANEPADA_UNVERIFIED = {
    ("dā", "loṭ"),
}

ATMANEPADA_PARADIGMS = {
    "kṛ": {
        "lṛṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "kariṣyate",
                ("prathama_purusha", "dvivacana"):  "kariṣyete",
                ("prathama_purusha", "bahuvacana"): "kariṣyante",
                ("madhyama_purusha", "ekavacana"):  "kariṣyase",
                ("madhyama_purusha", "dvivacana"):  "kariṣyethe",
                ("madhyama_purusha", "bahuvacana"): "kariṣyadhve",
                ("uttama_purusha",   "ekavacana"):  "kariṣye",
                ("uttama_purusha",   "dvivacana"):  "kariṣyāvahe",
                ("uttama_purusha",   "bahuvacana"): "kariṣyāmahe",
            },
        },
        "loṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "kurutām",
                ("prathama_purusha", "dvivacana"):  "kurvātām",
                ("prathama_purusha", "bahuvacana"): "kurvatām",
                ("madhyama_purusha", "ekavacana"):  "kuruṣva",
                ("madhyama_purusha", "dvivacana"):  "kurvāthām",
                ("madhyama_purusha", "bahuvacana"): "kurudhvam",
                ("uttama_purusha",   "ekavacana"):  "karavai",
                ("uttama_purusha",   "dvivacana"):  "karavāvahai",
                ("uttama_purusha",   "bahuvacana"): "karavāmahai",
            },
        },
    },
    "labh": {
        "laṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "labhate",
                ("prathama_purusha", "dvivacana"):  "labhete",
                ("prathama_purusha", "bahuvacana"): "labhante",
                ("madhyama_purusha", "ekavacana"):  "labhase",
                ("madhyama_purusha", "dvivacana"):  "labhethe",
                ("madhyama_purusha", "bahuvacana"): "labhadhve",
                ("uttama_purusha",   "ekavacana"):  "labhe",
                ("uttama_purusha",   "dvivacana"):  "labhāvahe",
                ("uttama_purusha",   "bahuvacana"): "labhāmahe",
            },
        },
        "laṅ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "alabhata",
                ("prathama_purusha", "dvivacana"):  "alabhetām",
                ("prathama_purusha", "bahuvacana"): "alabhanta",
                ("madhyama_purusha", "ekavacana"):  "alabhathāḥ",
                ("madhyama_purusha", "dvivacana"):  "alabhethām",
                ("madhyama_purusha", "bahuvacana"): "alabhadhvam",
                ("uttama_purusha",   "ekavacana"):  "alabhe",
                ("uttama_purusha",   "dvivacana"):  "alabhāvahi",
                ("uttama_purusha",   "bahuvacana"): "alabhāmahi",
            },
        },
        "lṛṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "lapsyate",
                ("prathama_purusha", "dvivacana"):  "lapsyete",
                ("prathama_purusha", "bahuvacana"): "lapsyante",
                ("madhyama_purusha", "ekavacana"):  "lapsyase",
                ("madhyama_purusha", "dvivacana"):  "lapsyethe",
                ("madhyama_purusha", "bahuvacana"): "lapsyadhve",
                ("uttama_purusha",   "ekavacana"):  "lapsye",
                ("uttama_purusha",   "dvivacana"):  "lapsyāvahe",
                ("uttama_purusha",   "bahuvacana"): "lapsyāmahe",
            },
        },
        "loṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "labhatām",
                ("prathama_purusha", "dvivacana"):  "labhetām",
                ("prathama_purusha", "bahuvacana"): "labhantām",
                ("madhyama_purusha", "ekavacana"):  "labhasva",
                ("madhyama_purusha", "dvivacana"):  "labhethām",
                ("madhyama_purusha", "bahuvacana"): "labhadhvam",
                ("uttama_purusha",   "ekavacana"):  "labhai",
                ("uttama_purusha",   "dvivacana"):  "labhāvahai",
                ("uttama_purusha",   "bahuvacana"): "labhāmahai",
            },
        },
    },
    "dā": {
        "laṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "datte",
                ("prathama_purusha", "dvivacana"):  "dadāte",
                ("prathama_purusha", "bahuvacana"): "dadate",
                ("madhyama_purusha", "ekavacana"):  "datse",
                ("madhyama_purusha", "dvivacana"):  "dadāthe",
                ("madhyama_purusha", "bahuvacana"): "daddhve",
                ("uttama_purusha",   "ekavacana"):  "dade",
                ("uttama_purusha",   "dvivacana"):  "dadvahe",
                ("uttama_purusha",   "bahuvacana"): "dadmahe",
            },
        },
        "laṅ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "adatta",
                ("prathama_purusha", "dvivacana"):  "adadātām",
                ("prathama_purusha", "bahuvacana"): "adadata",
                ("madhyama_purusha", "ekavacana"):  "adatthāḥ",
                ("madhyama_purusha", "dvivacana"):  "adadāthām",
                ("madhyama_purusha", "bahuvacana"): "adaddhvam",
                ("uttama_purusha",   "ekavacana"):  "adadi",
                ("uttama_purusha",   "dvivacana"):  "adadvahi",
                ("uttama_purusha",   "bahuvacana"): "adadmahi",
            },
        },
        "lṛṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "dāsyate",
                ("prathama_purusha", "dvivacana"):  "dāsyete",
                ("prathama_purusha", "bahuvacana"): "dāsyante",
                ("madhyama_purusha", "ekavacana"):  "dāsyase",
                ("madhyama_purusha", "dvivacana"):  "dāsyethe",
                ("madhyama_purusha", "bahuvacana"): "dāsyadhve",
                ("uttama_purusha",   "ekavacana"):  "dāsye",
                ("uttama_purusha",   "dvivacana"):  "dāsyāvahe",
                ("uttama_purusha",   "bahuvacana"): "dāsyāmahe",
            },
        },
    },
    "cur": {
        "laṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "corayate",
                ("prathama_purusha", "dvivacana"):  "corayete",
                ("prathama_purusha", "bahuvacana"): "corayante",
                ("madhyama_purusha", "ekavacana"):  "corayase",
                ("madhyama_purusha", "dvivacana"):  "corayethe",
                ("madhyama_purusha", "bahuvacana"): "corayadhve",
                ("uttama_purusha",   "ekavacana"):  "coraye",
                ("uttama_purusha",   "dvivacana"):  "corayāvahe",
                ("uttama_purusha",   "bahuvacana"): "corayāmahe",
            },
        },
        "laṅ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "acorayata",
                ("prathama_purusha", "dvivacana"):  "acorayetām",
                ("prathama_purusha", "bahuvacana"): "acorayanta",
                ("madhyama_purusha", "ekavacana"):  "acorayathāḥ",
                ("madhyama_purusha", "dvivacana"):  "acorayethām",
                ("madhyama_purusha", "bahuvacana"): "acorayadhvam",
                ("uttama_purusha",   "ekavacana"):  "acoraye",
                ("uttama_purusha",   "dvivacana"):  "acorayāvahi",
                ("uttama_purusha",   "bahuvacana"): "acorayāmahi",
            },
        },
        "lṛṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "corayiṣyate",
                ("prathama_purusha", "dvivacana"):  "corayiṣyete",
                ("prathama_purusha", "bahuvacana"): "corayiṣyante",
                ("madhyama_purusha", "ekavacana"):  "corayiṣyase",
                ("madhyama_purusha", "dvivacana"):  "corayiṣyethe",
                ("madhyama_purusha", "bahuvacana"): "corayiṣyadhve",
                ("uttama_purusha",   "ekavacana"):  "corayiṣye",
                ("uttama_purusha",   "dvivacana"):  "corayiṣyāvahe",
                ("uttama_purusha",   "bahuvacana"): "corayiṣyāmahe",
            },
        },
        "loṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "corayatām",
                ("prathama_purusha", "dvivacana"):  "corayetām",
                ("prathama_purusha", "bahuvacana"): "corayantām",
                ("madhyama_purusha", "ekavacana"):  "corayasva",
                ("madhyama_purusha", "dvivacana"):  "corayethām",
                ("madhyama_purusha", "bahuvacana"): "corayadhvam",
                ("uttama_purusha",   "ekavacana"):  "corayai",
                ("uttama_purusha",   "dvivacana"):  "corayāvahai",
                ("uttama_purusha",   "bahuvacana"): "corayāmahai",
            },
        },
    },
    "vah": {
        "laṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "vahate",
                ("prathama_purusha", "dvivacana"):  "vahete",
                ("prathama_purusha", "bahuvacana"): "vahante",
                ("madhyama_purusha", "ekavacana"):  "vahase",
                ("madhyama_purusha", "dvivacana"):  "vahethe",
                ("madhyama_purusha", "bahuvacana"): "vahadhve",
                ("uttama_purusha",   "ekavacana"):  "vahe",
                ("uttama_purusha",   "dvivacana"):  "vahāvahe",
                ("uttama_purusha",   "bahuvacana"): "vahāmahe",
            },
        },
        "laṅ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "avahata",
                ("prathama_purusha", "dvivacana"):  "avahetām",
                ("prathama_purusha", "bahuvacana"): "avahanta",
                ("madhyama_purusha", "ekavacana"):  "avahathāḥ",
                ("madhyama_purusha", "dvivacana"):  "avahethām",
                ("madhyama_purusha", "bahuvacana"): "avahadhvam",
                ("uttama_purusha",   "ekavacana"):  "avahe",
                ("uttama_purusha",   "dvivacana"):  "avahāvahi",
                ("uttama_purusha",   "bahuvacana"): "avahāmahi",
            },
        },
        "lṛṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "vakṣyate",
                ("prathama_purusha", "dvivacana"):  "vakṣyete",
                ("prathama_purusha", "bahuvacana"): "vakṣyante",
                ("madhyama_purusha", "ekavacana"):  "vakṣyase",
                ("madhyama_purusha", "dvivacana"):  "vakṣyethe",
                ("madhyama_purusha", "bahuvacana"): "vakṣyadhve",
                ("uttama_purusha",   "ekavacana"):  "vakṣye",
                ("uttama_purusha",   "dvivacana"):  "vakṣyāvahe",
                ("uttama_purusha",   "bahuvacana"): "vakṣyāmahe",
            },
        },
        "loṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "vahatām",
                ("prathama_purusha", "dvivacana"):  "vahetām",
                ("prathama_purusha", "bahuvacana"): "vahantām",
                ("madhyama_purusha", "ekavacana"):  "vahasva",
                ("madhyama_purusha", "dvivacana"):  "vahethām",
                ("madhyama_purusha", "bahuvacana"): "vahadhvam",
                ("uttama_purusha",   "ekavacana"):  "vahai",
                ("uttama_purusha",   "dvivacana"):  "vahāvahai",
                ("uttama_purusha",   "bahuvacana"): "vahāmahai",
            },
        },
    },
    "jñā": {
        "laṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "jānīte",
                ("prathama_purusha", "dvivacana"):  "jānāte",
                ("prathama_purusha", "bahuvacana"): "jānate",
                ("madhyama_purusha", "ekavacana"):  "jānīṣe",
                ("madhyama_purusha", "dvivacana"):  "jānāthe",
                ("madhyama_purusha", "bahuvacana"): "jānīdhve",
                ("uttama_purusha",   "ekavacana"):  "jāne",
                ("uttama_purusha",   "dvivacana"):  "jānīvahe",
                ("uttama_purusha",   "bahuvacana"): "jānīmahe",
            },
        },
        "laṅ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "ajānīta",
                ("prathama_purusha", "dvivacana"):  "ajānātām",
                ("prathama_purusha", "bahuvacana"): "ajānata",
                ("madhyama_purusha", "ekavacana"):  "ajānīthāḥ",
                ("madhyama_purusha", "dvivacana"):  "ajānāthām",
                ("madhyama_purusha", "bahuvacana"): "ajānīdhvam",
                ("uttama_purusha",   "ekavacana"):  "ajāni",
                ("uttama_purusha",   "dvivacana"):  "ajānīvahi",
                ("uttama_purusha",   "bahuvacana"): "ajānīmahi",
            },
        },
        "lṛṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "jñāsyate",
                ("prathama_purusha", "dvivacana"):  "jñāsyete",
                ("prathama_purusha", "bahuvacana"): "jñāsyante",
                ("madhyama_purusha", "ekavacana"):  "jñāsyase",
                ("madhyama_purusha", "dvivacana"):  "jñāsyethe",
                ("madhyama_purusha", "bahuvacana"): "jñāsyadhve",
                ("uttama_purusha",   "ekavacana"):  "jñāsye",
                ("uttama_purusha",   "dvivacana"):  "jñāsyāvahe",
                ("uttama_purusha",   "bahuvacana"): "jñāsyāmahe",
            },
        },
        "loṭ": {
            "ātmanepada": {
                ("prathama_purusha", "ekavacana"):  "jānītām",
                ("prathama_purusha", "dvivacana"):  "jānātām",
                ("prathama_purusha", "bahuvacana"): "jānatām",
                ("madhyama_purusha", "ekavacana"):  "jānīṣva",
                ("madhyama_purusha", "dvivacana"):  "jānāthām",
                ("madhyama_purusha", "bahuvacana"): "jānīdhvam",
                ("uttama_purusha",   "ekavacana"):  "jānai",
                ("uttama_purusha",   "dvivacana"):  "jānāvahai",
                ("uttama_purusha",   "bahuvacana"): "jānāmahai",
            },
        },
    },
}