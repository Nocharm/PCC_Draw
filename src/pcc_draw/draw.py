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
