# Flutter — 안드로이드 실제 기기 연동 가이드

개발 환경: macOS · Flutter 3.44.2 (stable) · Dart 3.12.2

실제 안드로이드 기기를 Flutter 개발 PC(macOS)에 연결하는 방법. USB 연결과 Wi-Fi 무선
디버깅 두 가지를 다룬다. (USB는 폰의 데이터 케이블과 개발 PC 간의 물리적 연결을 뜻한다.)

> 옛 가이드(구 API 25 이하 대응, Windows 전용 Google USB Driver 설치 등)는 현재 실기기
> 환경과 맞지 않아 제외했다 — 아래는 2026년 기준 최신 절차다.

---

## 1. 개발자 옵션 활성화 (기기 공통, USB·Wi-Fi 공통 선행 작업)

1. **설정 → 휴대전화 정보 → 빌드 번호**를 7번 연속 탭한다.
   (제조사 UI에 따라 [설정 → 시스템 → 휴대전화 정보] 경로일 수 있다.)
   "이제 개발자입니다" 토스트가 뜨면 **설정 → 시스템 → 개발자 옵션**이 새로 나타난다.
2. **개발자 옵션 → USB 디버깅**을 켠다.

---

## 2. USB로 연결하기

**macOS는 별도 USB 드라이버 설치가 필요 없다** — Google USB Driver는 Windows 전용이며,
macOS·Linux·ChromeOS에서는 케이블 연결만으로 기기가 인식된다
([공식 안내](https://developer.android.com/studio/run/device)).

1. USB 케이블로 기기와 맥을 연결한다.
2. 기기 화면에 "USB 디버깅을 허용하시겠습니까?" RSA 키 승인 다이얼로그가 뜨면 허용한다
   (Android 4.2.2/API 17 이상 필수 보안 절차 — 한 번 허용하면 같은 PC에서는 재확인 없이 인식된다).
3. 터미널에서 인식 여부를 확인한다.

   ```bash
   adb devices
   ```

4. Android Studio 실행 기기 드롭다운(또는 `flutter devices`)에서 연결된 기기를 선택하고 실행한다.

   ```bash
   flutter devices
   flutter run -d <device-id>
   ```

### 연결이 안 될 때

- Android Studio: **Tools → Troubleshoot Device Connections**로 USB 인식 → 디버깅 활성화 →
  ADB 서버 상태를 단계별로 점검할 수 있다.
- 케이블을 충전 전용이 아닌 데이터 전송 지원 케이블로 교체해본다.
- `adb kill-server && adb start-server`로 ADB 서버를 재시작해본다.

---

## 3. Wi-Fi 무선 디버깅 (Android 11 이상 권장 방식)

Android 11(API 30)부터는 최초 USB 연결 없이도 개발자 옵션 안의 **무선 디버깅** 기능으로
바로 페어링할 수 있다. (구버전 방식인 `adb tcpip 5555` + USB 최초 연결은 더 이상 필요 없다.)

**요구 사항**
- 기기: Android 11 이상
- 개발 PC와 기기가 **같은 Wi-Fi 네트워크**에 연결돼 있어야 함
- Android Studio 최신 버전 + Android SDK Platform Tools 최신 버전

**절차**

1. 기기: **설정 → 개발자 옵션 → 무선 디버깅**을 켠다.
2. Android Studio: **Device Manager**(또는 실행 기기 드롭다운) → **"Pair Devices Using Wi-Fi"** 선택.
3. 페어링 방식 중 하나를 고른다.
   - **QR 코드 방식(권장):** Android Studio에 뜨는 QR 코드를 기기의 "QR 코드로 기기 페어링"
     화면으로 스캔.
   - **페어링 코드 방식:** 기기에서 "페어링 코드로 기기 페어링"을 선택하면 6자리 코드가
     표시되고, Android Studio에 해당 코드를 입력.
4. 페어링이 끝나면 기기가 Android Studio 실행 기기 목록에 나타난다. 이후에는 같은 Wi-Fi에
   있는 한 케이블 없이 계속 빌드·실행할 수 있다.
5. 처음 연결할 때 "이 네트워크에서 무선 디버깅 허용" 다이얼로그가 뜨면 **"이 네트워크에서 항상
   허용"**을 체크해두면 다음부터 자동으로 재연결된다.

**페어링 해제**
- 기기: 설정 → 개발자 옵션 → 무선 디버깅 → 페어링된 기기 → 해당 PC 이름 → "삭제", 또는
- 개발자 옵션 → "adb 디버깅 승인 취소"로 전체 초기화.

---

## 4. 참고 공식 문서

- Android 실제 기기 연결(USB/Wi-Fi, 문제 해결): https://developer.android.com/studio/run/device
- 개발자 옵션 활성화: https://developer.android.com/studio/debug/dev-options
- adb 무선 디버깅 문제 해결: https://developer.android.com/tools/adb#wireless-android11-troubleshoot
