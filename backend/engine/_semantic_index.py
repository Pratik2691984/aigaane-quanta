"""
Aigaane v0.3.0 — Sanskrit Semantic Index

Extends the base lexicon with:
  - dhātu (verbal root)
  - gaṇa (verbal class)
  - nirukta (etymological gloss)
  - semantic gloss
  - synonyms, antonyms, related words
  - canonical citations

References:
  - Yāska's Nirukta (6th c. BCE)
  - Pāṇini's Dhātupāṭha (1.3.1–1.3.10)
  - Amarakośa (canonical synonym dictionary)
  - Apte's Practical Sanskrit Dictionary
"""

from typing import Dict, Any, Optional

# ==============================================================================
# SEMANTIC INDEX — 50 core Sanskrit terms
# ==============================================================================
# Each entry:
#   dhatu:       verbal root (IAST)
#   gana:        gana name (bhvādi, adādi, etc.)
#   gana_number: 1-10
#   nirukta:     etymological gloss (root + suffix)
#   gloss:       semantic meaning in English
#   synonyms:    Sanskrit synonyms (from Amarakośa)
#   antonyms:    Sanskrit antonyms
#   related:     Related nouns/verb stems
#   citations:   Canonical verse references
# ==============================================================================

SEMANTIC_INDEX: Dict[str, Dict[str, Any]] = {

    # =========================================================================
    # METAPHYSICAL CORE (Gītā + Upaniṣads)
    # =========================================================================
    "dharma": {
        "dhatu": "dhṛ",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "dhṛ + man (dhāraṇāt dharmaḥ)",
        "gloss": "that which sustains; duty; law; righteousness; cosmic order",
        "synonyms": ["dharmya", "sadācāra", "puṇya", "śreyas", "nyāya"],
        "antonyms": ["adharma", "pāpa", "anṛta"],
        "related": ["dhā", "dhi", "dhṛti", "dharmin", "dharmatā"],
        "citations": ["Gītā 4.7", "Gītā 1.1", "Kaṭha 1.20", "Chāndogya 1.167"],
    },
    "karma": {
        "dhatu": "kṛ",
        "gana": "tanādi",
        "gana_number": 8,
        "nirukta": "kṛ + man (kriyate iti karma)",
        "gloss": "action; deed; ritual; result of action",
        "synonyms": ["kriyā", "ceṣṭā", "vyāpāra", "phala", "kārya"],
        "antonyms": ["akarma", "niṣkriya", "akriyā"],
        "related": ["kṛ", "kartṛ", "kriyā", "kartavya", "kāraka"],
        "citations": ["Gītā 4.7", "Kaṭha 2.13", "Gītā 1.43"],
    },
    "ātman": {
        "dhatu": "ad",
        "gana": "adādi",
        "gana_number": 2,
        "nirukta": "ad + man (attīti ātmā)",
        "gloss": "self; soul; the unchanging witness-consciousness",
        "synonyms": ["jīva", "puruṣa", "cetana", "sva", "ahan"],
        "antonyms": ["anātman", "jaḍa"],
        "related": ["ad", "ātmīya", "ātmatva", "paramātman"],
        "citations": ["Kaṭha 2.13", "Chāndogya 6.8.7", "Māṇḍūkya 2"],
    },
    "brahman": {
        "dhatu": "bṛh",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "bṛh + man (bṛṃhaṇāt brahma)",
        "gloss": "the absolute; ultimate reality; infinite consciousness",
        "synonyms": ["paramātman", "satyam", "cit", "ānanda", "tattva"],
        "antonyms": ["māyā", "avidyā", "anṛta"],
        "related": ["bṛh", "brāhmaṇa", "brahmavidyā", "brahmacarya"],
        "citations": ["Chāndogya 3.14", "Bṛhadāraṇyaka 1.4.10", "Kena 1.1"],
    },
    "yoga": {
        "dhatu": "yuj",
        "gana": "rudhādi",
        "gana_number": 7,
        "nirukta": "yuj + ghañ (yujyate anena iti yogaḥ)",
        "gloss": "union; discipline; spiritual practice; connection",
        "synonyms": ["sanyoga", "sādhana", "dhyāna", "samādhi", "abhyāsa"],
        "antonyms": ["viyoga", "bheda"],
        "related": ["yuj", "yogin", "yogī", "yogya", "yukti"],
        "citations": ["Gītā 2.50", "Gītā 6.23", "Patañjali 1.1"],
    },
    "mokṣa": {
        "dhatu": "muc",
        "gana": "tudādi",
        "gana_number": 6,
        "nirukta": "muc + ghañ (mokṣaṇaṃ mokṣaḥ)",
        "gloss": "liberation; release; final emancipation",
        "synonyms": ["mukti", "kaivalya", "nirvāṇa", "vimukti", "apavarga"],
        "antonyms": ["bandha", "saṃsāra", "pāśa"],
        "related": ["muc", "moktṛ", "mukta", "mokṣya", "vimokṣa"],
        "citations": ["Gītā 5.24", "Gītā 6.15", "Kaṭha 2.3.14"],
    },
    "saṃsāra": {
        "dhatu": "sṛ",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "saṃ + sṛ + ghañ (saṃsarati iti saṃsāraḥ)",
        "gloss": "cycle of rebirth; worldly existence; wandering",
        "synonyms": ["punarjanma", "jagat", "bhava", "saṃcāra"],
        "antonyms": ["mokṣa", "nirvāṇa", "kaivalya"],
        "related": ["sṛ", "saṃsārin", "saṃsārika"],
        "citations": ["Gītā 8.15", "Gītā 13.8", "Kaṭha 1.6"],
    },
    "jñāna": {
        "dhatu": "jñā",
        "gana": "kryādi",
        "gana_number": 9,
        "nirukta": "jñā + lyuṭ (jñāyate anena iti jñānam)",
        "gloss": "knowledge; wisdom; direct insight; higher knowing",
        "synonyms": ["vidyā", "bodha", "vijñāna", "darśana", "prajñā"],
        "antonyms": ["ajñāna", "avidyā", "moha"],
        "related": ["jñā", "jñātṛ", "jñāna", "jñeya", "jñāna"],
        "citations": ["Gītā 4.38", "Gītā 13.8", "Muṇḍaka 1.1.9"],
    },
    "bhakti": {
        "dhatu": "bhaj",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "bhaj + ktin (bhajyate anayā iti bhaktiḥ)",
        "gloss": "devotion; loving attachment; surrender",
        "synonyms": ["śraddhā", "prema", "anurāga", "viśvāsa", "prapatti"],
        "antonyms": ["virakti", "dveṣa"],
        "related": ["bhaj", "bhakta", "bhajana", "bhāva"],
        "citations": ["Gītā 12.1", "Gītā 9.26", "Gītā 18.55"],
    },
    "satya": {
        "dhatu": "as",
        "gana": "adādi",
        "gana_number": 2,
        "nirukta": "sat + ya (sataḥ bhāvaḥ satyam)",
        "gloss": "truth; reality; that which is; being",
        "synonyms": ["ṛta", "tathya", "sadbhāva", "yathārthatā"],
        "antonyms": ["anṛta", "mithyā", "asatya"],
        "related": ["as", "sat", "sattā", "satyatā"],
        "citations": ["Chāndogya 6.8.7", "Kaṭha 2.13", "Gītā 17.15"],
    },
    "tapas": {
        "dhatu": "tap",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "tap + asun (tapati iti tapaḥ)",
        "gloss": "austerity; heat; ascetic discipline; spiritual effort",
        "synonyms": ["kṛcchra", "vrata", "sādhana", "niyama", "upavāsa"],
        "antonyms": ["sukha", "bhoga", "viṣaya"],
        "related": ["tap", "tapasvin", "tāpa", "tāpasa"],
        "citations": ["Gītā 17.14", "Praśna 4.1", "Chāndogya 4.13"],
    },
    "śraddhā": {
        "dhatu": "śrat + dhā",
        "gana": "tanādi",
        "gana_number": 8,
        "nirukta": "śrat (satyam) + dhā (dhāyate) → śraddhā",
        "gloss": "faith; trust; confidence; heart-felt conviction",
        "synonyms": ["viśvāsa", "bhakti", "āsthā", "pratyaya"],
        "antonyms": ["aśraddhā", "saṃśaya", "vimatitva"],
        "related": ["dhā", "śraddadhāna", "śraddhālu"],
        "citations": ["Gītā 4.39", "Gītā 17.3", "Kaṭha 1.12"],
    },
    "yajña": {
        "dhatu": "yaj",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "yaj + ghañ (ijyate anena iti yajñaḥ)",
        "gloss": "sacrifice; ritual offering; cosmic exchange",
        "synonyms": ["homa", "iṣṭi", "kratu", "sattra", "yāga"],
        "antonyms": [],
        "related": ["yaj", "yajamāna", "yajña", "yājñika"],
        "citations": ["Gītā 3.10", "Gītā 4.25", "Chāndogya 1.167"],
    },
    "puruṣa": {
        "dhatu": "pṝ",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "puri śete iti puruṣaḥ (or pūrṇatvāt)",
        "gloss": "person; cosmic being; spirit; the supreme self",
        "synonyms": ["pumān", "nara", "jīva", "ātman", "prajāpati"],
        "antonyms": ["prakṛti", "strī"],
        "related": ["pṝ", "pauruṣa", "puruṣatva", "puruṣārtha"],
        "citations": ["Ṛgveda 10.90.1", "Gītā 13.20", "Śvetāśvatara 3.10"],
    },
    "prakṛti": {
        "dhatu": "kṛ",
        "gana": "tanādi",
        "gana_number": 8,
        "nirukta": "pra + kṛ + ktin (prakṛṣṭā kṛtiḥ)",
        "gloss": "nature; primordial matter; the material cause",
        "synonyms": ["mūlaprakṛti", "jaḍa", "avyakta", "māyā"],
        "antonyms": ["puruṣa", "puruṣa-tattva"],
        "related": ["kṛ", "prākṛta", "prakṛti-stha", "vikṛti"],
        "citations": ["Gītā 13.20", "Sāṃkhya 3", "Śvetāśvatara 4.10"],
    },
    "māyā": {
        "dhatu": "mā",
        "gana": "juhotyādi",
        "gana_number": 3,
        "nirukta": "mā + ya (māyayā mīyate iti māyā)",
        "gloss": "illusion; creative power; the veil of phenomenal appearance",
        "synonyms": ["avidyā", "ajñāna", "indrajāla", "vikalpa"],
        "antonyms": ["vidyā", "brahman", "tattva"],
        "related": ["mā", "māyin", "māyika", "mahāmāyā"],
        "citations": ["Gītā 7.14", "Gītā 4.6", "Śvetāśvatara 4.10"],
    },
    "avidyā": {
        "dhatu": "vid",
        "gana": "tudādi",
        "gana_number": 6,
        "nirukta": "a + vid + ktin (avidyamānā vidyā)",
        "gloss": "ignorance; nescience; mistaking the unreal for the real",
        "synonyms": ["ajñāna", "māyā", "moha", "viparyaya"],
        "antonyms": ["vidyā", "jñāna", "jñāna"],
        "related": ["vid", "avidyā", "vidyā", "vidvas"],
        "citations": ["Kaṭha 2.5", "Chāndogya 6.1.3", "Gītā 5.16"],
    },
    "vidyā": {
        "dhatu": "vid",
        "gana": "tudādi",
        "gana_number": 6,
        "nirukta": "vid + ya (vidyate anayā iti vidyā)",
        "gloss": "knowledge; learning; science; sacred wisdom",
        "synonyms": ["jñāna", "prajñā", "darśana", "vijñāna"],
        "antonyms": ["avidyā", "ajñāna"],
        "related": ["vid", "vidyā", "viduṣ", "veda"],
        "citations": ["Muṇḍaka 1.1.4", "Chāndogya 7.1", "Kaṭha 2.24"],
    },
    "ananda": {
        "dhatu": "nand",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "ā + nand + ghañ (ānandaṃ nirvṛtiḥ)",
        "gloss": "bliss; joy; the natural ecstasy of the self",
        "synonyms": ["sukha", "harṣa", "prīti", "tuṣṭi", "santoṣa"],
        "antonyms": ["duḥkha", "śoka", "kleśa"],
        "related": ["nand", "ānandin", "ānandatva", "sacchidānanda"],
        "citations": ["Bṛhadāraṇyaka 4.3.32", "Taittirīya 2.5", "Gītā 6.21"],
    },
    "sukha": {
        "dhatu": "sukhin",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "su + kha (sukhena tiṣṭhati)",
        "gloss": "pleasure; ease; comfort; hedonic satisfaction",
        "synonyms": ["ānanda", "harṣa", "prīti", "tuṣṭi"],
        "antonyms": ["duḥkha", "kleśa", "kaṣṭa"],
        "related": ["sukhin", "saukha", "sukhatva"],
        "citations": ["Gītā 5.21", "Gītā 6.21", "Kaṭha 2.1.1"],
    },
    "duḥkha": {
        "dhatu": "duṣ + kha",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "duṣ (durgati) + kha (khaṇḍana)",
        "gloss": "suffering; pain; dissatisfaction; the first noble truth",
        "synonyms": ["kleśa", "pīḍā", "śoka", "vedanā", "tāpa"],
        "antonyms": ["sukha", "ānanda", "nirvāṇa"],
        "related": ["duṣ", "duḥkha", "duḥkhin", "duḥkhatva"],
        "citations": ["Gītā 6.23", "Gītā 18.36", "Kaṭha 2.2.2"],
    },
    "kleśa": {
        "dhatu": "kliś",
        "gana": "tudādi",
        "gana_number": 6,
        "nirukta": "kliś + ghañ (kliśyate anena iti kleśaḥ)",
        "gloss": "affliction; mental defilement; suffering (Patañjali: 5 kleśas)",
        "synonyms": ["duḥkha", "pīḍā", "bandhana", "saṃtāpa"],
        "antonyms": ["sukha", "śānti"],
        "related": ["kliś", "kliṣṭa", "kleśa", "saṃkleśa"],
        "citations": ["Gītā 6.23", "Patañjali 2.3", "Gītā 18.36"],
    },
    "moha": {
        "dhatu": "muh",
        "gana": "rudhādi",
        "gana_number": 7,
        "nirukta": "muh + ghañ (muhyate anena iti mohaḥ)",
        "gloss": "delusion; bewilderment; confusion; one of the 5 kleśas",
        "synonyms": ["avidyā", "māyā", "viparyaya", "bhrānti"],
        "antonyms": ["jñāna", "prajñā", "vidyā"],
        "related": ["muh", "mūḍha", "mohana", "vimoha"],
        "citations": ["Gītā 4.13", "Gītā 18.30", "Kaṭha 2.13"],
    },
    "rāga": {
        "dhatu": "rañj",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "rañj + ghañ (rajyate anena iti rāgaḥ)",
        "gloss": "attachment; passion; attraction; one of the 3 root defilements",
        "synonyms": ["anurāga", "prema", "āsakti", "tṛṣṇā"],
        "antonyms": ["dveṣa", "virakti", "vairāgya"],
        "related": ["rañj", "rakta", "rāgin", "rāgatva"],
        "citations": ["Gītā 2.64", "Gītā 3.34", "Gītā 14.7"],
    },
    "dveṣa": {
        "dhatu": "dviṣ",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "dviṣ + ghañ (dveṣṭi iti dveṣaḥ)",
        "gloss": "aversion; hatred; repulsion; one of the 3 root defilements",
        "synonyms": ["vaira", "droha", "pratigha", "vairāgya"],
        "antonyms": ["rāga", "prema", "anurāga"],
        "related": ["dviṣ", "dviṣṭa", "dveṣin", "dveṣatva"],
        "citations": ["Gītā 3.34", "Gītā 7.27", "Gītā 14.7"],
    },

    # =========================================================================
    # EPIC / PURANIC NOUNS
    # =========================================================================
    "rāma": {
        "dhatu": "ram",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "ram + ghañ (ramante asmin iti rāmaḥ)",
        "gloss": "Rāma; the seventh avatāra of Viṣṇu; 'pleasing'; 'delightful'",
        "synonyms": ["rāmacandra", "raghunandana", "sītāpati", "daśarathātmaja"],
        "antonyms": ["rāvaṇa"],
        "related": ["ram", "rāma", "rāma-rājya", "rāmāyaṇa"],
        "citations": ["Rāmāyaṇa 1.1", "Gītā 10.31"],
    },
    "kṛṣṇa": {
        "dhatu": "kṛṣ",
        "gana": "tudādi",
        "gana_number": 6,
        "nirukta": "kṛṣ + na (kṛṣṇa-varṇa)",
        "gloss": "Kṛṣṇa; the eighth avatāra of Viṣṇu; 'dark, black'; speaker of the Gītā",
        "synonyms": ["vāsudeva", "govinda", "mādhava", "keśava", "nārāyaṇa"],
        "antonyms": [],
        "related": ["kṛṣ", "kārṣṇya", "kṛṣṇa-pakṣa", "bhagavad-gītā"],
        "citations": ["Gītā 1.1", "Gītā 10.12", "Gītā 18.66"],
    },
    "arjuna": {
        "dhatu": "ṛj",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "arjuna (arjayati iti; or: white, bright)",
        "gloss": "Arjuna; the third Pāṇḍava; recipient of the Bhagavad Gītā",
        "synonyms": ["phalguna", "savyasācin", "pārtha", "kuntīputra"],
        "antonyms": [],
        "related": ["ṛj", "arj", "arjuna", "pāṇḍava"],
        "citations": ["Gītā 1.1", "Gītā 2.4", "Gītā 18.78"],
    },
    "pāṇḍava": {
        "dhatu": "paṇḍ",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "pāṇḍu + apatya (pāṇḍoḥ apatyam pāṇḍavaḥ)",
        "gloss": "Pāṇḍava; descendant of Pāṇḍu; the 5 brothers of the Mahābhārata",
        "synonyms": ["pāṇḍu-putra", "pāṇḍava-bhīma", "pāṇḍava-arjuna"],
        "antonyms": ["dhārtarāṣṭra", "kaurava"],
        "related": ["paṇḍ", "pāṇḍava", "pāṇḍu", "pāṇḍava"],
        "citations": ["Gītā 1.1", "Gītā 1.4"],
    },
    "kaurava": {
        "dhatu": "kuru",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "kuru + aṇ (kuroḥ apatyam kauravāḥ)",
        "gloss": "Kaurava; descendant of Kuru; the 100 sons of Dhṛtarāṣṭra",
        "synonyms": ["dhārtarāṣṭra", "kuru-putra", "kaurava-sainika"],
        "antonyms": ["pāṇḍava"],
        "related": ["kuru", "kaurava", "kuru-kṣetra"],
        "citations": ["Gītā 1.1", "Gītā 1.25"],
    },
    "dhṛtarāṣṭra": {
        "dhatu": "dhṛ + rāj",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "dhṛtaṃ rāṣṭraṃ yena iti dhṛtarāṣṭraḥ",
        "gloss": "Dhṛtarāṣṭra; blind king; father of the Kauravas",
        "synonyms": ["dhṛtarāṣṭra", "kuru-rāja"],
        "antonyms": [],
        "related": ["dhṛ", "rāj", "dhṛtarāṣṭra", "dhārtarāṣṭra"],
        "citations": ["Gītā 1.1", "Gītā 1.24"],
    },

    # =========================================================================
    # VEDIC DEITIES
    # =========================================================================
    "agni": {
        "dhatu": "ag",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "ag + ni (agre nīyate iti agniḥ)",
        "gloss": "Agni; fire; the sacred flame; messenger between humans and gods",
        "synonyms": ["vahni", "pāvaka", "hutāśana", "jātavedas"],
        "antonyms": [],
        "related": ["ag", "agni", "āgneya", "agni-hotra"],
        "citations": ["Ṛgveda 1.1.1", "Gītā 10.23"],
    },
    "indra": {
        "dhatu": "ind",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "ind + ra (indati iti indraḥ)",
        "gloss": "Indra; king of the gods; wielder of the vajra; god of rain and war",
        "synonyms": ["śakra", "devendra", "maghavan", "vāsava"],
        "antonyms": [],
        "related": ["ind", "aindra", "indriya", "indraloka"],
        "citations": ["Ṛgveda 1.2.1", "Gītā 10.22"],
    },
    "viṣṇu": {
        "dhatu": "viṣ",
        "gana": "tudādi",
        "gana_number": 6,
        "nirukta": "viṣ + ṇu (viṣṇuḥ vyāpakaḥ)",
        "gloss": "Viṣṇu; the preserver; one of the trimūrti; lord of preservation",
        "synonyms": ["nārāyaṇa", "hari", "vāsudeva", "mādhava", "govinda"],
        "antonyms": ["śiva (destructive aspect)"],
        "related": ["viṣ", "vaiṣṇava", "viṣṇu-tattva", "viṣṇu-loka"],
        "citations": ["Gītā 10.21", "Ṛgveda 1.154.1"],
    },
    "śiva": {
        "dhatu": "śī",
        "gana": "svādi",
        "gana_number": 5,
        "nirukta": "śī + va (śayānaḥ śivaḥ; or: auspicious)",
        "gloss": "Śiva; the auspicious one; one of the trimūrti; lord of dissolution",
        "synonyms": ["maheśvara", "mahādeva", "nīlakaṇṭha", "gaṅgādhara"],
        "antonyms": [],
        "related": ["śī", "śaiva", "śiva-tattva", "śiva-loka"],
        "citations": ["Śvetāśvatara 3.5", "Gītā 10.23"],
    },
    "gaṇeśa": {
        "dhatu": "gaṇ + īś",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "gaṇānāṃ īśaḥ gaṇeśaḥ",
        "gloss": "Gaṇeśa; the elephant-headed god; remover of obstacles",
        "synonyms": ["gaṇapati", "vighneśa", "vināyaka", "ekadanta"],
        "antonyms": [],
        "related": ["gaṇa", "īś", "gāṇeśa", "gaṇeśa-caturthī"],
        "citations": ["Gaṇeśa-purāṇa 1.1"],
    },
    "gaṇapati": {
        "dhatu": "gaṇ + pati",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "gaṇānāṃ patiḥ gaṇapatiḥ",
        "gloss": "Gaṇapati; lord of the gaṇas; another name for Gaṇeśa",
        "synonyms": ["gaṇeśa", "vighneśa", "vināyaka"],
        "antonyms": [],
        "related": ["gaṇa", "pati", "gāṇapatya"],
        "citations": ["Ṛgveda 2.23.1"],
    },
    "sūrya": {
        "dhatu": "sū",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "sū + kya (sūyate iti sūryaḥ)",
        "gloss": "Sūrya; the Sun; source of light and life",
        "synonyms": ["ravi", "bhānu", "divākara", "āditya", "arka"],
        "antonyms": [],
        "related": ["sū", "saura", "sūrya-namaskāra", "sūrya-loka"],
        "citations": ["Ṛgveda 1.115.1", "Gītā 10.21"],
    },
    "candra": {
        "dhatu": "cand",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "cand + rak (candati iti candraḥ)",
        "gloss": "Candra; the Moon; 'shining one'",
        "synonyms": ["soma", "śaśin", "himakara", "niśākara"],
        "antonyms": ["sūrya (in pairing)"],
        "related": ["cand", "cāndra", "candra-loka", "candra-grahaṇa"],
        "citations": ["Ṛgveda 9.1.1", "Gītā 10.21"],
    },

    # =========================================================================
    # ELEMENTS / COSMOLOGY
    # =========================================================================
    "pṛthivī": {
        "dhatu": "pṛth",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "pṛth + ivi (pṛthvī pṛthivī)",
        "gloss": "Earth; the wide one; earth element",
        "synonyms": ["bhūmi", "pṛthvī", "dharaṇī", "vasudhā"],
        "antonyms": ["ākāśa", "dyu"],
        "related": ["pṛth", "pārthiva", "pṛthivī-tattva"],
        "citations": ["Ṛgveda 1.1.1", "Gītā 7.4"],
    },
    "ap": {
        "dhatu": "āp",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "āp (āpnoti iti āpaḥ)",
        "gloss": "Water; liquid element; the waters",
        "synonyms": ["jala", "udaka", "toya", "vāri", "nīra"],
        "antonyms": ["agni (in pairing)"],
        "related": ["āp", "āpya", "ap-tattva"],
        "citations": ["Ṛgveda 10.9.1", "Gītā 7.4"],
    },
    "tejas": {
        "dhatu": "tij",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "tij + asun (tijati iti tejaḥ)",
        "gloss": "Fire; radiance; inner heat; spiritual fire",
        "synonyms": ["agni", "ojas", "varcas", "prabhā"],
        "antonyms": ["tamas", "śītatva"],
        "related": ["tij", "taijasa", "tejasvin", "tejas-tattva"],
        "citations": ["Gītā 7.4", "Chāndogya 6.4"],
    },
    "vāyu": {
        "dhatu": "vā",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "vā + yu (vāti iti vāyuḥ)",
        "gloss": "Wind; air; breath; the life-force (prāṇa)",
        "synonyms": ["anila", "pavana", "māruta", "prāṇa"],
        "antonyms": ["pṛthivī"],
        "related": ["vā", "vāyavya", "vāyu-tattva"],
        "citations": ["Ṛgveda 10.168.1", "Gītā 7.4"],
    },
    "ākāśa": {
        "dhatu": "kāś",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "ā + kāś + a (ākāśe prakāśate)",
        "gloss": "Space; ether; the subtlest element; sky",
        "synonyms": ["vyoman", "gagana", "nabha", "ambara"],
        "antonyms": ["pṛthivī"],
        "related": ["kāś", "ākāśa-tattva", "ākāśa-gamana"],
        "citations": ["Chāndogya 6.4", "Gītā 7.4"],
    },

    # =========================================================================
    # MORAL / SPIRITUAL CONCEPTS
    # =========================================================================
    "ahiṃsā": {
        "dhatu": "hiṃs",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "a + hiṃs + a (ahiṃsanaṃ ahiṃsā)",
        "gloss": "non-violence; non-harm; the first yama",
        "synonyms": ["abhaya", "kṣamā", "akrodha"],
        "antonyms": ["hiṃsā", "krūratā"],
        "related": ["hiṃs", "ahiṃsaka", "ahiṃsā-paramo-dharmaḥ"],
        "citations": ["Gītā 16.2", "Patañjali 2.30"],
    },
    "satya": {
        "dhatu": "as",
        "gana": "adādi",
        "gana_number": 2,
        "nirukta": "sat + ya (sataḥ bhāvaḥ satyam)",
        "gloss": "truth; reality; that which is",
        "synonyms": ["ṛta", "tathya", "yathārthatā"],
        "antonyms": ["anṛta", "mithyā"],
        "related": ["as", "sat", "sattā", "satyatā"],
        "citations": ["Gītā 17.15", "Chāndogya 6.8.7"],
    },
    "asteya": {
        "dhatu": "stai",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "a + steya (asteyanaṃ asteyam)",
        "gloss": "non-stealing; abstention from theft",
        "synonyms": ["asteya-vrata", "aparigraha"],
        "antonyms": ["steya", "caurya"],
        "related": ["stai", "stena", "asteya-vrata"],
        "citations": ["Patañjali 2.30", "Gītā 16.2"],
    },
    "aparigraha": {
        "dhatu": "grah",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "a + pari + grah + a (aparigrahaḥ)",
        "gloss": "non-possessiveness; non-grasping",
        "synonyms": ["vairāgya", "tyāga", "asaṅga"],
        "antonyms": ["parigraha", "saṅga"],
        "related": ["grah", "pari-grah", "aparigraha"],
        "citations": ["Patañjali 2.39", "Gītā 16.2"],
    },
    "saṃtoṣa": {
        "dhatu": "tuṣ",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "saṃ + tuṣ + a (saṃtoṣaḥ)",
        "gloss": "contentment; satisfaction",
        "synonyms": ["tuṣṭi", "santoṣa", "ānanda"],
        "antonyms": ["asaṃtoṣa", "tṛṣṇā"],
        "related": ["tuṣ", "tuṣṭa", "saṃtoṣa"],
        "citations": ["Gītā 17.16", "Patañjali 2.42"],
    },

    # =========================================================================
    # COMMON NOUNS (baseline coverage)
    # =========================================================================
    "rāja": {
        "dhatu": "rāj",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "rāj + a (rājati iti rājā)",
        "gloss": "king; ruler; sovereign",
        "synonyms": ["nṛpa", "bhūpati", "pārthiva", "mahīpati"],
        "antonyms": ["dāsa", "sevaka"],
        "related": ["rāj", "rājya", "rājñī", "rājādhikāra"],
        "citations": ["Gītā 1.1", "Rāmāyaṇa 1.1"],
    },
    "putra": {
        "dhatu": "puṣ",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "puṣ + tra (putraḥ)",
        "gloss": "son; child",
        "synonyms": ["suta", "tanaya", "ātmaja", "nandana"],
        "antonyms": ["duhitṛ"],
        "related": ["puṣ", "putra", "putrī", "putra-tva"],
        "citations": ["Gītā 1.32", "Rāmāyaṇa 1.1"],
    },
    "bhāryā": {
        "dhatu": "bhṛ",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "bhṛ + ṇyak (bhriyate iti bhāryā)",
        "gloss": "wife; the one to be supported",
        "synonyms": ["patnī", "kalatra", "jāyā", "vallabhā"],
        "antonyms": ["pati", "bhartṛ"],
        "related": ["bhṛ", "bhāryā", "bhāryā-tva"],
        "citations": ["Rāmāyaṇa 1.1", "Manusmṛti 9.1"],
    },
    "gṛha": {
        "dhatu": "grah",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "grah + a (gṛhṇāti iti gṛham)",
        "gloss": "house; home; dwelling",
        "synonyms": ["veśma", "nīḍa", "nilaya", "ālaya"],
        "antonyms": [],
        "related": ["grah", "gṛhastha", "gṛha-pati"],
        "citations": ["Rāmāyaṇa 1.1", "Manusmṛti 3.1"],
    },
    "jala": {
        "dhatu": "jal",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "jal (jalati iti jalam)",
        "gloss": "water; liquid; fluid",
        "synonyms": ["ap", "udaka", "toya", "vāri"],
        "antonyms": [],
        "related": ["jal", "jalaha", "jala-tattva"],
        "citations": ["Ṛgveda 10.9.1"],
    },
    "vanaspati": {
        "dhatu": "van + pati",
        "gana": "bhvādi",
        "gana_number": 1,
        "nirukta": "vanānāṃ patiḥ vanaspatiḥ",
        "gloss": "tree; lord of the forest; vegetation",
        "synonyms": ["vṛkṣa", "taru", "pādapa", "druma"],
        "antonyms": [],
        "related": ["van", "pati", "vanaspati", "vanaspatya"],
        "citations": ["Ṛgveda 10.97.1"],
    },
}


# ==============================================================================
# PUBLIC API
# ==============================================================================

def lookup_semantic(stem: str) -> Optional[Dict[str, Any]]:
    """
    Look up semantic metadata for a stem.
    Returns None if not in index.
    """
    if not stem:
        return None
    return SEMANTIC_INDEX.get(stem.strip().lower())


def search_by_dhatu(dhatu: str) -> list:
    """Return all stems derived from a given dhātu."""
    results = []
    for stem, entry in SEMANTIC_INDEX.items():
        if entry.get("dhatu") == dhatu:
            results.append({"stem": stem, **entry})
    return results


def search_by_synonym(synonym: str) -> list:
    """Return all stems whose synonym list contains the given term."""
    results = []
    for stem, entry in SEMANTIC_INDEX.items():
        if synonym in entry.get("synonyms", []):
            results.append({"stem": stem, **entry})
    return results


def get_stats() -> Dict[str, Any]:
    """Return statistics about the semantic index."""
    return {
        "total_entries": len(SEMANTIC_INDEX),
        "with_dhatu": sum(1 for e in SEMANTIC_INDEX.values() if e.get("dhatu")),
        "with_nirukta": sum(1 for e in SEMANTIC_INDEX.values() if e.get("nirukta")),
        "with_synonyms": sum(1 for e in SEMANTIC_INDEX.values() if e.get("synonyms")),
        "with_citations": sum(1 for e in SEMANTIC_INDEX.values() if e.get("citations")),
    }