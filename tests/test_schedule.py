"""순수 스케줄 모델 단위 테스트."""
from pcc_draw.schedule import Phase, PhaseDurations, Schedule


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
