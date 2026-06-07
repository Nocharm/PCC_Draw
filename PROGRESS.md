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
