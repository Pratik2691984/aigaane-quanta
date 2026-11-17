"""
L6 Śikṣā Articulatory Varṇa Inventory (P1-2).

Implements classical Pāṇinīya Śikṣā / Taittirīya Prātiśākhya articulatory
classification for every Sanskrit phoneme (IAST & Devanāgarī), preventing
modern Hindi phonological conflations (such as schwa deletion or v/w collapse).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Optional

Sthana = Literal[
    "kanthya",
    "talavya",
    "murdhanya",
    "dantya",
    "osthya",
    "nasikya",
    "kanthatalavya",
    "kanthosthya",
    "dantosthya",
    "urasya",
]

Prayatna = Literal[
    "sprsta",
    "isatsprsta",
    "isadvivrta",
    "vivrta",
    "samvrta",
]

Prana = Literal["alpaprana", "mahaprana", "none"]
MatraClass = Literal["hrasva", "dirgha", "pluta", "vyanjana", "ardhamatra"]
VarnaGroup = Literal[
    "svara_samanaksara",
    "svara_sandhyaksara",
    "sparsa_kavarga",
    "sparsa_cavarga",
    "sparsa_tavarga_retroflex",
    "sparsa_tavarga_dental",
    "sparsa_pavarga",
    "antastha",
    "usman",
    "ayogavaha",
]


@dataclass(frozen=True)
class VarnaSpec:
    iast: str
    devanagari: str
    ipa: str
    group: VarnaGroup
    sthana: Sthana
    secondary_sthana: Optional[Sthana]
    prayatna: Prayatna
    ghosa: bool
    prana: Prana
    matra_class: MatraClass
    matra_count: float


VARNA_INVENTORY: Dict[str, VarnaSpec] = {
    # --- Svara: Samānākṣara (Simple Vowels) ---
    "a":  VarnaSpec("a",  "अ", "ɐ",   "svara_samanaksara", "kanthya", None, "samvrta", True, "none", "hrasva", 1.0),
    "ā":  VarnaSpec("ā",  "आ", "ɑː",  "svara_samanaksara", "kanthya", None, "vivrta",  True, "none", "dirgha", 2.0),
    "a3": VarnaSpec("a3", "अ३", "ɑːː", "svara_samanaksara", "kanthya", None, "vivrta",  True, "none", "pluta",  3.0),
    "i":  VarnaSpec("i",  "इ", "i",   "svara_samanaksara", "talavya", None, "vivrta",  True, "none", "hrasva", 1.0),
    "ī":  VarnaSpec("ī",  "ई", "iː",  "svara_samanaksara", "talavya", None, "vivrta",  True, "none", "dirgha", 2.0),
    "u":  VarnaSpec("u",  "उ", "u",   "svara_samanaksara", "osthya",  None, "vivrta",  True, "none", "hrasva", 1.0),
    "ū":  VarnaSpec("ū",  "ऊ", "uː",  "svara_samanaksara", "osthya",  None, "vivrta",  True, "none", "dirgha", 2.0),
    "ṛ":  VarnaSpec("ṛ",  "ऋ", "r̩",   "svara_samanaksara", "murdhanya", None, "vivrta", True, "none", "hrasva", 1.0),
    "ṝ":  VarnaSpec("ṝ",  "ॠ", "r̩ː",  "svara_samanaksara", "murdhanya", None, "vivrta", True, "none", "dirgha", 2.0),
    "ḷ":  VarnaSpec("ḷ",  "ऌ", "l̩",   "svara_samanaksara", "dantya",  None, "vivrta",  True, "none", "hrasva", 1.0),

    # --- Svara: Sandhyakṣara (Diphthongs — always Dīrgha) ---
    "e":  VarnaSpec("e",  "ए", "eː",  "svara_sandhyaksara", "kanthatalavya", None, "vivrta", True, "none", "dirgha", 2.0),
    "ai": VarnaSpec("ai", "ऐ", "əi",  "svara_sandhyaksara", "kanthatalavya", None, "vivrta", True, "none", "dirgha", 2.0),
    "o":  VarnaSpec("o",  "ओ", "oː",  "svara_sandhyaksara", "kanthosthya",   None, "vivrta", True, "none", "dirgha", 2.0),
    "au": VarnaSpec("au", "औ", "əu",  "svara_sandhyaksara", "kanthosthya",   None, "vivrta", True, "none", "dirgha", 2.0),

    # --- Sparśa: Ka-varga (Velar / Kaṇṭhya) ---
    "k":  VarnaSpec("k",  "क्", "k",   "sparsa_kavarga", "kanthya", None,      "sprsta", False, "alpaprana", "vyanjana", 0.5),
    "kh": VarnaSpec("kh", "ख्", "kʰ",  "sparsa_kavarga", "kanthya", None,      "sprsta", False, "mahaprana", "vyanjana", 0.5),
    "g":  VarnaSpec("g",  "ग्", "ɡ",   "sparsa_kavarga", "kanthya", None,      "sprsta", True,  "alpaprana", "vyanjana", 0.5),
    "gh": VarnaSpec("gh", "घ्", "ɡʱ",  "sparsa_kavarga", "kanthya", None,      "sprsta", True,  "mahaprana", "vyanjana", 0.5),
    "ṅ":  VarnaSpec("ṅ",  "ङ्", "ŋ",   "sparsa_kavarga", "kanthya", "nasikya", "sprsta", True,  "alpaprana", "vyanjana", 0.5),

    # --- Sparśa: Ca-varga (Palatal / Tālavya) ---
    "c":  VarnaSpec("c",  "च्", "c",   "sparsa_cavarga", "talavya", None,      "sprsta", False, "alpaprana", "vyanjana", 0.5),
    "ch": VarnaSpec("ch", "छ्", "cʰ",  "sparsa_cavarga", "talavya", None,      "sprsta", False, "mahaprana", "vyanjana", 0.5),
    "j":  VarnaSpec("j",  "ज्", "ɟ",   "sparsa_cavarga", "talavya", None,      "sprsta", True,  "alpaprana", "vyanjana", 0.5),
    "jh": VarnaSpec("jh", "झ्", "ɟʱ",  "sparsa_cavarga", "talavya", None,      "sprsta", True,  "mahaprana", "vyanjana", 0.5),
    "ñ":  VarnaSpec("ñ",  "ञ्", "ɲ",   "sparsa_cavarga", "talavya", "nasikya", "sprsta", True,  "alpaprana", "vyanjana", 0.5),

    # --- Sparśa: Ṭa-varga (Retroflex / Mūrdhanya) ---
    "ṭ":  VarnaSpec("ṭ",  "ट्", "ʈ",   "sparsa_tavarga_retroflex", "murdhanya", None,      "sprsta", False, "alpaprana", "vyanjana", 0.5),
    "ṭh": VarnaSpec("ṭh", "ठ्", "ʈʰ",  "sparsa_tavarga_retroflex", "murdhanya", None,      "sprsta", False, "mahaprana", "vyanjana", 0.5),
    "ḍ":  VarnaSpec("ḍ",  "ड्", "ɖ",   "sparsa_tavarga_retroflex", "murdhanya", None,      "sprsta", True,  "alpaprana", "vyanjana", 0.5),
    "ḍh": VarnaSpec("ḍh", "ढ्", "ɖʱ",  "sparsa_tavarga_retroflex", "murdhanya", None,      "sprsta", True,  "mahaprana", "vyanjana", 0.5),
    "ṇ":  VarnaSpec("ṇ",  "ण्", "ɳ",   "sparsa_tavarga_retroflex", "murdhanya", "nasikya", "sprsta", True,  "alpaprana", "vyanjana", 0.5),

    # --- Sparśa: Ta-varga (Dental / Dantya) ---
    "t":  VarnaSpec("t",  "त्", "t̪",   "sparsa_tavarga_dental", "dantya", None,      "sprsta", False, "alpaprana", "vyanjana", 0.5),
    "th": VarnaSpec("th", "थ्", "t̪ʰ",  "sparsa_tavarga_dental", "dantya", None,      "sprsta", False, "mahaprana", "vyanjana", 0.5),
    "d":  VarnaSpec("d",  "द्", "d̪",   "sparsa_tavarga_dental", "dantya", None,      "sprsta", True,  "alpaprana", "vyanjana", 0.5),
    "dh": VarnaSpec("dh", "ध्", "d̪ʱ",  "sparsa_tavarga_dental", "dantya", None,      "sprsta", True,  "mahaprana", "vyanjana", 0.5),
    "n":  VarnaSpec("n",  "न्", "n̪",   "sparsa_tavarga_dental", "dantya", "nasikya", "sprsta", True,  "alpaprana", "vyanjana", 0.5),

    # --- Sparśa: Pa-varga (Labial / Oṣṭhya) ---
    "p":  VarnaSpec("p",  "प्", "p",   "sparsa_pavarga", "osthya", None,      "sprsta", False, "alpaprana", "vyanjana", 0.5),
    "ph": VarnaSpec("ph", "फ्", "pʰ",  "sparsa_pavarga", "osthya", None,      "sprsta", False, "mahaprana", "vyanjana", 0.5),
    "b":  VarnaSpec("b",  "ब्", "b",   "sparsa_pavarga", "osthya", None,      "sprsta", True,  "alpaprana", "vyanjana", 0.5),
    "bh": VarnaSpec("bh", "भ्", "bʱ",  "sparsa_pavarga", "osthya", None,      "sprsta", True,  "mahaprana", "vyanjana", 0.5),
    "m":  VarnaSpec("m",  "म्", "m",   "sparsa_pavarga", "osthya", "nasikya", "sprsta", True,  "alpaprana", "vyanjana", 0.5),

    # --- Antaḥstha (Semivowels / Approximants) ---
    "y":  VarnaSpec("y",  "य्", "j",   "antastha", "talavya",    None, "isatsprsta", True, "alpaprana", "vyanjana", 0.5),
    "r":  VarnaSpec("r",  "र्", "r",   "antastha", "murdhanya",  None, "isatsprsta", True, "alpaprana", "vyanjana", 0.5),
    "l":  VarnaSpec("l",  "ल्", "l",   "antastha", "dantya",     None, "isatsprsta", True, "alpaprana", "vyanjana", 0.5),
    "ḷ_vedic": VarnaSpec("ḷ_vedic", "ळ्", "ɭ", "antastha", "murdhanya", None, "isatsprsta", True, "alpaprana", "vyanjana", 0.5),
    "v":  VarnaSpec("v",  "व्", "ʋ",   "antastha", "dantosthya", None, "isatsprsta", True, "alpaprana", "vyanjana", 0.5),

    # --- Ūṣman (Sibilants & Aspirate) ---
    "ś":  VarnaSpec("ś",  "श्", "ɕ",   "usman", "talavya",   None, "isadvivrta", False, "mahaprana", "vyanjana", 0.5),
    "ṣ":  VarnaSpec("ṣ",  "ष्", "ʂ",   "usman", "murdhanya", None, "isadvivrta", False, "mahaprana", "vyanjana", 0.5),
    "s":  VarnaSpec("s",  "स्", "s",   "usman", "dantya",    None, "isadvivrta", False, "mahaprana", "vyanjana", 0.5),
    "h":  VarnaSpec("h",  "ह्", "ɦ",   "usman", "kanthya",   "urasya", "isadvivrta", True, "mahaprana", "vyanjana", 0.5),

    # --- Ayogavāha (Visarga, Anusvāra, Jihvāmūlīya, Upadhmānīya) ---
    "ḥ":  VarnaSpec("ḥ",  "ः",  "h",   "ayogavaha", "kanthya",   None,      "vivrta", False, "mahaprana", "ardhamatra", 0.5),
    "ṃ":  VarnaSpec("ṃ",  "ं",  "ŋ",   "ayogavaha", "nasikya",   None,      "sprsta", True,  "alpaprana", "ardhamatra", 0.5),
    "ḫ":  VarnaSpec("ḫ",  "ᳵ",  "x",   "ayogavaha", "kanthya",   None,      "isadvivrta", False, "mahaprana", "ardhamatra", 0.5),
    "ɸ":  VarnaSpec("ɸ",  "ᳶ",  "ɸ",   "ayogavaha", "osthya",    None,      "isadvivrta", False, "mahaprana", "ardhamatra", 0.5),
}


def lookup_varna(symbol: str) -> Optional[VarnaSpec]:
    """Lookup an articulatory VarnaSpec by IAST symbol."""
    return VARNA_INVENTORY.get((symbol or "").strip())


def is_svara(symbol: str) -> bool:
    spec = lookup_varna(symbol)
    return spec is not None and spec.group.startswith("svara_")
