// 리프레시 토큰 · 기기 식별자 로컬 보관. 토큰은 SharedPreferences에 두지 않고
// flutter_secure_storage(iOS Keychain / Android Keystore)만 쓴다.

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:uuid/uuid.dart';

const _kRefreshTokenKey = 'auth_refresh_token';
const _kDeviceIdKey = 'auth_device_id';

class AuthSessionStore {
  AuthSessionStore._();

  static const _storage = FlutterSecureStorage();

  static Future<void> writeRefreshToken(String token) =>
      _storage.write(key: _kRefreshTokenKey, value: token);

  static Future<String?> readRefreshToken() => _storage.read(key: _kRefreshTokenKey);

  static Future<bool> hasRefreshToken() async {
    final token = await readRefreshToken();
    return token != null && token.isNotEmpty;
  }

  static Future<void> clear() => _storage.delete(key: _kRefreshTokenKey);

  static Future<String> readOrCreateDeviceId() async {
    final existing = await _storage.read(key: _kDeviceIdKey);
    if (existing != null && existing.isNotEmpty) return existing;
    final id = const Uuid().v4();
    await _storage.write(key: _kDeviceIdKey, value: id);
    return id;
  }
}
