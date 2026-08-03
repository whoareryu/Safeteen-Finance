import Foundation
import UserNotifications

/// 알람은 스톱워치·타이머와 달리 "지금 흐르는 시간"이 아니라 "매일 특정 시각에 반복 발생하는
/// 예약"이라 CFAbsoluteTime 엔진이 아니라 UNUserNotificationCenter의 캘린더 트리거를 그대로 쓴다.
/// 알람 id는 Dart 쪽에서 화면에 표시하는 리스트의 정체성과 그대로 맞춰서 전달받는다.
enum AlarmActivity {
  static func requestAuthorization(completion: @escaping (Bool) -> Void) {
    UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) {
      granted, _ in
      DispatchQueue.main.async { completion(granted) }
    }
  }

  static func schedule(id: String, hour: Int, minute: Int, label: String) {
    let content = UNMutableNotificationContent()
    content.title = label
    content.body = "알람"
    content.sound = .default

    var dateComponents = DateComponents()
    dateComponents.hour = hour
    dateComponents.minute = minute

    let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)
    let request = UNNotificationRequest(identifier: id, content: content, trigger: trigger)
    UNUserNotificationCenter.current().add(request)
  }

  static func cancel(id: String) {
    UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: [id])
  }
}
