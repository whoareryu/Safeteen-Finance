// ios/Runner/counter/StopwatchActivity.swift와 연결되는 MethodChannel 클라이언트.
// 시간 측정(시작/중단/리셋/경과시간)은 네이티브가 담당하고, 랩 목록 관리는 Dart 쪽(StopwatchScreen)에 남긴다.

import 'package:flutter/services.dart';

class NativeStopwatchChannel {
  static const _channel = MethodChannel('cloud.whoareryu.saessak/stopwatch');

  Future<void> start() => _channel.invokeMethod('start');

  Future<void> stop() => _channel.invokeMethod('stop');

  Future<void> reset() => _channel.invokeMethod('reset');

  Future<Duration> elapsed() async {
    final ms = await _channel.invokeMethod<int>('elapsed');
    return Duration(milliseconds: ms ?? 0);
  }
}
