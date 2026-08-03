// www/app/page.tsx 대응 화면 (실제 배포된 whoareryu.cloud 루트 홈) — "새싹" 채팅 홈.
// GeminiChat(components/gemini-chat.tsx)의 apiPath="/api/plant/chat" 흐름을 네이티브로 옮겼다.

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import 'care_calendar_screen.dart';
import 'coming_soon_screen.dart';
import 'diagnosis_upload_screen.dart';
import 'plant_api.dart';
import 'plant_labels.dart';
import 'plant_models.dart';
import 'plant_style.dart';

const _kSuggestions = ['몬스테라 물 주기 주기가 어떻게 돼?', '잎이 노랗게 변했어, 왜 그럴까?', '초보자에게 좋은 식물 추천해줘'];
const _kDefaultRegion = '서울';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _picker = ImagePicker();
  final _inputCtrl = TextEditingController();
  final _messages = <ChatMessage>[];
  XFile? _attachedImage;
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _inputCtrl.dispose();
    super.dispose();
  }

  Future<String> _diagnoseFromChat(XFile file) async {
    final bytes = await file.readAsBytes();
    final diagnosis = await uploadPlantPhoto(
      photoBytes: bytes,
      region: _kDefaultRegion,
      photoFilename: file.name,
    );
    final speciesPct = (diagnosis.speciesConfidence * 100).toStringAsFixed(0);
    final symptomPct = (diagnosis.symptomConfidence * 100).toStringAsFixed(0);
    return [
      '🌱 진단 결과: ${translateSpecies(diagnosis.detectedSpecies)} (신뢰도 $speciesPct%)',
      '증상: ${translateSymptom(diagnosis.symptomLabel)} (신뢰도 $symptomPct%)',
      '',
      '케어 방법이 궁금하면 이어서 물어보세요!',
    ].join('\n');
  }

  Future<void> _pickImage(ImageSource source) async {
    final file = await _picker.pickImage(source: source, imageQuality: 90);
    if (file != null) setState(() => _attachedImage = file);
  }

  Future<void> _send() async {
    final text = _inputCtrl.text.trim();
    final image = _attachedImage;
    if ((text.isEmpty && image == null) || _loading) return;

    setState(() {
      _error = null;
      _inputCtrl.clear();
      _attachedImage = null;
    });

    final userLabel = image != null
        ? (text.isEmpty ? '📷 ${image.name}' : '📷 ${image.name}\n$text')
        : text;
    final historyBase = List<ChatMessage>.from(_messages);
    setState(() {
      _messages.add(ChatMessage(role: 'user', content: userLabel));
      _loading = true;
    });

    try {
      String? diagnosisText;
      if (image != null) {
        diagnosisText = await _diagnoseFromChat(image);
        if (text.isEmpty) {
          setState(() => _messages.add(ChatMessage(role: 'assistant', content: diagnosisText!)));
          return;
        }
      }
      final askText = diagnosisText != null ? '$diagnosisText\n\n$text' : text;
      final reply = await sendPlantChatMessage([
        ...historyBase,
        ChatMessage(role: 'user', content: askText),
      ]);
      setState(() => _messages.add(ChatMessage(role: 'assistant', content: reply)));
    } catch (e) {
      setState(() => _error = e is PlantApiException ? e.message : '요청에 실패했습니다.');
    } finally {
      if (mounted) setState(() => _loading = false);
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
              title: '새싹과 함께하는 반려식물 케어',
              subtitle: '궁금한 걸 물어보거나 잎사귀 사진을 올려보세요. 품종·증상 진단부터 날씨 기반\n물주기 알림까지, AI 에이전트가 초보 식집사를 도와드려요.',
              imageUrl:
                  'https://images.unsplash.com/photo-1755504980103-374cf009b201?w=1600&q=80&auto=format&fit=crop',
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: plantCardDecoration(context),
                    child: Column(
                      children: [
                        const Text(
                          '새싹에게 물어보세요',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 10),
                        Wrap(
                          alignment: WrapAlignment.center,
                          spacing: 8,
                          runSpacing: 8,
                          children: _kSuggestions
                              .map((s) => GestureDetector(
                                    onTap: () => setState(() => _inputCtrl.text = s),
                                    child: Container(
                                      padding:
                                          const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                      decoration: BoxDecoration(
                                        borderRadius: BorderRadius.circular(999),
                                        border: Border.all(
                                            color: Theme.of(context).colorScheme.outlineVariant),
                                      ),
                                      child: Text(s,
                                          style: TextStyle(
                                              fontSize: 11,
                                              color:
                                                  Theme.of(context).colorScheme.onSurfaceVariant)),
                                    ),
                                  ))
                              .toList(),
                        ),
                        const SizedBox(height: 14),
                        if (_attachedImage != null)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 10),
                            child: Stack(
                              children: [
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(16),
                                  child: Image.file(File(_attachedImage!.path),
                                      width: 96, height: 96, fit: BoxFit.cover),
                                ),
                                Positioned(
                                  right: -4,
                                  top: -4,
                                  child: GestureDetector(
                                    onTap: () => setState(() => _attachedImage = null),
                                    child: Container(
                                      padding: const EdgeInsets.all(4),
                                      decoration: const BoxDecoration(
                                          color: Colors.black54, shape: BoxShape.circle),
                                      child: const Icon(Icons.close, size: 14, color: Colors.white),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        TextField(
                          controller: _inputCtrl,
                          minLines: 1,
                          maxLines: 4,
                          enabled: !_loading,
                          decoration: const InputDecoration(
                            hintText: '새싹이에게 물어보기',
                            border: InputBorder.none,
                          ),
                          onSubmitted: (_) => _send(),
                        ),
                        if (_error != null)
                          Padding(
                            padding: const EdgeInsets.only(top: 6),
                            child: Text(_error!,
                                style: TextStyle(
                                    color: PlantColors.destructive(dark), fontSize: 12)),
                          ),
                        Divider(height: 20, color: Theme.of(context).colorScheme.outlineVariant),
                        Row(
                          children: [
                            IconButton(
                              onPressed: _loading ? null : () => _pickImage(ImageSource.gallery),
                              icon: const Icon(Icons.add),
                            ),
                            IconButton(
                              onPressed: _loading ? null : () => _pickImage(ImageSource.camera),
                              icon: const Icon(Icons.photo_camera_outlined),
                            ),
                            const Spacer(),
                            ListenableBuilder(
                              listenable: _inputCtrl,
                              builder: (_, _) {
                                final canSend =
                                    (_inputCtrl.text.trim().isNotEmpty || _attachedImage != null) &&
                                        !_loading;
                                return IconButton(
                                  onPressed: canSend ? _send : null,
                                  style: IconButton.styleFrom(
                                    backgroundColor:
                                        canSend ? PlantColors.primary(dark) : null,
                                    foregroundColor:
                                        canSend ? PlantColors.primaryForeground(dark) : null,
                                  ),
                                  icon: _loading
                                      ? const SizedBox(
                                          width: 16,
                                          height: 16,
                                          child: CircularProgressIndicator(strokeWidth: 2),
                                        )
                                      : const Icon(Icons.send),
                                );
                              },
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  if (_messages.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    Container(
                      constraints: const BoxConstraints(maxHeight: 260),
                      padding: const EdgeInsets.all(10),
                      decoration: plantCardDecoration(context),
                      child: ListView.builder(
                        shrinkWrap: true,
                        itemCount: _messages.length,
                        itemBuilder: (_, i) {
                          final m = _messages[i];
                          final isUser = m.role == 'user';
                          return Align(
                            alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                            child: Container(
                              margin: const EdgeInsets.symmetric(vertical: 4),
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              constraints: BoxConstraints(
                                  maxWidth: MediaQuery.sizeOf(context).width * 0.7),
                              decoration: BoxDecoration(
                                color: isUser
                                    ? Theme.of(context).colorScheme.surfaceContainerHighest
                                    : PlantColors.accentBg(dark),
                                borderRadius: BorderRadius.circular(14),
                              ),
                              child: Text(m.content, style: const TextStyle(fontSize: 13)),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                  const SizedBox(height: 20),
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 3,
                    mainAxisSpacing: 10,
                    crossAxisSpacing: 10,
                    childAspectRatio: 0.85,
                    children: [
                      _FeatureCard(
                        icon: Icons.eco_outlined,
                        title: 'AI 잎사귀 진단',
                        description: '사진 한 장으로 품종과 병징을 진단해요.',
                        onTap: () => Navigator.push(context,
                            MaterialPageRoute(builder: (_) => const DiagnosisUploadScreen())),
                      ),
                      _FeatureCard(
                        icon: Icons.calendar_month_outlined,
                        title: '케어 캘린더',
                        description: '물주기·시비 일정을 자동으로 챙겨드려요.',
                        onTap: () => Navigator.push(context,
                            MaterialPageRoute(builder: (_) => const CareCalendarScreen())),
                      ),
                      _FeatureCard(
                        icon: Icons.forum_outlined,
                        title: '식집사 커뮤니티',
                        description: '다른 식집사들과 케어 팁을 나눠보세요.',
                        onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (_) => const ComingSoonScreen(title: '식집사 커뮤니티'))),
                      ),
                    ],
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

class _FeatureCard extends StatelessWidget {
  const _FeatureCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String description;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final dark = isDark(context);
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: plantCardDecoration(context),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(color: PlantColors.accentBg(dark), shape: BoxShape.circle),
              child: Icon(icon, size: 18, color: PlantColors.primary(dark)),
            ),
            const SizedBox(height: 8),
            Text(title,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                maxLines: 2),
            const SizedBox(height: 4),
            Text(
              description,
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style:
                  TextStyle(fontSize: 10, color: Theme.of(context).colorScheme.onSurfaceVariant),
            ),
          ],
        ),
      ),
    );
  }
}
