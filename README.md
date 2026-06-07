# 게임 추천 전략 개선을 통한 전환율 상승 실험

## 프로젝트 개요

인기순 추천 방식의 한계를 데이터로 검증하고, 유저 취향 기반 rule-based 추천 로직을 설계하여 A/B 테스트로 비즈니스 임팩트를 측정한 분석 프로젝트입니다.

**핵심 질문**: 추천 방식이 구매 전환율에 유의미한 영향을 주는가?

**데이터**: 50,000개 게임 타이틀 (1985–2026), 35개 변수

---

## 문제 정의

현재 추천 방식(인기순)은 판매량 상위 장르에 노출이 집중됩니다.
분석 결과, 판매량 1위 Sports 장르의 평균 Metacritic 점수는 71.2점으로 최하위권인 반면,
RPG(77.5점)·Adventure(76.6점)는 품질이 높음에도 노출이 낮았습니다.
또한 Metacritic 80점 이상임에도 판매량 5M 미만인 타이틀이 1,486개 존재했습니다.

**가설**: 유저 취향 기반 추천으로 전환율이 상승한다.

---

## 주요 발견

| 분석 항목 | 결과 |
|---|---|
| GOTY 노미네이트 판매 uplift | +93.5% (48.4M vs 25.0M) |
| 온라인 멀티플레이어 판매 프리미엄 | +39.2% (30.2M vs 21.7M) |
| Metacritic–판매량 상관계수 | r = 0.22 (약한 양의 상관) |
| 숨겨진 고품질 미노출 타이틀 | 1,486개 |

평점과 판매량의 상관이 약하다는 점(r=0.22)은 품질 단독으로 추천 로직을 구성하기 어렵다는 근거입니다.
장르·플랫폼·온라인 기능 여부를 복합 변수로 사용하는 rule-based 접근을 채택한 이유입니다.

---

## 추천 로직 설계 (Rule-based)

ML 모델 없이 설명 가능한 3단계 로직으로 구성했습니다.

**Step 1 — 장르 매칭**
유저 최근 구매 장르 내에서 composite_score (Metacritic 70% + user_score 30%) 상위 20% 필터링

**Step 2 — 플랫폼 일치**
유저 보유 플랫폼 기준으로 추가 필터링 후 재정렬

**Step 3 — 숨겨진 보석 삽입**
최종 추천 목록의 10%를 고품질 미노출 타이틀로 교체하여 다양성 확보

rule-based를 선택한 이유는 각 추천 결과에 대해 "왜 이 타이틀을 추천했는가"를 비즈니스 이해관계자에게 명확히 설명할 수 있기 때문입니다.

---

## A/B 테스트 설계

| 항목 | 내용 |
|---|---|
| 대조군 (Control) | 인기순 추천 (기존 방식) |
| 실험군 (Treatment) | 개인화 rule-based 추천 |
| 표본 수 | 각 5,000명 (총 10,000명) |
| 유의수준 | α = 0.05 |
| CVR 검정 | Chi-squared test |
| ARPU 검정 | Welch t-test |
| 주요 KPI | CTR, CVR, ARPU |

---

## 실험 결과

| KPI | Control | Treatment | Lift | p-value |
|---|---|---|---|---|
| CVR | 2.91% | 4.04% | +38.8% | < 0.0001 |
| ARPU | $2.10 | $2.57 | +22.4% | < 0.0001 |

두 지표 모두 통계적으로 유의미합니다 (p < 0.05).
CVR 기준 uplift +38.8%는 전체 트래픽 적용 시 연간 매출 20% 이상 상승으로 추정됩니다.

---

## 액션 아이템

1. **개인화 추천 전면 도입**: A/B 테스트 결과를 근거로 전체 유저에 Treatment 로직 적용
2. **RPG·Adventure 세그먼트 타겟팅**: 고품질 대비 저노출 장르 유저에게 집중 추천 및 프로모션 연동
3. **숨겨진 보석 효과 측정 실험 확장**: inject_ratio 0.1 → 0.2 구간 추가 실험 설계, 재구매율 및 롱테일 매출 기여도 추적

---

## 폴더 구조

```
game-recommendation-ab-test/
├── data/
│   ├── raw/                  
│   └── processed/            
├── notebooks/
│   ├── 01_eda.ipynb          
│   ├── 02_recommendation_logic.ipynb
│   └── 03_ab_test.ipynb
├── src/
│   ├── preprocess.py         
│   ├── recommender.py        
│   └── ab_test.py           
├── outputs/
│   └── figures/             
└── requirements.txt
```

---

## 기술 스택

- **언어**: Python 3.11
- **분석**: Pandas, NumPy
- **시각화**: Matplotlib, Seaborn
- **통계 검정**: SciPy (chi2_contingency, ttest_ind)
- **환경**: Jupyter Notebook

---

## 실행 방법

```bash
pip install -r requirements.txt
```

notebooks 폴더 내 01 → 02 → 03 순서로 실행합니다.
01_eda.ipynb 실행 시 `data/processed/` 하위 파일이 자동 생성됩니다.
