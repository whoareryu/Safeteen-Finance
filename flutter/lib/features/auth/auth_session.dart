// 액세스 토큰은 메모리에만 보관(재시작하면 사라짐 — 정상, refresh로 다시 받는다).
// 401 발생 시 refresh를 1회로 합류시키고, 실패하면 로그인 화면으로 강제 이동한다.
// (Dio 인터셉터 대신 http 패키지 관용구로 동일한 보장을 구현 — 프로젝트에 Dio 사용
// 이력이 전혀 없어 이번에도 새로 들이지 않는다.)

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:http/http.dart' as http;

import 'auth_api.dart';
import 'auth_session_store.dart';

/// main.dart의 MaterialApp에 그대로 물린다 — 어디서든 강제 로그아웃 시 이걸로 이동.
final navigatorKey = GlobalKey<NavigatorState>();

const kLoginRouteName = '/auth';

class AuthSession {
  AuthSession._();

  static String? _accessToken;
  static Completer<String?>? _refreshInFlight;

  static void setAccessToken(String token) => _accessToken = token;

  static String? get accessToken => _accessToken;

  /// 401을 받으면 refresh를 1회 시도한 뒤 정확히 1번만 재시도한다 — 재시도 루프 없음.
  /// 동시에 여러 요청이 401을 받아도 refresh 호출은 하나로 합류한다.
  static Future<http.Response> authorizedRequest(
    Future<http.Response> Function(String? accessToken) send,
  ) async {
    final res = await send(_accessToken);
    if (res.statusCode != 401) return res;

    final refreshed = await _refreshOnce();
    if (refreshed == null) {
      await forceLogout();
      return res;
    }
    return send(refreshed);
  }

  static Future<String?> _refreshOnce() {
    final inFlight = _refreshInFlight;
    if (inFlight != null) return inFlight.future;

    final completer = Completer<String?>();
    _refreshInFlight = completer;
    () async {
      try {
        final refreshToken = await AuthSessionStore.readRefreshToken();
        if (refreshToken == null) {
          completer.complete(null);
          return;
        }
        final tokens = await refreshSession(refreshToken);
        _accessToken = tokens.accessToken;
        await AuthSessionStore.writeRefreshToken(tokens.refreshToken);
        completer.complete(tokens.accessToken);
      } catch (_) {
        completer.complete(null);
      } finally {
        _refreshInFlight = null;
      }
    }();
    return completer.future;
  }

  static Future<void> forceLogout() async {
    _accessToken = null;
    await AuthSessionStore.clear();
    navigatorKey.currentState?.pushNamedAndRemoveUntil(kLoginRouteName, (route) => false);
  }
}
