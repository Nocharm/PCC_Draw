"""렌더 스모크 테스트 — Agg 백엔드(창 없음), 예외·핵심 아티팩트만 확인."""
import matplotlib

matplotlib.use("Agg")  # GUI 없이 렌더 (pyplot import 전 설정)

from pcc_draw.draw import PHASE_COLORS, build_figure, draw_gantt, draw_process, render
from pcc_draw.schedule import ColumnState, Phase, PhaseDurations, Schedule


def test_phase_colors_cover_all_phases():
    assert set(PHASE_COLORS) == set(Phase)


def test_build_figure_returns_two_axes():
    fig, ax_process, ax_gantt = build_figure()
    assert fig is not None
    assert ax_process is not ax_gantt
    assert len(fig.axes) == 2


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


def test_draw_gantt_draws_now_line_and_phase_bands():
    fig, _, ax_gantt = build_figure()
    s = Schedule(PhaseDurations())
    draw_gantt(ax_gantt, s, t=200.0)
    # phase 띠 패치가 다수 + now 세로선 1개 이상
    assert len(ax_gantt.patches) > 4
    assert len(ax_gantt.lines) >= 1


def test_render_populates_both_axes():
    fig, ax_process, ax_gantt = build_figure()
    s = Schedule(PhaseDurations())
    render(fig, ax_process, ax_gantt, s, t=200.0, titer=1.52)
    assert len(ax_process.patches) >= 5   # 컬럼 + VI
    assert len(ax_gantt.lines) >= 1        # now 선
    assert len(ax_gantt.patches) > 4    # 간트 phase 띠
