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
    p.add_argument("--save", default=None,
                   help="GIF 저장 경로 (생략 시 실시간 창)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    schedule = Schedule(
        PhaseDurations(args.load, args.wash, args.elute, args.regen),
        num_columns=args.columns,
    )
    if schedule.num_columns < schedule.required_columns:
        raise SystemExit(
            f"--columns {schedule.num_columns} < 필요 컬럼 {schedule.required_columns}개: "
            "동시 활성 사이클이 누락됩니다. --columns를 늘리거나 단계 길이를 조정하세요."
        )
    run(schedule=schedule, titer=args.titer, dt=args.dt, save_path=args.save)


if __name__ == "__main__":
    main()
