# Progress

프로젝트 진행 현황 로그. 커밋 직전 갱신한다 (`rules/common/git.md` 규칙).

## 설계: PCC_Draw 애니메이션 (브레인스토밍 완료)

- **무엇**: 자체 PCC 스케줄 모델을 matplotlib 실시간 창에 애니메이션으로 그리는
  프로젝트의 설계 문서 작성 (`docs/superpowers/specs/2026-06-08-pcc-draw-animation-design.md`).
- **왜**: Excalidraw `for PCC.md` 느낌의 공정 다이어그램으로 컬럼 #01~#04의 단계 순환을
  시각화. 기존 `PCC_Schedule_simulator`와는 코드 분리(완전 독립 자체 모델).
- **결정**: 실시간 창(matplotlib FuncAnimation) / 풀 레이아웃(컬럼+VI+Titer+하단 타임라인) /
  깔끔한 다이어그램 / titer는 표시 값으로만 시작(Gompertz 결합 미구현, YAGNI).
- **다음**: 구현 계획(writing-plans) 작성.

## 템플릿 셋업 정리 + 공개 리포 초기화

- **무엇**: CLAUDE.md에 Project 섹션 추가 + 미사용 import(백엔드/Docker 블록, TypeScript) 제거,
  고아 rule 파일(`rules/backend/`, `rules/languages/typescript.md`)·템플릿 메타 문서(`docs/template/`) 삭제,
  README 플레이스홀더를 실제 프로젝트 설명으로 교체.
- **왜**: Python 전용 matplotlib 프로젝트라 백엔드/TS 룰이 불필요하고, 공개 리포에 템플릿 잔재·플레이스홀더를
  남기지 않기 위함 (문서화·setup-from-template 룰).

## 구현 계획 작성 (writing-plans)

- **무엇**: 12개 태스크의 TDD 구현 계획 작성 (`docs/superpowers/plans/2026-06-08-pcc-draw-animation.md`).
  schedule(모델, TDD) → draw(렌더, Agg 스모크) → animate(드라이버) → CLI → 검증/GIF/README.
- **왜**: 승인된 설계를 바이트사이즈 태스크로 분해해 task-by-task 구현·검증하기 위함.
- **다음**: 구현 실행 (subagent-driven 또는 inline).

## PCC_Draw 애니메이션 구현 완료 (Tasks 1–12)

- **무엇**: `src/pcc_draw/` 패키지 전체 구현 — `schedule.py`(순수 모델), `draw.py`(한 프레임 렌더),
  `animate.py`(FuncAnimation 드라이버), `__main__.py`(CLI). `docs/demo.gif` 데모 생성.
- **왜**: 설계 문서(`2026-06-08-pcc-draw-animation-design.md`)를 바탕으로 PCC 컬럼 4개의
  계단식 순환을 실시간 창 + GIF로 시각화하기 위함.
- **검증**: `uv run pytest -q` → 22 passed, `uv run ruff check .` → All checks passed.
  헤드리스 렌더 확인(process patches=5, gantt patches=40, gantt lines=1). demo.gif = 1.7 MB.
