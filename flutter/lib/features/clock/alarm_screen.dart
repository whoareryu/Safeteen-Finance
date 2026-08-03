// iOS 시계 앱의 "알람" 탭 참고. 실제 알람은 ios/Runner/counter/AlarmActivity.swift가
// UNUserNotificationCenter 매일 반복 트리거로 예약하므로, 앱이 꺼져 있어도 울린다.
// 목록 자체(라벨·on/off·삭제)는 Dart가 관리하고, 매 변경마다 네이티브에 schedule/cancel만 알린다.
// 목록은 앱을 재시작하면 초기화된다(비영속) — 영속 저장이 필요하면 알려줘.

import 'package:flutter/material.dart';

import 'native_alarm_channel.dart';

class _Alarm {
  _Alarm({required this.id, required this.time, required this.label});
  final String id;
  TimeOfDay time;
  String label;
  bool enabled = true;
}

class AlarmScreen extends StatefulWidget {
  const AlarmScreen({super.key});

  @override
  State<AlarmScreen> createState() => _AlarmScreenState();
}

class _AlarmScreenState extends State<AlarmScreen> {
  final _native = NativeAlarmChannel();
  final List<_Alarm> _alarms = [
    _Alarm(id: 'seed-wake', time: const TimeOfDay(hour: 7, minute: 0), label: '기상'),
  ];

  @override
  void initState() {
    super.initState();
    _native.requestPermission().then((granted) {
      if (granted) {
        for (final alarm in _alarms.where((a) => a.enabled)) {
          _native.schedule(id: alarm.id, time: alarm.time, label: alarm.label);
        }
      }
    });
  }

  Future<void> _addAlarm() async {
    final time = await showTimePicker(context: context, initialTime: TimeOfDay.now());
    if (time == null) return;
    final alarm = _Alarm(id: DateTime.now().microsecondsSinceEpoch.toString(), time: time, label: '알람');
    setState(() => _alarms.add(alarm));
    final granted = await _native.requestPermission();
    if (granted) {
      await _native.schedule(id: alarm.id, time: alarm.time, label: alarm.label);
    }
  }

  void _toggleAlarm(_Alarm alarm, bool enabled) {
    setState(() => alarm.enabled = enabled);
    if (enabled) {
      _native.schedule(id: alarm.id, time: alarm.time, label: alarm.label);
    } else {
      _native.cancel(alarm.id);
    }
  }

  void _removeAlarm(int index) {
    final alarm = _alarms[index];
    _native.cancel(alarm.id);
    setState(() => _alarms.removeAt(index));
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      floatingActionButton: FloatingActionButton(
        heroTag: 'alarmAddFab',
        onPressed: _addAlarm,
        child: const Icon(Icons.add),
      ),
      body: _alarms.isEmpty
          ? Center(
              child: Text('오른쪽 아래 + 버튼으로 알람을 추가해 보세요',
                  style: TextStyle(color: scheme.onSurfaceVariant)),
            )
          : ListView.separated(
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: _alarms.length,
              separatorBuilder: (_, _) => Divider(height: 1, color: scheme.outlineVariant),
              itemBuilder: (_, i) {
                final alarm = _alarms[i];
                return ListTile(
                  title: Text(
                    alarm.time.format(context),
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.w300,
                      color: alarm.enabled ? null : scheme.onSurfaceVariant,
                    ),
                  ),
                  subtitle: Text(alarm.label),
                  trailing: Switch(
                    value: alarm.enabled,
                    onChanged: (v) => _toggleAlarm(alarm, v),
                  ),
                  onLongPress: () => _removeAlarm(i),
                );
              },
            ),
    );
  }
}
