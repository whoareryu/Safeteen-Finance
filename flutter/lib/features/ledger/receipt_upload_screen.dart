// 마이페이지 "가계부" 탭 — 영수증 촬영/선택 → 업로드 화면.
// diagnosis_upload_screen.dart와 같은 구조: 로그인 사용자 소유 데이터라
// ledger_api.dart가 AuthSession으로 Bearer 토큰을 실어 보낸다.

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../shared/app_style.dart';
import 'ledger_api.dart';
import 'receipt_result_screen.dart';

class ReceiptUploadScreen extends StatefulWidget {
  const ReceiptUploadScreen({super.key});

  @override
  State<ReceiptUploadScreen> createState() => _ReceiptUploadScreenState();
}

class _ReceiptUploadScreenState extends State<ReceiptUploadScreen> {
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
      final receipt = await uploadReceiptPhoto(
        photoBytes: bytes,
        photoFilename: picked.name,
        mimeType: picked.mimeType,
      );
      if (!mounted) return;
      setState(() => _picked = null);
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => ReceiptResultScreen(receipt: receipt)),
      );
    } catch (e) {
      if (mounted) {
        setState(() => _error = e is LedgerApiException ? e.message : '영수증 처리 중 오류가 발생했습니다.');
      }
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = isDark(context);
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text(
          '영수증 사진 업로드',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 4),
        Text(
          '영수증을 찍어 올리면 상호명·금액·품목을 자동으로 읽어 가계부에 기록해요.',
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
                      Icon(Icons.receipt_long_outlined,
                          size: 40, color: Theme.of(context).colorScheme.onSurfaceVariant),
                      const SizedBox(height: 12),
                      const Text('탭해서 영수증 사진 선택', style: TextStyle(fontWeight: FontWeight.w500)),
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
                backgroundColor: AppColors.primary(dark),
                foregroundColor: AppColors.primaryForeground(dark),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
              ),
              child: _uploading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Text('가계부에 등록하기'),
            ),
          ),
        ],
        if (_error != null) ...[
          const SizedBox(height: 12),
          Text(_error!, style: TextStyle(color: AppColors.destructive(dark))),
        ],
      ],
    );
  }
}
