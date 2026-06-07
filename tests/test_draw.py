"""렌더 스모크 테스트 — Agg 백엔드(창 없음), 예외·핵심 아티팩트만 확인."""
import matplotlib

matplotlib.use("Agg")  # GUI 없이 렌더 (pyplot import 전 설정)

from pcc_draw.draw import PHASE_COLORS, build_figure, draw_process
from pcc_draw.schedule import ColumnState, Phase


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
