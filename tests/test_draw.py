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
