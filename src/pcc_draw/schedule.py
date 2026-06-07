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


@dataclass(frozen=True)
class ColumnState:
    """한 컬럼의 현재 점유 상태. cycle/phase가 None이면 유휴."""

    column: int
    cycle: int | None
    phase: Phase | None


@dataclass(frozen=True)
class Schedule:
    """겹치는 PCC 사이클 타임라인. 위상 간격 = load_duration."""

    durations: PhaseDurations
    num_columns: int = 4

    def cycle_start(self, cycle_index: int) -> float:
        """사이클 i의 load 시작 시각 = i * load_duration."""
        return cycle_index * self.durations.load

    def phase_at(self, cycle_index: int, t: float) -> Phase | None:
        """사이클 i가 시각 t에 있는 단계. 반열림 [start, end). 범위 밖이면 None."""
        offset = t - self.cycle_start(cycle_index)
        if offset < 0:
            return None
        acc = 0.0
        for phase, dur in self.durations.as_list():
            if acc <= offset < acc + dur:
                return phase
            acc += dur
        return None

    def active_cycles(self, t: float) -> list[tuple[int, Phase]]:
        """시각 t에 활성인 (cycle_index, phase) 목록. cycle_index 오름차순."""
        load = self.durations.load
        if load <= 0:
            raise ValueError(f"load duration must be positive, got {load}")
        total = self.durations.total
        lo = max(0, int((t - total) // load))
        hi = int(t // load)
        result: list[tuple[int, Phase]] = []
        for i in range(lo, hi + 1):
            phase = self.phase_at(i, t)
            if phase is not None:
                result.append((i, phase))
        return result

    def state_at(self, t: float) -> list[ColumnState]:
        """각 컬럼의 (활성 사이클, 단계). 사이클 i → 컬럼 i % num_columns."""
        states = [ColumnState(c, None, None) for c in range(self.num_columns)]
        for cycle, phase in self.active_cycles(t):
            c = cycle % self.num_columns
            states[c] = ColumnState(c, cycle, phase)
        return states
