import Foundation

/// 순수 네이티브 스톱워치 엔진. Flutter/MethodChannel을 전혀 모르는 채로 시간 측정만 책임진다
/// (SRP) — Flutter 쪽 연결은 AppDelegate의 채널 핸들러에서 담당한다.
final class StopwatchActivity {
  private var startTime: CFAbsoluteTime?
  private var accumulatedSeconds: CFAbsoluteTime = 0

  private(set) var isRunning = false

  func start() {
    guard !isRunning else { return }
    startTime = CFAbsoluteTimeGetCurrent()
    isRunning = true
  }

  func stop() {
    guard isRunning, let start = startTime else { return }
    accumulatedSeconds += CFAbsoluteTimeGetCurrent() - start
    startTime = nil
    isRunning = false
  }

  func reset() {
    startTime = nil
    accumulatedSeconds = 0
    isRunning = false
  }

  var elapsedMilliseconds: Int {
    var seconds = accumulatedSeconds
    if isRunning, let start = startTime {
      seconds += CFAbsoluteTimeGetCurrent() - start
    }
    return Int(seconds * 1000)
  }
}
