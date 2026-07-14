from __future__ import annotations

SPROUT = "새싹"
NEW_SHOOT = "새순"
MATURE = "성목"

_NEW_SHOOT_THRESHOLD = 100
_MATURE_THRESHOLD = 300


def compute_growth_stage(points: int) -> str:
    if points >= _MATURE_THRESHOLD:
        return MATURE
    if points >= _NEW_SHOOT_THRESHOLD:
        return NEW_SHOOT
    return SPROUT
