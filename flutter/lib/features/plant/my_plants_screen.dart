// www/app/plant/my-plants/page.tsx 대응 화면 (등록 폼 + 내 식물 목록).
// 게스트 모드: owner_user_id 없이 등록·조회하므로 모든 사용자의 식물이 함께 보인다.

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import 'leaderboard_screen.dart';
import 'plant_api.dart';
import 'plant_detail_screen.dart';
import 'plant_labels.dart';
import 'plant_models.dart';
import 'plant_style.dart';

class MyPlantsScreen extends StatefulWidget {
  const MyPlantsScreen({super.key});

  @override
  State<MyPlantsScreen> createState() => _MyPlantsScreenState();
}

class _MyPlantsScreenState extends State<MyPlantsScreen> {
  final _picker = ImagePicker();
  final _regionCtrl = TextEditingController();
  final _speciesCtrl = TextEditingController();
  XFile? _picked;

  List<MyPlant> _plants = [];
  bool _loadingList = true;
  bool _submitting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  @override
  void dispose() {
    _regionCtrl.dispose();
    _speciesCtrl.dispose();
    super.dispose();
  }

  Future<void> _refresh() async {
    setState(() => _loadingList = true);
    try {
      final list = await listMyPlants();
      if (mounted) setState(() => _plants = list);
    } catch (_) {
      if (mounted) setState(() => _plants = []);
    } finally {
      if (mounted) setState(() => _loadingList = false);
    }
  }

  Future<void> _pickPhoto() async {
    final file = await _picker.pickImage(source: ImageSource.gallery, imageQuality: 90);
    if (file != null) setState(() => _picked = file);
  }

  Future<void> _submit() async {
    final region = _regionCtrl.text.trim();
    final species = _speciesCtrl.text.trim();
    if (region.isEmpty || (species.isEmpty && _picked == null)) {
      setState(() => _error = '장소는 필수이고, 종류 입력 또는 사진 중 하나는 있어야 해요.');
      return;
    }
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      final picked = _picked;
      await registerMyPlant(
        region: region,
        speciesName: species.isEmpty ? null : species,
        photoBytes: picked == null ? null : await picked.readAsBytes(),
        photoFilename: picked?.name,
      );
      _regionCtrl.clear();
      _speciesCtrl.clear();
      setState(() => _picked = null);
      await _refresh();
    } catch (e) {
      setState(() => _error = e is PlantApiException ? e.message : '등록에 실패했어요.');
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = isDark(context);
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            const PlantHeroBanner(
              title: '마이플랜트',
              subtitle: '내 식물을 캐릭터처럼 키워보세요.',
              imageUrl:
                  'https://images.unsplash.com/photo-1750341005643-e79d6ec30979?w=1600&q=80&auto=format&fit=crop',
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          '내 반려식물을 등록하고, 매일 사진으로 출석체크하며 식물집사 포인트를 모아보세요.',
                          style: TextStyle(
                              fontSize: 13,
                              color: Theme.of(context).colorScheme.onSurfaceVariant),
                        ),
                      ),
                      TextButton(
                        onPressed: () => Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const LeaderboardScreen()),
                        ),
                        child: const Text('랭킹 보기 →'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: plantCardDecoration(context),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('새 식물 등록',
                            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 10),
                        TextField(
                          controller: _regionCtrl,
                          decoration: const InputDecoration(
                            labelText: '키우는 장소',
                            hintText: '예: 거실, 베란다',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 10),
                        TextField(
                          controller: _speciesCtrl,
                          decoration: const InputDecoration(
                            labelText: '종류 (사진으로 등록하면 생략 가능)',
                            hintText: '예: 몬스테라',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            OutlinedButton.icon(
                              onPressed: _pickPhoto,
                              icon: const Icon(Icons.photo_library_outlined, size: 16),
                              label: const Text('사진 선택'),
                            ),
                            if (_picked != null) ...[
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  _picked!.name,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(
                                      fontSize: 12,
                                      color: Theme.of(context).colorScheme.onSurfaceVariant),
                                ),
                              ),
                            ],
                          ],
                        ),
                        if (_error != null) ...[
                          const SizedBox(height: 10),
                          Text(_error!, style: TextStyle(color: PlantColors.destructive(dark))),
                        ],
                        const SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          child: FilledButton.icon(
                            onPressed: _submitting ? null : _submit,
                            style: FilledButton.styleFrom(
                              backgroundColor: PlantColors.primary(dark),
                              foregroundColor: PlantColors.primaryForeground(dark),
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
                            ),
                            icon: _submitting
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                  )
                                : const Icon(Icons.add, size: 18),
                            label: Text(_submitting ? '등록 중…' : '등록하기'),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Text('내 식물 목록', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 12),
                  if (_loadingList)
                    const Center(child: CircularProgressIndicator())
                  else if (_plants.isEmpty)
                    Text('아직 등록한 식물이 없어요.',
                        style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant))
                  else
                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: _plants.length,
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        mainAxisSpacing: 12,
                        crossAxisSpacing: 12,
                        childAspectRatio: 0.95,
                      ),
                      itemBuilder: (_, i) => GestureDetector(
                        onTap: () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => PlantDetailScreen(plantId: _plants[i].id),
                          ),
                        ),
                        child: _PlantCard(plant: _plants[i]),
                      ),
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

class _PlantCard extends StatelessWidget {
  const _PlantCard({required this.plant});
  final MyPlant plant;

  @override
  Widget build(BuildContext context) {
    final dark = isDark(context);
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: plantCardDecoration(context),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(stageEmoji[plant.growthStage] ?? '🌱', style: const TextStyle(fontSize: 24)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: PlantColors.accentBg(dark),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  plant.growthStage,
                  style: TextStyle(fontSize: 11, color: PlantColors.accentForeground(dark)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(plant.nickname,
              style: const TextStyle(fontWeight: FontWeight.w600), overflow: TextOverflow.ellipsis),
          const SizedBox(height: 2),
          Text(
            '${translateSpecies(plant.speciesName)} · ${plant.region}',
            style: TextStyle(fontSize: 12, color: Theme.of(context).colorScheme.onSurfaceVariant),
            overflow: TextOverflow.ellipsis,
          ),
          const Spacer(),
          Text(
            '${plant.points}P · 🔥 ${plant.streakCount}일 연속',
            style: TextStyle(fontSize: 11, color: Theme.of(context).colorScheme.onSurfaceVariant),
          ),
        ],
      ),
    );
  }
}
