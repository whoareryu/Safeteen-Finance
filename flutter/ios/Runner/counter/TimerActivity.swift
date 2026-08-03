import Foundation
import UserNotifications

/// 카운트다운 타이머 엔진. StopwatchActivity와 같은 CFAbsoluteTime 기반 정밀 측정이지만
/// 거꾸로 줄어든다. 앱이 백그라운드로 가도 종료 시각에 로컬 알림이 울리도록
/// UNUserNotificationCenter에 1회성 알림을 같이 예약한다(포그라운드 표시는 Dart가 폴링).
final class TimerActivity {
  private static let notificationId = "cloud.whoareryu.saessak.timer.finished"

  private var totalSeconds: TimeInterval = 0
  private var remainingAtPause: TimeInterval = 0
  private var startTime: CFAbsoluteTime?
  private(set) var isRunning = false

  func setDuration(seconds: Int) {
    totalSeconds = TimeInterval(seconds)
    remainingAtPause = totalSeconds
    startTime = nil
    isRunning = false
  }

  func start() {
    guard !isRunning, remainingAtPause > 0 else { return }
    startTime = CFAbsoluteTimeGetCurrent()
    isRunning = true
    scheduleFinishNotification(after: remainingAtPause)
  }

  func pause() {
    guard isRunning, let start = startTime else { return }
    remainingAtPause = max(0, remainingAtPause - (CFAbsoluteTimeGetCurrent() - start))
    startTime = nil
    isRunning = false
    cancelFinishNotification()
  }

  func cancel() {
    totalSeconds = 0
    remainingAtPause = 0
    startTime = nil
    isRunning = false
    cancelFinishNotification()
  }

  var remainingMilliseconds: Int {
    var remaining = remainingAtPause
    if isRunning, let start = startTime {
      remaining -= CFAbsoluteTimeGetCurrent() - start
    }
    return max(0, Int(remaining * 1000))
  }

  private func scheduleFinishNotification(after seconds: TimeInterval) {
    guard seconds > 0 else { return }
    let content = UNMutableNotificationContent()
    content.title = "타이머 종료"
    content.body = "설정한 타이머가 끝났습니다."
    content.sound = .default

    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: seconds, repeats: false)
    let request = UNNotificationRequest(
      identifier: Self.notificationId, content: content, trigger: trigger)
    UNUserNotificationCenter.current().add(request)
  }

  private func cancelFinishNotification() {
    UNUserNotificationCenter.current().removePendingNotificationRequests(
      withIdentifiers: [Self.notificationId])
  }
}
