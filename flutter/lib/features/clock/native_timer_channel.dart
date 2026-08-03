// ios/Runner/counter/TimerActivity.swift와 연결되는 MethodChannel 클라이언트.

import 'package:flutter/services.dart';

class NativeTimerChannel {
  static const _channel = MethodChannel('cloud.whoareryu.saessak/timer');

  Future<void> setDuration(Duration duration) =>
      _channel.invokeMethod('setDuration', {'seconds': duration.inSeconds});

  Future<void> start() => _channel.invokeMethod('start');

  Future<void> pause() => _channel.invokeMethod('pause');

  Future<void> cancel() => _channel.invokeMethod('cancel');

  Future<Duration> remaining() async {
    final ms = await _channel.invokeMethod<int>('remaining');
    return Duration(milliseconds: ms ?? 0);
  }
}
