// fastapi/apps/ledger 백엔드 클라이언트. www/lib/ledger-api.ts와 동일한 엔드포인트·
// 필드명을 쓴다. plant와 달리 가계부는 로그인한 사용자 소유 데이터라
// AuthSession.authorizedRequest로 Bearer 토큰을 실어 보낸다 (401이면 자동 refresh 1회
// 후 재시도, 그래도 실패하면 로그인 화면으로 강제 이동).

import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

import '../auth/auth_session.dart';
import 'ledger_models.dart';

const _kLedgerApiBase = 'https://api.whoareryu.cloud/api/ledger';

class LedgerApiException implements Exception {
  LedgerApiException(this.message);
  final String message;

  @override
  String toString() => message;
}

T _parseOrThrow<T>(
  http.Response res,
  T Function(dynamic json) parse,
) {
  dynamic decoded;
  try {
    decoded = res.body.isEmpty ? null : json.decode(res.body);
  } catch (_) {
    decoded = null;
  }
  if (res.statusCode < 200 || res.statusCode >= 300) {
    final detail = decoded is Map ? decoded['detail'] : null;
    throw LedgerApiException(detail is String ? detail : 'HTTP ${res.statusCode}');
  }
  return parse(decoded);
}

Future<Receipt> uploadReceiptPhoto({
  required Uint8List photoBytes,
  required String photoFilename,
}) async {
  final res = await AuthSession.authorizedRequest((accessToken) async {
    final req = http.MultipartRequest(
      'POST',
      Uri.parse('$_kLedgerApiBase/receipts/upload'),
    );
    if (accessToken != null) {
      req.headers['Authorization'] = 'Bearer $accessToken';
    }
    req.files.add(http.MultipartFile.fromBytes('file', photoBytes, filename: photoFilename));
    final streamed = await req.send().timeout(const Duration(seconds: 30));
    return http.Response.fromStream(streamed);
  });
  return _parseOrThrow(res, (j) => Receipt.fromJson(j as Map<String, dynamic>));
}

Future<List<Receipt>> listReceipts() async {
  final res = await AuthSession.authorizedRequest((accessToken) {
    return http.get(
      Uri.parse('$_kLedgerApiBase/receipts'),
      headers: accessToken != null ? {'Authorization': 'Bearer $accessToken'} : null,
    ).timeout(const Duration(seconds: 15));
  });
  return _parseOrThrow(
    res,
    (j) => (j as List<dynamic>).map((e) => Receipt.fromJson(e as Map<String, dynamic>)).toList(),
  );
}
