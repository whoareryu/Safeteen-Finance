class AuthTokens {
  const AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
  });

  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;

  factory AuthTokens.fromJson(Map<String, dynamic> json) => AuthTokens(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String,
        tokenType: json['token_type'] as String,
        expiresIn: json['expires_in'] as int,
      );
}

/// 카카오 로그인 응답 — 기존 유저면 [tokens]가 채워지고, 신규 유저면 동의가
/// 필요해 [consentToken]/[suggestedNickname]이 채워진다 (status로 구분).
class MobileLoginResult {
  const MobileLoginResult({
    required this.status,
    this.tokens,
    this.isNewUser,
    this.consentToken,
    this.suggestedNickname,
  });

  final String status; // "logged_in" | "consent_required"
  final AuthTokens? tokens;
  final bool? isNewUser;
  final String? consentToken;
  final String? suggestedNickname;

  bool get requiresConsent => status == 'consent_required';

  factory MobileLoginResult.fromJson(Map<String, dynamic> json) => MobileLoginResult(
        status: json['status'] as String,
        tokens: json['access_token'] != null ? AuthTokens.fromJson(json) : null,
        isNewUser: json['is_new_user'] as bool?,
        consentToken: json['consent_token'] as String?,
        suggestedNickname: json['suggested_nickname'] as String?,
      );
}
