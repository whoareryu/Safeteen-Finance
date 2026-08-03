// iOS 시계 앱의 "세계 시계" 탭 참고. 정확한 IANA 타임존/DST 처리 없이 고정 UTC 오프셋만 쓴다
// (실제 서머타임까지 반영하려면 timezone 패키지 도입이 필요 — 지금은 간단한 오프셋 표기로 대체).

import 'dart:async';

import 'package:flutter/material.dart';

class _WorldCity {
  const _WorldCity(this.name, this.utcOffsetHours);
  final String name;
  final double utcOffsetHours;
}

const _kAllCities = [
  _WorldCity('서울', 9),
  _WorldCity('도쿄', 9),
  _WorldCity('베이징', 8),
  _WorldCity('런던', 0),
  _WorldCity('파리', 1),
  _WorldCity('뉴욕', -5),
  _WorldCity('로스앤젤레스', -8),
  _WorldCity('시드니', 11),
  _WorldCity('두바이', 4),
  _WorldCity('싱가포르', 8),
];

class WorldClockScreen extends StatefulWidget {
  const WorldClockScreen({super.key});

  @override
  State<WorldClockScreen> createState() => _WorldClockScreenState();
}

class _WorldClockScreenState extends State<WorldClockScreen> {
  Timer? _ticker;
  final List<_WorldCity> _added = [_kAllCities[3], _kAllCities[5]]; // 런던, 뉴욕 기본 표시

  @override
  void initState() {
    super.initState();
    _ticker = Timer.periodic(const Duration(seconds: 1), (_) => setState(() {}));
  }

  @override
  void dispose() {
    _ticker?.cancel();
    super.dispose();
  }

  void _addCity() async {
    final available = _kAllCities.where((c) => !_added.contains(c)).toList();
    final picked = await showModalBottomSheet<_WorldCity>(
      context: context,
      builder: (_) => SafeArea(
        child: ListView(
          shrinkWrap: true,
          children: available
              .map((c) => ListTile(title: Text(c.name), onTap: () => Navigator.pop(context, c)))
              .toList(),
        ),
      ),
    );
    if (picked != null) setState(() => _added.add(picked));
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final now = DateTime.now().toUtc();

    return Scaffold(
      floatingActionButton: FloatingActionButton(
        heroTag: 'worldClockAddFab',
        onPressed: _addCity,
        child: const Icon(Icons.add),
      ),
      body: _added.isEmpty
          ? Center(
              child: Text('오른쪽 아래 + 버튼으로 도시를 추가해 보세요',
                  style: TextStyle(color: scheme.onSurfaceVariant)),
            )
          : ListView.separated(
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: _added.length,
              separatorBuilder: (_, _) => Divider(height: 1, color: scheme.outlineVariant),
              itemBuilder: (_, i) {
                final city = _added[i];
                final local = now.add(Duration(minutes: (city.utcOffsetHours * 60).round()));
                final dayDiff = local.day - DateTime.now().day;
                final dayLabel = dayDiff == 0 ? '오늘' : (dayDiff > 0 ? '내일' : '어제');
                return ListTile(
                  title: Text(city.name, style: const TextStyle(fontSize: 16)),
                  subtitle: Text(dayLabel),
                  trailing: Text(
                    '${local.hour.toString().padLeft(2, '0')}:${local.minute.toString().padLeft(2, '0')}',
                    style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w300),
                  ),
                  onLongPress: () => setState(() => _added.removeAt(i)),
                );
              },
            ),
    );
  }
}
