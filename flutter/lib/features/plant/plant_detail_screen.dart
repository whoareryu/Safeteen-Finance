// www/app/plant/my-plants/[id]/page.tsx 대응 화면.
// 식물 상세 + 오늘의 출석체크(사진 진단) + 뱃지 + 출석 이력, 케어 캘린더로 진입하는 버튼 포함.

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import 'care_calendar_screen.dart';
import 'plant_api.dart';
import 'plant_labels.dart';
import 'plant_models.dart';
import 'plant_style.dart';

const _kStageOrder = ['새싹', '새순', '성목'];

class PlantDetailScreen extends StatefulWidget {
  const PlantDetailScreen({super.key, required this.plantId});

  final int plantId;

  @override
  State<PlantDetailScreen> createState() => _PlantDetailScreenState();
}

class _PlantDetailScreenState extends State<PlantDetailScreen> {
  final _picker = ImagePicker();

  MyPlant? _plant;
  List<PlantBadge> _badges = [];
  List<CheckinHistoryItem> _history = [];
  bool _loading = true;
  bool _checkingIn = false;
  String? _message;
  String? _error;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    setState(() => _loading = true);
    try {
      final results = await Future.wait([
        getMyPlant(widget.plantId),
        listBadges(widget.plantId),
        listCheckins(widget.plantId),
      ]);
      setState(() {
        _plant = results[0] as MyPlant;
        _badges = results[1] as List<PlantBadge>;
        _history = results[2] as List<CheckinHistoryItem>;
      });
    } catch (e) {
      setState(() => _error = e is PlantApiException ? e.message : '정보를 불러오지 못했어요.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _checkin(ImageSource source) async {
    if (_checkingIn) return;
    final file = await _picker.pickImage(source: source, imageQuality: 90);
    if (file == null) return;
    setState(() {
      _checkingIn = true;
      _error = null;
      _message = null;
    });
    try {
      final bytes = await file.readAsBytes();
      final result = await checkinMyPlant(widget.plantId, bytes, file.name);
      final badgeText =
          result.newBadges.isNotEmpty ? ' 🎉 새 뱃지 획득: ${result.newBadges.join(", ")}' : '';
      setState(() {
        _message =
            '출석 완료! 건강도 ${result.healthScore}점, +${result.pointsEarned}P (연속 ${result.streakDay}일)$badgeText';
      });
      await _refresh();
    } catch (e) {
      setState(() => _error = e is PlantApiException ? e.message : '출석체크에 실패했어요.');
    } finally {
      if (mounted) setState(() => _checkingIn = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = isDark(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(_plant?.nickname ?? '식물 상세'),
        actions: [
          if (_plant != null)
            IconButton(
              tooltip: '케어 캘린더',
              icon: const Icon(Icons.calendar_month_outlined),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) =>
                      CareCalendarScreen(plantId: _plant!.id, region: _plant!.region),
                ),
              ),
            ),
        ],
      ),
      body: SafeArea(
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _plant == null
                ? Center(child: Text(_error ?? '식물을 찾을 수 없어요.'))
                : ListView(
                    padding: const EdgeInsets.all(20),
                    children: [
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: plantCardDecoration(context),
                        child: Column(
                          children: [
                            Text(stageEmoji[_plant!.growthStage] ?? '🌱',
                                style: const TextStyle(fontSize: 48)),
                            const SizedBox(height: 8),
                            Text(_plant!.nickname,
                                style:
                                    const TextStyle(fontSize: 20, fontWeight: FontWeight.w600)),
                            Text(
                              '${translateSpecies(_plant!.speciesName)} · ${_plant!.region}',
                              style: TextStyle(
                                  fontSize: 13,
                                  color: Theme.of(context).colorScheme.onSurfaceVariant),
                            ),
                            const SizedBox(height: 12),
                            Wrap(
                              spacing: 8,
                              children: _kStageOrder
                                  .map((stage) => Container(
                                        padding: const EdgeInsets.symmetric(
                                            horizontal: 12, vertical: 6),
                                        decoration: BoxDecoration(
                                          color: stage == _plant!.growthStage
                                              ? PlantColors.primary(dark)
                                              : Theme.of(context)
                                                  .colorScheme
                                                  .surfaceContainerHighest,
                                          borderRadius: BorderRadius.circular(999),
                                        ),
                                        child: Text(
                                          '${stageEmoji[stage]} $stage',
                                          style: TextStyle(
                                            fontSize: 12,
                                            color: stage == _plant!.growthStage
                                                ? PlantColors.primaryForeground(dark)
                                                : Theme.of(context).colorScheme.onSurfaceVariant,
                                          ),
                                        ),
                                      ))
                                  .toList(),
                            ),
                            const SizedBox(height: 16),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                _Stat(label: '포인트', value: '${_plant!.points}'),
                                const SizedBox(width: 32),
                                _Stat(label: '연속 출석', value: '🔥 ${_plant!.streakCount}'),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: plantCardDecoration(context),
                        child: Column(
                          children: [
                            const Text('오늘의 출석체크',
                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                            const SizedBox(height: 4),
                            Text(
                              '오늘 식물 사진을 찍어서 올리면 건강도에 따라 포인트를 받아요.',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                  fontSize: 12,
                                  color: Theme.of(context).colorScheme.onSurfaceVariant),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                FilledButton.icon(
                                  onPressed: _checkingIn ? null : () => _checkin(ImageSource.camera),
                                  style: FilledButton.styleFrom(
                                    backgroundColor: PlantColors.primary(dark),
                                    foregroundColor: PlantColors.primaryForeground(dark),
                                  ),
                                  icon: _checkingIn
                                      ? const SizedBox(
                                          width: 14,
                                          height: 14,
                                          child: CircularProgressIndicator(
                                              strokeWidth: 2, color: Colors.white),
                                        )
                                      : const Icon(Icons.photo_camera_outlined, size: 16),
                                  label: const Text('사진 찍기'),
                                ),
                                const SizedBox(width: 8),
                                OutlinedButton.icon(
                                  onPressed:
                                      _checkingIn ? null : () => _checkin(ImageSource.gallery),
                                  icon: const Icon(Icons.photo_library_outlined, size: 16),
                                  label: const Text('앨범에서 선택'),
                                ),
                              ],
                            ),
                            if (_message != null) ...[
                              const SizedBox(height: 10),
                              Text(_message!,
                                  textAlign: TextAlign.center,
                                  style: TextStyle(color: PlantColors.primary(dark), fontSize: 13)),
                            ],
                            if (_error != null) ...[
                              const SizedBox(height: 10),
                              Text(_error!,
                                  textAlign: TextAlign.center,
                                  style: TextStyle(color: PlantColors.destructive(dark))),
                            ],
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                      const Text('뱃지', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 10),
                      GridView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: _badges.length,
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 4,
                          mainAxisSpacing: 8,
                          crossAxisSpacing: 8,
                          childAspectRatio: 0.9,
                        ),
                        itemBuilder: (_, i) {
                          final b = _badges[i];
                          return Opacity(
                            opacity: b.earned ? 1 : 0.4,
                            child: Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(14),
                                border: Border.all(
                                  color: b.earned
                                      ? PlantColors.primary(dark)
                                      : Theme.of(context).colorScheme.outlineVariant,
                                ),
                                color: b.earned
                                    ? PlantColors.accentBg(dark)
                                    : Theme.of(context).colorScheme.surfaceContainerHighest,
                              ),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(b.icon, style: const TextStyle(fontSize: 20)),
                                  const SizedBox(height: 4),
                                  Text(
                                    b.name,
                                    textAlign: TextAlign.center,
                                    style: const TextStyle(fontSize: 9),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                      const SizedBox(height: 24),
                      const Text('출석체크 이력',
                          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 10),
                      if (_history.isEmpty)
                        Text('아직 출석체크 기록이 없어요.',
                            style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant))
                      else
                        ..._history.map(
                          (h) => Container(
                            margin: const EdgeInsets.only(bottom: 8),
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                            decoration: plantCardDecoration(context),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(h.checkinDate,
                                    style: TextStyle(
                                        fontSize: 13,
                                        color: Theme.of(context).colorScheme.onSurfaceVariant)),
                                Text('건강도 ${h.healthScore}', style: const TextStyle(fontSize: 13)),
                                Text('+${h.pointsEarned}P',
                                    style: TextStyle(
                                        fontSize: 13,
                                        fontWeight: FontWeight.w600,
                                        color: PlantColors.primary(dark))),
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

class _Stat extends StatelessWidget {
  const _Stat({required this.label, required this.value});
  final String label, value;

  @override
  Widget build(BuildContext context) => Column(
        children: [
          Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
          Text(label,
              style:
                  TextStyle(fontSize: 11, color: Theme.of(context).colorScheme.onSurfaceVariant)),
        ],
      );
}
