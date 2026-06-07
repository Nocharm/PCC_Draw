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
