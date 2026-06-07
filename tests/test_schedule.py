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
