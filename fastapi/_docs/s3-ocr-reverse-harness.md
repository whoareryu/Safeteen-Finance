# 영수증 OCR 자동화 파이프라인 — 리버스 하네스 (사전 조정판)

> 이 문서는 그린필드 전제(S3 Presigned URL + Lambda/SQS 이벤트 파이프라인 + WebSocket 브로드캐스트)로
> 작성된 원본 스펙을, **이 저장소에 이미 존재하는 인프라·컨벤션**에 맞춰 다시 쓴 것이다.
> [[fastapi/_docs/flutter-kakao-oauth-harness\|카카오 로그인 하네스]]와 달리 아직 구현되지 않았으므로
> "이렇게 만들어져 있다"가 아니라 "이렇게 조정해야 한다" + **아직 열려 있는 결정**을 함께 남긴다.
> 구현 전에 반드시 §6의 미결정 사항을 확정해야 한다 — 가정으로 채우지 않는다.

---

## 1. 원본 스펙과 실제 인프라가 충돌하는 지점

| 원본 스펙 | 이 프로젝트의 실제 상태 |
|---|---|
| S3 Presigned PUT URL 발급 | 존재하지 않음 — 기존 업로드는 **클라이언트→백엔드 멀티파트→백엔드가 `put_object`로 S3 적재** 방식뿐 (`admin`/`plant`) |
| S3 ObjectCreated Event → SQS/Lambda 핸들러 | **AWS Lambda를 전혀 쓰지 않는다.** 배포는 Docker Compose(EC2) + Cloudflare Tunnel뿐 — Lambda 핸들러라는 실행 단위 자체가 이 인프라에 없다 |
| OCR Provider (Clova/Textract/Vision 중 택1) | 이 프로젝트에 OCR 전용 어댑터가 **하나도 없다.** 다만 `GEMINI_API_KEY`/`google.genai`가 이미 전역 AI 백본이고, `apps/ontology`가 이미지 분류·객체 탐지·Gemini 비전(`vision_use_case.py`) 허브 포트를 갖고 있다 |
| WebSocket/SSE Gateway | 이 코드베이스 어디에도 WebSocket·SSE 구현이 없다 — 완전히 새로 만들어야 한다 |

---

## 2. 재사용 가능한 기존 자산

### 2.1 S3 업로드 — 이미 배선된 허브 패턴

`apps/ontology`(허브)가 이미 S3 저장을 포트/어댑터로 캡슐화해 두 개의 스포크(`admin`, `plant`)에 공급 중이다.

```
ontology/app/ports/output/image_storage_gateway.py   # ImageStorageGateway(ABC).save(filename, content_type, data) -> url
ontology/adapter/outbound/s3/s3_image_storage_gateway.py  # boto3 put_object 구현체, prefix로 스포크 구분
ontology/dependencies/image_storage_provider.py       # get_admin_image_storage_gateway() 등 스포크별 provider
core/infra/s3_manager.py                             # 저수준 boto3 클라이언트 (secret_manager 경유 자격 증명)
```

새 스포크(영수증)가 S3에 이미지를 올려야 한다면 **`S3ImageStorageGateway`나 `ImageStorageGateway` 포트를 새로 만들지 않는다** — [[s3-bucket-pending\|기존 메모]]가 확인한 패턴 그대로, `image_storage_provider.py`에 그 스포크 전용 provider 함수(자기 bucket/prefix)만 추가하면 된다.

### 2.2 텍스트 추출 포트 패턴 — `admin/pdf_text_extractor_port.py`

OCR 결과 파싱과 개념적으로 가장 가까운 기존 코드는 `apps/admin/app/ports/output/pdf_text_extractor_port.py`(PDF 텍스트 추출)다. "외부 문서 처리 엔진 → 구조화 데이터" 포트를 어떻게 얇게 자르는지 참고할 레퍼런스로 쓴다.

### 2.3 외부 이벤트 수신 패턴 — Gmail 파이프라인

원본 스펙의 "S3 Event Webhook"에 가장 가까운 기존 선례는 **Gmail Push→Pub/Sub→Cloudflare Tunnel→n8n→FastAPI** 파이프라인이다(`[[gmail-pipeline\|메모]]` 참고). 이 프로젝트에서 "외부 클라우드 이벤트를 백엔드로 들여오는" 유일한 실제 패턴은 **공인 도메인(Cloudflare Tunnel)으로 노출된 HTTP 웹훅 엔드포인트**다 — Lambda 실행 단위가 아니다.

---

## 3. 조정된 아키텍처 — 스타 토폴로지 배치

영수증 도메인은 `titanic`/`restaurant`/`plant`와 동급인 **신규 스포크(`apps/receipt`)**로 둔다. 스포크→스포크 직접 참조는 금지이므로, OCR·S3 저장은 반드시 `ontology`(허브)의 포트를 경유한다.

```
         [ontology] ← Hub (image_storage_gateway, 신규: ocr_gateway 포트 후보)
        /      |
 [...] [receipt] ← 신규 Spoke
```

- `receipt`가 `ontology`의 `ImageStorageGateway`(기존)와 신규 `ReceiptOcrGateway`(output port, 허브에 신설) 인터페이스만 import한다.
- `ReceiptOcrGateway`의 구현체(Gemini든 Clova든)는 `ontology/adapter/outbound/`에 두고, `ontology/dependencies/`에서 조립해 `receipt`에 공급한다 — §2.1과 동일한 배선 원칙.

---

## 4. Phase별 조정

### 4.1 Inbound — Presigned URL 발급 (신규, 결정 필요)

`POST /api/receipt/presigned-url` 자체는 새로 만들어야 한다(기존 업로드 라우터는 전부 멀티파트 통과형이라 재사용 불가). 다만 **이 프로젝트에 처음 도입되는 패턴**이므로 아래 중 하나를 확정해야 한다:

- **(A) 원안 그대로 Presigned PUT** — 클라이언트가 S3에 직접 업로드, 백엔드는 URL 발급만. 대용량 이미지에 유리하지만 이 저장소에 선례가 없다.
- **(B) 기존 관성 유지 — 멀티파트 통과형** — `admin/s3_image_upload_router.py`와 동일하게 백엔드가 파일을 받아 `put_object`. 새 패턴을 안 늘리는 대신 대용량 파일에서 백엔드 대역폭을 씀.

키 경로(`receipts/{userId}/{timestamp}_{filename}`)는 원안 그대로 유지 가능 — `S3ImageStorageGateway`의 `prefix` 파라미터로 표현하되, `{userId}`/`{timestamp}` 세그먼트를 넣으려면 현재 구현(`{prefix}/{uuid4().hex}.{ext}`, 사용자 미분리)을 확장해야 한다.

### 4.2 Hub Processing — S3 Event 처리 (신규, 결정 필요)

Lambda/SQS 핸들러 대신 이 프로젝트 인프라에서 실제로 가능한 두 경로:

- **(A) S3 Event Notification → SNS → HTTPS 구독 → `api.whoareryu.cloud` 웹훅** — Gmail 파이프라인과 동형. AWS 쪽에 SNS 토픽 설정이 추가로 필요하다.
- **(B) 이벤트 없이 (A) 자체를 스킵 — presigned 업로드 완료 후 클라이언트가 직접 `POST /api/receipt/{id}/process` 호출** — 인프라 추가 없이 가장 단순하지만 "S3가 진실의 원천"이라는 원안의 허브 패턴을 포기하는 것.

`ProcessReceiptOCR` 유스케이스 자체(S3에서 이미지 스트림 fetch → OCR → 파싱 → DB 저장)는 트리거 방식과 무관하게 동일하게 짤 수 있다.

### 4.3 OCR 엔진 (결정 필요)

이 프로젝트는 이미 `GEMINI_API_KEY`를 전역으로 쓰고 `ontology`가 Gemini 비전 유스케이스(`gemini_use_case.py`, `vision_use_case.py`)를 갖고 있다. **새 외부 서비스(Naver Clova/AWS Textract)를 추가로 계약·연동하기보다, Gemini에 "영수증 이미지 → JSON(merchantName/transactionDate/totalAmount/items)" 구조화 추출을 시키는 편이 기존 인프라를 재사용하는 최소 변경안**이다. 단, 이 선택은 정확도·비용 트레이드오프가 있는 실제 의사결정이므로 구현 착수 전 사용자 확인이 필요하다.

### 4.4 Outbound — 실시간 알림 (신규, 결정 필요)

WebSocket이든 SSE든 이 코드베이스에 선례가 전혀 없다. Cloudflare Tunnel을 통과해야 하므로:

- **SSE** — 순수 HTTP 스트림이라 프록시/터널 통과가 단순하고, 기존 REST 라우터 컨벤션(`APIRouter`)과 잘 맞는다.
- **WebSocket** — FastAPI 네이티브 지원이 있지만, Cloudflare Tunnel의 WS 패스스루 동작을 별도로 검증해야 한다.

두 경우 모두 `userId`별 연결 관리(연결 레지스트리)가 새로 필요하다 — 기존 `apps/auth`의 `X-User-Id` 인증 패턴을 그대로 재사용해 연결 주체를 식별한다.

---

## 5. Fractal 11-File Set 매핑 (신규 앱이므로 `_docs/architecture.md` §12 적용)

`apps/plant`부터 적용된 신규 앱 규약을 따른다(레거시 8~9파일 구성 아님). 테이블명 `receipt` 기준:

```
router:       apps/receipt/adapter/inbound/api/v1/receipt_router.py
use_case:     apps/receipt/app/ports/input/receipt_use_case.py
interactor:   apps/receipt/app/use_cases/receipt_interactor.py
port:         apps/receipt/app/ports/output/receipt_repository.py   # {Feature}Port 아니라 {Feature}Repository
repository:   apps/receipt/adapter/outbound/pg/receipt_pg_repository.py
schema:       apps/receipt/adapter/inbound/api/schemas/receipt_schema.py
dto:          apps/receipt/app/dtos/receipt_dto.py
orm:          apps/receipt/adapter/outbound/orm/receipt_orm.py
entity:       apps/receipt/domain/entities/receipt_entity.py
mapper:       apps/receipt/adapter/inbound/mappers/receipt_mapper.py
orm_mapper:   apps/receipt/adapter/outbound/orm_mappers/receipt_orm_mapper.py
provider:     apps/receipt/dependencies/receipt_provider.py   # get_receipt_use_case()
```

- 첫 검증은 `GET /receipt/myself`(하드코딩 왕복)로 DI 배선부터 확인한다 — §12 규칙 그대로.
- `status`(`PROCESSED`/`FAILED`)는 원안대로 두되, 이 저장소 컨벤션상 Python 쪽은 Enum(`ReceiptStatus`), DB 컬럼은 문자열로 저장한다(`apps/auth/user_role.py`의 `UserRole` 패턴 참고).

---

## 6. 미결정 사항 (구현 전 확정 필요)

| 항목 | 후보 | 비고 |
|---|---|---|
| 업로드 방식 | (A) Presigned PUT / (B) 멀티파트 통과형 | §4.1 |
| S3→백엔드 트리거 | (A) SNS 웹훅 / (B) 클라이언트 직접 트리거 | §4.2 — 인프라 추가 여부 결정 |
| OCR 엔진 | Gemini Vision(기존 인프라 재사용) / Clova / Textract | §4.3 |
| 실시간 통지 | SSE / WebSocket | §4.4 |
| 버킷 분리 | 기존 `VISION_S3_BUCKET`/`PLANT_S3_BUCKET` 재사용(prefix로 구분) vs 신규 `RECEIPT_S3_BUCKET` | 영수증은 개인정보 성격이 강해 버킷 분리가 안전할 수 있음 |

---

## 7. 환경 변수 (결정 이후 `.env.example`에 추가할 후보)

```dotenv
# 버킷을 분리하기로 하면 (§6)
RECEIPT_S3_BUCKET=your_s3_bucket_name

# OCR 엔진을 Gemini 외 다른 것으로 정하면 추가
# CLOVA_OCR_SECRET_KEY=
# CLOVA_OCR_INVOKE_URL=
```

기존 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`AWS_DEFAULT_REGION`은 이미 등록돼 있어 추가 불필요(`core/infra/s3_manager.py`, `secret_manager` 경유).

---

## 관련 문서

[[fastapi/CLAUDE\|Backend CLAUDE]] · [[fastapi/_docs/CLAUDE\|Backend Docs 인덱스]] · [[_docs/architecture\|Master Architecture]] · [[.claude/rules/api-standards\|API 규칙]] · [[.claude/rules/security/secrets-and-auth\|시크릿·인증 규칙]] · [[gmail-pipeline\|Gmail 파이프라인 메모]] · [[s3-bucket-pending\|S3 업로드 배선 메모]]
