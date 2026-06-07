"""애니메이션 순수 헬퍼 + CLI 파싱 테스트."""
import matplotlib

matplotlib.use("Agg")

from pcc_draw.animate import advance


def test_advance_moves_time_by_dt_when_running():
    assert advance(100.0, 2.0, paused=False) == 102.0


def test_advance_holds_time_when_paused():
    assert advance(100.0, 2.0, paused=True) == 100.0


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
