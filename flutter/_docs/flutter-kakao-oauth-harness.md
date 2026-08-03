# 카카오 소셜 로그인 인증 모듈 — 플러터 클라이언트 (구현 완료)

> 원래 그린필드 전제로 쓴 사양이었으나, 백엔드 구현 과정에서 API 계약이 바뀌어
> (snake_case, `/auth/mobile/*` 경로, 동의 화면 추가) 실제 구현 기준으로 다시 썼다.
>
> 짝 문서: [[fastapi/_docs/flutter-kakao-oauth-harness\|백엔드 인증 하네스]]

---

## 1. 목표

Flutter는 카카오 SDK로 로그인해 `id_token`을 얻고, `auth.whoareryu.cloud`(백엔드 §2)에
전달해 자체 access/refresh JWT를 받는다. **Flutter는 신원을 직접 검증하지 않는다.**

---

## 2. 실제 구현 파일

```
flutter/lib/
├── auth.dart                          # KakaoLoginScreen — 카카오 로그인 버튼 화면
└── features/auth/
    ├── auth_api.dart                  # 백엔드 호출 (plant_api.dart와 동일 스타일)
    ├── auth_models.dart                # AuthTokens, MobileLoginResult
    ├── auth_session_store.dart         # flutter_secure_storage 래퍼 (refresh token, device_id)
    ├── auth_session.dart               # 메모리 access token + 401→refresh 단일-비행 게이트
    └── consent_screen.dart             # 신규 유저 닉네임+약관동의 화면
```

`pubspec.yaml`: `kakao_flutter_sdk_user`, `flutter_secure_storage`, `uuid`,
`kakao_flutter_sdk_common`(명시적 direct dependency — `depend_on_referenced_packages` 린트 때문에 추가).

---

## 3. 로그인 흐름 (실제 구현)

```dart
// lib/auth.dart
final nonce = _generateNonce();  // Random.secure() → base64Url, 새 패키지 불필요
OAuthToken token;
try {
  token = await UserApi.instance.loginWithKakaoTalk(nonce: nonce);
} catch (_) {
  token = await UserApi.instance.loginWithKakaoAccount(nonce: nonce);
}
final result = await loginWithKakao(idToken: token.idToken!, nonce: nonce, deviceId: deviceId);

if (result.requiresConsent) {
  // → ConsentScreen(consentToken, suggestedNickname, deviceId)
} else {
  // → MainShell (기존 유저, 바로 로그인)
}
```

- **`UserApi.instance.me()`는 호출하지 않는다** (서버가 클라이언트 프로필을 신뢰하지 않는다는 원칙).
- 신규 유저는 `ConsentScreen`에서 닉네임 확인 + 약관 동의 후 `completeConsent()` 호출 →
  성공 시 `MainShell`로 이동. (하네스 원안엔 없던 화면 — 사용자가 "동의 화면도 같이 만들어야
  함"으로 결정.)

---

## 4. API 계약 — snake_case (하네스 원안의 camelCase 아님)

백엔드가 `apps/auth/schemas.py`의 기존 snake_case 컨벤션(`consent_token`, `agree_terms`
등)을 따르고 있어서 모바일 API도 그것에 맞췄다.

| 엔드포인트 | 요청 | 응답(성공) |
|---|---|---|
| `POST /auth/mobile/kakao/login` | `{id_token, nonce, device_id}` | `{status, access_token?, refresh_token?, ..., consent_token?, suggested_nickname?}` |
| `POST /auth/mobile/consent/complete` | `{consent_token, nickname, agree_terms, device_id}` | `{access_token, refresh_token, token_type, expires_in}` |
| `POST /auth/mobile/refresh` | `{refresh_token}` | `{access_token, refresh_token, token_type, expires_in}` |
| `POST /auth/mobile/logout` | `Authorization: Bearer <access_token>` | 204 |

베이스 URL: `https://auth.whoareryu.cloud/auth/mobile` (plant_api.dart가 쓰는
`api.whoareryu.cloud`와 **다른 호스트** — auth 서비스가 토큰 발급 전용으로 분리돼 있어서).

### 에러 처리 — `X-Error-Code` 응답 헤더로 분기

백엔드가 `detail`은 한국어 문자열(기존 관례), 머신 판별용 코드는 `X-Error-Code` 헤더로
따로 준다. `auth_api.dart::AuthApiException`이 `res.headers['x-error-code']`를 읽어
`errorCode` 필드에 담는다 — JSON 바디 안에 `code` 필드가 있는 게 아니다.

---

## 5. 세션 유지 — `main.dart`의 `_goToApp()`

```dart
Future<void> _goToApp() async {
  if (_navigated) return;
  _navigated = true;
  final hasSession = await AuthSessionStore.hasRefreshToken();  // 로컬만 확인, 네트워크 없음
  Navigator.of(context).pushReplacement(MaterialPageRoute(
    builder: (_) => hasSession ? const MainShell() : const KakaoLoginScreen(),
  ));
}
```

- 세션 유효성(만료·로테이션·블랙리스트)은 여기서 확인하지 않는다 — `MainShell` 진입 후
  첫 인증 API 호출에서 401→refresh로 지연 확인된다(§6).
- 인트로 영상은 실측 4.01초(`ffprobe`)라 기존 `_onTick`(영상 종료 리스너)이 이미 자연스럽게
  ~4초에 `_goToApp()`을 호출한다 — 별도 4초 타이머는 추가하지 않았다. 기존 6초 안전장치
  타이머(영상 초기화 실패 대비)도 그대로 둠, 목적이 다름.
- `_MainShell` → `MainShell`(public)로 이름만 바꿈 — `auth.dart`/`consent_screen.dart`가
  참조해야 해서. `lib/auth.dart`가 `main.dart`를 `show MainShell`로 import하고, `main.dart`도
  `auth.dart`를 import한다 — Dart는 라이브러리 간 순환 import를 허용하므로 문제없다.

---

## 6. 401 → refresh (Dio 없이, `http` 패키지)

프로젝트에 Dio 사용 이력이 전혀 없어(`plant_api.dart` 포함 전부 `http`) 이번에도 Dio를
새로 들이지 않았다. `AuthSession.authorizedRequest()`가 `Completer` 기반으로 401을 처리한다:

```dart
static Future<http.Response> authorizedRequest(
  Future<http.Response> Function(String? accessToken) send,
) async {
  final res = await send(_accessToken);
  if (res.statusCode != 401) return res;
  final refreshed = await _refreshOnce();  // 동시 요청은 이 Completer에 합류
  if (refreshed == null) { await forceLogout(); return res; }
  return send(refreshed);  // 정확히 1회만 재시도
}
```

- `forceLogout()`은 `navigatorKey`(전역 `GlobalKey<NavigatorState>`, `auth_session.dart`에
  정의)로 `/auth` 라우트(`kLoginRouteName`)로 강제 이동한다. `main.dart`의 `MaterialApp`에
  `navigatorKey`와 `routes: {kLoginRouteName: (_) => const KakaoLoginScreen()}`를 등록.

참고: `kakao_flutter_sdk_user`가 내부적으로 `dio`를 transitive dependency로 끌고 오지만
(카카오 SDK 자체 구현), **우리 앱 코드(auth_api.dart 등)는 여전히 `http` 패키지만 쓴다** —
카카오 SDK 내부 구현과는 무관.

---

## 7. 토큰 저장

- 액세스 토큰: 메모리만(`AuthSession._accessToken`, static 필드) — 앱 재시작하면 사라짐, 정상.
- 리프레시 토큰 + device_id: `flutter_secure_storage`(`AuthSessionStore`). **`SharedPreferences` 사용 안 함.**

---

## 8. iOS 네이티브 설정 (완료) — Android는 미착수

카카오 콘솔에 Android 플랫폼이 아직 등록 안 돼 있어(`applicationId`도 `com.example.taper`
placeholder 그대로) 이번엔 **iOS만** 구현했다.

- `Info.plist`에 `CFBundleURLTypes`(scheme `kakao{NATIVE_APP_KEY}`) + `LSApplicationQueriesSchemes`
  (`kakaokompassauth`, `kakaolink`, `kakaoplus`) 추가 — `REPLACE_WITH_KAKAO_NATIVE_APP_KEY`
  플레이스홀더로 되어 있음, 실값 확인되면 여기와 `lib/main.dart`의 `KakaoSdk.init()` 둘 다 교체해야 함(반드시 동일한 값).
- **`AppDelegate.swift`는 수정 안 함.** `kakao_flutter_sdk_auth` 플러그인이
  `registrar.addApplicationDelegate(instance)`/`addSceneDelegate(instance)`로 URL 콜백
  처리를 자체 등록한다(`KakaoFlutterSdkAuthPlugin.swift` 확인함) — 하네스 원안이 가정한
  수동 `application(_:open:options:)` 오버라이드는 이 플러그인 버전(2.0.0+1)에서는 불필요.
- `main()`에서 `WidgetsFlutterBinding.ensureInitialized()` 후 `await KakaoSdk.init(nativeAppKey: '...')`.
- Android(`AndroidManifest.xml`, `applicationId` 정정 포함)는 **미완성 — 후속 작업.**

---

## 9. 테스트

`flutter analyze` — 클린 통과 확인. `flutter build ios --release --no-codesign`으로 pod
install + 네이티브 컴파일까지 확인함. 실기기 로그인 E2E는 `KAKAO_NATIVE_APP_KEY` 실값이
채워져야 가능 — 아직 미완.

---

## 10. 알려진 갭

- `KAKAO_NATIVE_APP_KEY` 실값 미입력(`main.dart`/`Info.plist` 둘 다 플레이스홀더).
- Android 전체(콘솔 등록, `applicationId` 정정, `AndroidManifest.xml`) 미착수.
- 로그아웃 UI 없음 — `logoutSession()` API 클라이언트 함수는 있지만 호출하는 화면이 아직 없다
  (`MainShell`의 "마이페이지"가 현재 `ComingSoonScreen`).

---

## 관련 문서

[[flutter/CLAUDE\|Flutter CLAUDE]] · [[flutter/_docs/flutter-android-harness\|Android 하네스]] · [[flutter/_docs/flutter-ios-harness\|iOS 하네스]] · [[fastapi/_docs/flutter-kakao-oauth-harness\|백엔드 인증 하네스(짝 문서)]]
