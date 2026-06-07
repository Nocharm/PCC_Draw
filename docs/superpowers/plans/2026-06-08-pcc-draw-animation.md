# PCC_Draw Animation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** PCC 컬럼 #01~#04가 시간에 따라 LOAD→WASH→ELUTE→REGEN 단계를 도는 모습을 matplotlib 실시간 창에 애니메이션으로 그린다.

**Architecture:** 순수 스케줄 모델(`schedule.py`, matplotlib 무관·결정적·테스트 가능)을 핵심으로 두고, 그 위에 프레임 렌더러(`draw.py`)와 FuncAnimation 드라이버(`animate.py`)를 얇게 얹는다. 사이클 총길이 > 위상 간격(load_duration)이라 사이클이 겹쳐 한 시점에 4개 컬럼이 서로 다른 단계에 동시 존재한다.

**Tech Stack:** Python 3.11+, matplotlib (런타임), pytest·ruff·pillow (dev). uv 관리, src 레이아웃.

---

## File Structure

| 파일 | 책임 |
|------|------|
| `pyproject.toml` | 패키지 메타·의존성·entry point·pytest pythonpath |
| `src/pcc_draw/__init__.py` | 공개 심볼 재노출 |
| `src/pcc_draw/schedule.py` | 순수 모델: `Phase`, `PhaseDurations`, `ColumnState`, `Schedule`(cycle_start/phase_at/active_cycles/state_at) |
| `src/pcc_draw/draw.py` | `PHASE_COLORS`, `build_figure`, `draw_process`, `draw_gantt`, `render` |
| `src/pcc_draw/animate.py` | `advance`, `run`(FuncAnimation + 키 핸들러 + GIF 저장) |
| `src/pcc_draw/__main__.py` | `parse_args`, `main` (argparse CLI) |
| `tests/test_schedule.py` | 모델 단위 테스트 (TDD) |
| `tests/test_draw.py` | 렌더 스모크 테스트 (Agg) |
| `tests/test_animate.py` | `advance` 단위 + `parse_args` 테스트 |

분리 원칙: 모델은 matplotlib을 모르고(순수·결정적), 렌더는 상태→그림(부수효과 없는 입력), 애니는 시간 전진만 담당. 시각 검증 불가 부분은 스모크 테스트(예외 없음·핵심 아티팩트 존재) + 수동 육안 확인으로 보강한다.

---

## Task 1: 프로젝트 스캐폴딩

**Files:**
- Create: `pyproject.toml`
- Create: `src/pcc_draw/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: pyproject.toml 작성**

```toml
[project]
name = "pcc-draw"
version = "0.1.0"
description = "PCC 크로마토그래피 컬럼 스케줄 matplotlib 애니메이션"
requires-python = ">=3.11"
dependencies = ["matplotlib>=3.8"]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.5", "pillow>=10"]

[project.scripts]
pcc-draw = "pcc_draw.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/pcc_draw"]

[tool.pytest.ini_options]
pythonpath = ["src"]

[tool.ruff]
line-length = 100
```

- [ ] **Step 2: 빈 패키지/테스트 init 생성**

`src/pcc_draw/__init__.py`:

```python
"""PCC 컬럼 스케줄을 matplotlib 애니메이션으로 그리는 패키지."""
```

`tests/__init__.py`: 빈 파일.

- [ ] **Step 3: 의존성 설치 확인**

Run: `uv sync --extra dev`
Expected: `.venv` 생성, matplotlib·pytest·ruff·pillow 설치 성공.

- [ ] **Step 4: pytest 수집 확인**

Run: `uv run pytest -q`
Expected: `no tests ran` (테스트 0개, 에러 없음).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/pcc_draw/__init__.py tests/__init__.py
git commit -m "chore(setup): scaffold pcc_draw package — 패키지 스캐폴딩"
```

---

## Task 2: Phase + PhaseDurations

**Files:**
- Create: `src/pcc_draw/schedule.py`
- Test: `tests/test_schedule.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_schedule.py`:

```python
"""순수 스케줄 모델 단위 테스트."""
from pcc_draw.schedule import Phase, PhaseDurations


def test_phase_durations_total_sums_all_phases():
    d = PhaseDurations(load=30.0, wash=20.0, elute=40.0, regen=30.0)
    assert d.total == 120.0


def test_phase_durations_as_list_in_cycle_order():
    d = PhaseDurations(load=30.0, wash=20.0, elute=40.0, regen=30.0)
    assert d.as_list() == [
        (Phase.LOAD, 30.0),
        (Phase.WASH, 20.0),
        (Phase.ELUTE, 40.0),
        (Phase.REGEN, 30.0),
    ]
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_schedule.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'pcc_draw.schedule'`.

- [ ] **Step 3: 최소 구현**

`src/pcc_draw/schedule.py`:

```python
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
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_schedule.py -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/pcc_draw/schedule.py tests/test_schedule.py
git commit -m "feat(schedule): add Phase and PhaseDurations — 단계·고정 길이 모델"
```

---

## Task 3: Schedule.cycle_start + phase_at (반열림 경계)

**Files:**
- Modify: `src/pcc_draw/schedule.py`
- Test: `tests/test_schedule.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_schedule.py`에 추가:

```python
from pcc_draw.schedule import Schedule


def _sched():
    return Schedule(PhaseDurations(load=30.0, wash=20.0, elute=40.0, regen=30.0))


def test_cycle_start_is_index_times_load():
    s = _sched()
    assert s.cycle_start(0) == 0.0
    assert s.cycle_start(3) == 90.0


def test_phase_at_start_boundary_belongs_to_load():
    # 반열림 [start, end): 사이클 시작 시각은 LOAD 소유
    assert _sched().phase_at(0, 0.0) is Phase.LOAD


def test_phase_at_phase_boundary_belongs_to_next_phase():
    # load=30 → t=30.0은 WASH (LOAD의 끝이 아니라 WASH의 시작)
    assert _sched().phase_at(0, 30.0) is Phase.WASH


def test_phase_at_returns_none_before_cycle_and_at_total_end():
    s = _sched()
    assert s.phase_at(1, 10.0) is None       # 사이클1은 t=30부터 시작 → 이전
    assert s.phase_at(0, 120.0) is None       # total=120 → 사이클 종료(반열림)
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_schedule.py -q`
Expected: FAIL — `cannot import name 'Schedule'`.

- [ ] **Step 3: 최소 구현**

`src/pcc_draw/schedule.py`에 추가:

```python
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
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_schedule.py -q`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add src/pcc_draw/schedule.py tests/test_schedule.py
git commit -m "feat(schedule): add cycle_start and phase_at with half-open bounds — 반열림 단계 조회"
```

---

## Task 4: Schedule.active_cycles (겹침/파이프라이닝)

**Files:**
- Modify: `src/pcc_draw/schedule.py`
- Test: `tests/test_schedule.py`

- [ ] **Step 1: 실패하는 테스트 추가**

```python
def test_active_cycles_steady_state_has_four_concurrent():
    # total=120, load=30 → 정상 상태에서 동시 활성 4개
    s = _sched()
    active = s.active_cycles(200.0)
    assert len(active) == 4


def test_active_cycles_excludes_cycle_ending_exactly_at_t():
    # t=200, total=120 → start=80 사이클은 offset=120=total → 제외(반열림)
    s = _sched()
    indices = [i for i, _ in s.active_cycles(200.0)]
    assert 80 / 30 not in indices  # 정수 아님이지만 의미상: start=80인 사이클 없음
    # start=90,120,150,180 → 인덱스 3,4,5,6
    assert indices == [3, 4, 5, 6]


def test_active_cycles_raises_on_nonpositive_load():
    s = Schedule(PhaseDurations(load=0.0))
    try:
        s.active_cycles(10.0)
        raised = False
    except ValueError:
        raised = True
    assert raised
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_schedule.py -q`
Expected: FAIL — `'Schedule' object has no attribute 'active_cycles'`.

- [ ] **Step 3: 최소 구현**

`src/pcc_draw/schedule.py`의 `Schedule`에 메서드 추가:

```python
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
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_schedule.py -q`
Expected: PASS (9 passed).

- [ ] **Step 5: Commit**

```bash
git add src/pcc_draw/schedule.py tests/test_schedule.py
git commit -m "feat(schedule): add active_cycles for overlapping pipeline — 겹침 사이클 조회"
```

---

## Task 5: ColumnState + Schedule.state_at + eluting

**Files:**
- Modify: `src/pcc_draw/schedule.py`
- Modify: `src/pcc_draw/__init__.py`
- Test: `tests/test_schedule.py`

- [ ] **Step 1: 실패하는 테스트 추가**

```python
from pcc_draw.schedule import ColumnState


def test_state_at_returns_one_entry_per_column():
    s = _sched()
    states = s.state_at(200.0)
    assert len(states) == 4
    assert [st.column for st in states] == [0, 1, 2, 3]


def test_state_at_assigns_active_cycles_to_distinct_columns():
    # 동시 활성 4개가 4개 컬럼에 1:1 (round-robin mod 4)
    s = _sched()
    states = s.state_at(200.0)
    assert all(st.cycle is not None for st in states)
    assert all(st.cycle % 4 == st.column for st in states)


def test_eluting_columns_match_elute_phase():
    s = _sched()
    t = 200.0
    states = s.state_at(t)
    eluting = [st for st in states if st.phase is Phase.ELUTE]
    # 직접 phase_at로 교차검증
    expected = [st for st in states if st.cycle is not None
                and s.phase_at(st.cycle, t) is Phase.ELUTE]
    assert eluting == expected
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_schedule.py -q`
Expected: FAIL — `cannot import name 'ColumnState'`.

- [ ] **Step 3: 최소 구현**

`src/pcc_draw/schedule.py`에 `ColumnState` 추가(파일 상단 dataclass 영역) + `Schedule.state_at` 메서드:

```python
@dataclass(frozen=True)
class ColumnState:
    """한 컬럼의 현재 점유 상태. cycle/phase가 None이면 유휴."""

    column: int
    cycle: int | None
    phase: Phase | None
```

```python
    def state_at(self, t: float) -> list[ColumnState]:
        """각 컬럼의 (활성 사이클, 단계). 사이클 i → 컬럼 i % num_columns."""
        states = [ColumnState(c, None, None) for c in range(self.num_columns)]
        for cycle, phase in self.active_cycles(t):
            c = cycle % self.num_columns
            states[c] = ColumnState(c, cycle, phase)
        return states
```

- [ ] **Step 4: 공개 API 재노출**

`src/pcc_draw/__init__.py`:

```python
"""PCC 컬럼 스케줄을 matplotlib 애니메이션으로 그리는 패키지."""
from pcc_draw.schedule import (
    ColumnState,
    Phase,
    PhaseDurations,
    Schedule,
)

__all__ = ["ColumnState", "Phase", "PhaseDurations", "Schedule"]
```

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest tests/test_schedule.py -q`
Expected: PASS (12 passed).

- [ ] **Step 6: Commit**

```bash
git add src/pcc_draw/schedule.py src/pcc_draw/__init__.py tests/test_schedule.py
git commit -m "feat(schedule): add ColumnState and state_at with column assignment — 컬럼별 상태 조회"
```

---

## Task 6: PHASE_COLORS + build_figure

**Files:**
- Create: `src/pcc_draw/draw.py`
- Test: `tests/test_draw.py`

- [ ] **Step 1: 실패하는 스모크 테스트 작성**

`tests/test_draw.py`:

```python
"""렌더 스모크 테스트 — Agg 백엔드(창 없음), 예외·핵심 아티팩트만 확인."""
import matplotlib

matplotlib.use("Agg")  # GUI 없이 렌더 (pyplot import 전 설정)

from pcc_draw.draw import PHASE_COLORS, build_figure
from pcc_draw.schedule import Phase


def test_phase_colors_cover_all_phases():
    assert set(PHASE_COLORS) == set(Phase)


def test_build_figure_returns_two_axes():
    fig, ax_process, ax_gantt = build_figure()
    assert fig is not None
    assert ax_process is not ax_gantt
    assert len(fig.axes) == 2
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_draw.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'pcc_draw.draw'`.

- [ ] **Step 3: 최소 구현**

`src/pcc_draw/draw.py`:

```python
"""모델 상태를 받아 한 프레임을 그리는 렌더러. 색은 PHASE_COLORS 단일 출처."""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from pcc_draw.schedule import Phase

PHASE_COLORS: dict[Phase, str] = {
    Phase.LOAD: "#4C9F70",   # green
    Phase.WASH: "#F0C808",   # yellow
    Phase.ELUTE: "#DD6E42",  # orange
    Phase.REGEN: "#5B8DEF",  # blue
}
IDLE_COLOR = "#E0E0E0"
COLUMN_LABELS = ["#01", "#02", "#03", "#04"]


def build_figure() -> tuple[Figure, plt.Axes, plt.Axes]:
    """상단 공정 패널 + 하단 간트 패널, 시간축 의미 공유."""
    fig, (ax_process, ax_gantt) = plt.subplots(
        2, 1, figsize=(10, 6), gridspec_kw={"height_ratios": [3, 2]}
    )
    return fig, ax_process, ax_gantt
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_draw.py -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/pcc_draw/draw.py tests/test_draw.py
git commit -m "feat(draw): add PHASE_COLORS and build_figure — 색 정의·도화면 골격"
```

---

## Task 7: draw_process (컬럼 + VI + Titer + 화살표)

**Files:**
- Modify: `src/pcc_draw/draw.py`
- Test: `tests/test_draw.py`

- [ ] **Step 1: 실패하는 스모크 테스트 추가**

`tests/test_draw.py`에 추가:

```python
from pcc_draw.draw import draw_process
from pcc_draw.schedule import ColumnState


def test_draw_process_adds_a_patch_per_column_plus_vi():
    fig, ax_process, _ = build_figure()
    states = [
        ColumnState(0, 0, Phase.LOAD),
        ColumnState(1, 1, Phase.WASH),
        ColumnState(2, 2, Phase.ELUTE),
        ColumnState(3, 3, Phase.REGEN),
    ]
    draw_process(ax_process, states, titer=1.52)
    # 컬럼 4개 + VI 박스 1개 = 최소 5개 패치
    assert len(ax_process.patches) >= 5
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_draw.py -q`
Expected: FAIL — `cannot import name 'draw_process'`.

- [ ] **Step 3: 최소 구현**

`src/pcc_draw/draw.py`에 추가:

```python
from matplotlib.patches import Rectangle

from pcc_draw.schedule import ColumnState


def draw_process(ax: plt.Axes, states: list[ColumnState], titer: float) -> None:
    """상단 패널: 컬럼 박스(단계 색) + VI + Titer + elute→VI 화살표."""
    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("PCC — Pro A columns", loc="left")

    box_w, box_h, gap, y0 = 1.4, 2.0, 0.4, 1.0
    for st in states:
        x0 = 0.5 + st.column * (box_w + gap)
        color = PHASE_COLORS[st.phase] if st.phase else IDLE_COLOR
        ax.add_patch(Rectangle((x0, y0), box_w, box_h,
                               facecolor=color, edgecolor="black", lw=1.5))
        label = (COLUMN_LABELS[st.column] if st.column < len(COLUMN_LABELS)
                 else f"#{st.column + 1:02d}")
        ax.text(x0 + box_w / 2, y0 + box_h - 0.3, label,
                ha="center", va="top", fontweight="bold")
        ax.text(x0 + box_w / 2, y0 + 0.3, st.phase.value if st.phase else "idle",
                ha="center", va="bottom")

    vi_x = 0.5 + len(states) * (box_w + gap) + 0.3
    eluting = [st for st in states if st.phase is Phase.ELUTE]
    vi_color = PHASE_COLORS[Phase.ELUTE] if eluting else IDLE_COLOR
    ax.add_patch(Rectangle((vi_x, y0 + 0.5), 1.0, 1.0,
                           facecolor=vi_color, edgecolor="black", lw=1.5))
    ax.text(vi_x + 0.5, y0 + 1.0, "VI", ha="center", va="center", fontweight="bold")

    if eluting:
        src = eluting[0]
        sx = 0.5 + src.column * (box_w + gap) + box_w
        ax.annotate("", xy=(vi_x, y0 + 1.0), xytext=(sx, y0 + 1.0),
                    arrowprops=dict(arrowstyle="->", lw=2,
                                    color=PHASE_COLORS[Phase.ELUTE]))

    ax.text(9.8, 3.7, f"Titer: {titer:.2f}", ha="right", va="top", fontsize=11,
            bbox=dict(boxstyle="round", fc="white", ec="gray"))
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_draw.py -q`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/pcc_draw/draw.py tests/test_draw.py
git commit -m "feat(draw): render column/VI/titer process panel — 공정 패널 렌더"
```

---

## Task 8: draw_gantt (미니 간트 + now 선)

**Files:**
- Modify: `src/pcc_draw/draw.py`
- Test: `tests/test_draw.py`

- [ ] **Step 1: 실패하는 스모크 테스트 추가**

```python
from pcc_draw.draw import draw_gantt
from pcc_draw.schedule import PhaseDurations, Schedule


def test_draw_gantt_draws_now_line_and_phase_bands():
    fig, _, ax_gantt = build_figure()
    s = Schedule(PhaseDurations())
    draw_gantt(ax_gantt, s, t=200.0)
    # phase 띠 패치가 다수 + now 세로선 1개 이상
    assert len(ax_gantt.patches) > 4
    assert len(ax_gantt.lines) >= 1
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_draw.py -q`
Expected: FAIL — `cannot import name 'draw_gantt'`.

- [ ] **Step 3: 최소 구현**

`src/pcc_draw/draw.py`에 추가:

```python
from pcc_draw.schedule import Schedule


def draw_gantt(ax: plt.Axes, schedule: Schedule, t: float,
               window_min: float = 180.0) -> None:
    """하단 패널: 컬럼별 단계 색 띠 + now 세로선. now는 창의 60% 지점."""
    ax.clear()
    t0 = t - window_min * 0.6
    t1 = t + window_min * 0.4
    ax.set_xlim(t0, t1)
    ax.set_ylim(-0.5, schedule.num_columns - 0.5)
    ax.set_yticks(range(schedule.num_columns))
    ax.set_yticklabels(COLUMN_LABELS[:schedule.num_columns])
    ax.set_xlabel("time (min)")
    ax.set_title("timeline", loc="left")

    load = schedule.durations.load
    total = schedule.durations.total
    lo = max(0, int((t0 - total) // load))
    hi = int(t1 // load)
    for cyc in range(lo, hi + 1):
        row = cyc % schedule.num_columns
        acc = schedule.cycle_start(cyc)
        for phase, dur in schedule.durations.as_list():
            ax.add_patch(Rectangle((acc, row - 0.3), dur, 0.6,
                                   facecolor=PHASE_COLORS[phase], edgecolor="none"))
            acc += dur

    ax.axvline(t, color="green", lw=2)  # now 세로선
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_draw.py -q`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/pcc_draw/draw.py tests/test_draw.py
git commit -m "feat(draw): render mini-gantt timeline with now line — 타임라인 패널 렌더"
```

---

## Task 9: render (두 패널 합성)

**Files:**
- Modify: `src/pcc_draw/draw.py`
- Test: `tests/test_draw.py`

- [ ] **Step 1: 실패하는 스모크 테스트 추가**

```python
from pcc_draw.draw import render


def test_render_populates_both_axes():
    fig, ax_process, ax_gantt = build_figure()
    s = Schedule(PhaseDurations())
    render(fig, ax_process, ax_gantt, s, t=200.0, titer=1.52)
    assert len(ax_process.patches) >= 5   # 컬럼 + VI
    assert len(ax_gantt.lines) >= 1        # now 선
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_draw.py -q`
Expected: FAIL — `cannot import name 'render'`.

- [ ] **Step 3: 최소 구현**

`src/pcc_draw/draw.py`에 추가:

```python
def render(fig: Figure, ax_process: plt.Axes, ax_gantt: plt.Axes,
           schedule: Schedule, t: float, titer: float) -> None:
    """한 프레임: 모델 상태 조회 → 두 패널 렌더."""
    states = schedule.state_at(t)
    draw_process(ax_process, states, titer)
    draw_gantt(ax_gantt, schedule, t)
    fig.tight_layout()
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_draw.py -q`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add src/pcc_draw/draw.py tests/test_draw.py
git commit -m "feat(draw): add render combining both panels — 프레임 합성 렌더"
```

---

## Task 10: animate.advance + run

**Files:**
- Create: `src/pcc_draw/animate.py`
- Test: `tests/test_animate.py`

- [ ] **Step 1: 실패하는 테스트 작성 (순수 헬퍼)**

`tests/test_animate.py`:

```python
"""애니메이션 순수 헬퍼 + CLI 파싱 테스트."""
import matplotlib

matplotlib.use("Agg")

from pcc_draw.animate import advance


def test_advance_moves_time_by_dt_when_running():
    assert advance(100.0, 2.0, paused=False) == 102.0


def test_advance_holds_time_when_paused():
    assert advance(100.0, 2.0, paused=True) == 100.0
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_animate.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'pcc_draw.animate'`.

- [ ] **Step 3: 최소 구현**

`src/pcc_draw/animate.py`:

```python
"""FuncAnimation 드라이버 — 시간을 전진시키며 프레임을 렌더. 키: space=정지, ↑/↓=속도."""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from pcc_draw.draw import build_figure, render
from pcc_draw.schedule import PhaseDurations, Schedule


def advance(t: float, dt: float, paused: bool) -> float:
    """정지 중이면 시각 유지, 아니면 dt만큼 전진. (순수 함수, 테스트용)"""
    return t if paused else t + dt


def run(schedule: Schedule | None = None, titer: float = 1.52, dt: float = 2.0,
        frames: int = 600, interval: int = 50, save_path: str | None = None):
    """실시간 창 표시(save_path 없음) 또는 GIF 저장. interval[ms]."""
    schedule = schedule or Schedule(PhaseDurations())
    fig, ax_process, ax_gantt = build_figure()
    sim = {"t": 0.0, "dt": dt, "paused": False}

    def update(_frame):
        sim["t"] = advance(sim["t"], sim["dt"], sim["paused"])
        render(fig, ax_process, ax_gantt, schedule, sim["t"], titer)

    anim = FuncAnimation(fig, update, frames=frames, interval=interval, repeat=True)

    def on_key(event):
        if event.key == " ":
            sim["paused"] = not sim["paused"]
        elif event.key == "up":
            sim["dt"] *= 1.5
        elif event.key == "down":
            sim["dt"] /= 1.5

    fig.canvas.mpl_connect("key_press_event", on_key)

    if save_path:
        anim.save(save_path, writer=PillowWriter(fps=max(1, 1000 // interval)))
    else:
        plt.show()
    return anim
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_animate.py -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/pcc_draw/animate.py tests/test_animate.py
git commit -m "feat(animate): add advance helper and FuncAnimation run — 시간 전진·애니 드라이버"
```

---

## Task 11: CLI (__main__)

**Files:**
- Create: `src/pcc_draw/__main__.py`
- Test: `tests/test_animate.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_animate.py`에 추가:

```python
from pcc_draw.__main__ import parse_args


def test_parse_args_defaults():
    args = parse_args([])
    assert args.titer == 1.52
    assert args.columns == 4
    assert args.save is None


def test_parse_args_custom_values():
    args = parse_args(["--titer", "2.0", "--load", "25", "--save", "out.gif"])
    assert args.titer == 2.0
    assert args.load == 25.0
    assert args.save == "out.gif"
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest tests/test_animate.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'pcc_draw.__main__'`.

- [ ] **Step 3: 최소 구현**

`src/pcc_draw/__main__.py`:

```python
"""python -m pcc_draw / pcc-draw 진입점."""
from __future__ import annotations

import argparse

from pcc_draw.animate import run
from pcc_draw.schedule import PhaseDurations, Schedule


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="pcc-draw",
                                description="PCC 컬럼 스케줄 애니메이션")
    p.add_argument("--titer", type=float, default=1.52, help="Titer 표시 값 [g/L]")
    p.add_argument("--dt", type=float, default=2.0, help="프레임당 진행 시간 [분]")
    p.add_argument("--load", type=float, default=30.0, help="LOAD 길이 [분]")
    p.add_argument("--wash", type=float, default=20.0, help="WASH 길이 [분]")
    p.add_argument("--elute", type=float, default=40.0, help="ELUTE 길이 [분]")
    p.add_argument("--regen", type=float, default=30.0, help="REGEN 길이 [분]")
    p.add_argument("--columns", type=int, default=4, help="컬럼 수")
    p.add_argument("--save", type=str, default=None,
                   help="GIF 저장 경로 (생략 시 실시간 창)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    schedule = Schedule(
        PhaseDurations(args.load, args.wash, args.elute, args.regen),
        num_columns=args.columns,
    )
    run(schedule=schedule, titer=args.titer, dt=args.dt, save_path=args.save)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_animate.py -q`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/pcc_draw/__main__.py tests/test_animate.py
git commit -m "feat(cli): add argparse entry point — 명령줄 진입점"
```

---

## Task 12: 전체 검증 + GIF 산출 + README 갱신

**Files:**
- Modify: `README.md`
- Create: `docs/demo.gif` (산출물)

- [ ] **Step 1: 전체 테스트 + 린트**

Run: `uv run pytest -q && uv run ruff check .`
Expected: 전체 PASS (18개 내외), ruff clean.

- [ ] **Step 2: GIF 산출 (수동 시각 검증)**

Run: `uv run python -m pcc_draw --save docs/demo.gif`
Expected: 에러 없이 `docs/demo.gif` 생성. 파일을 열어 — 컬럼 4개가 단계 색으로 바뀌고, elute 컬럼→VI 화살표가 켜지고, 하단 간트의 now 선이 스윕하는지 육안 확인.

- [ ] **Step 3: 실시간 창 확인 (수동, 환경 가능 시)**

Run: `uv run python -m pcc_draw`
Expected: 창이 뜨고 애니메이션 재생. space=일시정지, ↑/↓=속도 변경 동작 확인. (헤드리스 환경이면 생략하고 그 사실을 보고)

- [ ] **Step 4: README 실행 섹션 갱신**

`README.md`의 "현재 상태"를 구현 완료로 바꾸고 "요구사항" 아래에 실행 예시 추가:

```markdown
## 실행

```bash
uv sync --extra dev
uv run python -m pcc_draw                 # 실시간 창 (space=정지, ↑/↓=속도)
uv run python -m pcc_draw --save demo.gif # GIF 저장
uv run python -m pcc_draw --titer 2.0 --load 25  # 파라미터 조정
```

![demo](docs/demo.gif)
```

- [ ] **Step 5: PROGRESS.md 갱신 + Commit**

`PROGRESS.md`에 구현 완료 항목 추가 후:

```bash
git add README.md PROGRESS.md docs/demo.gif
git commit -m "docs: add demo gif and run instructions — 데모·실행법 추가"
```

- [ ] **Step 6: 푸시**

```bash
git push
```

---

## Self-Review

**Spec 커버리지:**
- 시간 따라 도는 애니메이션 → Task 10 (run/FuncAnimation). ✅
- 독립 자체 모델 → Task 2–5 (schedule.py, 기존 시뮬레이터 import 없음). ✅
- 실시간 창(matplotlib) + GIF 저장 → Task 10 (plt.show / PillowWriter), Task 12 산출. ✅
- 풀 레이아웃(컬럼+VI+Titer+하단 타임라인+now 선) → Task 7 (process), Task 8 (gantt). ✅
- 겹침/4컬럼 동시 → Task 4 (active_cycles), Task 5 (state_at 컬럼 배정). ✅
- elute→VI 흐름 → Task 7 (eluting 화살표·VI 강조). ✅
- Titer 표시 값(Gompertz 결합 없음) → Task 7 (titer 텍스트), Task 11 (--titer). 모델에 결합 없음. ✅
- 반열림 [start,end) → Task 3. ✅
- 색 단일 출처 → Task 6 (PHASE_COLORS). ✅
- 검증(pytest 모델 + 수동 시각) → Task 2–11 TDD/스모크, Task 12 수동. ✅
- 의존성 matplotlib/pillow, dev 분리 → Task 1. ✅

**플레이스홀더 스캔:** 없음 — 모든 코드 단계에 실제 코드 포함.

**타입 일관성:** `Phase`, `PhaseDurations(load/wash/elute/regen/total/as_list)`, `Schedule(durations/num_columns/cycle_start/phase_at/active_cycles/state_at)`, `ColumnState(column/cycle/phase)`, `build_figure→(fig,ax_process,ax_gantt)`, `draw_process(ax,states,titer)`, `draw_gantt(ax,schedule,t,window_min)`, `render(fig,ax_process,ax_gantt,schedule,t,titer)`, `advance(t,dt,paused)`, `run(schedule,titer,dt,frames,interval,save_path)`, `parse_args/main` — 태스크 간 시그니처 일치 확인. ✅
