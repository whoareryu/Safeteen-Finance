// 카카오 OIDC 로그인 화면 — main.dart의 인트로 화면 다음에 뜬다(세션 없을 때만).
// id_token만 서버로 보낸다. UserApi.instance.me()는 호출하지 않는다(서버가
// 클라이언트 프로필을 신뢰하지 않는다는 원칙 — flutter/_docs/flutter-kakao-oauth-harness.md).

import 'dart:convert';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:kakao_flutter_sdk_user/kakao_flutter_sdk_user.dart';

import 'features/auth/auth_api.dart';
import 'features/auth/auth_session.dart';
import 'features/auth/auth_session_store.dart';
import 'features/auth/consent_screen.dart';
import 'main.dart' show MainShell;

String _generateNonce() {
  final bytes = List<int>.generate(24, (_) => Random.secure().nextInt(256));
  return base64UrlEncode(bytes).replaceAll('=', '');
}

class KakaoLoginScreen extends StatefulWidget {
  const KakaoLoginScreen({super.key});

  @override
  State<KakaoLoginScreen> createState() => _KakaoLoginScreenState();
}

class _KakaoLoginScreenState extends State<KakaoLoginScreen> {
  bool _loading = false;

  Future<void> _login() async {
    if (_loading) return;
    setState(() => _loading = true);
    try {
      final nonce = _generateNonce();
      OAuthToken token;
      try {
        token = await UserApi.instance.loginWithKakaoTalk(nonce: nonce);
      } catch (_) {
        token = await UserApi.instance.loginWithKakaoAccount(nonce: nonce);
      }

      final idToken = token.idToken;
      if (idToken == null) {
        throw AuthApiException('카카오 로그인 설정에 문제가 있습니다 (OpenID Connect 미활성화).');
      }

      final deviceId = await AuthSessionStore.readOrCreateDeviceId();
      final result = await loginWithKakao(idToken: idToken, nonce: nonce, deviceId: deviceId);

      if (!mounted) return;

      if (result.requiresConsent) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => ConsentScreen(
              consentToken: result.consentToken!,
              suggestedNickname: result.suggestedNickname ?? '사용자',
              deviceId: deviceId,
            ),
          ),
        );
        return;
      }

      final tokens = result.tokens!;
      AuthSession.setAccessToken(tokens.accessToken);
      await AuthSessionStore.writeRefreshToken(tokens.refreshToken);
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const MainShell()),
      );
    } on AuthApiException catch (e) {
      _showError(e.message);
    } catch (e) {
      _showError('카카오 로그인에 실패했습니다. 다시 시도해 주세요.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('Saessak',
                    style: TextStyle(fontSize: 28, fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                const Text('카카오 계정으로 시작해 보세요', style: TextStyle(fontSize: 14, color: Colors.grey)),
                const SizedBox(height: 40),
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _login,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFFEE500),
                      foregroundColor: const Color(0xFF191919),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                    child: _loading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('카카오로 시작하기', style: TextStyle(fontWeight: FontWeight.w600)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
