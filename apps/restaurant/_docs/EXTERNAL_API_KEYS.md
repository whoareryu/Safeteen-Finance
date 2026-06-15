# GourmetMate — 외부 API 키 (직접 발급 필요)

백엔드 `backend/.env` 에 넣을 환경 변수입니다.  
**내부 API**(카테고리·메뉴·주변·검색 제안·`/gourmet/chat` 맥락)는 DB만으로 동작하고, 아래 키는 **데이터 보강·날씨·고품질 AI** 용입니다.

---

## 이미 쓰는 키

| 변수 | 용도 | 발급 |
|------|------|------|
| `DATABASE_URL` | Neon PostgreSQL | [Neon](https://neon.tech) 콘솔 Connection string |
| `GEMINI_API_KEY` | `POST /gourmet/chat`, `POST /chat` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `RESTAURANTS_CSV` | 소상공인 음식 CSV → `restaurants` 적재 | 파일 경로만 (API 키 없음) |

---

## 보강·배치용 (추가 권장)

| 변수 | 용도 | 발급처 | 비고 |
|------|------|--------|------|
| `KAKAO_REST_API_KEY` | 매장 전화·URL·좌표 보정 | [Kakao Developers](https://developers.kakao.com) → 앱 → **REST API 키** | **JavaScript 키 넣으면 401** (`KA Header is required`) |
| `LOCALDATA_API_URL` | 공공데이터포털 **요청 URL** (필수) | 활용신청 상세의 엔드포인트 | `?serviceKey=` 는 코드가 붙임 |
| `LOCALDATA_API_KEY` | 위 URL용 인증키 | 공공데이터포털 일반 인증키 | 구 `localdata.go.kr` 직접 API는 종료(code 999) |
| `OPENWEATHER_API_KEY` | 헤더 날씨 (`GET /weather`) | [OpenWeatherMap](https://openweathermap.org/api) | **`backend/.env`만** — Next는 rewrite로 백엔드 호출 |
| `OPENWEATHER_CITY` | 위치 거부 시 기본 도시 | — | 기본값 `Seoul` |
| `LOCALDATA_BASE_URL` | (선택) 구 API만 | — | `LOCALDATA_API_URL` 없을 때만 시도 |

---

## 선택 (상권·지도)

| 변수 | 용도 | 발급처 |
|------|------|--------|
| `SBIZ_API_KEY` | 소상공인 **상권정보 API** (실시간) | 공공데이터포털 소상공인시장진흥공단 API |
| `NAVER_MAP_CLIENT_ID` / `NAVER_MAP_CLIENT_SECRET` | 지도·길찾기 링크 | [네이버 클라우드 Maps](https://www.ncloud.com/product/applicationService/maps) |

> **권장:** 서울 13만 건 전수는 **CSV + 배치**(`import_restaurants_from_csv.py`). 상권 API는 **주변 상권·보완**용으로만.

---

## 키 없이 동작하는 내부 API (이번에 추가)

| 메서드 | 경로 |
|--------|------|
| GET | `/gourmet/categories` |
| GET | `/gourmet/restaurants/{id}/menus` |
| GET | `/gourmet/topics/{topic_slug}/restaurants` |
| GET | `/gourmet/nearby?lat=&lng=` |
| GET | `/gourmet/search/suggest?q=` |
| POST | `/gourmet/chat` (맥락 RAG — **Gemini 키 필요**) |
| GET | `/gourmet/restaurants/{id}/enrichment` (소스 설정 상태만, 외부 호출 전) |
| GET | `/auth/me` (`X-User-Id` 헤더) |

즐겨찾기·식비: `X-User-Id: {users.id}` 헤더 (localStorage 로그인 사용자).

---

## `.env` 예시 (`backend/.env.example` 복사)

```env
GEMINI_API_KEY=your_gemini_api_key
KAKAO_REST_API_KEY=your_kakao_rest_api_key
LOCALDATA_API_KEY=your_localdata_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
OPENWEATHER_CITY=Seoul
```

- **날씨:** 프론트 `frontend/.env.local` 에 있던 `OPENWEATHER_API_KEY` 는 **`backend/.env`로 옮기세요.**
- **보강:** `GET /gourmet/restaurants/{id}/enrichment` 호출 시 Kakao·LOCALDATA 키가 있으면 실시간 조회합니다.

적용 후: `cd backend` → 서버 재시작. 프론트는 `BACKEND_URL` 만 있으면 됩니다.

---

## 관련 문서

[[whoareryu/_claude/CLAUDE\|Backend CLAUDE]] · [[GOURMET_ERD]] · [[gourmetmate_v2_erd]]
