// www/app/plant/page.tsx + components/plant-photo-upload.tsx 대응 화면 ("진단" 탭).
// 게스트 모드라 지역은 항상 기본값('서울')을 쓴다 (웹의 user?.region 폴백과 동일한 기본값).

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import 'diagnosis_result_screen.dart';
import 'plant_api.dart';
import 'plant_style.dart';

const _kDefaultRegion = '서울';

class DiagnosisUploadScreen extends StatefulWidget {
  const DiagnosisUploadScreen({super.key});

  @override
  State<DiagnosisUploadScreen> createState() => _DiagnosisUploadScreenState();
}

class _DiagnosisUploadScreenState extends State<DiagnosisUploadScreen> {
  final _picker = ImagePicker();
  XFile? _picked;
  bool _uploading = false;
  String? _error;

  Future<void> _pick(ImageSource source) async {
    final file = await _picker.pickImage(source: source, imageQuality: 90);
    if (file == null) return;
    setState(() {
      _picked = file;
      _error = null;
    });
  }

  Future<void> _upload() async {
    final picked = _picked;
    if (picked == null || _uploading) return;
    setState(() {
      _uploading = true;
      _error = null;
    });
    try {
      final bytes = await picked.readAsBytes();
      final diagnosis = await uploadPlantPhoto(
        photoBytes: bytes,
        region: _kDefaultRegion,
        photoFilename: picked.name,
      );
      if (!mounted) return;
      setState(() => _picked = null);
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => DiagnosisResultScreen(diagnosisId: diagnosis.id)),
      );
    } catch (e) {
      if (mounted) {
        setState(() => _error = e is PlantApiException ? e.message : '사진 진단 중 오류가 발생했습니다.');
      }
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = isDark(context);
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            const PlantHeroBanner(
              title: 'AI 잎사귀 진단',
              subtitle: '잎사귀 사진 한 장이면 품종과 병징을 바로 알려드려요.',
              imageUrl:
                  'https://images.unsplash.com/photo-1667395941567-9892435d0240?w=1600&q=80&auto=format&fit=crop',
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '반려식물 잎사귀 사진 업로드',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '잎사귀 사진을 업로드하면 품종과 증상을 진단하고 케어 처방을 안내해 드려요.',
                    style: TextStyle(
                      fontSize: 13,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 16),
                  GestureDetector(
                    onTap: () => _pick(ImageSource.gallery),
                    child: Container(
                      width: double.infinity,
                      height: 200,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: Theme.of(context).colorScheme.outlineVariant,
                          width: 2,
                          style: BorderStyle.solid,
                        ),
                        color: Theme.of(context).colorScheme.surfaceContainerHighest,
                      ),
                      clipBehavior: Clip.antiAlias,
                      child: _picked != null
                          ? Image.file(File(_picked!.path), fit: BoxFit.contain)
                          : Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.cloud_upload_outlined,
                                    size: 40, color: Theme.of(context).colorScheme.onSurfaceVariant),
                                const SizedBox(height: 12),
                                const Text('탭해서 잎사귀 사진 선택', style: TextStyle(fontWeight: FontWeight.w500)),
                                const SizedBox(height: 4),
                                Text('JPG, PNG 등',
                                    style: TextStyle(
                                        fontSize: 12,
                                        color: Theme.of(context).colorScheme.onSurfaceVariant)),
                              ],
                            ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => _pick(ImageSource.gallery),
                          icon: const Icon(Icons.photo_library_outlined, size: 18),
                          label: const Text('사진 선택'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => _pick(ImageSource.camera),
                          icon: const Icon(Icons.photo_camera_outlined, size: 18),
                          label: const Text('촬영하기'),
                        ),
                      ),
                    ],
                  ),
                  if (_picked != null) ...[
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton(
                        onPressed: _uploading ? null : _upload,
                        style: FilledButton.styleFrom(
                          backgroundColor: PlantColors.primary(dark),
                          foregroundColor: PlantColors.primaryForeground(dark),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
                        ),
                        child: _uploading
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                              )
                            : const Text('진단하기'),
                      ),
                    ),
                  ],
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(_error!, style: TextStyle(color: PlantColors.destructive(dark))),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
