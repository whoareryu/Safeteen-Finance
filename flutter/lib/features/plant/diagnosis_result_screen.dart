// www/app/plant/diagnosis/[id]/page.tsx + components/plant-diagnosis-result-card.tsx 대응 화면.

import 'package:flutter/material.dart';

import 'plant_api.dart';
import 'plant_labels.dart';
import 'plant_models.dart';
import 'plant_style.dart';

// 분류기 자체 확신도가 이 미만이면 결과를 단정적으로 보여주지 않고 재촬영을 안내한다.
// (www/components/plant-diagnosis-result-card.tsx의 LOW_CONFIDENCE_THRESHOLD와 동일)
const _kLowConfidenceThreshold = 0.5;

class DiagnosisResultScreen extends StatefulWidget {
  const DiagnosisResultScreen({super.key, required this.diagnosisId});

  final int diagnosisId;

  @override
  State<DiagnosisResultScreen> createState() => _DiagnosisResultScreenState();
}

class _DiagnosisResultScreenState extends State<DiagnosisResultScreen> {
  DiagnosisResult? _diagnosis;
  String? _loadError;

  bool _guideLoading = false;
  String? _prescription;
  String? _guideError;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final result = await fetchDiagnosis(widget.diagnosisId);
      if (mounted) setState(() => _diagnosis = result);
    } catch (e) {
      if (mounted) setState(() => _loadError = '진단 결과를 불러오지 못했습니다.');
    }
  }

  Future<void> _generateCareGuide() async {
    setState(() {
      _guideLoading = true;
      _guideError = null;
    });
    try {
      final guide = await generateCareGuide(widget.diagnosisId);
      if (mounted) setState(() => _prescription = guide.prescriptionText);
    } catch (e) {
      if (mounted) {
        setState(() => _guideError = e is PlantApiException ? e.message : '케어 처방 생성 중 오류가 발생했습니다.');
      }
    } finally {
      if (mounted) setState(() => _guideLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('진단 결과')),
      body: SafeArea(
        child: _loadError != null
            ? Center(child: Text(_loadError!))
            : _diagnosis == null
                ? const Center(child: CircularProgressIndicator())
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(20),
                    child: _buildCard(context, _diagnosis!),
                  ),
      ),
    );
  }

  Widget _buildCard(BuildContext context, DiagnosisResult d) {
    final dark = isDark(context);
    final isLowConfidence = d.speciesConfidence < _kLowConfidenceThreshold;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: plantCardDecoration(context),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Image.network(
              d.photoUrl,
              width: double.infinity,
              height: 220,
              fit: BoxFit.contain,
              errorBuilder: (_, _, _) => Container(
                height: 220,
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                child: const Center(child: Icon(Icons.image_not_supported_outlined)),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _Badge(
                text: translateSpecies(d.detectedSpecies),
                bg: PlantColors.accentBg(dark),
                fg: PlantColors.accentForeground(dark),
              ),
              _Badge(
                text: translateSymptom(d.symptomLabel),
                bg: Theme.of(context).colorScheme.surfaceContainerHighest,
                fg: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _ConfidenceTile(
                  label: '품종 확신도',
                  value: d.speciesConfidence,
                  warn: isLowConfidence,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _ConfidenceTile(
                  label: '증상 확신도',
                  value: d.symptomConfidence,
                  warn: isLowConfidence,
                ),
              ),
            ],
          ),
          if (isLowConfidence) ...[
            const SizedBox(height: 12),
            _MessageBox(
              text: '확신도가 낮아요. 잎 전체가 잘 보이도록 밝은 곳에서 사진을 다시 찍어보시면 더 정확해요.',
              bg: PlantColors.destructiveBg(dark),
              fg: PlantColors.destructive(dark),
            ),
          ],
          const SizedBox(height: 16),
          if (_prescription != null)
            _MessageBox(
              text: _prescription!,
              bg: PlantColors.accentBg(dark),
              fg: PlantColors.accentForeground(dark),
            )
          else
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _guideLoading ? null : _generateCareGuide,
                style: FilledButton.styleFrom(
                  backgroundColor: PlantColors.primary(dark),
                  foregroundColor: PlantColors.primaryForeground(dark),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
                ),
                child: _guideLoading
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Text('케어 처방 받기'),
              ),
            ),
          if (_guideError != null) ...[
            const SizedBox(height: 12),
            _MessageBox(
              text: _guideError!,
              bg: PlantColors.destructiveBg(dark),
              fg: PlantColors.destructive(dark),
            ),
          ],
        ],
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  const _Badge({required this.text, required this.bg, required this.fg});
  final String text;
  final Color bg, fg;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(999)),
        child: Text(text, style: TextStyle(color: fg, fontSize: 13, fontWeight: FontWeight.w600)),
      );
}

class _ConfidenceTile extends StatelessWidget {
  const _ConfidenceTile({required this.label, required this.value, required this.warn});
  final String label;
  final double value;
  final bool warn;

  @override
  Widget build(BuildContext context) {
    final dark = isDark(context);
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 10),
      decoration: BoxDecoration(
        color: warn
            ? PlantColors.destructiveBg(dark)
            : Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: warn
              ? PlantColors.destructive(dark).withValues(alpha: 0.4)
              : Theme.of(context).colorScheme.outlineVariant,
        ),
      ),
      child: Column(
        children: [
          Text(label,
              style: TextStyle(fontSize: 12, color: Theme.of(context).colorScheme.onSurfaceVariant)),
          const SizedBox(height: 2),
          Text(
            '${(value * 100).toStringAsFixed(0)}%',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }
}

class _MessageBox extends StatelessWidget {
  const _MessageBox({required this.text, required this.bg, required this.fg});
  final String text;
  final Color bg, fg;

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(14)),
        child: Text(text, style: TextStyle(color: fg, fontSize: 13, height: 1.5)),
      );
}
