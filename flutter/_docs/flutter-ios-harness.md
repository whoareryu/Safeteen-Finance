# Flutter — iOS 실제 기기 연동 가이드

개발 환경: macOS (iOS 개발은 macOS 필수) · Flutter 3.44.2 (stable) · Dart 3.12.2 · Xcode 최신 버전

실제 아이폰을 Flutter 개발 맥에 연결해서 앱을 실행하는 방법. (USB는 폰의 데이터 케이블과
개발 PC 간의 물리적 연결을 뜻한다.)

> 옛 가이드의 Apple Silicon용 `ffi` 재설치 워크어라운드와 iOS 14 릴리즈 모드 전환 노트는
> 현재 CocoaPods·Xcode 버전에서는 더 이상 필요 없어 제외했다 — 아래는 2026년 기준 최신 절차다.

---

## 1. Xcode 준비

1. App Store에서 **Xcode**를 최신 버전으로 설치(또는 업데이트)한다.
2. 커맨드라인 도구 경로를 설정하고 최초 실행을 완료한다.

   ```bash
   sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
   sudo xcodebuild -runFirstLaunch
   ```

3. 라이선스에 동의한다.

   ```bash
   sudo xcodebuild -license
   ```

4. iOS 시뮬레이터/플랫폼 지원 파일을 받는다.

   ```bash
   xcodebuild -downloadPlatform iOS
   ```

---

## 2. CocoaPods 설치

Flutter 플러그인이 네이티브 iOS 코드를 쓰는 경우 CocoaPods가 필요하다.

```bash
sudo gem install cocoapods
# 이미 설치돼 있다면
sudo gem install cocoapods --upgrade
```

Apple Silicon(M1 이후)에서도 위 명령만으로 설치된다 — 과거 알려졌던 `ffi` gem 재설치
워크어라운드는 현재 CocoaPods 버전에서는 필요 없다. 시스템 Ruby 관련 권한 문제가 계속되면
Homebrew로 별도 Ruby를 설치한 뒤 그 Ruby로 `gem install cocoapods`를 실행한다
(`brew install ruby`).

---

## 3. 아이폰을 맥에 연결하고 신뢰하기

1. USB 케이블로 아이폰을 맥에 연결한다.
2. 아이폰에 "이 컴퓨터를 신뢰하시겠습니까?" 알림이 뜨면 **[신뢰]**를 누른다.

---

## 4. Developer Mode 활성화 (iOS 16 이상 필수)

Apple의 악성 소프트웨어 방지 정책으로 iOS 16부터는 기기에서 개발자 모드를 별도로 켜야 한다.

1. 아이폰: **설정 → 개인정보 보호 및 보안 → 개발자 모드**를 켠다.
2. 기기가 재시작되면 "개발자 모드를 켜시겠습니까?" 다이얼로그에서 **켜기**를 선택하고 잠금
   해제 비밀번호를 입력한다.

**"개발자 모드" 메뉴 자체가 안 보이는 경우**: 아이폰을 맥에 연결한 상태에서 Xcode를 실행하거나
`flutter run`을 한 번 시도하면 기기 구성이 초기화되면서 메뉴가 나타난다. 그 후 위 절차를 다시
진행한다.

---

## 5. 코드 서명 (Signing & Capabilities)

1. 프로젝트의 `ios/Runner.xcworkspace`를 Xcode로 연다.

   ```bash
   open ios/Runner.xcworkspace
   ```

2. 좌측에서 **Runner** 프로젝트 → TARGETS의 **Runner** → **Signing & Capabilities** 탭을 선택한다.
3. **Bundle Identifier**를 고유한 값으로 바꾼다. 실기기·심사에 등록된 다른 앱과 겹치면 안
   되므로, 연습용이면 `com.<본인 영문 이름>.<임의 단어>` 형태로 지정한다.
4. **Automatically manage signing**을 체크한다.
5. **Team**에서 Apple ID 계정을 선택한다(없으면 로그인). 개인 무료 Apple Developer 계정으로도
   실기기 테스트 빌드는 가능하다 — App Store 배포에는 유료 Apple Developer Program 등록이 필요하다.
6. 최초 실행 시 아이폰에서 **설정 → 일반 → VPN 및 기기 관리**로 들어가 개발자 앱 인증서를
   **[신뢰]**해야 앱이 실행된다.

---

## 6. 실기기에서 실행

```bash
flutter devices
flutter run -d <device-id>
```

---

## 7. 알려진 이슈

| 증상 | 원인 | 해결 |
|------|------|------|
| `Xcode not found` | 커맨드라인 도구 경로 미설정 | `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer` |
| 개발자 모드 메뉴가 안 보임 | 기기 구성 미완료 | 기기 연결 후 Xcode/`flutter run` 한 번 실행 → 재확인 |
| 코드 서명 오류 | 기기에서 인증서 미신뢰 | 설정 → VPN 및 기기 관리 → 인증서 [신뢰] |
| macOS 키체인 접근 요청 반복 | codesign 키체인 권한 | 맥 비밀번호 입력 후 "항상 허용" 선택 |
| CocoaPods 의존성 오류 | Pod 캐시/버전 불일치 | `pod repo update` 또는 `flutter clean` 후 재실행 |

---

## 8. 참고 공식 문서

- iOS 개발 환경 설정: https://docs.flutter.dev/platform-integration/ios/setup
- iOS 앱 빌드 및 배포: https://docs.flutter.dev/deployment/ios
- iOS 디버깅 활성화: https://docs.flutter.dev/platform-integration/ios/ios-debugging