// iOS 시계 앱의 "타이머" 탭 참고. 카운트다운 정밀 측정은 네이티브
// (ios/Runner/counter/TimerActivity.swift)가 담당하고, 종료 시각에는 네이티브가 로컬 알림도
// 예약해 앱이 백그라운드에 있어도 울린다 — Dart는 1초 주기로 남은 시간을 폴링해 화면만 갱신한다.

import 'dart:async';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

import 'native_timer_channel.dart';

class TimerScreen extends StatefulWidget {
  const TimerScreen({super.key});

  @override
  State<TimerScreen> createState() => _TimerScreenState();
}

class _TimerScreenState extends State<TimerScreen> {
  final _native = NativeTimerChannel();

  Duration _picked = const Duration(minutes: 5);
  Duration _remaining = Duration.zero;
  Timer? _ticker;
  bool _running = false;
  bool _started = false;
  bool _finished = false;

  bool get _isCounting => _started || _running;

  Future<void> _pollRemaining() async {
    final remaining = await _native.remaining();
    if (!mounted) return;
    setState(() {
      _remaining = remaining;
      if (_remaining <= Duration.zero) {
        _remaining = Duration.zero;
        _running = false;
        _finished = true;
        _ticker?.cancel();
      }
    });
  }

  Future<void> _start() async {
    if (!_started) {
      await _native.setDuration(_picked);
      _remaining = _picked;
    }
    await _native.start();
    setState(() {
      _running = true;
      _started = true;
      _finished = false;
    });
    _ticker = Timer.periodic(const Duration(seconds: 1), (_) => _pollRemaining());
  }

  Future<void> _pause() async {
    _ticker?.cancel();
    await _native.pause();
    await _pollRemaining();
    setState(() => _running = false);
  }

  Future<void> _cancel() async {
    _ticker?.cancel();
    await _native.cancel();
    setState(() {
      _running = false;
      _started = false;
      _finished = false;
      _remaining = Duration.zero;
    });
  }

  @override
  void dispose() {
    _ticker?.cancel();
    super.dispose();
  }

  static String _format(Duration d) {
    final h = d.inHours;
    final m = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return h > 0 ? '$h:$m:$s' : '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: _isCounting
                  ? Center(
                      child: Text(
                        _format(_remaining),
                        style: const TextStyle(fontSize: 64, fontWeight: FontWeight.w300),
                      ),
                    )
                  : CupertinoTimerPicker(
                      mode: CupertinoTimerPickerMode.hm,
                      initialTimerDuration: _picked,
                      onTimerDurationChanged: (d) => setState(() => _picked = d),
                    ),
            ),
            if (_finished)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Text('타이머 종료!',
                    style: TextStyle(
                        color: scheme.primary, fontSize: 16, fontWeight: FontWeight.w600)),
              ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 24),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  if (_isCounting)
                    OutlinedButton(onPressed: _cancel, child: const Text('취소'))
                  else
                    const SizedBox(width: 80),
                  FilledButton(
                    onPressed:
                        _running ? _pause : (_picked == Duration.zero ? null : _start),
                    child: Text(_running ? '일시정지' : (_started ? '재개' : '시작')),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
