"""
Praat TextGrid Alignment Parser & Acoustic Evaluation Metrics (P2-1).

Provides L10 perceptual/acoustic verification primitives:
  - parse_textgrid(): parses Praat IntervalTier blocks from ooTextFile TextGrids
  - evaluate_f0_and_timing(): computes F0 RMSE (Hz & cents), F0 correlation,
    and boundary duration MAE (ms) against reference TextGrid + F0 tracks.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple


@dataclass(frozen=True)
class TextGridInterval:
    xmin: float
    xmax: float
    text: str

    @property
    def duration_ms(self) -> float:
        return max(0.0, (self.xmax - self.xmin) * 1000.0)


@dataclass(frozen=True)
class AcousticEvalReport:
    interval_count: int
    f0_rmse_hz: float
    f0_rmse_cents: float
    f0_correlation: float
    duration_mae_ms: float
    certified_authentic: bool


def parse_textgrid(content: str) -> Dict[str, List[TextGridInterval]]:
    """
    Parse Praat ooTextFile TextGrid text into {tier_name: [TextGridInterval, ...]}.
    Supports standard long-form Praat TextGrid exports.
    """
    tiers: Dict[str, List[TextGridInterval]] = {}
    tier_blocks = re.split(r"item\s*\[\d+\]\s*:", content)
    for block in tier_blocks[1:]:
        name_match = re.search(r'name\s*=\s*"([^"]*)"', block)
        class_match = re.search(r'class\s*=\s*"([^"]*)"', block)
        if not name_match or (class_match and class_match.group(1) != "IntervalTier"):
            continue
        tier_name = name_match.group(1)
        intervals: List[TextGridInterval] = []
        for m in re.finditer(
            r'intervals\s*\[\d+\]\s*:\s*xmin\s*=\s*([0-9.eE+-]+)\s*xmax\s*=\s*([0-9.eE+-]+)\s*text\s*=\s*"([^"]*)"',
            block,
        ):
            intervals.append(
                TextGridInterval(
                    xmin=float(m.group(1)),
                    xmax=float(m.group(2)),
                    text=m.group(3),
                )
            )
        tiers[tier_name] = intervals
    return tiers


def _pearson_corr(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = len(xs)
    if n < 2:
        return 1.0 if n == 1 and math.isclose(xs[0], ys[0]) else 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0.0 or den_y == 0.0:
        return 1.0 if math.isclose(mx, my) else 0.0
    return max(-1.0, min(1.0, num / (den_x * den_y)))


def evaluate_f0_and_timing(
    predicted_f0_hz: Sequence[float],
    reference_f0_hz: Sequence[float],
    predicted_durations_ms: Sequence[float],
    reference_intervals: Sequence[TextGridInterval],
    *,
    expert_reviewed: bool = False,
) -> AcousticEvalReport:
    """
    Compute acoustic alignment error between predicted contours and reference
    TextGrid intervals. Note: `certified_authentic` stays False unless
    `expert_reviewed=True` (enforcing the P0 governing acceptance rule).
    """
    n_f0 = min(len(predicted_f0_hz), len(reference_f0_hz))
    if n_f0 == 0:
        raise ValueError("Cannot evaluate F0 metrics on empty F0 sequences")

    sq_hz = 0.0
    sq_cents = 0.0
    valid_pairs: List[Tuple[float, float]] = []
    for p_hz, r_hz in zip(predicted_f0_hz[:n_f0], reference_f0_hz[:n_f0]):
        if p_hz <= 0.0 or r_hz <= 0.0:
            continue
        diff = p_hz - r_hz
        sq_hz += diff * diff
        cents = 1200.0 * math.log2(p_hz / r_hz)
        sq_cents += cents * cents
        valid_pairs.append((p_hz, r_hz))

    if not valid_pairs:
        raise ValueError("No voiced (>0 Hz) F0 pairs available for evaluation")

    rmse_hz = math.sqrt(sq_hz / len(valid_pairs))
    rmse_cents = math.sqrt(sq_cents / len(valid_pairs))
    corr = _pearson_corr([p for p, _ in valid_pairs], [r for _, r in valid_pairs])

    non_empty = [iv for iv in reference_intervals if iv.text.strip()]
    n_dur = min(len(predicted_durations_ms), len(non_empty))
    if n_dur > 0:
        dur_mae = sum(
            abs(p_ms - iv.duration_ms)
            for p_ms, iv in zip(predicted_durations_ms[:n_dur], non_empty[:n_dur])
        ) / n_dur
    else:
        dur_mae = 0.0

    return AcousticEvalReport(
        interval_count=n_dur,
        f0_rmse_hz=round(rmse_hz, 4),
        f0_rmse_cents=round(rmse_cents, 4),
        f0_correlation=round(corr, 4),
        duration_mae_ms=round(dur_mae, 4),
        certified_authentic=bool(expert_reviewed),
    )
