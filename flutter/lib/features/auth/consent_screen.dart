import 'package:flutter/material.dart';

import '../../main.dart' show MainShell;
import 'auth_api.dart';
import 'auth_session.dart';
import 'auth_session_store.dart';

/// 카카오 로그인 신규 유저 — 닉네임 확인 + 서비스 약관 동의 후 계정을 확정 생성한다.
class ConsentScreen extends StatefulWidget {
  const ConsentScreen({
    super.key,
    required this.consentToken,
    required this.suggestedNickname,
    required this.deviceId,
  });

  final String consentToken;
  final String suggestedNickname;
  final String deviceId;

  @override
  State<ConsentScreen> createState() => _ConsentScreenState();
}

class _ConsentScreenState extends State<ConsentScreen> {
  late final TextEditingController _nicknameController =
      TextEditingController(text: widget.suggestedNickname);
  bool _agreeTerms = false;
  bool _submitting = false;
  String? _error;

  @override
  void dispose() {
    _nicknameController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_submitting) return;
    final nickname = _nicknameController.text.trim();
    if (nickname.isEmpty) {
      setState(() => _error = '닉네임을 입력해 주세요.');
      return;
    }
    if (!_agreeTerms) {
      setState(() => _error = '이용약관 및 개인정보처리방침에 동의해야 합니다.');
      return;
    }

    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      final tokens = await completeConsent(
        consentToken: widget.consentToken,
        nickname: nickname,
        agreeTerms: _agreeTerms,
        deviceId: widget.deviceId,
      );
      AuthSession.setAccessToken(tokens.accessToken);
      await AuthSessionStore.writeRefreshToken(tokens.refreshToken);
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const MainShell()),
      );
    } on AuthApiException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error = '가입 처리 중 문제가 발생했습니다. 다시 시도해 주세요.');
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('가입 완료')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('새싹에서 쓸 닉네임을 확인해 주세요',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
              const SizedBox(height: 12),
              TextField(
                controller: _nicknameController,
                decoration: const InputDecoration(border: OutlineInputBorder(), isDense: true),
              ),
              const SizedBox(height: 20),
              CheckboxListTile(
                value: _agreeTerms,
                onChanged: (v) => setState(() => _agreeTerms = v ?? false),
                controlAffinity: ListTileControlAffinity.leading,
                contentPadding: EdgeInsets.zero,
                title: const Text('이용약관 및 개인정보처리방침에 동의합니다', style: TextStyle(fontSize: 13)),
              ),
              if (_error != null) ...[
                const SizedBox(height: 8),
                Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error, fontSize: 13)),
              ],
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: _submitting ? null : _submit,
                  child: Text(_submitting ? '처리 중…' : '가입 완료'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
