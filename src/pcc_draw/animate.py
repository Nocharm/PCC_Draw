"""FuncAnimation 드라이버 — 시간을 전진시키며 프레임을 렌더. 키: space=정지, ↑/↓=속도."""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from pcc_draw.draw import build_figure, render
from pcc_draw.schedule import PhaseDurations, Schedule

_SPEED_FACTOR = 1.5  # ↑/↓ 키 1회당 속도 배율


def advance(t: float, dt: float, paused: bool) -> float:
    """정지 중이면 시각 유지, 아니면 dt만큼 전진. (순수 함수, 테스트용)"""
    return t if paused else t + dt


def run(schedule: Schedule | None = None, titer: float = 1.52, dt: float = 2.0,
        frames: int = 600, interval: int = 50, save_path: str | None = None) -> FuncAnimation:
    """실시간 창 표시(save_path 없음) 또는 GIF 저장. interval[ms]."""
    schedule = schedule or Schedule(PhaseDurations())
    fig, ax_process, ax_gantt = build_figure()
    sim = {"t": 0.0, "dt": dt, "paused": False}

    def update(_frame):
        sim["t"] = advance(sim["t"], sim["dt"], sim["paused"])
        render(fig, ax_process, ax_gantt, schedule, sim["t"], titer)

    anim = FuncAnimation(fig, update, frames=frames, interval=interval, repeat=True)

    def on_key(event):
        if event.key == " ":
            sim["paused"] = not sim["paused"]
        elif event.key == "up":
            sim["dt"] *= _SPEED_FACTOR
        elif event.key == "down":
            sim["dt"] /= _SPEED_FACTOR

    fig.canvas.mpl_connect("key_press_event", on_key)

    if save_path:
        # interval >= 1000ms면 fps=0 → PillowWriter 예외, 최소 1 보장
        anim.save(save_path, writer=PillowWriter(fps=max(1, 1000 // interval)))
    else:
        plt.show()
    return anim
