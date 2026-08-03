# 카카오 소셜 로그인 인증 모듈 구현 하네스 — 백엔드

> 이 문서는 Claude Code가 본 저장소의 **백엔드(fastapi)** 영역에서 카카오 로그인 인증
> 모듈을 구현할 때 반드시 준수해야 하는 사양이다.
> 아래 규칙과 충돌하는 구현은 어떤 이유로도 채택하지 않는다.
> 사양이 모호하거나 기존 코드와 충돌하면 **임의로 추측하지 말고 질문**한다.
>
> 짝 문서: [[flutter/_docs/flutter-kakao-oauth-harness\|플러터 클라이언트 하네스]] —
> Flutter가 지켜야 할 클라이언트 요구사항·API 호출 계약은 그쪽에 있다. 이 문서는 그
> 계약을 **정의하는 쪽**이며, 여기 §6 API 명세를 임의로 바꾸면 플러터 쪽 구현이 깨진다.

---

## 0. 작업 전 필수 확인 (Discovery First)

코드를 한 줄이라도 작성하기 전에 아래를 먼저 조사하고 결과를 요약 보고할 것.

- [ ] `fastapi/docker-compose.yaml`에 `redis` 서비스가 존재하는가? (없으면 §5.3에 따라 추가)
- [ ] 기존 인증/유저 관련 도메인, 유즈케이스, 어댑터가 있는가? (`apps/auth/` 등) 있다면 경로와 책임 범위
- [ ] 기존 `User` 엔티티 및 테이블 스키마 (PK 타입, 소프트 삭제 여부, 타임스탬프 컬럼 규칙) — `apps/auth/user_model.py`
- [ ] 환경변수 로딩 방식 — `core/matrix/secret_manager.py`의 `secret_manager.get_secret()` 사용 (§9, [[.claude/rules/security/secrets-and-auth\|시크릿·인증 규칙]] 참고)
- [ ] 기존 예외 처리 / 에러 응답 포맷 컨벤션
- [ ] 테스트 디렉터리 구조와 실행 커맨드 (`fastapi/pytest.ini`, `apps/<앱명>/tests/`)

**중복 구현 금지.** 이미 존재하는 컴포넌트는 재사용하거나 확장한다.

---

## 1. 목표

Flutter 앱에서 카카오 OAuth를 수행하고, **자체 API 서버가 신원을 검증한 뒤 자체 JWT를 발급**하는 인증 체계를 구축한다.

핵심 원칙:

1. **서버는 클라이언트가 보낸 프로필 정보를 절대 신뢰하지 않는다.** 신뢰의 근거는 오직 카카오가 서명한 `id_token`뿐이다.
2. **모바일과 웹의 로그인 경로는 철저히 분리한다.** (§3, 최우선 제약)
3. 최초 로그인 시에만 카카오와 통신한다. 이후 세션 유지는 자체 JWT만으로 이루어진다.

---

## 2. 인증 플로우 (OIDC 방식 — 필수)

### 2.1 채택 방식

카카오 개발자 콘솔에서 **OpenID Connect를 활성화**하고, 로그인 결과로 받은 `id_token`(JWT)을 서버로 전달받는다.
서버는 **JWKS 기반 로컬 서명 검증**만으로 인증을 완료한다.

### 2.2 금지된 대안

- `access_token`을 서버로 받아 `GET /v2/user/me`로 신원을 확인하는 방식 → **채택 금지**
  (서버→카카오 네트워크 왕복이 발생하고, `app_id` 별도 검증 없이는 타 앱 발급 토큰을 구분하지 못함)
- 클라이언트가 보낸 프로필 필드(닉네임·이메일 등)를 검증 없이 신뢰 → **채택 금지**
- 카카오 `refresh_token`을 서버에 저장 → **채택 금지** (§7 참조)

### 2.3 전체 시퀀스

```
[Flutter]
  loginWithKakaoTalk() / loginWithKakaoAccount()
    → OAuthToken { idToken, accessToken, refreshToken }
    → accessToken/refreshToken은 서버로 보내지 않고 폐기 또는 로컬 보관
  POST /api/auth/kakao/mobile  { "idToken": "...", "nonce": "..." }

[API Server]
  1. JWKS 캐시에서 kid 매칭 공개키 조회
  2. RS256 서명 검증
  3. 클레임 검증: iss / aud / exp / nonce
  4. sub(카카오 회원번호)로 User 조회
       - 존재하지 않으면 → 신규 가입 처리 (DB INSERT)
       - 존재하면       → 최종 로그인 시각 갱신
  5. 자체 access JWT + refresh JWT 발급
  6. refresh 토큰을 Redis 모바일 네임스페이스에 저장 (§5)
    → { "accessToken": "...", "refreshToken": "...", "expiresIn": 1800 }
```

클라이언트 쪽 상세 동작(카카오 SDK 호출, 토큰 저장, 인터셉터 등)은 이 문서의 책임이 아니다 —
[[flutter/_docs/flutter-kakao-oauth-harness\|플러터 하네스]] §2·§5를 따른다.

### 2.4 id_token 검증 규칙 (하나라도 실패 시 401)

| 항목 | 기대값 |
|---|---|
| 알고리즘 | `RS256` (헤더의 `alg`를 신뢰하지 말고 서버에서 강제 지정) |
| 서명 | `https://kauth.kakao.com/.well-known/jwks.json` 공개키로 검증 |
| `iss` | `https://kauth.kakao.com` |
| `aud` | 카카오 **네이티브 앱 키** (환경변수) |
| `exp` | 현재 시각 기준 미만료 (clock skew 허용 ≤ 60초) |
| `nonce` | 클라이언트가 로그인 요청 시 생성한 값과 일치 |

- JWKS는 애플리케이션 시작 시 로드하고 **Redis에 캐싱**(TTL 6시간)한다.
- 캐시에 없는 `kid`가 등장하면 **1회에 한해** JWKS를 재조회한다. (무한 재조회 방지 — 최소 5분 쿨다운)

### 2.5 id_token 클레임에서 얻는 정보

`sub`, `nickname`, `picture`, `email`(동의 시). 그 외 확장 정보(성별, 연령대 등)는 포함되지 않는다.
**추가 정보가 실제로 필요한 경우에만** `GET /v2/user/me`를 별도 유즈케이스로 호출한다. 로그인 경로에는 절대 포함시키지 않는다.

---

## 3. 【최우선 제약】 모바일 / 웹 로그인 완전 분리

모바일과 웹은 **서로 다른 인증 채널**로 취급한다. 코드, 저장소, 토큰이 어느 지점에서도 섞이지 않아야 한다.

### 3.1 분리 대상

| 구분 | 모바일 | 웹 |
|---|---|---|
| 로그인 엔드포인트 | `POST /api/auth/kakao/mobile` | `POST /api/auth/kakao/web` |
| 리프레시 엔드포인트 | `POST /api/auth/mobile/refresh` | `POST /api/auth/web/refresh` |
| 로그아웃 엔드포인트 | `POST /api/auth/mobile/logout` | `POST /api/auth/web/logout` |
| 입력 자격증명 | Flutter SDK가 발급한 `id_token` | 인가 코드(Authorization Code) 교환 결과 |
| `aud` 검증 대상 | 네이티브 앱 키 | JavaScript 앱 키 (REST 앱 키) |
| 토큰 전달 방식 | 응답 바디(JSON) | refresh는 `HttpOnly` + `Secure` + `SameSite=Lax` 쿠키 |
| 토큰 저장소 | Redis `auth:mobile:*` | Redis `auth:web:*` |
| Access TTL | 30분 | 15분 |
| Refresh TTL | 60일 | 14일 |
| 동시 세션 | 기기별 다중 허용 | 단일 세션 |

### 3.2 강제 규칙

- 발급하는 모든 JWT payload에 **`platform` 클레임을 필수 포함**한다. 값은 `"mobile"` 또는 `"web"`.
- 리프레시/로그아웃 시 **요청 엔드포인트의 플랫폼과 토큰의 `platform` 클레임이 일치하지 않으면 즉시 401**을 반환하고 해당 세션을 폐기한다.
- 모바일 refresh 토큰으로 웹 세션을 얻거나, 그 반대가 가능한 경로가 **단 하나라도 존재해서는 안 된다.**
- 웹/모바일 로직을 `if platform == "web"` 같은 분기로 한 함수에 뭉치지 않는다. **유즈케이스와 어댑터를 물리적으로 분리**한다. 공통 로직은 순수 도메인 서비스로만 추출한다.
- `User` 레코드 자체는 카카오 `sub` 기준으로 **공유**한다. 분리 대상은 계정이 아니라 **세션과 토큰**이다.

---

## 4. 아키텍처 규칙

기존 헥사고날(포트 & 어댑터) 구조를 따른다. `fastapi/CLAUDE.md`의 feature 슬라이스 규약과 정합성을 맞춘다. 예시 배치:

```
apps/auth/
├── domain/
│   ├── model/            # User, AuthSession, Platform(Enum) — 프레임워크 의존 0
│   └── exception/        # InvalidIdTokenError, PlatformMismatchError ...
├── application/
│   ├── port/
│   │   ├── inbound/      # MobileKakaoLoginUseCase, WebKakaoLoginUseCase, RefreshTokenUseCase
│   │   └── outbound/     # IdTokenVerifierPort, TokenStorePort, UserRepositoryPort, JwtIssuerPort
│   └── service/          # 유즈케이스 구현 (모바일/웹 각각 별도 클래스)
└── adapter/
    ├── inbound/web/      # FastAPI 라우터, Pydantic 스키마
    └── outbound/
        ├── kakao/        # JWKS 클라이언트, OIDC 검증기
        ├── persistence/  # User 리포지토리
        └── redis/        # TokenStore 구현
```

- 의존 방향은 **바깥 → 안쪽 단방향**. 도메인은 `fastapi`, `redis`, `jose` 등을 import하지 않는다.
- 유즈케이스는 **포트 인터페이스에만 의존**한다. 구체 클래스 주입 금지.
- `import-linter` 계약이 설정되어 있다면 새 레이어 규칙을 계약에 추가한다.
- 패키지 관리는 `uv`를 사용한다.
- 기존 `apps/auth/dependencies.py`(`get_current_user`, X-User-Id 헤더 임시 방식)와의 관계를 먼저 파악하고, 이 모듈이 그것을 대체하는지 병행하는지 §0 Discovery 단계에서 확인·보고한다.

---

## 5. Redis — 모바일 로그인 토큰 저장소

> Redis에는 "컬럼" 개념이 없으므로, **전용 키 네임스페이스 + Hash 필드**로 설계한다.
> 모바일과 웹은 키 프리픽스부터 분리하여 조회 자체가 교차되지 않게 한다.

### 5.1 키 스키마

```
# 모바일 refresh 토큰 (Hash)
auth:mobile:refresh:{jti}
  ├─ user_id      : "1024"
  ├─ kakao_sub    : "3456789012"
  ├─ platform     : "mobile"          # 고정값, 검증용
  ├─ device_id    : "a1b2c3..."       # 기기 식별자
  ├─ issued_at    : "2026-08-03T09:12:33Z"
  ├─ expires_at   : "2026-10-02T09:12:33Z"
  └─ rotated_from : "{이전 jti}"       # 최초 발급 시 빈 문자열
  TTL = 60일

# 사용자별 활성 모바일 세션 인덱스 (Set) — 전체 로그아웃/강제 만료용
auth:mobile:sessions:{user_id}  → { jti, jti, ... }
  TTL = 60일 (갱신 시 연장)

# 웹 (별도 프리픽스, 모바일 코드에서 접근 금지)
auth:web:refresh:{jti}
auth:web:sessions:{user_id}

# 블랙리스트 (로그아웃된 access 토큰의 잔여 수명 동안 차단)
auth:blacklist:{platform}:{jti}   TTL = access 토큰 잔여 TTL

# JWKS 캐시
auth:jwks:kakao                   TTL = 6시간
```

### 5.2 동작 규칙

- **Refresh Token Rotation 필수.** 리프레시 성공 시 기존 `jti` 키를 삭제하고 새 `jti`를 발급한다.
- **재사용 탐지:** 이미 삭제된 `jti`로 리프레시 요청이 들어오면 탈취로 간주하고, 해당 `user_id`의 **모바일 세션 전체를 폐기**(`auth:mobile:sessions:{user_id}` 순회 삭제)한 뒤 401을 반환하고 경고 로그를 남긴다.
- TTL은 Redis에 위임하고, 애플리케이션에서 별도 만료 배치를 돌리지 않는다.
- 삭제·조회는 반드시 `TokenStorePort` 구현체를 경유한다. 유즈케이스에서 Redis 클라이언트를 직접 호출하지 않는다.
- `MobileTokenStore`와 `WebTokenStore`는 **별도 구현 클래스**로 만들고, 각자 자신의 프리픽스만 다룬다. 프리픽스를 파라미터로 받는 공용 클래스로 합치지 않는다.

### 5.3 docker-compose

`redis` 서비스가 없으면 아래 기준으로 추가한다. 이미 있으면 **기존 설정을 존중**하고 필요한 부분만 보완한다 — 신규/재생성 전에 [[fastapi/_docs/docker-rules\|Docker 규칙(중복 생성 방지)]]의 체크리스트를 먼저 따른다.

- 이미지: `redis:7-alpine`
- 네트워크: 기존 백엔드 네트워크에 연결, **포트는 호스트로 노출하지 않는다** (컨테이너 내부 통신만)
- 영속화: AOF 활성화 (`appendonly yes`) + named volume
- 인증: `requirepass`를 환경변수로 주입
- healthcheck: `redis-cli ping`
- FastAPI 서비스에 `depends_on: redis (condition: service_healthy)` 추가

---

## 6. API 명세

**이 절이 백엔드↔플러터 간의 계약이다.** 필드명·타입·에러 코드를 임의로 바꾸지 않는다 — 바꿔야 하면 플러터 쪽 하네스도 함께 갱신하고 사용자에게 보고한다.

### 6.1 `POST /api/auth/kakao/mobile`

```jsonc
// Request
{ "idToken": "eyJ...", "nonce": "5f3a...", "deviceId": "a1b2c3..." }

// 200 OK
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "tokenType": "Bearer",
  "expiresIn": 1800,
  "isNewUser": true
}
```

### 6.2 `POST /api/auth/mobile/refresh`

```jsonc
// Request
{ "refreshToken": "eyJ..." }

// 200 OK — 새 access + 새 refresh (rotation)
```

### 6.3 `POST /api/auth/mobile/logout`

현재 세션의 refresh 키 삭제 + access `jti` 블랙리스트 등록. 204 반환.

### 6.4 에러 코드

| 상황 | HTTP | code |
|---|---|---|
| id_token 서명/클레임 검증 실패 | 401 | `INVALID_ID_TOKEN` |
| id_token 만료 | 401 | `EXPIRED_ID_TOKEN` |
| aud 불일치 (타 앱 토큰) | 401 | `INVALID_AUDIENCE` |
| nonce 불일치 | 401 | `INVALID_NONCE` |
| 플랫폼 클레임 불일치 | 401 | `PLATFORM_MISMATCH` |
| refresh 재사용 탐지 | 401 | `TOKEN_REUSE_DETECTED` |
| JWKS 조회 실패 | 503 | `IDP_UNAVAILABLE` |

에러 응답 포맷은 **기존 프로젝트 컨벤션을 따른다.** 새 포맷을 만들지 않는다.

---

## 7. 보안 규칙

- 카카오 `access_token` / `refresh_token`은 **서버로 전송받지도, 저장하지도 않는다.**
  (서버가 사용자 대신 카카오 API를 호출할 요구사항이 생기면 그때 별도 설계 — 지금은 범위 밖)
- 자체 JWT 서명 키는 환경변수로 주입한다(`secret_manager` 경유, §9). 코드/저장소에 하드코딩 금지.
- 로그에 `id_token`, JWT 원문, `email` 전체를 남기지 않는다. 마스킹하거나 `jti`·`user_id`만 기록한다.
- `nonce`는 클라이언트가 CSPRNG로 생성한 값을 서버가 **1회용으로 소비**한다 (Redis `SET NX` + 짧은 TTL).
- 회원 탈퇴 시 어드민 키로 카카오 `POST /v1/user/unlink`를 호출하고, 해당 유저의 **모바일·웹 전체 세션을 폐기**한다.

---

## 8. 환경변수

```dotenv
# Kakao
KAKAO_NATIVE_APP_KEY=        # 모바일 aud 검증용
KAKAO_JS_APP_KEY=            # 웹 aud 검증용
KAKAO_REST_API_KEY=
KAKAO_ADMIN_KEY=             # unlink 전용
KAKAO_ISSUER=https://kauth.kakao.com
KAKAO_JWKS_URL=https://kauth.kakao.com/.well-known/jwks.json

# 자체 JWT
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_MOBILE_ACCESS_TTL_MINUTES=30
JWT_MOBILE_REFRESH_TTL_DAYS=60
JWT_WEB_ACCESS_TTL_MINUTES=15
JWT_WEB_REFRESH_TTL_DAYS=14

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

`fastapi/.env.example`을 실제 값 없이 함께 갱신한다. 값 로딩은 `os.getenv` 직접 호출이 아니라
`secret_manager.get_secret()` 경유 — [[.claude/rules/security/secrets-and-auth\|시크릿·인증 규칙]] 참고.

카카오 네이티브 앱 키는 여기(`.env`)에서는 **검증용**으로만 쓰인다. 플러터 앱에 실제로 심는
네이티브 키·URL 스킴 설정은 `AndroidManifest.xml`/`Info.plist` 쪽이며 그건 백엔드 책임이
아니다 — [[flutter/_docs/flutter-kakao-oauth-harness\|플러터 하네스]] §7 참고.

---

## 9. 테스트 (필수)

작성하지 않으면 완료로 간주하지 않는다.

**단위 테스트 — 외부 의존 전부 페이크/스텁** (DB 없이 돌아야 함, [[.claude/rules/testing\|테스트 규칙]] 참고)

- [ ] 유효한 id_token → 신규 유저 생성 + 토큰 발급
- [ ] 유효한 id_token → 기존 유저 재로그인 (중복 생성 없음)
- [ ] 서명 위조 → `INVALID_ID_TOKEN`
- [ ] `aud`가 웹 앱 키인 토큰을 모바일 엔드포인트로 → `INVALID_AUDIENCE`
- [ ] `exp` 만료 → `EXPIRED_ID_TOKEN`
- [ ] `nonce` 불일치 / 재사용 → `INVALID_NONCE`
- [ ] **웹 refresh 토큰으로 `/api/auth/mobile/refresh` 호출 → `PLATFORM_MISMATCH`**
- [ ] **모바일 refresh 토큰으로 `/api/auth/web/refresh` 호출 → `PLATFORM_MISMATCH`**
- [ ] rotation 후 이전 refresh 재사용 → `TOKEN_REUSE_DETECTED` + 해당 유저 모바일 세션 전체 폐기

**통합 테스트**

- [ ] 실제 Redis 컨테이너(testcontainers 또는 compose 테스트 프로파일) 대상으로 키 생성/TTL/삭제 검증
- [ ] `auth:mobile:*`와 `auth:web:*` 키가 상호 조회되지 않음을 확인

JWKS와 카카오 응답은 **테스트에서 실제 네트워크를 타지 않도록** 고정 키페어로 스텁 처리한다.

---

## 10. 작업 순서 (백엔드)

1. Discovery(§0) 수행 후 결과 보고 → **승인받고 다음 단계 진행**
2. 도메인 모델 + 포트 인터페이스 정의
3. OIDC 검증기 어댑터 + JWKS 캐시
4. Redis TokenStore (모바일/웹 각각) + docker-compose 반영
5. 모바일 로그인/리프레시/로그아웃 유즈케이스 + 라우터
6. 웹 유즈케이스 + 라우터 (모바일과 동일 구조, 코드 공유 없음)
7. 테스트 작성 및 전체 통과 확인
8. `.env.example`, README 인증 섹션 갱신

§6 API 명세가 확정·구현되어야 [[flutter/_docs/flutter-kakao-oauth-harness\|플러터 쪽 작업]]이
실제 서버를 상대로 진행될 수 있다 — 순서상 백엔드가 선행이거나, 최소한 §6 계약만 먼저 확정해서
플러터와 병행한다.

각 단계 완료 시 **변경 파일 목록과 핵심 결정 사항을 요약 보고**한다.

---

## 11. 금지 사항 요약 (백엔드)

- ❌ `access_token` 기반 서버측 신원 확인
- ❌ 카카오 refresh token을 서버에 저장
- ❌ 모바일/웹 로직을 하나의 유즈케이스에서 분기 처리
- ❌ 모바일/웹 토큰을 같은 Redis 키 네임스페이스에 저장
- ❌ 유즈케이스에서 Redis·HTTP 클라이언트 직접 호출
- ❌ 도메인 레이어의 프레임워크 import
- ❌ 시크릿 하드코딩, 토큰 원문 로깅
- ❌ 테스트 없이 완료 보고

---

## 관련 문서

[[fastapi/CLAUDE\|Backend CLAUDE]] · [[fastapi/_docs/CLAUDE\|Backend Docs 인덱스]] · [[fastapi/_docs/docker-rules\|Docker 규칙]] · [[flutter/_docs/flutter-kakao-oauth-harness\|플러터 클라이언트 하네스(짝 문서)]] · [[.claude/rules/security/secrets-and-auth\|시크릿·인증 규칙]]
