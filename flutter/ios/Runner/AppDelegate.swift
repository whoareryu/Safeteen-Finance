import Flutter
import UIKit
import UserNotifications

private let stopwatchChannelName = "cloud.whoareryu.saessak/stopwatch"
private let timerChannelName = "cloud.whoareryu.saessak/timer"
private let alarmChannelName = "cloud.whoareryu.saessak/alarm"

@main
@objc class AppDelegate: FlutterAppDelegate, FlutterImplicitEngineDelegate {
  private let stopwatch = StopwatchActivity()
  private let timer = TimerActivity()

  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    UNUserNotificationCenter.current().delegate = self
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  // 타이머/알람 알림이 앱이 켜져 있는 동안에도(포그라운드) 배너·소리로 보이게 한다.
  // FlutterAppDelegate가 이미 UNUserNotificationCenterDelegate를 채택하고 있어 override로 재정의한다.
  override func userNotificationCenter(
    _ center: UNUserNotificationCenter,
    willPresent notification: UNNotification,
    withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
  ) {
    completionHandler([.alert, .sound])
  }

  func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
    GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)

    let messenger = engineBridge.applicationRegistrar.messenger()
    setUpStopwatchChannel(messenger: messenger)
    setUpTimerChannel(messenger: messenger)
    setUpAlarmChannel(messenger: messenger)
  }

  private func setUpStopwatchChannel(messenger: FlutterBinaryMessenger) {
    let channel = FlutterMethodChannel(name: stopwatchChannelName, binaryMessenger: messenger)
    channel.setMethodCallHandler { [weak self] call, result in
      guard let self else { return }
      switch call.method {
      case "start":
        self.stopwatch.start()
        result(nil)
      case "stop":
        self.stopwatch.stop()
        result(nil)
      case "reset":
        self.stopwatch.reset()
        result(nil)
      case "elapsed":
        result(self.stopwatch.elapsedMilliseconds)
      default:
        result(FlutterMethodNotImplemented)
      }
    }
  }

  private func setUpTimerChannel(messenger: FlutterBinaryMessenger) {
    let channel = FlutterMethodChannel(name: timerChannelName, binaryMessenger: messenger)
    channel.setMethodCallHandler { [weak self] call, result in
      guard let self else { return }
      switch call.method {
      case "setDuration":
        let args = call.arguments as? [String: Any]
        let seconds = args?["seconds"] as? Int ?? 0
        self.timer.setDuration(seconds: seconds)
        result(nil)
      case "start":
        self.timer.start()
        result(nil)
      case "pause":
        self.timer.pause()
        result(nil)
      case "cancel":
        self.timer.cancel()
        result(nil)
      case "remaining":
        result(self.timer.remainingMilliseconds)
      default:
        result(FlutterMethodNotImplemented)
      }
    }
  }

  private func setUpAlarmChannel(messenger: FlutterBinaryMessenger) {
    let channel = FlutterMethodChannel(name: alarmChannelName, binaryMessenger: messenger)
    channel.setMethodCallHandler { call, result in
      switch call.method {
      case "requestPermission":
        AlarmActivity.requestAuthorization { granted in
          result(granted)
        }
      case "schedule":
        guard let args = call.arguments as? [String: Any],
          let id = args["id"] as? String,
          let hour = args["hour"] as? Int,
          let minute = args["minute"] as? Int,
          let label = args["label"] as? String
        else {
          result(
            FlutterError(code: "invalid_args", message: "id/hour/minute/label이 필요합니다", details: nil))
          return
        }
        AlarmActivity.schedule(id: id, hour: hour, minute: minute, label: label)
        result(nil)
      case "cancel":
        guard let args = call.arguments as? [String: Any], let id = args["id"] as? String else {
          result(FlutterError(code: "invalid_args", message: "id가 필요합니다", details: nil))
          return
        }
        AlarmActivity.cancel(id: id)
        result(nil)
      default:
        result(FlutterMethodNotImplemented)
      }
    }
  }
}
