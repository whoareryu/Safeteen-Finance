// ios/Runner/counter/AlarmActivity.swift와 연결되는 MethodChannel 클라이언트.
// 알람은 UNUserNotificationCenter의 매일 반복 캘린더 트리거로 예약되므로,
// 앱이 꺼져 있어도(백그라운드/종료) 실제로 울린다.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class NativeAlarmChannel {
  static const _channel = MethodChannel('cloud.whoareryu.saessak/alarm');

  Future<bool> requestPermission() async {
    final granted = await _channel.invokeMethod<bool>('requestPermission');
    return granted ?? false;
  }

  Future<void> schedule({
    required String id,
    required TimeOfDay time,
    required String label,
  }) =>
      _channel.invokeMethod('schedule', {
        'id': id,
        'hour': time.hour,
        'minute': time.minute,
        'label': label,
      });

  Future<void> cancel(String id) => _channel.invokeMethod('cancel', {'id': id});
}
