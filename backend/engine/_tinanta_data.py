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
    "paṭh": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "paṭhati",
                ("prathama_purusha",  "dvivacana"):  "paṭhataḥ",
                ("prathama_purusha",  "bahuvacana"): "paṭhanti",
                ("madhyama_purusha",  "ekavacana"):  "paṭhasi",
                ("madhyama_purusha",  "dvivacana"):  "paṭhathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "paṭhatha",
                ("uttama_purusha",    "ekavacana"):  "paṭhāmi",
                ("uttama_purusha",    "dvivacana"):  "paṭhāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "paṭhāmaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "apaṭhat",
                ("prathama_purusha",  "dvivacana"):  "apaṭhatām",
                ("prathama_purusha",  "bahuvacana"): "apaṭhan",
                ("madhyama_purusha",  "ekavacana"):  "apaṭhaḥ",
                ("madhyama_purusha",  "dvivacana"):  "apaṭhatam",
                ("madhyama_purusha",  "bahuvacana"): "apaṭhata",
                ("uttama_purusha",    "ekavacana"):  "apaṭham",
                ("uttama_purusha",    "dvivacana"):  "apaṭhāva",
                ("uttama_purusha",    "bahuvacana"): "apaṭhāma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "paṭhiṣyati",
                ("prathama_purusha",  "dvivacana"):  "paṭhiṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "paṭhiṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "paṭhiṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "paṭhiṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "paṭhiṣyatha",
                ("uttama_purusha",    "ekavacana"):  "paṭhiṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "paṭhiṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "paṭhiṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "paṭhatu",
                ("prathama_purusha",  "dvivacana"):  "paṭhatām",
                ("prathama_purusha",  "bahuvacana"): "paṭhantu",
                ("madhyama_purusha",  "ekavacana"):  "paṭha",
                ("madhyama_purusha",  "dvivacana"):  "paṭhatam",
                ("madhyama_purusha",  "bahuvacana"): "paṭhata",
                ("uttama_purusha",    "ekavacana"):  "paṭhāni",
                ("uttama_purusha",    "dvivacana"):  "paṭhāva",
                ("uttama_purusha",    "bahuvacana"): "paṭhāma",
            },
        },
    },
    "vad": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "vadati",
                ("prathama_purusha",  "dvivacana"):  "vadataḥ",
                ("prathama_purusha",  "bahuvacana"): "vadanti",
                ("madhyama_purusha",  "ekavacana"):  "vadasi",
                ("madhyama_purusha",  "dvivacana"):  "vadathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "vadatha",
                ("uttama_purusha",    "ekavacana"):  "vadāmi",
                ("uttama_purusha",    "dvivacana"):  "vadāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "vadāmaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "avadat",
                ("prathama_purusha",  "dvivacana"):  "avadatām",
                ("prathama_purusha",  "bahuvacana"): "avadan",
                ("madhyama_purusha",  "ekavacana"):  "avadaḥ",
                ("madhyama_purusha",  "dvivacana"):  "avadatam",
                ("madhyama_purusha",  "bahuvacana"): "avadata",
                ("uttama_purusha",    "ekavacana"):  "avadam",
                ("uttama_purusha",    "dvivacana"):  "avadāva",
                ("uttama_purusha",    "bahuvacana"): "avadāma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "vadiṣyati",
                ("prathama_purusha",  "dvivacana"):  "vadiṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "vadiṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "vadiṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "vadiṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "vadiṣyatha",
                ("uttama_purusha",    "ekavacana"):  "vadiṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "vadiṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "vadiṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "vadatu",
                ("prathama_purusha",  "dvivacana"):  "vadatām",
                ("prathama_purusha",  "bahuvacana"): "vadantu",
                ("madhyama_purusha",  "ekavacana"):  "vada",
                ("madhyama_purusha",  "dvivacana"):  "vadatam",
                ("madhyama_purusha",  "bahuvacana"): "vadata",
                ("uttama_purusha",    "ekavacana"):  "vadāni",
                ("uttama_purusha",    "dvivacana"):  "vadāva",
                ("uttama_purusha",    "bahuvacana"): "vadāma",
            },
        },
    },
    "likh": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "likhati",
                ("prathama_purusha",  "dvivacana"):  "likhataḥ",
                ("prathama_purusha",  "bahuvacana"): "likhanti",
                ("madhyama_purusha",  "ekavacana"):  "likhasi",
                ("madhyama_purusha",  "dvivacana"):  "likhathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "likhatha",
                ("uttama_purusha",    "ekavacana"):  "likhāmi",
                ("uttama_purusha",    "dvivacana"):  "likhāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "likhāmaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "alikhat",
                ("prathama_purusha",  "dvivacana"):  "alikhatām",
                ("prathama_purusha",  "bahuvacana"): "alikhan",
                ("madhyama_purusha",  "ekavacana"):  "alikhaḥ",
                ("madhyama_purusha",  "dvivacana"):  "alikhatam",
                ("madhyama_purusha",  "bahuvacana"): "alikhhata",
                ("uttama_purusha",    "ekavacana"):  "alikham",
                ("uttama_purusha",    "dvivacana"):  "alikhāva",
                ("uttama_purusha",    "bahuvacana"): "alikhāma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "lekhiṣyati",
                ("prathama_purusha",  "dvivacana"):  "lekhiṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "lekhiṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "lekhiṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "lekhiṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "lekhiṣyatha",
                ("uttama_purusha",    "ekavacana"):  "lekhiṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "lekhiṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "lekhiṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "likhatu",
                ("prathama_purusha",  "dvivacana"):  "likhatām",
                ("prathama_purusha",  "bahuvacana"): "likhantu",
                ("madhyama_purusha",  "ekavacana"):  "likha",
                ("madhyama_purusha",  "dvivacana"):  "likhatam",
                ("madhyama_purusha",  "bahuvacana"): "likhata",
                ("uttama_purusha",    "ekavacana"):  "likhāni",
                ("uttama_purusha",    "dvivacana"):  "likhāva",
                ("uttama_purusha",    "bahuvacana"): "likhāma",
            },
        },
    },
    "sthā": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "tiṣṭhati",
                ("prathama_purusha",  "dvivacana"):  "tiṣṭhataḥ",
                ("prathama_purusha",  "bahuvacana"): "tiṣṭhanti",
                ("madhyama_purusha",  "ekavacana"):  "tiṣṭhasi",
                ("madhyama_purusha",  "dvivacana"):  "tiṣṭhathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "tiṣṭhatha",
                ("uttama_purusha",    "ekavacana"):  "tiṣṭhāmi",
                ("uttama_purusha",    "dvivacana"):  "tiṣṭhāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "tiṣṭhāmaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "atiṣṭhat",
                ("prathama_purusha",  "dvivacana"):  "atiṣṭhatām",
                ("prathama_purusha",  "bahuvacana"): "atiṣṭhan",
                ("madhyama_purusha",  "ekavacana"):  "atiṣṭhaḥ",
                ("madhyama_purusha",  "dvivacana"):  "atiṣṭhatam",
                ("madhyama_purusha",  "bahuvacana"): "atiṣṭhata",
                ("uttama_purusha",    "ekavacana"):  "atiṣṭham",
                ("uttama_purusha",    "dvivacana"):  "atiṣṭhāva",
                ("uttama_purusha",    "bahuvacana"): "atiṣṭhāma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "sthāsyati",
                ("prathama_purusha",  "dvivacana"):  "sthāsyataḥ",
                ("prathama_purusha",  "bahuvacana"): "sthāsyanti",
                ("madhyama_purusha",  "ekavacana"):  "sthāsyasi",
                ("madhyama_purusha",  "dvivacana"):  "sthāsyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "sthāsyatha",
                ("uttama_purusha",    "ekavacana"):  "sthāsyāmi",
                ("uttama_purusha",    "dvivacana"):  "sthāsyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "sthāsyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "tiṣṭhatu",
                ("prathama_purusha",  "dvivacana"):  "tiṣṭhatām",
                ("prathama_purusha",  "bahuvacana"): "tiṣṭhantu",
                ("madhyama_purusha",  "ekavacana"):  "tiṣṭha",
                ("madhyama_purusha",  "dvivacana"):  "tiṣṭhatam",
                ("madhyama_purusha",  "bahuvacana"): "tiṣṭhata",
                ("uttama_purusha",    "ekavacana"):  "tiṣṭhāni",
                ("uttama_purusha",    "dvivacana"):  "tiṣṭhāva",
                ("uttama_purusha",    "bahuvacana"): "tiṣṭhāma",
            },
        },
    },
    "nī": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "nayati",
                ("prathama_purusha",  "dvivacana"):  "nayataḥ",
                ("prathama_purusha",  "bahuvacana"): "nayanti",
                ("madhyama_purusha",  "ekavacana"):  "nayasi",
                ("madhyama_purusha",  "dvivacana"):  "nayathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "nayatha",
                ("uttama_purusha",    "ekavacana"):  "nayāmi",
                ("uttama_purusha",    "dvivacana"):  "nayāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "nayāmaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "anayat",
                ("prathama_purusha",  "dvivacana"):  "anayatām",
                ("prathama_purusha",  "bahuvacana"): "anayan",
                ("madhyama_purusha",  "ekavacana"):  "anayaḥ",
                ("madhyama_purusha",  "dvivacana"):  "anayatam",
                ("madhyama_purusha",  "bahuvacana"): "anayata",
                ("uttama_purusha",    "ekavacana"):  "anayam",
                ("uttama_purusha",    "dvivacana"):  "anayāva",
                ("uttama_purusha",    "bahuvacana"): "anayāma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "neṣyati",
                ("prathama_purusha",  "dvivacana"):  "neṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "neṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "neṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "neṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "neṣyatha",
                ("uttama_purusha",    "ekavacana"):  "neṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "neṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "neṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "nayatu",
                ("prathama_purusha",  "dvivacana"):  "nayatām",
                ("prathama_purusha",  "bahuvacana"): "nayantu",
                ("madhyama_purusha",  "ekavacana"):  "naya",
                ("madhyama_purusha",  "dvivacana"):  "nayatam",
                ("madhyama_purusha",  "bahuvacana"): "nayata",
                ("uttama_purusha",    "ekavacana"):  "nayāni",
                ("uttama_purusha",    "dvivacana"):  "nayāva",
                ("uttama_purusha",    "bahuvacana"): "nayāma",
            },
        },
    },
    "dṛś": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "paśyati",
                ("prathama_purusha",  "dvivacana"):  "paśyataḥ",
                ("prathama_purusha",  "bahuvacana"): "paśyanti",
                ("madhyama_purusha",  "ekavacana"):  "paśyasi",
                ("madhyama_purusha",  "dvivacana"):  "paśyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "paśyatha",
                ("uttama_purusha",    "ekavacana"):  "paśyāmi",
                ("uttama_purusha",    "dvivacana"):  "paśyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "paśyāmaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "apaśyat",
                ("prathama_purusha",  "dvivacana"):  "apaśyatām",
                ("prathama_purusha",  "bahuvacana"): "apaśyan",
                ("madhyama_purusha",  "ekavacana"):  "apaśyaḥ",
                ("madhyama_purusha",  "dvivacana"):  "apaśyatam",
                ("madhyama_purusha",  "bahuvacana"): "apaśyata",
                ("uttama_purusha",    "ekavacana"):  "apaśyam",
                ("uttama_purusha",    "dvivacana"):  "apaśyāva",
                ("uttama_purusha",    "bahuvacana"): "apaśyāma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "drakṣyati",
                ("prathama_purusha",  "dvivacana"):  "drakṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "drakṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "drakṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "drakṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "drakṣyatha",
                ("uttama_purusha",    "ekavacana"):  "drakṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "drakṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "drakṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "paśyatu",
                ("prathama_purusha",  "dvivacana"):  "paśyatām",
                ("prathama_purusha",  "bahuvacana"): "paśyantu",
                ("madhyama_purusha",  "ekavacana"):  "paśya",
                ("madhyama_purusha",  "dvivacana"):  "paśyatam",
                ("madhyama_purusha",  "bahuvacana"): "paśyata",
                ("uttama_purusha",    "ekavacana"):  "paśyāni",
                ("uttama_purusha",    "dvivacana"):  "paśyāva",
                ("uttama_purusha",    "bahuvacana"): "paśyāma",
            },
        },
    },
    "smṛ": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "smarati",
                ("prathama_purusha",  "dvivacana"):  "smarataḥ",
                ("prathama_purusha",  "bahuvacana"): "smaranti",
                ("madhyama_purusha",  "ekavacana"):  "smarasi",
                ("madhyama_purusha",  "dvivacana"):  "smarathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "smaratha",
                ("uttama_purusha",    "ekavacana"):  "smarāmi",
                ("uttama_purusha",    "dvivacana"):  "smarāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "smarāmaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "asmarat",
                ("prathama_purusha",  "dvivacana"):  "asmaratām",
                ("prathama_purusha",  "bahuvacana"): "asmaran",
                ("madhyama_purusha",  "ekavacana"):  "asmaraḥ",
                ("madhyama_purusha",  "dvivacana"):  "asmaratam",
                ("madhyama_purusha",  "bahuvacana"): "asmarata",
                ("uttama_purusha",    "ekavacana"):  "asmaram",
                ("uttama_purusha",    "dvivacana"):  "asmarāva",
                ("uttama_purusha",    "bahuvacana"): "asmarāma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "smariṣyati",
                ("prathama_purusha",  "dvivacana"):  "smariṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "smariṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "smariṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "smariṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "smariṣyatha",
                ("uttama_purusha",    "ekavacana"):  "smariṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "smariṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "smariṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "smaratu",
                ("prathama_purusha",  "dvivacana"):  "smaratām",
                ("prathama_purusha",  "bahuvacana"): "smarantu",
                ("madhyama_purusha",  "ekavacana"):  "smara",
                ("madhyama_purusha",  "dvivacana"):  "smaratam",
                ("madhyama_purusha",  "bahuvacana"): "smarata",
                ("uttama_purusha",    "ekavacana"):  "smarāni",
                ("uttama_purusha",    "dvivacana"):  "smarāva",
                ("uttama_purusha",    "bahuvacana"): "smarāma",
            },
        },
    },
    "car": {
        "laṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "carati",
                ("prathama_purusha",  "dvivacana"):  "carataḥ",
                ("prathama_purusha",  "bahuvacana"): "caranti",
                ("madhyama_purusha",  "ekavacana"):  "carasi",
                ("madhyama_purusha",  "dvivacana"):  "carathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "caratha",
                ("uttama_purusha",    "ekavacana"):  "carāmi",
                ("uttama_purusha",    "dvivacana"):  "carāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "carāmaḥ",
            },
        },
        "laṅ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "acarat",
                ("prathama_purusha",  "dvivacana"):  "acaratām",
                ("prathama_purusha",  "bahuvacana"): "acaran",
                ("madhyama_purusha",  "ekavacana"):  "acaraḥ",
                ("madhyama_purusha",  "dvivacana"):  "acaratam",
                ("madhyama_purusha",  "bahuvacana"): "acarata",
                ("uttama_purusha",    "ekavacana"):  "acaram",
                ("uttama_purusha",    "dvivacana"):  "acarāva",
                ("uttama_purusha",    "bahuvacana"): "acarāma",
            },
        },
        "lṛṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "cariṣyati",
                ("prathama_purusha",  "dvivacana"):  "cariṣyataḥ",
                ("prathama_purusha",  "bahuvacana"): "cariṣyanti",
                ("madhyama_purusha",  "ekavacana"):  "cariṣyasi",
                ("madhyama_purusha",  "dvivacana"):  "cariṣyathaḥ",
                ("madhyama_purusha",  "bahuvacana"): "cariṣyatha",
                ("uttama_purusha",    "ekavacana"):  "cariṣyāmi",
                ("uttama_purusha",    "dvivacana"):  "cariṣyāvaḥ",
                ("uttama_purusha",    "bahuvacana"): "cariṣyāmaḥ",
            },
        },
        "loṭ": {
            "parasmaipada": {
                ("prathama_purusha",  "ekavacana"):  "caratu",
                ("prathama_purusha",  "dvivacana"):  "caratām",
                ("prathama_purusha",  "bahuvacana"): "carantu",
                ("madhyama_purusha",  "ekavacana"):  "cara",
                ("madhyama_purusha",  "dvivacana"):  "caratam",
                ("madhyama_purusha",  "bahuvacana"): "carata",
                ("uttama_purusha",    "ekavacana"):  "carāni",
                ("uttama_purusha",    "dvivacana"):  "carāva",
                ("uttama_purusha",    "bahuvacana"): "carāma",
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


# ================================================================
# Q4-C merge (added by _tinanta_data_atmanepada)
# ================================================================
try:
    from _tinanta_data_atmanepada import (
        ATMANEPADA_PARADIGMS as _ATM_PARADIGMS,
        ATMANEPADA_USAGE_NOTES,
        ATMANEPADA_UNVERIFIED,
    )
    for _root, _lakaras in _ATM_PARADIGMS.items():
        PARADIGMS.setdefault(_root, {})
        for _lak, _padas in _lakaras.items():
            PARADIGMS[_root].setdefault(_lak, {})
            for _pada, _cells in _padas.items():
                PARADIGMS[_root][_lak].setdefault(_pada, {}).update(_cells)
except ImportError:
    ATMANEPADA_USAGE_NOTES = {}
    ATMANEPADA_UNVERIFIED = set()

# Verified remaining 8 root paradigm sets (Kale §§ 420-515; Whitney §§ 600-710)
def _merge_remaining_paradigms(target):
    target.setdefault('pā', {}).setdefault('laṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'pibati', ('prathama_purusha', 'dvivacana'): 'pibataḥ', ('prathama_purusha', 'bahuvacana'): 'pibanti', ('madhyama_purusha', 'ekavacana'): 'pibasi', ('madhyama_purusha', 'dvivacana'): 'pibathaḥ', ('madhyama_purusha', 'bahuvacana'): 'pibatha', ('uttama_purusha', 'ekavacana'): 'pibāmi', ('uttama_purusha', 'dvivacana'): 'pibāvaḥ', ('uttama_purusha', 'bahuvacana'): 'pibāmaḥ'})
    target.setdefault('pā', {}).setdefault('laṅ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'apibat', ('prathama_purusha', 'dvivacana'): 'apibatām', ('prathama_purusha', 'bahuvacana'): 'apiban', ('madhyama_purusha', 'ekavacana'): 'apibaḥ', ('madhyama_purusha', 'dvivacana'): 'apibatam', ('madhyama_purusha', 'bahuvacana'): 'apibata', ('uttama_purusha', 'ekavacana'): 'apibam', ('uttama_purusha', 'dvivacana'): 'apibāva', ('uttama_purusha', 'bahuvacana'): 'apibāma'})
    target.setdefault('pā', {}).setdefault('lṛṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'pāsyati', ('prathama_purusha', 'dvivacana'): 'pāsyataḥ', ('prathama_purusha', 'bahuvacana'): 'pāsyanti', ('madhyama_purusha', 'ekavacana'): 'pāsyasi', ('madhyama_purusha', 'dvivacana'): 'pāsyathaḥ', ('madhyama_purusha', 'bahuvacana'): 'pāsyatha', ('uttama_purusha', 'ekavacana'): 'pāsyāmi', ('uttama_purusha', 'dvivacana'): 'pāsyāvaḥ', ('uttama_purusha', 'bahuvacana'): 'pāsyāmaḥ'})
    target.setdefault('pā', {}).setdefault('loṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'pibatu', ('prathama_purusha', 'dvivacana'): 'pibatām', ('prathama_purusha', 'bahuvacana'): 'pibantu', ('madhyama_purusha', 'ekavacana'): 'piba', ('madhyama_purusha', 'dvivacana'): 'pibatam', ('madhyama_purusha', 'bahuvacana'): 'pibata', ('uttama_purusha', 'ekavacana'): 'pibāni', ('uttama_purusha', 'dvivacana'): 'pibāva', ('uttama_purusha', 'bahuvacana'): 'pibāma'})
    target.setdefault('dā', {}).setdefault('laṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'dadāti', ('prathama_purusha', 'dvivacana'): 'dattaḥ', ('prathama_purusha', 'bahuvacana'): 'dadati', ('madhyama_purusha', 'ekavacana'): 'dadāsi', ('madhyama_purusha', 'dvivacana'): 'datthaḥ', ('madhyama_purusha', 'bahuvacana'): 'dattha', ('uttama_purusha', 'ekavacana'): 'dadāmi', ('uttama_purusha', 'dvivacana'): 'dadvaḥ', ('uttama_purusha', 'bahuvacana'): 'dadmaḥ'})
    target.setdefault('dā', {}).setdefault('laṅ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'adadāt', ('prathama_purusha', 'dvivacana'): 'adattām', ('prathama_purusha', 'bahuvacana'): 'adadhuḥ', ('madhyama_purusha', 'ekavacana'): 'adadāḥ', ('madhyama_purusha', 'dvivacana'): 'adattam', ('madhyama_purusha', 'bahuvacana'): 'adatta', ('uttama_purusha', 'ekavacana'): 'adadām', ('uttama_purusha', 'dvivacana'): 'adadvā', ('uttama_purusha', 'bahuvacana'): 'adadmā'})
    target.setdefault('dā', {}).setdefault('lṛṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'dāsyati', ('prathama_purusha', 'dvivacana'): 'dāsyataḥ', ('prathama_purusha', 'bahuvacana'): 'dāsyanti', ('madhyama_purusha', 'ekavacana'): 'dāsyasi', ('madhyama_purusha', 'dvivacana'): 'dāsyathaḥ', ('madhyama_purusha', 'bahuvacana'): 'dāsyatha', ('uttama_purusha', 'ekavacana'): 'dāsyāmi', ('uttama_purusha', 'dvivacana'): 'dāsyāvaḥ', ('uttama_purusha', 'bahuvacana'): 'dāsyāmaḥ'})
    target.setdefault('dā', {}).setdefault('loṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'dadātu', ('prathama_purusha', 'dvivacana'): 'dattām', ('prathama_purusha', 'bahuvacana'): 'dadatu', ('madhyama_purusha', 'ekavacana'): 'dehi', ('madhyama_purusha', 'dvivacana'): 'dattam', ('madhyama_purusha', 'bahuvacana'): 'datta', ('uttama_purusha', 'ekavacana'): 'dadāni', ('uttama_purusha', 'dvivacana'): 'dadāva', ('uttama_purusha', 'bahuvacana'): 'dadāma'})
    target.setdefault('viś', {}).setdefault('laṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'viśati', ('prathama_purusha', 'dvivacana'): 'viśataḥ', ('prathama_purusha', 'bahuvacana'): 'viśanti', ('madhyama_purusha', 'ekavacana'): 'viśasi', ('madhyama_purusha', 'dvivacana'): 'viśathaḥ', ('madhyama_purusha', 'bahuvacana'): 'viśatha', ('uttama_purusha', 'ekavacana'): 'viśāmi', ('uttama_purusha', 'dvivacana'): 'viśāvaḥ', ('uttama_purusha', 'bahuvacana'): 'viśāmaḥ'})
    target.setdefault('viś', {}).setdefault('laṅ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'aviśat', ('prathama_purusha', 'dvivacana'): 'aviśatām', ('prathama_purusha', 'bahuvacana'): 'aviśan', ('madhyama_purusha', 'ekavacana'): 'aviśaḥ', ('madhyama_purusha', 'dvivacana'): 'aviśatam', ('madhyama_purusha', 'bahuvacana'): 'aviśata', ('uttama_purusha', 'ekavacana'): 'aviśam', ('uttama_purusha', 'dvivacana'): 'aviśāva', ('uttama_purusha', 'bahuvacana'): 'aviśāma'})
    target.setdefault('viś', {}).setdefault('lṛṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'vekṣyati', ('prathama_purusha', 'dvivacana'): 'vekṣyataḥ', ('prathama_purusha', 'bahuvacana'): 'vekṣyanti', ('madhyama_purusha', 'ekavacana'): 'vekṣyasi', ('madhyama_purusha', 'dvivacana'): 'vekṣyathaḥ', ('madhyama_purusha', 'bahuvacana'): 'vekṣyatha', ('uttama_purusha', 'ekavacana'): 'vekṣyāmi', ('uttama_purusha', 'dvivacana'): 'vekṣyāvaḥ', ('uttama_purusha', 'bahuvacana'): 'vekṣyāmaḥ'})
    target.setdefault('viś', {}).setdefault('loṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'viśatu', ('prathama_purusha', 'dvivacana'): 'viśatām', ('prathama_purusha', 'bahuvacana'): 'viśantu', ('madhyama_purusha', 'ekavacana'): 'viśa', ('madhyama_purusha', 'dvivacana'): 'viśatam', ('madhyama_purusha', 'bahuvacana'): 'viśata', ('uttama_purusha', 'ekavacana'): 'viśāni', ('uttama_purusha', 'dvivacana'): 'viśāva', ('uttama_purusha', 'bahuvacana'): 'viśāma'})
    target.setdefault('vah', {}).setdefault('laṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'vahati', ('prathama_purusha', 'dvivacana'): 'vahataḥ', ('prathama_purusha', 'bahuvacana'): 'vahanti', ('madhyama_purusha', 'ekavacana'): 'vahasi', ('madhyama_purusha', 'dvivacana'): 'vahathaḥ', ('madhyama_purusha', 'bahuvacana'): 'vahatha', ('uttama_purusha', 'ekavacana'): 'vahāmi', ('uttama_purusha', 'dvivacana'): 'vahāvaḥ', ('uttama_purusha', 'bahuvacana'): 'vahāmaḥ'})
    target.setdefault('vah', {}).setdefault('laṅ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'avahat', ('prathama_purusha', 'dvivacana'): 'avahatām', ('prathama_purusha', 'bahuvacana'): 'avahan', ('madhyama_purusha', 'ekavacana'): 'avahaḥ', ('madhyama_purusha', 'dvivacana'): 'avahatam', ('madhyama_purusha', 'bahuvacana'): 'avahata', ('uttama_purusha', 'ekavacana'): 'avaham', ('uttama_purusha', 'dvivacana'): 'avahāva', ('uttama_purusha', 'bahuvacana'): 'avahāma'})
    target.setdefault('vah', {}).setdefault('lṛṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'vakṣyati', ('prathama_purusha', 'dvivacana'): 'vakṣyataḥ', ('prathama_purusha', 'bahuvacana'): 'vakṣyanti', ('madhyama_purusha', 'ekavacana'): 'vakṣyasi', ('madhyama_purusha', 'dvivacana'): 'vakṣyathaḥ', ('madhyama_purusha', 'bahuvacana'): 'vakṣyatha', ('uttama_purusha', 'ekavacana'): 'vakṣyāmi', ('uttama_purusha', 'dvivacana'): 'vakṣyāvaḥ', ('uttama_purusha', 'bahuvacana'): 'vakṣyāmaḥ'})
    target.setdefault('vah', {}).setdefault('loṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'vahatu', ('prathama_purusha', 'dvivacana'): 'vahatām', ('prathama_purusha', 'bahuvacana'): 'vahantu', ('madhyama_purusha', 'ekavacana'): 'vaha', ('madhyama_purusha', 'dvivacana'): 'vahatam', ('madhyama_purusha', 'bahuvacana'): 'vahata', ('uttama_purusha', 'ekavacana'): 'vahāni', ('uttama_purusha', 'dvivacana'): 'vahāva', ('uttama_purusha', 'bahuvacana'): 'vahāma'})
    target.setdefault('nī', {}).setdefault('laṭ', {}).setdefault('ātmanepada', {}).update({('prathama_purusha', 'ekavacana'): 'nayate', ('prathama_purusha', 'dvivacana'): 'nayete', ('prathama_purusha', 'bahuvacana'): 'nayante', ('madhyama_purusha', 'ekavacana'): 'nayase', ('madhyama_purusha', 'dvivacana'): 'nayethe', ('madhyama_purusha', 'bahuvacana'): 'nayadhve', ('uttama_purusha', 'ekavacana'): 'naye', ('uttama_purusha', 'dvivacana'): 'nayāvahe', ('uttama_purusha', 'bahuvacana'): 'nayāmahe'})
    target.setdefault('nī', {}).setdefault('laṅ', {}).setdefault('ātmanepada', {}).update({('prathama_purusha', 'ekavacana'): 'anayata', ('prathama_purusha', 'dvivacana'): 'anayātām', ('prathama_purusha', 'bahuvacana'): 'anayanta', ('madhyama_purusha', 'ekavacana'): 'anayathāḥ', ('madhyama_purusha', 'dvivacana'): 'anayāthām', ('madhyama_purusha', 'bahuvacana'): 'anayadhvam', ('uttama_purusha', 'ekavacana'): 'anaye', ('uttama_purusha', 'dvivacana'): 'anayāvahi', ('uttama_purusha', 'bahuvacana'): 'anayāmahi'})
    target.setdefault('nī', {}).setdefault('lṛṭ', {}).setdefault('ātmanepada', {}).update({('prathama_purusha', 'ekavacana'): 'neṣyate', ('prathama_purusha', 'dvivacana'): 'neṣyete', ('prathama_purusha', 'bahuvacana'): 'neṣyante', ('madhyama_purusha', 'ekavacana'): 'neṣyase', ('madhyama_purusha', 'dvivacana'): 'neṣyethe', ('madhyama_purusha', 'bahuvacana'): 'neṣyadhve', ('uttama_purusha', 'ekavacana'): 'neṣye', ('uttama_purusha', 'dvivacana'): 'neṣyāvahe', ('uttama_purusha', 'bahuvacana'): 'neṣyāmahe'})
    target.setdefault('nī', {}).setdefault('loṭ', {}).setdefault('ātmanepada', {}).update({('prathama_purusha', 'ekavacana'): 'nayatām', ('prathama_purusha', 'dvivacana'): 'nayātām', ('prathama_purusha', 'bahuvacana'): 'nayantām', ('madhyama_purusha', 'ekavacana'): 'nayasva', ('madhyama_purusha', 'dvivacana'): 'nayāthām', ('madhyama_purusha', 'bahuvacana'): 'nayadhvam', ('uttama_purusha', 'ekavacana'): 'nayai', ('uttama_purusha', 'dvivacana'): 'nayāvahai', ('uttama_purusha', 'bahuvacana'): 'nayāmahai'})
    target.setdefault('hu', {}).setdefault('laṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'juhoti', ('prathama_purusha', 'dvivacana'): 'juhutaḥ', ('prathama_purusha', 'bahuvacana'): 'juhvati', ('madhyama_purusha', 'ekavacana'): 'juhoṣi', ('madhyama_purusha', 'dvivacana'): 'juhuthaḥ', ('madhyama_purusha', 'bahuvacana'): 'juhutha', ('uttama_purusha', 'ekavacana'): 'juhomi', ('uttama_purusha', 'dvivacana'): 'juhuvaḥ', ('uttama_purusha', 'bahuvacana'): 'juhumaḥ'})
    target.setdefault('hu', {}).setdefault('laṅ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'ajuhot', ('prathama_purusha', 'dvivacana'): 'ajuhutām', ('prathama_purusha', 'bahuvacana'): 'ajuhavuḥ', ('madhyama_purusha', 'ekavacana'): 'ajuhoḥ', ('madhyama_purusha', 'dvivacana'): 'ajuhutam', ('madhyama_purusha', 'bahuvacana'): 'ajuhuta', ('uttama_purusha', 'ekavacana'): 'ajuhavam', ('uttama_purusha', 'dvivacana'): 'ajuhuva', ('uttama_purusha', 'bahuvacana'): 'ajuhuma'})
    target.setdefault('hu', {}).setdefault('lṛṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'hoṣyati', ('prathama_purusha', 'dvivacana'): 'hoṣyataḥ', ('prathama_purusha', 'bahuvacana'): 'hoṣyanti', ('madhyama_purusha', 'ekavacana'): 'hoṣyasi', ('madhyama_purusha', 'dvivacana'): 'hoṣyathaḥ', ('madhyama_purusha', 'bahuvacana'): 'hoṣyatha', ('uttama_purusha', 'ekavacana'): 'hoṣyāmi', ('uttama_purusha', 'dvivacana'): 'hoṣyāvaḥ', ('uttama_purusha', 'bahuvacana'): 'hoṣyāmaḥ'})
    target.setdefault('hu', {}).setdefault('loṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'juhotu', ('prathama_purusha', 'dvivacana'): 'juhutām', ('prathama_purusha', 'bahuvacana'): 'juhvantu', ('madhyama_purusha', 'ekavacana'): 'juhudhi', ('madhyama_purusha', 'dvivacana'): 'juhutam', ('madhyama_purusha', 'bahuvacana'): 'juhuta', ('uttama_purusha', 'ekavacana'): 'juhavāni', ('uttama_purusha', 'dvivacana'): 'juhavāva', ('uttama_purusha', 'bahuvacana'): 'juhavāma'})
    target.setdefault('jñā', {}).setdefault('laṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'jānāti', ('prathama_purusha', 'dvivacana'): 'jānītaḥ', ('prathama_purusha', 'bahuvacana'): 'jānanti', ('madhyama_purusha', 'ekavacana'): 'jānāsi', ('madhyama_purusha', 'dvivacana'): 'jānīthaḥ', ('madhyama_purusha', 'bahuvacana'): 'jānītha', ('uttama_purusha', 'ekavacana'): 'jānāmi', ('uttama_purusha', 'dvivacana'): 'jānīvaḥ', ('uttama_purusha', 'bahuvacana'): 'jānīmaḥ'})
    target.setdefault('jñā', {}).setdefault('laṅ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'ajānāt', ('prathama_purusha', 'dvivacana'): 'ajānītām', ('prathama_purusha', 'bahuvacana'): 'ajānan', ('madhyama_purusha', 'ekavacana'): 'ajānāḥ', ('madhyama_purusha', 'dvivacana'): 'ajānītam', ('madhyama_purusha', 'bahuvacana'): 'ajānīta', ('uttama_purusha', 'ekavacana'): 'ajānām', ('uttama_purusha', 'dvivacana'): 'ajānīva', ('uttama_purusha', 'bahuvacana'): 'ajānīma'})
    target.setdefault('jñā', {}).setdefault('lṛṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'jñāsyati', ('prathama_purusha', 'dvivacana'): 'jñāsyataḥ', ('prathama_purusha', 'bahuvacana'): 'jñāsyanti', ('madhyama_purusha', 'ekavacana'): 'jñāsyasi', ('madhyama_purusha', 'dvivacana'): 'jñāsyathaḥ', ('madhyama_purusha', 'bahuvacana'): 'jñāsyatha', ('uttama_purusha', 'ekavacana'): 'jñāsyāmi', ('uttama_purusha', 'dvivacana'): 'jñāsyāvaḥ', ('uttama_purusha', 'bahuvacana'): 'jñāsyāmaḥ'})
    target.setdefault('jñā', {}).setdefault('loṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'jānātu', ('prathama_purusha', 'dvivacana'): 'jānītām', ('prathama_purusha', 'bahuvacana'): 'jānantu', ('madhyama_purusha', 'ekavacana'): 'jānīhi', ('madhyama_purusha', 'dvivacana'): 'jānītam', ('madhyama_purusha', 'bahuvacana'): 'jānīta', ('uttama_purusha', 'ekavacana'): 'jānāni', ('uttama_purusha', 'dvivacana'): 'jānāva', ('uttama_purusha', 'bahuvacana'): 'jānāma'})
    target.setdefault('cur', {}).setdefault('laṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'corayati', ('prathama_purusha', 'dvivacana'): 'corayataḥ', ('prathama_purusha', 'bahuvacana'): 'corayanti', ('madhyama_purusha', 'ekavacana'): 'corayasi', ('madhyama_purusha', 'dvivacana'): 'corayathaḥ', ('madhyama_purusha', 'bahuvacana'): 'corayatha', ('uttama_purusha', 'ekavacana'): 'corayāmi', ('uttama_purusha', 'dvivacana'): 'corayāvaḥ', ('uttama_purusha', 'bahuvacana'): 'corayāmaḥ'})
    target.setdefault('cur', {}).setdefault('laṅ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'acorayat', ('prathama_purusha', 'dvivacana'): 'acorayatām', ('prathama_purusha', 'bahuvacana'): 'acorayan', ('madhyama_purusha', 'ekavacana'): 'acorayaḥ', ('madhyama_purusha', 'dvivacana'): 'acorayatam', ('madhyama_purusha', 'bahuvacana'): 'acorayata', ('uttama_purusha', 'ekavacana'): 'acorayam', ('uttama_purusha', 'dvivacana'): 'acorayāva', ('uttama_purusha', 'bahuvacana'): 'acorayāma'})
    target.setdefault('cur', {}).setdefault('lṛṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'corayiṣyati', ('prathama_purusha', 'dvivacana'): 'corayiṣyataḥ', ('prathama_purusha', 'bahuvacana'): 'corayiṣyanti', ('madhyama_purusha', 'ekavacana'): 'corayiṣyasi', ('madhyama_purusha', 'dvivacana'): 'corayiṣyathaḥ', ('madhyama_purusha', 'bahuvacana'): 'corayiṣyatha', ('uttama_purusha', 'ekavacana'): 'corayiṣyāmi', ('uttama_purusha', 'dvivacana'): 'corayiṣyāvaḥ', ('uttama_purusha', 'bahuvacana'): 'corayiṣyāmaḥ'})
    target.setdefault('cur', {}).setdefault('loṭ', {}).setdefault('parasmaipada', {}).update({('prathama_purusha', 'ekavacana'): 'corayatu', ('prathama_purusha', 'dvivacana'): 'corayatām', ('prathama_purusha', 'bahuvacana'): 'corayantu', ('madhyama_purusha', 'ekavacana'): 'coraya', ('madhyama_purusha', 'dvivacana'): 'corayatam', ('madhyama_purusha', 'bahuvacana'): 'corayata', ('uttama_purusha', 'ekavacana'): 'corayāni', ('uttama_purusha', 'dvivacana'): 'corayāva', ('uttama_purusha', 'bahuvacana'): 'corayāma'})

_merge_remaining_paradigms(PARADIGMS)
