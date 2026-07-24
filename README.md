# Healing Trip Gyeonggi

경기도 **템플스테이 · 자연관광 · 공연(문화행사)** 정보를 한곳에서 살펴보는 웹 서비스입니다.

공공 Open API 데이터를 FastAPI 서버가 수집·정제한 뒤 SQLite에 저장하고, React 프론트엔드는 **백엔드 API만** 호출합니다.

- 기획 문서: [`docs/PRD.md`](docs/PRD.md)
- 작업 목록: [`docs/TASKS.md`](docs/TASKS.md)

---

## 주요 기능

- **템플스테이**: 목록·상세, 지역/예약가능일 검색, 지도, 사찰별 SNS·체험 프로그램·소개/안내/시설/갤러리/후기
- **자연관광**: 경기도 관광지·단지·가이드북, 목록·상세, 지도
- **공연**: 경기도 문화행사(2026 기준 필터), 목록·상세, 지도
- **통합 검색**: 홈에서 사찰·관광·공연 키워드 검색
- **주변 추천**: 템플스테이 상세에서 인근 자연관광 추천

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | React 18, Vite, React Router |
| Backend | FastAPI, SQLAlchemy, SQLite |
| 환경 | conda (`youthhub`) |
| 데이터 | 경기도 Open API (템플스테이, 관광지, 문화행사), odcloud 가이드북 |

---

## 폴더 구조

```
├── backend/          # FastAPI + SQLite
├── frontend/         # React (Vite)
├── docs/             # PRD, TASKS, API 메모
└── README.md
```

---

## 사전 준비

1. **conda 환경** `youthhub` 사용 (새 venv를 만들지 않습니다)
2. **Node.js** (프론트 `npm` 실행용)
3. `backend/.env`에 API 키 설정 (코드에 하드코딩하지 않음)

`backend/.env` 예시:

```env
TEMPLESTAY_API_KEY=발급받은_키
TEMPLESTAY_BASE_URL=https://openapi.gg.go.kr/Templestay

TOURRESORT_API_KEY=발급받은_키
TOURRESORT_BASE_URL=https://openapi.gg.go.kr/TouristResort

TOURGUIDE_API_KEY=발급받은_키
TOURGUIDE_BASE_URL=https://api.odcloud.kr/api/15123631/v1/uddi:33264f0a-158f-4a5d-95cd-99c740c8a097

CONCERT_API_KEY=발급받은_키
CONCERT_BASE_URL=https://openapi.gg.go.kr/Ggculturevent

DATABASE_URL=sqlite:///./app.db
```

API 명세 메모는 `docs/api_templestay.md`, `docs/api_tourguide2.md`, `docs/api_concert.md` 등을 참고하세요.

---

## 실행 방법

백엔드는 **8001** 포트, 프론트는 Vite 기본 **5173** 포트를 사용합니다.  
(`frontend/src/api.js`의 `BASE_URL`이 `http://127.0.0.1:8001`입니다.)

### 1) 백엔드

```bash
conda activate youthhub
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

- Health: http://127.0.0.1:8001/health
- OpenAPI 문서: http://127.0.0.1:8001/docs

### 2) 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

- 접속 주소: **http://localhost:5173/Healing_Trip_Gyeonggi/**

> Vite `base`와 React Router `basename`이 `/Healing_Trip_Gyeonggi` 로 설정되어 있습니다.  
> 루트(`http://localhost:5173/`)가 아니라 위 경로로 접속해야 합니다.

---

## 데이터 동기화

최초 실행 또는 데이터 갱신 시 백엔드 sync API를 호출합니다.

```bash
# 템플스테이
curl -X POST http://127.0.0.1:8001/temples/sync

# 자연관광
curl -X POST http://127.0.0.1:8001/attractions/sync

# 공연·문화행사
curl -X POST http://127.0.0.1:8001/concerts/sync
```

프론트 **공연** 탭의 「공연 데이터 동기화」 버튼으로도 공연 sync가 가능합니다.

---

## 주요 API (요약)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 |
| GET | `/temples` | 템플스테이 목록 (`q`, `region`, `date`) |
| GET | `/temples/{id}` | 템플스테이 상세 |
| GET | `/temples/{id}/nearby` | 주변 관광지 |
| GET | `/attractions` | 자연관광 목록 |
| GET | `/concerts` | 공연 목록 (2026 기준 필터) |
| GET | `/search` | 통합 검색 |
| POST | `/temples/sync` 등 | 공공데이터 동기화 |

전체 스키마는 http://127.0.0.1:8001/docs 에서 확인할 수 있습니다.

---

## 아키텍처 규칙

- 프론트엔드는 **공공 Open API를 직접 호출하지 않습니다.**
- FastAPI가 공공 API를 호출 → 정제 → SQLite 저장 → 프론트에 제공합니다.
- 비밀값(API 키)은 `backend/.env`에만 둡니다. `.env`는 커밋하지 마세요.

---

## 라이선스 / 데이터 출처

- 경기도 공공데이터 Open API (템플스테이, 관광지, 문화행사)
- 공공데이터포털(odcloud) 여행 가이드북 데이터

서비스·데이터 이용 시 각 제공 기관의 이용약관을 따릅니다.
