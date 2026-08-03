# 카카오 소셜 로그인 인증 모듈 — 백엔드 (구현 완료)

> 이 문서는 원래 그린필드 전제로 쓴 사양이었으나, 실제 구현 과정에서 기존 인프라
> (`auth_main.py`/`main.py` 분리, `core/security.py`의 RS256 인프라)와 충돌하는 부분이
> 드러나 **실제 구현 기준으로 다시 썼다.** 지금부터는 "이렇게 만들어라"가 아니라
> "이렇게 만들어져 있다"는 as-built 레퍼런스다.
>
> 짝 문서: [[flutter/_docs/flutter-kakao-oauth-harness\|플러터 클라이언트 하네스]]

---

## 1. 목표 · 핵심 원칙 (변경 없음)

1. **서버는 클라이언트가 보낸 프로필 정보를 절대 신뢰하지 않는다.** 신뢰의 근거는 오직 카카오가 서명한 `id_token`뿐이다.
2. **모바일과 웹의 로그인 경로는 철저히 분리한다** (§3).
3. 최초 로그인 시에만 카카오와 통신한다. 이후 세션 유지는 자체 JWT만으로 이루어진다.
4. **id_token은 OIDC 방식으로 검증한다** — `access_token`으로 `GET /v2/user/me`를 호출해 신원을 확인하는 기존 웹 플로우(`apps/auth/services.py`)의 패턴은 모바일에서 재사용하지 않는다.

---

## 2. 실제 아키텍처 — 두 서비스로 분리돼 있다

```
auth.whoareryu.cloud (auth_main.py)  ← JWT_PRIVATE_KEY 보유, 토큰 "발급" 전용
api.whoareryu.cloud  (main.py)       ← JWT_PUBLIC_KEY만 보유, 토큰 "검증"만
```

모바일 카카오 로그인 엔드포인트는 토큰을 발급하므로 **반드시 `auth_main.py`(auth.whoareryu.cloud)에 있다.** 이건 원래 하네스 문서가 전혀 몰랐던 제약이었다.

---

## 3. JWT 발급 — 새로 안 만들고 `core/security.py` 확장

기존 RS256 인프라(웹 로그인이 이미 씀)를 **가산적으로 확장**했다. 별도 `JWT_SECRET_KEY`/HS256 체계는 안 만들었다 — 두 체계가 공존하면 `api.whoareryu.cloud`의 공용 검증 로직(`core/dependencies.py::get_current_user`)이 모바일 토큰을 못 읽는다.

- `TokenPayload.platform: str = "web"` 필드 추가 (기본값 있어 기존 호출부 전부 그대로 유효)
- `create_access_token(..., platform: str = "web")`
- `create_refresh_token`/`rotate_refresh_token`/`revoke_refresh_family`/`blacklist_token`/`is_token_blacklisted` 전부에 `namespace: str = ""` 키워드 인자 추가 — 기본값이면 기존 웹 키(`refresh:{token}` 등)와 100% 동일. 모바일은 `namespace="auth:mobile:"`로 호출해 `auth:mobile:refresh:{token}` 등으로 격리된다.
- `create_refresh_token(..., extra: dict | None = None)` — Redis에 저장되는 JSON에 `device_id`/`platform` 같은 부가 필드를 얹는다. **하네스 원안의 7필드 Redis Hash 스키마는 안 씀** — JSON 문자열 + `extra` 병합이 충분히 단순하고 기존 저장 방식과 동일하다.
- 회귀 테스트로 "네임스페이스 기본값이면 기존 웹 동작과 동일함"을 증명함 — `apps/auth/tests/test_security.py` 참고.

---

## 4. 인증 플로우 — 신규 유저는 동의(약관) 화면을 거친다

> 원래 문서엔 없던 부분. 웹 로그인(`apps/auth/consent_flow.py` + `consent_router.py`)이
> 이미 "신규 OAuth 유저는 동의를 받고 나서만 계정을 생성"하는 패턴을 갖고 있어서,
> 모바일도 **그 패턴을 그대로 재사용**했다 (동의 화면 없이 바로 가입시키는 방안은
> 기각됨 — 사용자 확인).

```
[Flutter]
  loginWithKakaoTalk(nonce:) / loginWithKakaoAccount(nonce:)
    → OAuthToken.idToken (OIDC 활성화 시에만 채워짐)
  POST /auth/mobile/kakao/login  { "id_token", "nonce", "device_id" }

[auth_main.py]
  1. PyJWKClient로 카카오 JWKS에서 서명키 조회 (자체 Redis 캐시 없음 — PyJWKClient가
     이미 kid 기반 인프로세스 캐싱을 함, auth_main.py가 단일 프로세스라 충분)
  2. jwt.decode(algorithms=["RS256"], issuer=, audience=KAKAO_NATIVE_APP_KEY, leeway=60)
  3. nonce 1회 소비 확인 (Redis SET NX auth:mobile:nonce:{nonce} EX 300)
  4. sub로 기존 유저 조회 (find_existing_user 재사용)
       - 있으면 → 바로 로그인, { "status": "logged_in", "access_token", ... }
       - 없으면 → pending_signup 생성(consent_flow.py 재사용),
                  { "status": "consent_required", "consent_token", "suggested_nickname" }

[Flutter, 신규 유저인 경우만]
  ConsentScreen에서 닉네임 확인 + 약관 동의
  POST /auth/mobile/consent/complete { "consent_token", "nickname", "agree_terms", "device_id" }
    → 계정 생성(policy_agreed_at 채움) + 로그인
```

---

## 5. 【최우선 제약】 모바일 / 웹 분리 — 실제 값

| 구분 | 모바일 | 웹 |
|---|---|---|
| 로그인 | `POST /auth/mobile/kakao/login` | `POST /auth/kakao/login` (기존) |
| 동의 완료 | `POST /auth/mobile/consent/complete` | `POST /auth/consent/complete` (기존) |
| 리프레시 | `POST /auth/mobile/refresh` | `POST /auth/refresh` (기존) |
| 로그아웃 | `POST /auth/mobile/logout` | `POST /auth/logout` (기존) |
| Redis 프리픽스 | `auth:mobile:*` | 기본 네임스페이스(`refresh:*`, `refresh_family:*`, `jwt_blacklist:*`) |
| `platform` 클레임 | `"mobile"` | `"web"` |
| 토큰 전달 | JSON 바디 | 쿠키(`wr_session`/`wr_refresh`, HttpOnly) |

**`/api` 프리픽스는 안 붙는다** — `auth_main.py`가 원래 그렇게 마운트돼 있어서(기존 `/auth/kakao/*` 컨벤션과 통일). 하네스 원안의 `POST /api/auth/kakao/mobile`은 폐기.

`apps/auth/adapter/inbound/api/v1/mobile_auth_router.py`에서 `platform` 불일치를 401(`PLATFORM_MISMATCH`)로 강제한다 (모바일 로그아웃 유스케이스가 `core.dependencies.get_current_user`로 얻은 토큰의 `platform`을 검사).

---

## 6. 아키텍처 — `apps/titanic` 레퍼런스 패턴 (하네스 원안의 레이어명과 다름)

```
fastapi/apps/auth/
├── domain/
│   ├── model/mobile_kakao_identity.py
│   └── exception/mobile_auth_exceptions.py
├── app/                                    # ← "application/"이 아니라 "app/" (titanic 컨벤션)
│   ├── dtos/mobile_auth_dto.py
│   ├── ports/{input,output}/               # ← "port/{inbound,outbound}"이 아니라 "ports/{input,output}"
│   └── use_cases/
├── adapter/
│   ├── inbound/api/{schemas,v1}/
│   └── outbound/{kakao,redis,persistence,mappers}/
└── dependencies/mobile_auth_provider.py    # get_mobile_*_use_case()
```

기존 `apps/auth/`의 플랫(레거시) 파일들(`router.py`, `services.py`, `user_model.py`,
`user_provisioning.py`, `consent_flow.py`)은 **그대로 재사용, 수정 없음** — 새 코드가
그 위에 얹힌다.

---

## 7. API 명세 — 실제 필드명은 **snake_case**

> 하네스 원안은 camelCase(`idToken`, `accessToken` 등)를 가정했는데, `auth_main.py`의
> 기존 스키마(`apps/auth/schemas.py`의 `ConsentCompleteRequest.consent_token`,
> `agree_terms` 등)가 이미 snake_case라 그것에 맞췄다.

### `POST /auth/mobile/kakao/login`
```jsonc
// Request
{ "id_token": "eyJ...", "nonce": "...", "device_id": "..." }

// 200 — 기존 유저
{ "status": "logged_in", "access_token": "...", "refresh_token": "...",
  "token_type": "Bearer", "expires_in": 7200, "is_new_user": false }

// 200 — 신규 유저 (동의 필요)
{ "status": "consent_required", "consent_token": "...", "suggested_nickname": "..." }
```

### `POST /auth/mobile/consent/complete`
```jsonc
// Request
{ "consent_token": "...", "nickname": "...", "agree_terms": true, "device_id": "..." }
// 200 → { "access_token", "refresh_token", "token_type", "expires_in" }
```

### `POST /auth/mobile/refresh`
```jsonc
{ "refresh_token": "..." } → { "access_token", "refresh_token", "token_type", "expires_in" }
```

### `POST /auth/mobile/logout`
`Authorization: Bearer <access_token>` 헤더 필요. 204 반환.

### 에러 — Korean `detail` + `X-Error-Code` 헤더

> 하네스 원안은 `detail`을 `{code, message}` 딕셔너리로 하려 했는데, 이 저장소의
> `.claude/rules/api-standards.md` §4("`detail`은 한국어 문자열")와 충돌해서 바꿨다.
> 에러 코드는 **응답 헤더**로 분리했다 — `detail`은 여전히 한국어 문자열.

| 상황 | HTTP | `X-Error-Code` |
|---|---|---|
| id_token 서명/클레임 검증 실패 | 401 | `INVALID_ID_TOKEN` |
| id_token 만료 | 401 | `EXPIRED_ID_TOKEN` |
| aud 불일치 | 401 | `INVALID_AUDIENCE` |
| nonce 불일치/재사용 | 401 | `INVALID_NONCE` |
| 플랫폼 클레임 불일치 | 401 | `PLATFORM_MISMATCH` |
| refresh 재사용 탐지 | 401 | `TOKEN_REUSE_DETECTED` |
| JWKS 조회 실패 | 503 | `IDP_UNAVAILABLE` |
| 약관 미동의 | 422 | `TERMS_NOT_AGREED` |
| 닉네임 미입력 | 422 | `NICKNAME_REQUIRED` |
| 닉네임 중복 | 409 | `NICKNAME_TAKEN` |
| consent_token 만료/무효 | 400 | `CONSENT_TOKEN_INVALID` |

실제 매핑 표는 `apps/auth/adapter/inbound/api/v1/mobile_auth_router.py::_ERROR_MAP`.

---

## 8. 환경변수 — 실제 값

```dotenv
KAKAO_NATIVE_APP_KEY=   # 플러터 KakaoSdk.init(nativeAppKey:)와 동일한 값
KAKAO_ISSUER=https://kauth.kakao.com
KAKAO_JWKS_URL=https://kauth.kakao.com/.well-known/jwks.json
```

`REDIS_URL` 단일 연결 문자열을 그대로 씀(하네스 원안의 분해형 `REDIS_HOST/PORT/DB`는 폐기).
`.env.example`에 추가 완료. `.env`는 훅으로 보호돼 있어 Claude가 직접 못 고침 — 사람이
Native App Key 실값을 채워야 한다. 새 Python 의존성 없음(`PyJWT`의 `PyJWKClient` 사용).

---

## 9. 테스트 — `fastapi/apps/auth/tests/`

`python -m pytest apps/auth/tests/ -v` — 58개 전부 통과 확인(기존 웹 로그인 테스트 포함, 회귀 없음).

- `test_mobile_kakao_login_interactor.py` / `test_mobile_consent_complete_interactor.py` /
  `test_mobile_refresh_interactor.py` / `test_mobile_logout_interactor.py` — 단위, 포트 전부 페이크
- `test_kakao_id_token_verifier.py` — 단위, 로컬 RSA 키페어로 만든 가짜 JWKS(`PyJWKClient` 몽키패치), 실네트워크 없음
- `test_mobile_kakao_token_store.py` — 통합, 실제 Redis 필요(`REDIS_URL`, 기본 `redis://localhost:16379/0`)
- `test_security.py`에 `namespace`/`platform` 회귀 케이스 추가

---

## 10. 알려진 갭 (의도적으로 남겨둠)

- Android는 이번 범위에서 뺐다 — 사용자가 카카오 콘솔에 Android 플랫폼을 아직 등록하지 않음. iOS만 구현.
- `KAKAO_NATIVE_APP_KEY` 실값 미입력 — 사용자가 확인 후 채워야 실제 로그인 테스트 가능.
- 카카오 회원 탈퇴 시 `POST /v1/user/unlink` 연동은 이번 범위 밖(원 하네스 §7에 있었지만 미구현).

---

## 관련 문서

[[fastapi/CLAUDE\|Backend CLAUDE]] · [[fastapi/_docs/CLAUDE\|Backend Docs 인덱스]] · [[flutter/_docs/flutter-kakao-oauth-harness\|플러터 클라이언트 하네스(짝 문서)]] · [[.claude/rules/security/secrets-and-auth\|시크릿·인증 규칙]] · [[.claude/rules/api-standards\|API 규칙]]
