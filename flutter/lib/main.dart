import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:kakao_flutter_sdk_common/kakao_flutter_sdk_common.dart';

import 'auth.dart';
import 'features/auth/auth_session.dart';
import 'features/auth/auth_session_store.dart';
import 'features/mypage/my_page_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // KAKAO_NATIVE_APP_KEY와 동일한 값이어야 한다 (fastapi/.env) — id_token의 aud 검증이
  // 이 값 기준이라, 둘이 다르면 로그인 시도가 전부 INVALID_AUDIENCE로 실패한다.
  await KakaoSdk.init(nativeAppKey: '33804733ae14a6be9efe61e59867b8be');
  runApp(const SafeTeenApp());
}

// ─── global state ─────────────────────────────────────────────────────────────
final _themeMode = ValueNotifier<ThemeMode>(ThemeMode.light);

// ─── palette · light ──────────────────────────────────────────────────────────
// SafeTeen 트러스트 인디고 — www(app/globals.css)의 --primary와 같은 계열로 맞춘다.
class _C {
  static const bg      = Color(0xFFfbfbfd);
  static const ink     = Color(0xFF1d1d1f);
  static const muted   = Color(0xFF86868b);
  static const indigo  = Color(0xFF4F46E5);
}

// ─── palette · dark ───────────────────────────────────────────────────────────
class _DC {
  static const bg      = Color(0xFF0a0a0a);
  static const ink     = Color(0xFFf5f5f7);
  static const muted   = Color(0xFF636366);
}

// ─── adaptive color extension ─────────────────────────────────────────────────
extension _Adp on BuildContext {
  bool  get dark    => Theme.of(this).brightness == Brightness.dark;
  Color get bg      => dark ? _DC.bg      : _C.bg;
  Color get muted   => dark ? _DC.muted   : _C.muted;
}

// ─── theme builder ────────────────────────────────────────────────────────────
ThemeData _buildTheme(Brightness b) {
  final isLight = b == Brightness.light;
  return ThemeData(
    useMaterial3: true,
    brightness: b,
    scaffoldBackgroundColor: isLight ? _C.bg : _DC.bg,
    colorScheme: ColorScheme.fromSeed(seedColor: _C.indigo, brightness: b),
    appBarTheme: AppBarTheme(
      backgroundColor: isLight ? _C.bg : _DC.bg,
      foregroundColor: isLight ? _C.ink : _DC.ink,
      elevation: 0,
      scrolledUnderElevation: 0,
      titleTextStyle: TextStyle(
        color: isLight ? _C.ink : _DC.ink,
        fontSize: 18,
        fontWeight: FontWeight.w600,
        letterSpacing: -0.3,
      ),
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: isLight ? _C.bg : _DC.bg,
      selectedItemColor: isLight ? _C.ink : _DC.ink,
      unselectedItemColor: isLight ? _C.muted : _DC.muted,
      type: BottomNavigationBarType.fixed,
      elevation: 0,
      selectedLabelStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.w500),
      unselectedLabelStyle: const TextStyle(fontSize: 10),
    ),
  );
}

// ─── app ──────────────────────────────────────────────────────────────────────
class SafeTeenApp extends StatelessWidget {
  const SafeTeenApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: _themeMode,
      builder: (_, mode, _) => MaterialApp(
        title: 'SafeTeen Finance',
        debugShowCheckedModeBanner: false,
        navigatorKey: navigatorKey,
        themeMode: mode,
        theme: _buildTheme(Brightness.light),
        darkTheme: _buildTheme(Brightness.dark),
        home: const _SplashScreen(),
        routes: {
          kLoginRouteName: (_) => const KakaoLoginScreen(),
        },
      ),
    );
  }
}

// ─── splash ───────────────────────────────────────────────────────────────────
class _SplashScreen extends StatefulWidget {
  const _SplashScreen();
  @override
  State<_SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<_SplashScreen> {
  @override
  void initState() {
    super.initState();
    _goToApp();
  }

  Future<void> _goToApp() async {
    // 세션 유효성(만료·로테이션·블랙리스트)은 여기서 확인하지 않는다 — 로컬에 리프레시
    // 토큰이 있는지만 보고 즉시 분기한다(네트워크 왕복 없음). 실제 유효성은 MainShell
    // 진입 후 첫 인증 API 호출에서 401→refresh로 지연 확인된다.
    final hasSession = await AuthSessionStore.hasRefreshToken();
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => hasSession ? const MainShell() : const KakaoLoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: _C.indigo,
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'SafeTeen Finance',
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 16),
            SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white70),
            ),
          ],
        ),
      ),
    );
  }
}

// ─── main shell ───────────────────────────────────────────────────────────────
class MainShell extends StatefulWidget {
  const MainShell({super.key});
  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.bg,
      appBar: AppBar(
        backgroundColor: context.bg.withAlpha(240),
        surfaceTintColor: Colors.transparent,
        title: const Text('SafeTeen Finance'),
        titleSpacing: 16,
        actions: [
          ValueListenableBuilder<ThemeMode>(
            valueListenable: _themeMode,
            builder: (_, mode, _) => IconButton(
              tooltip: mode == ThemeMode.dark ? '라이트 모드' : '다크 모드',
              icon: Icon(
                mode == ThemeMode.dark
                    ? CupertinoIcons.sun_max
                    : CupertinoIcons.moon_stars,
                size: 20,
              ),
              color: context.muted,
              onPressed: () => _themeMode.value =
                  mode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark,
            ),
          ),
          IconButton(
            tooltip: '마이페이지',
            icon: const Icon(CupertinoIcons.person, size: 20),
            color: context.muted,
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const MyPageScreen()),
            ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: const _HomePlaceholderScreen(),
    );
  }
}

// ─── home (placeholder) ────────────────────────────────────────────────────────
// SNS 불법 금융 광고 위험도 진단 등 SafeTeen 핵심 기능은 아직 모바일에 없다
// (현재는 www/app/scan 하위에만 구현돼 있음) — 준비되는 대로 이 화면을 채운다.
class _HomePlaceholderScreen extends StatelessWidget {
  const _HomePlaceholderScreen();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(CupertinoIcons.shield, size: 40, color: context.muted),
            const SizedBox(height: 16),
            Text(
              'SafeTeen Finance',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: context.dark ? _DC.ink : _C.ink,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'SNS 불법 금융 광고 위험도 진단 기능을 준비 중입니다.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: context.muted),
            ),
          ],
        ),
      ),
    );
  }
}
