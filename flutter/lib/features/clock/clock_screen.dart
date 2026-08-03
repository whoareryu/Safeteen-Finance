// iOS 시계 앱 전체를 참고한 컨테이너 — 세계시계·알람·스톱워치·타이머 4개를 내부 탭으로 묶는다.
// 메인 셸의 하단 탭 하나("시계") 안에 또 하나의 하단 탭바가 중첩되는 구조.

import 'package:flutter/material.dart';

import '../stopwatch/stopwatch_screen.dart';
import 'alarm_screen.dart';
import 'timer_screen.dart';
import 'world_clock_screen.dart';

class ClockScreen extends StatefulWidget {
  const ClockScreen({super.key});

  @override
  State<ClockScreen> createState() => _ClockScreenState();
}

class _ClockScreenState extends State<ClockScreen> {
  int _subTab = 2; // 스크린샷과 동일하게 스톱워치를 기본으로 보여준다.

  static const _screens = [
    WorldClockScreen(),
    AlarmScreen(),
    StopwatchScreen(),
    TimerScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _subTab, children: _screens),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _subTab,
        onTap: (i) => setState(() => _subTab = i),
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.public), label: '세계 시계'),
          BottomNavigationBarItem(icon: Icon(Icons.alarm), label: '알람'),
          BottomNavigationBarItem(icon: Icon(Icons.timer_outlined), label: '스톱워치'),
          BottomNavigationBarItem(icon: Icon(Icons.hourglass_empty), label: '타이머'),
        ],
      ),
    );
  }
}
