// www/app/plant/leaderboard/page.tsx 대응 화면.

import 'package:flutter/material.dart';

import 'plant_api.dart';
import 'plant_labels.dart';
import 'plant_models.dart';
import 'plant_style.dart';

const _kRankMedal = {1: '🥇', 2: '🥈', 3: '🥉'};

class LeaderboardScreen extends StatefulWidget {
  const LeaderboardScreen({super.key});

  @override
  State<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> {
  List<LeaderboardEntry> _entries = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    getLeaderboard(limit: 50).then((entries) {
      if (mounted) setState(() => _entries = entries);
    }).whenComplete(() {
      if (mounted) setState(() => _loading = false);
    });
  }

  @override
  Widget build(BuildContext context) {
    final dark = isDark(context);
    return Scaffold(
      appBar: AppBar(title: const Text('식물집사 랭킹')),
      body: SafeArea(
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _entries.isEmpty
                ? Center(
                    child: Text('아직 랭킹에 등록된 식물이 없어요.',
                        style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant)),
                  )
                : ListView.separated(
                    padding: const EdgeInsets.all(20),
                    itemCount: _entries.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 8),
                    itemBuilder: (_, i) {
                      final e = _entries[i];
                      return Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        decoration: plantCardDecoration(context),
                        child: Row(
                          children: [
                            SizedBox(
                              width: 32,
                              child: Text(
                                _kRankMedal[e.rank] ?? '${e.rank}',
                                textAlign: TextAlign.center,
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(stageEmoji[e.growthStage] ?? '🌱', style: const TextStyle(fontSize: 20)),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(e.nickname,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(fontWeight: FontWeight.w600)),
                                  Text(translateSpecies(e.speciesName),
                                      style: TextStyle(
                                          fontSize: 11,
                                          color: Theme.of(context).colorScheme.onSurfaceVariant)),
                                ],
                              ),
                            ),
                            Text('${e.points}P',
                                style: TextStyle(
                                    fontWeight: FontWeight.w600, color: PlantColors.primary(dark))),
                          ],
                        ),
                      );
                    },
                  ),
      ),
    );
  }
}
