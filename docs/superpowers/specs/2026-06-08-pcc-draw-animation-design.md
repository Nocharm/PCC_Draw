# PCC_Draw — 애니메이션 설계 문서

작성일: 2026-06-08
상태: 승인됨 (구현 계획 단계로 진행)

## 목표

자체 PCC(연속 크로마토그래피) 스케줄 모델을 시간 축으로 돌려, Protein A 컬럼
#01~#04가 `LOAD → WASH → ELUTE → REGEN` 단계를 도는 모습을 matplotlib 실시간
창에 깔끔한 다이어그램으로 그린다.

- 출력: 시간에 따라 단계가 도는 **애니메이션** (실시간 창, 선택적 GIF/MP4 저장).
- 데이터: 기존 `PCC_Schedule_simulator`와 **코드 분리** — PCC_Draw 안에 단순 자체 모델을 둔다.
- 스타일: **깔끔한 다이어그램**(손그림 질감 모사 안 함). 참조: Obsidian Excalidraw `for PCC.md`
  (Pro A columns #01~#04 / PCC / VI / Titer / RT·VVD 라벨).
- 제약: Python only.

## 비목표 (YAGNI)

- 기존 시뮬레이터 import·재사용. (완전 독립)
- titer → load_duration(Gompertz) 결합. (titer는 표시 값으로만 시작 — 아래 "결정" 참조)
- 손그림(rough.js류) 질감.
- 회귀/예측/SQLite/실측 비교.

## 아키텍처

순수 모델은 테스트 가능하게 분리하고, 렌더·애니메이션은 얇게 얹는다.

```
src/pcc_draw/
├── schedule.py   # 순수 모델: Phase, 고정 길이, 사이클 타임라인, state_at(t)
├── draw.py       # 한 프레임 렌더: 모델 상태 → matplotlib 도형 (컬럼/VI/Titer/타임라인)
├── animate.py    # FuncAnimation 드라이버: t 전진, 재생/일시정지/속도, --save GIF/MP4
└── __main__.py   # python -m pcc_draw 진입점 (argparse)
tests/            # schedule.py 단위 테스트
```

### 계층 책임

- **schedule.py (matplotlib 무관, 순수 함수):**
  - `Phase`(LOAD/WASH/ELUTE/REGEN) + 고정 길이 설정.
  - 사이클 타임라인 빌드(겹침 포함).
  - `state_at(t)` → 각 컬럼의 현재 단계 + 지금 elute 중(=VI로 흐름)인 컬럼을 담은 결정적 구조 반환.
  - 단계 구간은 반열림 `[start, end)` (경계 시각은 다음 단계 소유).
- **draw.py:** 모델 상태 1개 → 프레임 1장. 입력만 받아 그린다. matplotlib 외 의존 없음.
- **animate.py:** 시간을 전진시키며 `draw` 호출. 키 입력으로 재생/일시정지/속도 조절,
  `--save out.gif`면 파일로 출력.
- **색 단일 출처:** `PHASE_COLORS = {LOAD, WASH, ELUTE, REGEN}` 한 곳에 정의, draw와 타임라인이 공유.

## 모델 (자체, 단순 — PCC의 핵심 "겹침"은 보존)

- 4단계 **고정 길이**(설정 가능). 기본값: LOAD 30 / WASH 20 / ELUTE 40 / REGEN 30분
  → 사이클 총 120분.
- **위상 간격 = load_duration(30분).** 사이클 총길이(120) > 간격(30)이므로 사이클이 시간상
  **겹친다** → 한 시점에 4개 컬럼이 서로 다른 단계에 동시 존재. 사이클을 #01~#04에 라운드로빈 배정.
  이 겹침이 PCC다운 계단식 움직임의 근거이며, "동시 활성 사이클 수 = 필요 컬럼 수"를 화면으로 보여준다.
- 단계 구간은 반열림 `[start, end)`.

## 화면 레이아웃 (풀 — Excalidraw에 가장 근접)

- **상단:** 컬럼 4개 박스(현재 단계 색) + 우측 **Titer 패널**(값 표시) + elute 중인 컬럼에서
  **VI** 박스로 가는 **흐름 화살표**(elute 중일 때 강조).
- **하단:** **미니 간트** — 컬럼별 단계 색 띠 + 스윕하는 **now 세로선**.
- 상·하단이 같은 `now`(현재 시각)를 공유해, 한 수직선에서 "그 시각 어느 컬럼이 어느 단계"가 읽힌다.

```
  Pro A columns        Titer: 1.52
  ┌─┐┌─┐┌─┐┌─┐    RT/VVD/Titer
  │01││02││03││04│
  │LD││WS││EL││RG│ → ┌───┐
  └─┘└─┘└─┘└─┘     │VI │
  ──────────────    └───┘
  #01 ▓▓░░▒▒██
  #02   ▓▓░░▒▒██
  #03     ▓▓░░▒▒
   ▲ now = 04:12
```

## 결정 — Titer의 역할

**Titer는 패널에 표시만 하는 값**(설정 상수)으로 시작한다. 기존 도메인의
"titer → load_duration(Gompertz)" 결합은 넣지 않는다 ("완전 독립·깔끔" 선택과 YAGNI에 따름).
나중에 "titer를 바꾸면 load 길이/컬럼 점유가 변하는 것까지 보고 싶다"는 요구가 생기면,
모델에 단순 단조 결합을 추가하는 가역적 확장으로 처리한다.

## 검증

- **모델 (자동, pytest):**
  - `state_at` 단계 경계 — 반열림 `[start, end)`가 경계 시각을 올바른 단계에 귀속.
  - 겹침 — 정상 상태에서 동시 활성 컬럼 4개.
  - elute → VI 판정 — elute 중인 컬럼을 정확히 식별.
- **시각 (수동):** 자동 검증 불가. 창 실행 / GIF 저장 후 육안 확인. 실제 실행 명령과 관찰 결과를 보고한다.

## 의존성

- 런타임: `matplotlib`만. GIF 저장 시 `pillow`.
- 개발: `pytest`, `ruff` (dev 분리).
- 금지(불필요): 기존 시뮬레이터, pandas, plotly, scipy, numpy(필요 시 재검토).

## 프로젝트 셋업

- `pyproject.toml` + `src/pcc_draw/` (src 레이아웃) + `tests/`. 형제 프로젝트(`PCC_Schedule_simulator`)
  컨벤션과 정렬: uv 관리, `pythonpath = ["src"]`.
- 루트 `README.md` 템플릿 플레이스홀더를 이 프로젝트 설명으로 교체.
