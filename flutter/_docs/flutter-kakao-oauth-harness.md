# 카카오 소셜 로그인 인증 모듈 구현 하네스 — 플러터 클라이언트

> 이 문서는 Claude Code가 본 저장소의 **플러터(flutter)** 영역에서 카카오 로그인
> 클라이언트를 구현할 때 반드시 준수해야 하는 사양이다.
> 아래 규칙과 충돌하는 구현은 어떤 이유로도 채택하지 않는다.
> 사양이 모호하거나 기존 코드와 충돌하면 **임의로 추측하지 말고 질문**한다.
>
> 짝 문서: [[fastapi/_docs/flutter-kakao-oauth-harness\|백엔드 인증 하네스]] — API 명세,
> id_token 검증 규칙, Redis 토큰 저장소 등 서버 쪽 구현은 그쪽에 있다. 이 문서는 그
> 서버 계약(§4)을 **호출하는 쪽**이며, 계약을 임의로 바꾸지 않는다 — 바꿔야 하면 백엔드
> 하네스도 함께 갱신하고 사용자에게 보고한다.

---

## 0. 작업 전 필수 확인 (Discovery First)

코드를 한 줄이라도 작성하기 전에 아래를 먼저 조사하고 결과를 요약 보고할 것.

- [ ] `pubspec.yaml`에 `kakao_flutter_sdk_user`가 이미 등록되어 있는가? 버전은?
- [ ] `android/app/src/main/AndroidManifest.xml` / `ios/Runner/Info.plist`에 카카오
      네이티브 앱 키·URL 스킴이 이미 설정돼 있는가 — [[flutter/_docs/flutter-android-harness\|Android 하네스]] / [[flutter/_docs/flutter-ios-harness\|iOS 하네스]] 참고
- [ ] 기존 로그인 화면·라우팅 진입점이 있는가 (`lib/main.dart` 등 현재 구조 파악)
- [ ] 기존 HTTP 클라이언트(Dio/http) 설정과 인터셉터 유무 — `lib/features/plant/plant_api.dart` 등 기존 API 클라이언트 패턴 참고
- [ ] 토큰 저장 방식 — 현재 `flutter_secure_storage` 또는 `SharedPreferences` 중 뭘 쓰고 있는가
- [ ] 백엔드 API 베이스 URL을 관리하는 방식 (환경별 설정이 이미 있는가)

**중복 구현 금지.** 이미 존재하는 컴포넌트는 재사용하거나 확장한다.

---

## 1. 목표

Flutter는 카카오 SDK로 로그인해 카카오가 서명한 `id_token`을 얻고, 그것을 서버
(`POST /api/auth/kakao/mobile`)로 전달해 **자체 access/refresh JWT**를 발급받는다.

핵심 원칙:

1. **Flutter는 신원을 직접 검증하지 않는다.** 검증은 전적으로 서버 책임이다 ([[fastapi/_docs/flutter-kakao-oauth-harness\|백엔드 하네스]] §2). 클라이언트는 `id_token`을 그대로 전달하기만 한다.
2. **모바일 전용 엔드포인트만 호출한다.** 웹 로그인 경로(`/api/auth/kakao/web` 등)는 절대 호출하지 않는다 (§3).
3. 최초 로그인 이후에는 자체 JWT로만 세션을 유지한다 — 매 요청마다 카카오와 통신하지 않는다.

---

## 2. 클라이언트 인증 흐름

### 2.1 전체 시퀀스

```
[Flutter]
  loginWithKakaoTalk() / loginWithKakaoAccount()
    → OAuthToken { idToken, accessToken, refreshToken }
    → accessToken/refreshToken은 서버로 보내지 않고 폐기하거나 로컬에만 둔다
  POST /api/auth/kakao/mobile  { "idToken": "...", "nonce": "...", "deviceId": "..." }

[API Server] — 상세는 백엔드 하네스 §2.3
  id_token 서명·클레임 검증 → User 조회/생성 → 자체 JWT 발급 → Redis에 refresh 저장
    → { "accessToken": "...", "refreshToken": "...", "expiresIn": 1800 }

[Flutter]
  accessToken은 메모리, refreshToken은 flutter_secure_storage에 저장 (§5)
```

### 2.2 금지된 대안

- **`UserApi.instance.me()`를 호출해 프로필을 서버로 전송하는 방식 → 채택 금지.** 서버가 검증할 수 없는 정보는 의미가 없다.
- 카카오 `access_token`을 서버로 보내는 방식 → **채택 금지** (서버가 신뢰하지 않음)
- 카카오 `refresh_token`을 서버로 전송/저장 → **채택 금지**

### 2.3 nonce

로그인 요청 직전에 클라이언트가 CSPRNG로 `nonce`를 생성해 카카오 SDK 로그인 호출과
서버 요청 양쪽에 동일하게 사용한다. 서버는 이 값을 1회용으로 소비한다 — 재사용 금지.

---

## 3. 호출 대상 엔드포인트 (모바일 전용)

| 항목 | 값 |
|---|---|
| 로그인 | `POST /api/auth/kakao/mobile` |
| 리프레시 | `POST /api/auth/mobile/refresh` |
| 로그아웃 | `POST /api/auth/mobile/logout` |
| 입력 자격증명 | Flutter SDK가 발급한 `id_token` |
| 토큰 전달 방식 | 응답 바디(JSON) |
| Access TTL | 30분 |
| Refresh TTL | 60일 |
| 동시 세션 | 기기별 다중 허용 |

**웹 전용 엔드포인트(`/api/auth/kakao/web`, `/api/auth/web/refresh` 등)는 모바일
클라이언트가 절대 호출하지 않는다.** 서버가 `platform` 클레임 불일치를 401로 막긴 하지만,
애초에 클라이언트 코드에 web 엔드포인트 URL이 등장해서는 안 된다.

---

## 4. API 요청/응답 계약

계약의 원본은 [[fastapi/_docs/flutter-kakao-oauth-harness\|백엔드 하네스]] §6이다 — 여기 값과
어긋나면 백엔드 문서를 기준으로 맞추고, 서버 구현이 실제로 다르면 사용자에게 보고한다.

### 4.1 `POST /api/auth/kakao/mobile`

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

### 4.2 `POST /api/auth/mobile/refresh`

```jsonc
// Request
{ "refreshToken": "eyJ..." }

// 200 OK — 새 access + 새 refresh (rotation). 이전 refreshToken은 폐기하고 새 값으로 교체 저장한다.
```

### 4.3 `POST /api/auth/mobile/logout`

바디 없음(또는 저장된 refreshToken). 204 반환 — 로컬 토큰(메모리 access, secure storage
refresh)도 함께 정리하고 로그인 화면으로 이동한다.

### 4.4 에러 코드 — UI 분기 기준

| 상황 | HTTP | code | 클라이언트 처리 |
|---|---|---|---|
| id_token 검증 실패 | 401 | `INVALID_ID_TOKEN` | 로그인 재시도 유도 |
| id_token 만료 | 401 | `EXPIRED_ID_TOKEN` | 카카오 재로그인부터 다시 |
| aud 불일치 | 401 | `INVALID_AUDIENCE` | 앱 설정 오류 — 로그 남기고 사용자에게 일반 오류 표시 |
| nonce 불일치 | 401 | `INVALID_NONCE` | 로그인 재시도 |
| 플랫폼 클레임 불일치 | 401 | `PLATFORM_MISMATCH` | 세션 폐기됨 — 강제 로그아웃 처리 |
| refresh 재사용 탐지 | 401 | `TOKEN_REUSE_DETECTED` | 전체 세션 폐기됨 — 강제 로그아웃 + 재로그인 유도 |
| JWKS 조회 실패 | 503 | `IDP_UNAVAILABLE` | 일시 오류 안내, 재시도 버튼 |

---

## 5. Flutter 클라이언트 요구사항

- `kakao_flutter_sdk_user` 사용. `loginWithKakaoTalk()` 실패(미설치·사용자 취소) 시 `loginWithKakaoAccount()`로 폴백.
- **`UserApi.instance.me()`를 호출하지 않는다.**
- 서버로는 `idToken`, `nonce`, `deviceId`만 전송한다.
- 자체 access 토큰은 메모리, refresh 토큰은 `flutter_secure_storage`에 보관한다. **`SharedPreferences` 사용 금지.**
- Dio `Interceptor`로 401 감지 → refresh 1회 시도 → 실패 시 로그인 화면으로 이동. **재시도 루프 방지 플래그 필수.**
- 동시에 여러 요청이 401을 받아도 refresh 호출은 **1회로 합류**시킨다 (Completer/Mutex).

---

## 6. 보안 규칙 (클라이언트 측)

- 카카오 `access_token` / `refresh_token`은 서버로 전송하지도, 앱 저장소에 영구 저장하지도 않는다.
- 자체 access 토큰은 메모리에만 — 앱 종료 시 사라지는 게 정상이다. refresh 토큰만 `flutter_secure_storage`.
- 로그에 `id_token`, 자체 JWT 원문, `email` 전체를 남기지 않는다.
- `nonce`는 매 로그인 시도마다 새로 생성한다 (재사용 금지).

---

## 7. 환경/설정

카카오 네이티브 앱 키·URL 스킴은 `.env` 같은 런타임 환경변수가 아니라
`android/app/src/main/AndroidManifest.xml`/`ios/Runner/Info.plist`에 직접 설정한다 —
[[flutter/_docs/flutter-android-harness\|Android 하네스]] / [[flutter/_docs/flutter-ios-harness\|iOS 하네스]] 참고.

이 네이티브 앱 키는 백엔드가 `aud` 검증에 쓰는 `KAKAO_NATIVE_APP_KEY`([[fastapi/_docs/flutter-kakao-oauth-harness\|백엔드 하네스]] §8)와 **같은 값**이어야 한다 — 다르면 모든 로그인 시도가 `INVALID_AUDIENCE`로 실패한다. 값이 일치하는지 구현 전에 확인한다.

백엔드 API 베이스 URL은 기존 프로젝트 방식(§0에서 확인한 환경별 설정)을 따른다. 새 설정
방식을 임의로 도입하지 않는다.

---

## 8. 테스트

원본 사양에 플러터 전용 테스트 체크리스트가 정의되어 있지 않다 — 임의로 항목을 확정하지
않는다. 구현 착수 시 최소한 아래는 `flutter test`로 검증 대상인지 사용자와 확인한다:

- 401 인터셉터의 재시도-루프 방지 동작
- 동시 다발 401에서 refresh 호출이 1회로 합류되는지
- refresh 실패 시 로그인 화면으로의 강제 이동

검증 방법은 [[.claude/rules/testing\|테스트 규칙]] — `flutter test` (+ `flutter analyze`).

---

## 9. 작업 순서 (플러터)

백엔드 §6/§4 API 계약이 확정된 뒤 착수하거나, 최소한 계약이 고정된 상태에서 병행한다.

1. Discovery(§0) 수행 후 결과 보고 → **승인받고 다음 단계 진행**
2. Kakao SDK 초기화 확인/추가 (네이티브 앱 키, URL 스킴 — §7)
3. 로그인 화면/버튼 + `loginWithKakaoTalk()` → `loginWithKakaoAccount()` 폴백
4. 서버 로그인 API 연동 (`idToken`/`nonce`/`deviceId` 전송, §4.1)
5. 토큰 저장(secure storage) + Dio 인터셉터(401 → refresh 1회 합류, §5)
6. 로그아웃 연동
7. 테스트 작성 (§8에서 합의된 범위)
8. 필요 시 환경별 설정·README 갱신

각 단계 완료 시 **변경 파일 목록과 핵심 결정 사항을 요약 보고**한다.

---

## 10. 금지 사항 요약 (플러터)

- ❌ `UserApi.instance.me()` 결과를 서버로 전송
- ❌ 카카오 `access_token`을 서버로 전송 (서버측 신원 확인 시도)
- ❌ 카카오 `refresh_token`을 서버로 전송/저장 요청
- ❌ `SharedPreferences`에 토큰 저장
- ❌ 재시도 루프 방지 없이 401 인터셉터 구현
- ❌ 동시 요청마다 refresh를 각각 호출 (합류 없이 중복 호출)
- ❌ 웹 전용 엔드포인트를 모바일 코드에서 호출
- ❌ 시크릿·토큰 원문 로깅
- ❌ 테스트 없이 완료 보고

---

## 관련 문서

[[flutter/CLAUDE\|Flutter CLAUDE]] · [[flutter/_docs/flutter-android-harness\|Android 하네스]] · [[flutter/_docs/flutter-ios-harness\|iOS 하네스]] · [[fastapi/_docs/flutter-kakao-oauth-harness\|백엔드 인증 하네스(짝 문서)]]
