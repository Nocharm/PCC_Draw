"""애니메이션 순수 헬퍼 + CLI 파싱 테스트."""
import matplotlib

matplotlib.use("Agg")

from pcc_draw.animate import advance


def test_advance_moves_time_by_dt_when_running():
    assert advance(100.0, 2.0, paused=False) == 102.0


def test_advance_holds_time_when_paused():
    assert advance(100.0, 2.0, paused=True) == 100.0
