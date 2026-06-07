"""모델 상태를 받아 한 프레임을 그리는 렌더러. 색은 PHASE_COLORS 단일 출처."""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from pcc_draw.schedule import ColumnState, Phase, Schedule

PHASE_COLORS: dict[Phase, str] = {
    Phase.LOAD: "#4C9F70",   # green
    Phase.WASH: "#F0C808",   # yellow
    Phase.ELUTE: "#DD6E42",  # orange
    Phase.REGEN: "#5B8DEF",  # blue
}
IDLE_COLOR: str = "#E0E0E0"
NOW_LINE_COLOR: str = "#2CA02C"  # now 세로선 (초록)


def build_figure() -> tuple[Figure, plt.Axes, plt.Axes]:
    """상단 공정 패널 + 하단 간트 패널, 시간축 의미 공유."""
    fig, (ax_process, ax_gantt) = plt.subplots(
        2, 1, figsize=(10, 6), gridspec_kw={"height_ratios": [3, 2]}
    )
    return fig, ax_process, ax_gantt


def draw_process(ax: plt.Axes, states: list[ColumnState], titer: float) -> None:
    """상단 패널: 컬럼 박스(단계 색) + VI + Titer + elute→VI 화살표. xlim은 컬럼 수에 맞춰 동적."""
    ax.clear()
    box_w, box_h, gap, y0 = 1.4, 2.0, 0.4, 1.0
    n = len(states)
    vi_x = 0.5 + n * (box_w + gap) + 0.3
    x_right = vi_x + 1.0 + 0.7  # VI 박스 너비(1.0) + 우측 여백
    ax.set_xlim(0, x_right)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("PCC — Pro A columns", loc="left")

    for st in states:
        x0 = 0.5 + st.column * (box_w + gap)
        color = PHASE_COLORS[st.phase] if st.phase else IDLE_COLOR
        ax.add_patch(Rectangle((x0, y0), box_w, box_h,
                               facecolor=color, edgecolor="black", lw=1.5))
        ax.text(x0 + box_w / 2, y0 + box_h - 0.3, f"#{st.column + 1:02d}",
                ha="center", va="top", fontweight="bold")
        ax.text(x0 + box_w / 2, y0 + 0.3, st.phase.value if st.phase else "idle",
                ha="center", va="bottom")

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

    ax.text(x_right - 0.2, 3.7, f"Titer: {titer:.2f}", ha="right", va="top", fontsize=11,
            bbox=dict(boxstyle="round", fc="white", ec="gray"))


def draw_gantt(ax: plt.Axes, schedule: Schedule, t: float,
               window_min: float = 180.0) -> None:
    """하단 패널: 컬럼별 단계 색 띠 + now 세로선. now는 창의 60% 지점."""
    ax.clear()
    t0 = t - window_min * 0.6
    t1 = t + window_min * 0.4
    ax.set_xlim(t0, t1)
    ax.set_ylim(-0.5, schedule.num_columns - 0.5)
    ax.set_yticks(range(schedule.num_columns))
    ax.set_yticklabels([f"#{i + 1:02d}" for i in range(schedule.num_columns)])
    ax.set_xlabel("time (min)")
    ax.set_title("timeline", loc="left")

    load = schedule.durations.load
    total = schedule.durations.total
    # 후보 하한: bar 끝(start+total)이 t0 이후인 사이클만 창에 보일 수 있음
    lo = max(0, int((t0 - total) // load))
    hi = int(t1 // load)
    for cyc in range(lo, hi + 1):
        row = cyc % schedule.num_columns
        acc = schedule.cycle_start(cyc)
        for phase, dur in schedule.durations.as_list():
            ax.add_patch(Rectangle((acc, row - 0.3), dur, 0.6,
                                   facecolor=PHASE_COLORS[phase], edgecolor="none"))
            acc += dur

    ax.axvline(t, color=NOW_LINE_COLOR, lw=2)  # now 세로선


def render(fig: Figure, ax_process: plt.Axes, ax_gantt: plt.Axes,
           schedule: Schedule, t: float, titer: float) -> None:
    """한 프레임: 모델 상태 조회 → 두 패널 렌더."""
    states = schedule.state_at(t)
    draw_process(ax_process, states, titer)
    draw_gantt(ax_gantt, schedule, t)
    fig.tight_layout()
