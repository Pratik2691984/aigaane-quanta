"""
Tiṅanta data tables for Q4-B (laṅ, lṛṭ, loṭ, laṭ).

Companion to _lexicon.py. Keeps paradigm tables for the four priority
roots (kṛ, bhū, gam, as) and the imperative ending tables.

Each entry is a dict keyed by (purusha, vacana) → surface form.
"""

# ----------------------------------------------------------------
# Imperative (loṭ) endings — 3.4.85–3.4.91
# ----------------------------------------------------------------

_LOT_PARASMAI = [
    ("tu",   "ekavacana",  "prathama_purusha"),
    ("tām",  "dvivacana",  "prathama_purusha"),
    ("antu", "bahuvacana", "prathama_purusha"),
    ("hi",   "ekavacana",  "madhyama_purusha"),
    ("tam",  "dvivacana",  "madhyama_purusha"),
    ("ta",   "bahuvacana", "madhyama_purusha"),
    ("āni",  "ekavacana",  "uttama_purusha"),
    ("āva",  "dvivacana",  "uttama_purusha"),
    ("āma",  "bahuvacana", "uttama_purusha"),
]

_LOT_ATMANE = [
    ("tām",   "ekavacana",  "prathama_purusha"),
    ("etām",  "dvivacana",  "prathama_purusha"),
    ("antām", "bahuvacana", "prathama_purusha"),
    ("svā",   "ekavacana",  "madhyama_purusha"),
    ("ethām", "dvivacana",  "madhyama_purusha"),
    ("dhvam", "bahuvacana", "madhyama_purusha"),
    ("ai",    "ekavacana",  "uttama_purusha"),
    ("āvahai","dvivacana",  "uttama_purusha"),
    ("āmahai","bahuvacana", "uttama_purusha"),
]

# ----------------------------------------------------------------
# Paradigm tables — verified forms
# Keyed as: PARADIGMS[dhatu][lakara][pada][(purusha, vacana)] = surface
# Only parasmaipada is populated for all four roots.
# Atmanepada is populated for kṛ and cur (the ubhayapada roots we trust).
# ----------------------------------------------------------------

PARADIGMS = {
    "bhū": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "bhavati",
                ("prathama_purusha",  "dvivacana"):  "bhavataḥ",
                ("prathama_purusha",  "bahuvacana"): "bhavanti",
                ("madhyama_purusha",  "ekavacana"):  "bhavasi",
                ("madhyama_purusha",  "dvivacana"):  "bhavathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "bhavatha",
                ("uttama_purusha",    "ekavacana"):  "bhavāmi",
                ("uttama_purusha",    "dvivacana"):  "bhavāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "bhavāmaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "abhavat",
                ("prathama_purusha",  "dvivacana"):  "abhavatām",
                ("prathama_purusha",  "bahuvacana"): "abhavan",
                ("madhyama_purusha",  "ekavacana"):  "abhavaḥ",
                ("madhyama_purusha",  "dvivacana"):  "abhavatam",
                ("madhyama_purusha",  "bahuvacana"): "abhavata",
                ("uttama_purusha",    "ekavacana"):  "abhavam",
                ("uttama_purusha",    "dvivacana"):  "abhavāva",
                ("uttama_purusha",    "bahuvacana"): "abhavāma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "bhaviṣyati",
                ("prathama_purusha",  "dvivacana"):  "bhaviṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "bhaviṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "bhaviṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "bhaviṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "bhaviṣyatha",
                ("uttama_purusha",    "ekavacana"):  "bhaviṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "bhaviṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "bhaviṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "bhavatu",
                ("prathama_purusha",  "dvivacana"):  "bhavatām",
                ("prathama_purusha",  "bahuvacana"): "bhavantu",
                ("madhyama_purusha",  "ekavacana"):  "bhava",
                ("madhyama_purusha",  "dvivacana"):  "bhavatam",
                ("madhyama_purusha",  "bahuvacana"): "bhavata",
                ("uttama_purusha",    "ekavacana"):  "bhavāni",
                ("uttama_purusha",    "dvivacana"):  "bhavāva",
                ("uttama_purusha",    "bahuvacana"): "bhavāma",
            },
        },
    },
    "gam": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "gacchati",
                ("prathama_purusha",  "dvivacana"):  "gacchataḥ",
                ("prathama_purusha",  "bahuvacana"): "gacchanti",
                ("madhyama_purusha",  "ekavacana"):  "gacchasi",
                ("madhyama_purusha",  "dvivacana"):  "gacchathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "gacchatha",
                ("uttama_purusha",    "ekavacana"):  "gacchāmi",
                ("uttama_purusha",    "dvivacana"):  "gacchāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "gacchāmaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "agacchat",
                ("prathama_purusha",  "dvivacana"):  "agacchatām",
                ("prathama_purusha",  "bahuvacana"): "agacchan",
                ("madhyama_purusha",  "ekavacana"):  "agacchaḥ",
                ("madhyama_purusha",  "dvivacana"):  "agacchatam",
                ("madhyama_purusha",  "bahuvacana"): "agacchata",
                ("uttama_purusha",    "ekavacana"):  "agaccham",
                ("uttama_purusha",    "dvivacana"):  "agacchāva",
                ("uttama_purusha",    "bahuvacana"): "agacchāma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "gamiṣyati",
                ("prathama_purusha",  "dvivacana"):  "gamiṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "gamiṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "gamiṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "gamiṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "gamiṣyatha",
                ("uttama_purusha",    "ekavacana"):  "gamiṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "gamiṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "gamiṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "gacchatu",
                ("prathama_purusha",  "dvivacana"):  "gacchatām",
                ("prathama_purusha",  "bahuvacana"): "gacchantu",
                ("madhyama_purusha",  "ekavacana"):  "gaccha",
                ("madhyama_purusha",  "dvivacana"):  "gacchatam",
                ("madhyama_purusha",  "bahuvacana"): "gacchata",
                ("uttama_purusha",    "ekavacana"):  "gacchāni",
                ("uttama_purusha",    "dvivacana"):  "gacchāva",
                ("uttama_purusha",    "bahuvacana"): "gacchāma",
            },
        },
    },
    "kṛ": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "karoti",
                ("prathama_purusha",  "dvivacana"):  "kurutaḥ",
                ("prathama_purusha",  "bahuvacana"): "kurvanti",
                ("madhyama_purusha",  "ekavacana"):  "karoṣi",
                ("madhyama_purusha",  "dvivacana"):  "kuruthaḥ",
                ("madhyama_purusha",  "bahuvacana"): "kurutha",
                ("uttama_purusha",    "ekavacana"):  "karomi",
                ("uttama_purusha",    "dvivacana"):  "kurvaḥ",
                ("uttama_purusha",    "bahuvacana"): "kurmaḥ",
            },
            "ātmanepada": {
                ("prathama_purusha",  "ekavacana"):  "kurute",
                ("prathama_purusha",  "dvivacana"):  "kurvāte",
                ("prathama_purusha",  "bahuvacana"): "kurvate",
                ("madhyama_purusha",  "ekavacana"):  "kurviṣe",
                ("madhyama_purusha",  "dvivacana"):  "kurvāthe",
                ("madhyama_purusha",  "bahuvacana"): "kurudhve",
                ("uttama_purusha",    "ekavacana"):  "kurve",
                ("uttama_purusha",    "dvivacana"):  "kurvahe",
                ("uttama_purusha",    "bahuvacana"): "kurmahe",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "akarot",
                ("prathama_purusha",  "dvivacana"):  "akurutām",
                ("prathama_purusha",  "bahuvacana"): "akurvan",
                ("madhyama_purusha",  "ekavacana"):  "akaroḥ",
                ("madhyama_purusha",  "dvivacana"):  "akurutam",
                ("madhyama_purusha",  "bahuvacana"): "akuruta",
                ("uttama_purusha",    "ekavacana"):  "akaram",
                ("uttama_purusha",    "dvivacana"):  "akurva",
                ("uttama_purusha",    "bahuvacana"): "akurma",
            },
            "ātmanepada": {
                ("prathama_purusha",  "ekavacana"):  "akuruta",
                ("prathama_purusha",  "dvivacana"):  "akurvātām",
                ("prathama_purusha",  "bahuvacana"): "akurvata",
                ("madhyama_purusha",  "ekavacana"):  "akuruthāḥ",
                ("madhyama_purusha",  "dvivacana"):  "akurvāthām",
                ("madhyama_purusha",  "bahuvacana"): "akurudhvam",
                ("uttama_purusha",    "ekavacana"):  "akurvi",
                ("uttama_purusha",    "dvivacana"):  "akurvahi",
                ("uttama_purusha",    "bahuvacana"): "akurmahi",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "kariṣyati",
                ("prathama_purusha",  "dvivacana"):  "kariṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "kariṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "kariṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "kariṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "kariṣyatha",
                ("uttama_purusha",    "ekavacana"):  "kariṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "kariṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "kariṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "karotu",
                ("prathama_purusha",  "dvivacana"):  "kurutām",
                ("prathama_purusha",  "bahuvacana"): "kurvantu",
                ("madhyama_purusha",  "ekavacana"):  "kuru",
                ("madhyama_purusha",  "dvivacana"):  "kurutam",
                ("madhyama_purusha",  "bahuvacana"): "kuruta",
                ("uttama_purusha",    "ekavacana"):  "karavāni",
                ("uttama_purusha",    "dvivacana"):  "karavāva",
                ("uttama_purusha",    "bahuvacana"): "karavāma",
            },
        },
    },
    "as": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "asti",
                ("prathama_purusha",  "dvivacana"):  "staḥ",
                ("prathama_purusha",  "bahuvacana"): "santi",
                ("madhyama_purusha",  "ekavacana"):  "asi",
                ("madhyama_purusha",  "dvivacana"):  "sthaḥ",
                ("madhyama_purusha",  "bahuvacana"): "stha",
                ("uttama_purusha",    "ekavacana"):  "asmi",
                ("uttama_purusha",    "dvivacana"):  "svaḥ",
                ("uttama_purusha",    "bahuvacana"): "smaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "āsīt",
                ("prathama_purusha",  "dvivacana"):  "āstām",
                ("prathama_purusha",  "bahuvacana"): "āsan",
                ("madhyama_purusha",  "ekavacana"):  "āsīḥ",
                ("madhyama_purusha",  "dvivacana"):  "āstam",
                ("madhyama_purusha",  "bahuvacana"): "āsta",
                ("uttama_purusha",    "ekavacana"):  "āsam",
                ("uttama_purusha",    "dvivacana"):  "āsva",
                ("uttama_purusha",    "bahuvacana"): "āsma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "bhaviṣyati",
                ("prathama_purusha",  "dvivacana"):  "bhaviṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "bhaviṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "bhaviṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "bhaviṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "bhaviṣyatha",
                ("uttama_purusha",    "ekavacana"):  "bhaviṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "bhaviṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "bhaviṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "astu",
                ("prathama_purusha",  "dvivacana"):  "stām",
                ("prathama_purusha",  "bahuvacana"): "santu",
                ("madhyama_purusha",  "ekavacana"):  "edhi",
                ("madhyama_purusha",  "dvivacana"):  "stam",
                ("madhyama_purusha",  "bahuvacana"): "sta",
                ("uttama_purusha",    "ekavacana"):  "asāni",
                ("uttama_purusha",    "dvivacana"):  "asāva",
                ("uttama_purusha",    "bahuvacana"): "asāma",
            },
        },
    },
}