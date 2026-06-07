"""순수 PCC 스케줄 모델 — matplotlib 무관, 결정적 함수. 시간 단위는 분(float)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Phase(Enum):
    LOAD = "LOAD"
    WASH = "WASH"
    ELUTE = "ELUTE"
    REGEN = "REGEN"


@dataclass(frozen=True)
class PhaseDurations:
    """각 단계 고정 길이[분]. load만 가변 의미를 갖지만 여기선 모두 상수."""

    load: float = 30.0
    wash: float = 20.0
    elute: float = 40.0
    regen: float = 30.0

    @property
    def total(self) -> float:
        return self.load + self.wash + self.elute + self.regen

    def as_list(self) -> list[tuple[Phase, float]]:
        return [
            (Phase.LOAD, self.load),
            (Phase.WASH, self.wash),
            (Phase.ELUTE, self.elute),
            (Phase.REGEN, self.regen),
        ]
