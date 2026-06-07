# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

PCC(연속 크로마토그래피) 컬럼 스케줄을 matplotlib 실시간 창에 애니메이션으로 그리는 도구.
Protein A 컬럼 #01~#04가 `LOAD → WASH → ELUTE → REGEN` 단계를 시간에 따라 도는 모습을
깔끔한 공정 다이어그램(컬럼 + VI + Titer + 하단 미니 간트)으로 시각화한다.

순수 Python (matplotlib only). 형제 프로젝트 `PCC_Schedule_simulator`와는 **코드 분리** —
PCC_Draw 안에 단순 자체 스케줄 모델을 둔다 (import·재사용 안 함).

**현재 상태: 설계 완료, 구현 대기.** 설계 문서: `docs/superpowers/specs/2026-06-08-pcc-draw-animation-design.md`.
계층 구조는 `schedule.py`(순수 모델) / `draw.py`(프레임 렌더) / `animate.py`(FuncAnimation 드라이버)로 분리 예정.

## Working Style — 최우선 (모든 룰보다 먼저)

**모든 작업의 행동 기반.** 아래 도메인 룰과 충돌해도 이 가이드의 원칙이 우선한다.

@rules/guidelines.md

---

## Rules — 범용 (유지)

@rules/common/comments.md
@rules/common/naming.md
@rules/common/git.md
@rules/common/security.md
@rules/common/error-handling.md
@rules/common/dependencies.md
@rules/common/documentation.md
@rules/common/testing.md

## Language-Specific Rules

@rules/languages/python.md
