// www/app/plant/care-calendar/page.tsx + components/plant-care-calendar-list.tsx 대응 화면.

import 'package:flutter/material.dart';

import 'plant_api.dart';
import 'plant_models.dart';
import 'plant_style.dart';

class CareCalendarScreen extends StatefulWidget {
  /// [plantId]/[region]을 안 주면(하단 탭에서 직접 진입) 등록된 첫 번째 식물을 자동으로 찾아 쓴다
  /// (웹의 plantId=1 기본값과 달리, 실제 존재하는 식물을 조회해서 쓰므로 더 안전하다).
  ///
  /// [showAppBar]는 메인 셸의 탭으로 쓰일 때(공용 AppBar가 이미 있음)만 false로 준다.
  const CareCalendarScreen({super.key, this.plantId, this.region, this.showAppBar = true});

  final int? plantId;
  final String? region;
  final bool showAppBar;

  @override
  State<CareCalendarScreen> createState() => _CareCalendarScreenState();
}

class _CareCalendarScreenState extends State<CareCalendarScreen> {
  List<NotificationEvent> _notifications = [];
  WeatherSnapshot? _weather;
  bool _loading = true;
  bool _noPlant = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      int? plantId = widget.plantId;
      String? region = widget.region;
      if (plantId == null) {
        final plants = await listMyPlants();
        if (plants.isEmpty) {
          setState(() => _noPlant = true);
          return;
        }
        plantId = plants.first.id;
        region = plants.first.region;
      }

      final notifications = await fetchNotifications(plantId);
      WeatherSnapshot? weather;
      try {
        weather = await fetchWeatherStatus(region ?? '서울');
      } catch (_) {
        weather = null;
      }
      setState(() {
        _notifications = notifications;
        _weather = weather;
      });
    } catch (e) {
      setState(() => _error = e is PlantApiException ? e.message : '케어 일정을 불러오지 못했습니다.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = isDark(context);
    return Scaffold(
      appBar: widget.showAppBar ? AppBar(title: const Text('물주기 일정 & 알림 이력')) : null,
      body: SafeArea(
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _noPlant
                ? Center(
                    child: Text('등록된 식물이 없어요. 마이플랜트에서 먼저 식물을 등록해 주세요.',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                            color: Theme.of(context).colorScheme.onSurfaceVariant)),
                  )
                : ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  if (_weather != null)
                    Container(
                      padding: const EdgeInsets.all(14),
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: plantCardDecoration(context),
                      child: Row(
                        children: [
                          Container(
                            width: 40,
                            height: 40,
                            decoration: BoxDecoration(
                              color: PlantColors.accentBg(dark),
                              shape: BoxShape.circle,
                            ),
                            child: Icon(Icons.water_drop_outlined,
                                size: 20, color: PlantColors.primary(dark)),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              '${_weather!.region} 현재 온도 ${_weather!.tempC.toStringAsFixed(0)}°C · '
                              '습도 ${_weather!.humidityPct.toStringAsFixed(0)}%'
                              '${_weather!.isDryDay ? " · 건조한 날씨예요 🌵" : ""}',
                              style: const TextStyle(fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                  if (_error != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: Text(_error!, style: TextStyle(color: PlantColors.destructive(dark))),
                    ),
                  if (_notifications.isEmpty)
                    Text('아직 발송된 알림이 없어요.',
                        style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant))
                  else
                    ..._notifications.map(
                      (e) => Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(14),
                        decoration: plantCardDecoration(context),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 40,
                              height: 40,
                              decoration: BoxDecoration(
                                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.notifications_outlined, size: 18),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(e.message, style: const TextStyle(fontSize: 13)),
                                  const SizedBox(height: 4),
                                  Text(
                                    '채널: ${e.channel} · 상태: ${e.deliveryStatus}',
                                    style: TextStyle(
                                        fontSize: 11,
                                        color: Theme.of(context).colorScheme.onSurfaceVariant),
                                  ),
                                  if (e.coupangLink != null) ...[
                                    const SizedBox(height: 4),
                                    Text('영양제 보러 가기',
                                        style: TextStyle(
                                            fontSize: 11,
                                            fontWeight: FontWeight.w600,
                                            color: PlantColors.primary(dark))),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
      ),
    );
  }
}
