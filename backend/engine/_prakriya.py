"""
P2 Deterministic Paninian Prakriya Derivation Engine Prototype.

Models a declarative rule registry, adhikara (governing scope) and anuvrtti
(inherited context) bindings, intermediate PrakriyaState snapshots, Tripadi
(8.2.1 purvatrasiddham) vs. Sapadasaptadhyayee adjudication, and reproducible
step-by-step traces for canonical forms such as *gacchati* and *ramah*.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Callable, Dict, List, Literal, Optional, Tuple

PrakriyaClassification = Literal[
    "DETERMINISTIC_DERIVATION",
    "AMBIGUOUS_DERIVATION",
    "UNRESOLVED",
]


@dataclass(frozen=True)
class SutraRule:
    sutra_id: str
    title: str
    domain: Literal["samjna", "paribhasa", "adhikara", "pratyaya", "vikarana", "anga", "sandhi", "tripadi"]
    adhikara: str
    is_tripadi: bool = False
    priority: int = 100
    authority: str = "Kasika_Vrtti"


@dataclass
class PrakriyaStep:
    step_index: int
    stage: str
    sutra_id: str
    rule_title: str
    adhikara: str
    before_segments: List[str]
    after_segments: List[str]
    surface_after: str
    anuvrtti_snapshot: Dict[str, str]
    notes: str = ""


@dataclass
class PrakriyaTrace:
    query_form: str
    prakruti: str
    category: Literal["tinanta", "subanta"]
    adhikaras_active: List[str]
    anuvrtti: Dict[str, str]
    segments: List[str]
    surface: str
    sutra_chain: List[str]
    steps: List[PrakriyaStep] = field(default_factory=list)
    branches: List[List[str]] = field(default_factory=list)
    result_classification: PrakriyaClassification = "UNRESOLVED"

    def to_dict(self) -> Dict[str, object]:
        return {
            "query_form": self.query_form,
            "prakruti": self.prakruti,
            "category": self.category,
            "adhikaras_active": list(self.adhikaras_active),
            "anuvrtti": dict(self.anuvrtti),
            "segments": list(self.segments),
            "surface": self.surface,
            "sutra_chain": list(self.sutra_chain),
            "steps": [asdict(s) for s in self.steps],
            "branches": [list(b) for b in self.branches],
            "result_classification": self.result_classification,
        }


RULE_REGISTRY: Dict[str, SutraRule] = {
    "1.3.2": SutraRule("1.3.2", "upadese 'janunasika it", "samjna", "pratyaya", is_tripadi=False, priority=10),
    "1.3.3": SutraRule("1.3.3", "hal antyam", "samjna", "pratyaya", is_tripadi=False, priority=11),
    "1.3.8": SutraRule("1.3.8", "lasakvataddhite", "samjna", "pratyaya", is_tripadi=False, priority=12),
    "1.3.9": SutraRule("1.3.9", "tasya lopah", "samjna", "pratyaya", is_tripadi=False, priority=13),
    "1.4.2": SutraRule("1.4.2", "vipratisedhe param karyam", "paribhasa", "sarvam", is_tripadi=False, priority=5),
    "1.4.14": SutraRule("1.4.14", "suptinantam padam", "samjna", "pada", is_tripadi=False, priority=90),
    "1.4.101": SutraRule("1.4.101", "tinah trini trini prathamamadhyamottamah", "samjna", "pratyaya", is_tripadi=False, priority=20),
    "2.3.46": SutraRule("2.3.46", "pratipadhikarthalingaparimanavacanamatram prathama", "adhikara", "sup", is_tripadi=False, priority=21),
    "3.1.68": SutraRule("3.1.68", "kartari sap", "vikarana", "dhatu", is_tripadi=False, priority=30),
    "3.2.123": SutraRule("3.2.123", "vartamane lat", "pratyaya", "dhatu", is_tripadi=False, priority=15),
    "3.4.78": SutraRule("3.4.78", "tiptasjhisipthasthamibvasmas...", "pratyaya", "dhatu", is_tripadi=False, priority=22),
    "2.3.50": SutraRule("2.3.50", "sasthi sese", "adhikara", "sup", is_tripadi=False, priority=19),
    "4.1.2": SutraRule("4.1.2", "svaujasamaut...", "pratyaya", "sup", is_tripadi=False, priority=20),
    "7.3.77": SutraRule("7.3.77", "isugamiyamamasau chandi / gamu-gaccha adesa", "anga", "angasya", is_tripadi=False, priority=40),
    "7.3.84": SutraRule("7.3.84", "sarvadhatukardhadhatukayoh", "anga", "angasya", is_tripadi=False, priority=42),
    "7.4.61": SutraRule("7.4.61", "saurih / stha-tistha abhyasa-adesa", "anga", "angasya", is_tripadi=False, priority=44),
    "8.2.1": SutraRule("8.2.1", "purvatrasiddham", "adhikara", "tripadi", is_tripadi=True, priority=1),
    "8.2.66": SutraRule("8.2.66", "sasajuso ruh", "tripadi", "tripadi", is_tripadi=True, priority=50),
    "8.3.15": SutraRule("8.3.15", "kharavasanayor visarjaniyah", "tripadi", "tripadi", is_tripadi=True, priority=60),
}


def _record_step(
    trace: PrakriyaTrace,
    stage: str,
    sutra_ids: List[str],
    rule_title: str,
    adhikara: str,
    next_segments: List[str],
    next_surface: str,
    notes: str = "",
) -> None:
    for sid in sutra_ids:
        if sid not in RULE_REGISTRY:
            raise KeyError(f"Unregistered sutra_id: {sid}")
        if sid not in trace.sutra_chain:
            trace.sutra_chain.append(sid)

    step = PrakriyaStep(
        step_index=len(trace.steps),
        stage=stage,
        sutra_id=" + ".join(sutra_ids),
        rule_title=rule_title,
        adhikara=adhikara,
        before_segments=list(trace.segments),
        after_segments=list(next_segments),
        surface_after=next_surface,
        anuvrtti_snapshot=dict(trace.anuvrtti),
        notes=notes,
    )
    trace.segments = list(next_segments)
    trace.surface = next_surface
    trace.steps.append(step)


def derive_gacchati(
    dhatu: str = "gam",
    lakara: str = "laṭ",
    purusha: str = "prathama_purusha",
    vacana: str = "ekavacana",
    pada: str = "parasmaipada",
) -> PrakriyaTrace:
    """Deterministic step-by-step prakriya trace for *gacchati*."""
    if dhatu != "gam":
        return PrakriyaTrace(
            query_form="gacchati",
            prakruti=dhatu,
            category="tinanta",
            adhikaras_active=[],
            anuvrtti={},
            segments=[dhatu],
            surface=dhatu,
            sutra_chain=[],
            result_classification="UNRESOLVED",
        )

    anuvrtti: Dict[str, str] = {
        "dhatu": dhatu,
        "gana": "1 (bhvadi)",
        "lakara": lakara,
        "purusha": purusha,
        "vacana": vacana,
        "pada": pada,
    }
    trace = PrakriyaTrace(
        query_form="gacchati",
        prakruti=dhatu,
        category="tinanta",
        adhikaras_active=["dhatu", "pratyaya", "angasya", "pada"],
        anuvrtti=anuvrtti,
        segments=[dhatu],
        surface=dhatu,
        sutra_chain=[],
        result_classification="UNRESOLVED",
    )

    _record_step(
        trace=trace,
        stage="pratyaya_yojana",
        sutra_ids=["3.2.123", "3.4.78", "1.4.101", "1.3.3", "1.3.9"],
        rule_title="lat -> tip (3sg parasmaipada) -> ti after halantyam/tasya lopah",
        adhikara="pratyaya",
        next_segments=[dhatu, "ti"],
        next_surface=f"{dhatu}+ti",
        notes="Final p of tip is it (1.3.3) and elided (1.3.9).",
    )

    trace.anuvrtti["vikarana"] = "sap (a)"
    _record_step(
        trace=trace,
        stage="vikarana_anga",
        sutra_ids=["3.1.68", "1.3.8", "1.3.3", "1.3.9"],
        rule_title="kartari sap -> a between dhatu and tin ending",
        adhikara="dhatu",
        next_segments=[dhatu, "a", "ti"],
        next_surface=f"{dhatu}+a+ti",
        notes="s and p of sap are it-markers elided by 1.3.9, leaving a.",
    )

    trace.anuvrtti["anga_stem"] = "gaccha"
    _record_step(
        trace=trace,
        stage="anga",
        sutra_ids=["7.3.77"],
        rule_title="gamu -> gaccha stem replacement before sap/sarvadhatuka",
        adhikara="angasya",
        next_segments=["gaccha", "ti"],
        next_surface="gaccha+ti",
        notes="gaccha combines with pratyaya ti.",
    )

    _record_step(
        trace=trace,
        stage="final",
        sutra_ids=["1.4.14"],
        rule_title="suptinantam padam closure",
        adhikara="pada",
        next_segments=["gacchati"],
        next_surface="gacchati",
        notes="Complete tinanta pada form.",
    )

    trace.result_classification = "DETERMINISTIC_DERIVATION"
    return trace


def derive_ramah(
    pratipadika: str = "rāma",
    vibhakti: str = "prathama",
    vacana: str = "ekavacana",
    sandhi_context: Literal["avasana", "samhita_visarga"] = "avasana",
) -> PrakriyaTrace:
    """Deterministic step-by-step prakriya trace for *ramah*."""
    if pratipadika not in ("rāma", "rama"):
        return PrakriyaTrace(
            query_form="rāmaḥ",
            prakruti=pratipadika,
            category="subanta",
            adhikaras_active=[],
            anuvrtti={},
            segments=[pratipadika],
            surface=pratipadika,
            sutra_chain=[],
            result_classification="UNRESOLVED",
        )

    base = "rāma"
    anuvrtti: Dict[str, str] = {
        "pratipadika": base,
        "linga": "pullinga",
        "vibhakti": vibhakti,
        "vacana": vacana,
        "sandhi_context": sandhi_context,
    }
    trace = PrakriyaTrace(
        query_form="rāmaḥ",
        prakruti=base,
        category="subanta",
        adhikaras_active=["sup", "pratyaya", "pada", "tripadi"],
        anuvrtti=anuvrtti,
        segments=[base],
        surface=base,
        sutra_chain=[],
        result_classification="UNRESOLVED",
    )

    _record_step(
        trace=trace,
        stage="pratyaya_yojana",
        sutra_ids=["4.1.2", "2.3.46"],
        rule_title="attach sup suffix su for prathama-ekavacana",
        adhikara="sup",
        next_segments=[base, "su"],
        next_surface=f"{base}+su",
        notes="Nominative singular sup ending su.",
    )

    _record_step(
        trace=trace,
        stage="sapadasaptadhyayee",
        sutra_ids=["1.3.2", "1.3.9"],
        rule_title="elide anunnasika it vowel u of su -> s",
        adhikara="pratyaya",
        next_segments=[base, "s"],
        next_surface=f"{base}+s",
        notes="u is an it-marker under 1.3.2 and elided under 1.3.9.",
    )

    _record_step(
        trace=trace,
        stage="tripadi",
        sutra_ids=["8.2.1", "8.2.66", "8.3.15"],
        rule_title="tripadi purvatrasiddham: s -> ru (8.2.66) -> visarjaniya h (8.3.15)",
        adhikara="tripadi",
        next_segments=[base, "ḥ"],
        next_surface=f"{base}ḥ",
        notes="Evaluated in Tripadi domain under avasana/final visarga rule 8.3.15.",
    )

    _record_step(
        trace=trace,
        stage="final",
        sutra_ids=["1.4.14"],
        rule_title="suptinantam padam closure",
        adhikara="pada",
        next_segments=["rāmaḥ"],
        next_surface="rāmaḥ",
        notes="Complete subanta pada form.",
    )

    trace.result_classification = "DETERMINISTIC_DERIVATION"
    return trace


def derive_bhavati(
    dhatu: str = "bhū",
    lakara: str = "laṭ",
    purusha: str = "prathama_purusha",
    vacana: str = "ekavacana",
    pada: str = "parasmaipada",
) -> PrakriyaTrace:
    """Deterministic step-by-step prakriya trace for *bhavati*."""
    if dhatu not in ("bhū", "bhu"):
        return PrakriyaTrace(
            query_form="bhavati",
            prakruti=dhatu,
            category="tinanta",
            adhikaras_active=[],
            anuvrtti={},
            segments=[dhatu],
            surface=dhatu,
            sutra_chain=[],
            result_classification="UNRESOLVED",
        )

    canonical_dhatu = "bhū"
    anuvrtti: Dict[str, str] = {
        "dhatu": canonical_dhatu,
        "gana": "1 (bhvadi)",
        "lakara": lakara,
        "purusha": purusha,
        "vacana": vacana,
        "pada": pada,
    }
    trace = PrakriyaTrace(
        query_form="bhavati",
        prakruti=canonical_dhatu,
        category="tinanta",
        adhikaras_active=["dhatu", "pratyaya", "angasya", "pada"],
        anuvrtti=anuvrtti,
        segments=[canonical_dhatu],
        surface=canonical_dhatu,
        sutra_chain=[],
        result_classification="UNRESOLVED",
    )

    _record_step(
        trace=trace,
        stage="pratyaya_yojana",
        sutra_ids=["3.2.123", "3.4.78", "1.4.101", "1.3.3", "1.3.9"],
        rule_title="lat -> tip (3sg parasmaipada) -> ti after halantyam/tasya lopah",
        adhikara="pratyaya",
        next_segments=[canonical_dhatu, "ti"],
        next_surface=f"{canonical_dhatu}+ti",
        notes="Final p of tip is it (1.3.3) and elided (1.3.9).",
    )

    trace.anuvrtti["vikarana"] = "sap (a)"
    _record_step(
        trace=trace,
        stage="vikarana_anga",
        sutra_ids=["3.1.68", "1.3.8", "1.3.9"],
        rule_title="kartari sap -> a between dhatu and tin ending",
        adhikara="dhatu",
        next_segments=[canonical_dhatu, "a", "ti"],
        next_surface=f"{canonical_dhatu}+a+ti",
        notes="s and p of sap are it-markers elided by 1.3.9, leaving a.",
    )

    trace.anuvrtti["anga_stem"] = "bhava"
    _record_step(
        trace=trace,
        stage="anga",
        sutra_ids=["7.3.84"],
        rule_title="sarvadhatukardhadhatukayoh: guna on bhu -> bho -> bhava before sap",
        adhikara="angasya",
        next_segments=["bhava", "ti"],
        next_surface="bhava+ti",
        notes="Guna vowel o before a yields avadesa bhava with sap a.",
    )

    _record_step(
        trace=trace,
        stage="final",
        sutra_ids=["1.4.14"],
        rule_title="suptinantam padam closure",
        adhikara="pada",
        next_segments=["bhavati"],
        next_surface="bhavati",
        notes="Complete tinanta pada form.",
    )

    trace.result_classification = "DETERMINISTIC_DERIVATION"
    return trace


def derive_tisthati(
    dhatu: str = "sthā",
    lakara: str = "laṭ",
    purusha: str = "prathama_purusha",
    vacana: str = "ekavacana",
    pada: str = "parasmaipada",
) -> PrakriyaTrace:
    """Deterministic step-by-step prakriya trace for *tisthati*."""
    if dhatu not in ("sthā", "stha"):
        return PrakriyaTrace(
            query_form="tiṣṭhati",
            prakruti=dhatu,
            category="tinanta",
            adhikaras_active=[],
            anuvrtti={},
            segments=[dhatu],
            surface=dhatu,
            sutra_chain=[],
            result_classification="UNRESOLVED",
        )

    canonical_dhatu = "sthā"
    anuvrtti: Dict[str, str] = {
        "dhatu": canonical_dhatu,
        "gana": "1 (bhvadi)",
        "lakara": lakara,
        "purusha": purusha,
        "vacana": vacana,
        "pada": pada,
    }
    trace = PrakriyaTrace(
        query_form="tiṣṭhati",
        prakruti=canonical_dhatu,
        category="tinanta",
        adhikaras_active=["dhatu", "pratyaya", "angasya", "pada"],
        anuvrtti=anuvrtti,
        segments=[canonical_dhatu],
        surface=canonical_dhatu,
        sutra_chain=[],
        result_classification="UNRESOLVED",
    )

    _record_step(
        trace=trace,
        stage="pratyaya_yojana",
        sutra_ids=["3.2.123", "3.4.78", "1.4.101", "1.3.3", "1.3.9"],
        rule_title="lat -> tip (3sg parasmaipada) -> ti after halantyam/tasya lopah",
        adhikara="pratyaya",
        next_segments=[canonical_dhatu, "ti"],
        next_surface=f"{canonical_dhatu}+ti",
        notes="Final p of tip is it (1.3.3) and elided (1.3.9).",
    )

    trace.anuvrtti["vikarana"] = "sap (a)"
    _record_step(
        trace=trace,
        stage="vikarana_anga",
        sutra_ids=["3.1.68", "1.3.8", "1.3.9"],
        rule_title="kartari sap -> a between dhatu and tin ending",
        adhikara="dhatu",
        next_segments=[canonical_dhatu, "a", "ti"],
        next_surface=f"{canonical_dhatu}+a+ti",
        notes="s and p of sap are it-markers elided by 1.3.9, leaving a.",
    )

    trace.anuvrtti["anga_stem"] = "tiṣṭha"
    _record_step(
        trace=trace,
        stage="anga",
        sutra_ids=["7.4.61"],
        rule_title="stha -> tistha stem replacement before sarvadhatuka/sap",
        adhikara="angasya",
        next_segments=["tiṣṭha", "ti"],
        next_surface="tiṣṭha+ti",
        notes="Stem replacement yields tistha before tin ending ti.",
    )

    _record_step(
        trace=trace,
        stage="final",
        sutra_ids=["1.4.14"],
        rule_title="suptinantam padam closure",
        adhikara="pada",
        next_segments=["tiṣṭhati"],
        next_surface="tiṣṭhati",
        notes="Complete tinanta pada form.",
    )

    trace.result_classification = "DETERMINISTIC_DERIVATION"
    return trace


def derive_ramasya(
    pratipadika: str = "rāma",
    vibhakti: str = "shasthi",
    vacana: str = "ekavacana",
) -> PrakriyaTrace:
    """Deterministic step-by-step prakriya trace for *ramasya*."""
    if pratipadika not in ("rāma", "rama"):
        return PrakriyaTrace(
            query_form="rāmasya",
            prakruti=pratipadika,
            category="subanta",
            adhikaras_active=[],
            anuvrtti={},
            segments=[pratipadika],
            surface=pratipadika,
            sutra_chain=[],
            result_classification="UNRESOLVED",
        )

    base = "rāma"
    anuvrtti: Dict[str, str] = {
        "pratipadika": base,
        "linga": "pullinga",
        "vibhakti": vibhakti,
        "vacana": vacana,
    }
    trace = PrakriyaTrace(
        query_form="rāmasya",
        prakruti=base,
        category="subanta",
        adhikaras_active=["sup", "pratyaya", "pada"],
        anuvrtti=anuvrtti,
        segments=[base],
        surface=base,
        sutra_chain=[],
        result_classification="UNRESOLVED",
    )

    _record_step(
        trace=trace,
        stage="pratyaya_yojana",
        sutra_ids=["4.1.2", "2.3.50"],
        rule_title="attach sup suffix nas for shasthi-ekavacana",
        adhikara="sup",
        next_segments=[base, "ṅas"],
        next_surface=f"{base}+ṅas",
        notes="Genitive singular sup ending nas.",
    )

    _record_step(
        trace=trace,
        stage="sapadasaptadhyayee",
        sutra_ids=["1.3.2", "1.3.3", "1.3.9"],
        rule_title="elide it markers n and a of nas -> sya (after a-stem)",
        adhikara="pratyaya",
        next_segments=[base, "sya"],
        next_surface=f"{base}+sya",
        notes="It markers elided under 1.3.2/1.3.3/1.3.9; final pada form rāmasya.",
    )

    _record_step(
        trace=trace,
        stage="final",
        sutra_ids=["1.4.14"],
        rule_title="suptinantam padam closure",
        adhikara="pada",
        next_segments=["rāmasya"],
        next_surface="rāmasya",
        notes="Complete subanta pada form.",
    )

    trace.result_classification = "DETERMINISTIC_DERIVATION"
    return trace


DERIVATION_TRACES: Dict[str, Callable[[], PrakriyaTrace]] = {
    "gacchati": derive_gacchati,
    "bhavati": derive_bhavati,
    "tiṣṭhati": derive_tisthati,
    "rāmaḥ": derive_ramah,
    "ramah": derive_ramah,
    "rāmasya": derive_ramasya,
    "ramasya": derive_ramasya,
}


TRIPADI_START: Tuple[int, int, int] = (8, 2, 1)
TRIPADI_END: Tuple[int, int, int] = (8, 4, 68)


def parse_sutra_coord(sutra_id: str) -> Tuple[int, int, int]:
    """Parse canonical 'adhyaya.pada.sutra' identifier into an integer tuple."""
    parts = sutra_id.strip().split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"Invalid sutra_id format: {sutra_id!r}")
    return (int(parts[0]), int(parts[1]), int(parts[2]))


def is_tripadi_coord(coord: Tuple[int, int, int]) -> bool:
    """Return True if coord falls within the Ashtadhyayi Tripadi (8.2.1 - 8.4.68)."""
    return TRIPADI_START <= coord <= TRIPADI_END


def validate_prakriya_trace(trace: PrakriyaTrace) -> List[str]:
    """
    Validate Tripadi (8.2.1 purvatrasiddham) ordering and adhikara scope
    across a PrakriyaTrace. Returns a list of deterministic violation codes
    (empty list means valid).
    """
    violations: List[str] = []
    seen_tripadi = False
    last_tripadi_coord: Optional[Tuple[int, int, int]] = None
    active_adhikaras = set(trace.adhikaras_active)

    for step in trace.steps:
        step_sids = [s.strip() for s in step.sutra_id.split("+") if s.strip()]
        if not step_sids:
            violations.append(f"MISSING_SUTRA_AT_STEP_{step.step_index}")
            continue

        if active_adhikaras and step.adhikara not in active_adhikaras:
            violations.append(
                f"INACTIVE_ADHIKARA:{step.adhikara}@step_{step.step_index}"
            )

        rules: List[Tuple[str, SutraRule, Tuple[int, int, int]]] = []
        for sid in step_sids:
            rule = RULE_REGISTRY.get(sid)
            if rule is None:
                violations.append(f"UNREGISTERED_SUTRA:{sid}@step_{step.step_index}")
                continue
            coord = parse_sutra_coord(sid)
            rules.append((sid, rule, coord))

        if len(rules) == 1:
            sid, rule, _ = rules[0]
            if (
                rule.adhikara != "sarvam"
                and step.adhikara != rule.adhikara
                and not (rule.is_tripadi and step.adhikara == "tripadi")
                and not (rule.adhikara == "pada" and step.adhikara == "pada")
            ):
                violations.append(
                    f"ADHIKARA_MISMATCH:{sid}:step={step.adhikara}:rule={rule.adhikara}@step_{step.step_index}"
                )

        is_terminal_pada_closure = (
            step.stage == "final"
            and step.adhikara == "pada"
            and [sid for sid, _, _ in rules] == ["1.4.14"]
        )

        for sid, rule, coord in rules:
            in_tripadi = is_tripadi_coord(coord) or rule.is_tripadi
            if in_tripadi:
                seen_tripadi = True
                if last_tripadi_coord is not None and coord < last_tripadi_coord:
                    violations.append(
                        f"TRIPADI_ORDER_VIOLATION:{sid}({coord})<prev({last_tripadi_coord})@step_{step.step_index}"
                    )
                last_tripadi_coord = coord
            else:
                if seen_tripadi and not is_terminal_pada_closure:
                    violations.append(
                        f"PURVATRASIDDHAM_VIOLATION:sapadasaptadhyayee:{sid}({coord})_after_tripadi({last_tripadi_coord})@step_{step.step_index}"
                    )

    return violations

def derive_form(form: str) -> Optional[PrakriyaTrace]:
    key = form.strip()
    fn = DERIVATION_TRACES.get(key)
    if fn is None:
        return None
    return fn()
