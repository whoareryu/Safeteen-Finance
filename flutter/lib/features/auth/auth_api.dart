// 백엔드 auth 서비스(auth.whoareryu.cloud) 모바일 카카오 로그인 API 클라이언트.
// plant_api.dart와 동일한 스타일(top-level Future<T> 함수, timeout, 예외 래핑)을 따르되,
// 에러 코드는 JSON 바디가 아니라 X-Error-Code 응답 헤더로 온다(백엔드 api-standards.md
// 관례상 detail은 한국어 문자열이라 머신 판별용 코드를 헤더로 분리했기 때문).

import 'dart:convert';

import 'package:http/http.dart' as http;

import 'auth_models.dart';

const _kAuthApiBase = 'https://auth.whoareryu.cloud/auth/mobile';

class AuthApiException implements Exception {
  AuthApiException(this.message, {this.errorCode});
  final String message;
  final String? errorCode;

  @override
  String toString() => 'AuthApiException($errorCode): $message';
}

T _parseOrThrow<T>(http.Response res, T Function(dynamic json) onSuccess) {
  dynamic decoded;
  try {
    decoded = res.body.isEmpty ? null : json.decode(res.body);
  } catch (_) {
    decoded = null;
  }
  if (res.statusCode < 200 || res.statusCode >= 300) {
    final message = decoded is Map && decoded['detail'] is String
        ? decoded['detail'] as String
        : 'HTTP ${res.statusCode}';
    throw AuthApiException(message, errorCode: res.headers['x-error-code']);
  }
  return onSuccess(decoded);
}

Future<MobileLoginResult> loginWithKakao({
  required String idToken,
  required String nonce,
  required String deviceId,
}) async {
  final res = await http
      .post(
        Uri.parse('$_kAuthApiBase/kakao/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'id_token': idToken, 'nonce': nonce, 'device_id': deviceId}),
      )
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(res, (j) => MobileLoginResult.fromJson(j as Map<String, dynamic>));
}

Future<AuthTokens> completeConsent({
  required String consentToken,
  required String nickname,
  required bool agreeTerms,
  required String deviceId,
}) async {
  final res = await http
      .post(
        Uri.parse('$_kAuthApiBase/consent/complete'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'consent_token': consentToken,
          'nickname': nickname,
          'agree_terms': agreeTerms,
          'device_id': deviceId,
        }),
      )
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(res, (j) => AuthTokens.fromJson(j as Map<String, dynamic>));
}

Future<AuthTokens> refreshSession(String refreshToken) async {
  final res = await http
      .post(
        Uri.parse('$_kAuthApiBase/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'refresh_token': refreshToken}),
      )
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(res, (j) => AuthTokens.fromJson(j as Map<String, dynamic>));
}

Future<void> logoutSession(String accessToken) async {
  final res = await http.post(
    Uri.parse('$_kAuthApiBase/logout'),
    headers: {'Authorization': 'Bearer $accessToken'},
  ).timeout(const Duration(seconds: 15));
  _parseOrThrow(res, (_) => null);
}
