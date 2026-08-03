// iOS 시계 앱의 스톱워치 탭(랩 기록 + 최단/최장 랩 강조)을 참고한 화면.
// 시간 측정 자체는 네이티브(ios/Runner/counter/StopwatchActivity.swift)가 담당하고,
// Dart는 MethodChannel로 30ms마다 경과 시간을 물어봐서 화면만 갱신한다. 랩 목록 관리는
// 여전히 Dart 쪽 책임 — 네이티브는 "지금까지 흐른 시간"만 알고 랩 개념은 모른다.

import 'dart:async';

import 'package:flutter/material.dart';

import 'native_stopwatch_channel.dart';

class StopwatchScreen extends StatefulWidget {
  const StopwatchScreen({super.key});

  @override
  State<StopwatchScreen> createState() => _StopwatchScreenState();
}

class _StopwatchScreenState extends State<StopwatchScreen> {
  final _native = NativeStopwatchChannel();
  Timer? _ticker;

  bool _isRunning = false;
  Duration _elapsed = Duration.zero;

  final List<Duration> _laps = [];
  Duration _lastLapMark = Duration.zero;

  bool get _hasElapsed => _elapsed > Duration.zero;

  Future<void> _pollElapsed() async {
    final elapsed = await _native.elapsed();
    if (mounted) setState(() => _elapsed = elapsed);
  }

  void _start() async {
    await _native.start();
    setState(() => _isRunning = true);
    _ticker = Timer.periodic(const Duration(milliseconds: 30), (_) => _pollElapsed());
  }

  void _stop() async {
    _ticker?.cancel();
    await _native.stop();
    await _pollElapsed();
    setState(() => _isRunning = false);
  }

  void _lap() {
    if (!_isRunning) return;
    setState(() {
      _laps.insert(0, _elapsed - _lastLapMark);
      _lastLapMark = _elapsed;
    });
  }

  void _reset() async {
    await _native.reset();
    setState(() {
      _elapsed = Duration.zero;
      _laps.clear();
      _lastLapMark = Duration.zero;
    });
  }

  @override
  void dispose() {
    _ticker?.cancel();
    super.dispose();
  }

  static String _format(Duration d) {
    final minutes = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    final centis = (d.inMilliseconds.remainder(1000) ~/ 10).toString().padLeft(2, '0');
    return '$minutes:$seconds.$centis';
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;

    Duration? shortest;
    Duration? longest;
    if (_laps.length > 1) {
      shortest = _laps.reduce((a, b) => a < b ? a : b);
      longest = _laps.reduce((a, b) => a > b ? a : b);
      if (shortest == longest) {
        shortest = null;
        longest = null;
      }
    }

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: 48),
            Text(
              _format(_elapsed),
              style: const TextStyle(
                fontSize: 56,
                fontWeight: FontWeight.w300,
                fontFeatures: [FontFeature.tabularFigures()],
              ),
            ),
            const SizedBox(height: 32),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _RoundButton(
                    label: _isRunning ? '랩' : '재설정',
                    onTap: _isRunning ? _lap : (_hasElapsed ? _reset : null),
                    background: scheme.surfaceContainerHighest,
                    foreground: scheme.onSurface,
                  ),
                  _RoundButton(
                    label: _isRunning ? '중단' : '시작',
                    onTap: _isRunning ? _stop : _start,
                    background: _isRunning
                        ? const Color(0xFFFBEAE9)
                        : const Color(0xFFDCF3E1),
                    foreground: _isRunning ? const Color(0xFFB3382D) : const Color(0xFF1E7A34),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            const Divider(height: 1),
            Expanded(
              child: _laps.isEmpty
                  ? Center(
                      child: Text('랩을 기록해 보세요',
                          style: TextStyle(color: scheme.onSurfaceVariant)),
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                      itemCount: _laps.length,
                      separatorBuilder: (_, _) => Divider(height: 1, color: scheme.outlineVariant),
                      itemBuilder: (_, i) {
                        final lap = _laps[i];
                        final lapNumber = _laps.length - i;
                        Color? color;
                        if (shortest != null && lap == shortest) color = const Color(0xFF1E7A34);
                        if (longest != null && lap == longest) color = const Color(0xFFB3382D);
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('랩 $lapNumber', style: TextStyle(color: color)),
                              Text(
                                _format(lap),
                                style: TextStyle(
                                  color: color,
                                  fontFeatures: const [FontFeature.tabularFigures()],
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RoundButton extends StatelessWidget {
  const _RoundButton({
    required this.label,
    required this.onTap,
    required this.background,
    required this.foreground,
  });

  final String label;
  final VoidCallback? onTap;
  final Color background;
  final Color foreground;

  @override
  Widget build(BuildContext context) {
    final disabled = onTap == null;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 76,
        height: 76,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: disabled ? background.withValues(alpha: 0.4) : background,
        ),
        alignment: Alignment.center,
        child: Text(
          label,
          style: TextStyle(
            color: disabled ? foreground.withValues(alpha: 0.4) : foreground,
            fontWeight: FontWeight.w600,
            fontSize: 14,
          ),
        ),
      ),
    );
  }
}
