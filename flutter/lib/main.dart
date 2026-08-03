import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

import 'features/clock/clock_screen.dart';
import 'features/plant/care_calendar_screen.dart';
import 'features/plant/coming_soon_screen.dart';
import 'features/plant/diagnosis_upload_screen.dart';
import 'features/plant/home_screen.dart';
import 'features/plant/my_plants_screen.dart';

void main() => runApp(const SaessakApp());

// ─── global state ─────────────────────────────────────────────────────────────
final _themeMode = ValueNotifier<ThemeMode>(ThemeMode.light);

// ─── palette · light ──────────────────────────────────────────────────────────
class _C {
  static const bg      = Color(0xFFfbfbfd);
  static const ink     = Color(0xFF1d1d1f);
  static const muted   = Color(0xFF86868b);
  static const border  = Color(0x1A1d1d1f);
  static const navy    = Color(0xFF1e3a5f);
}

// ─── palette · dark ───────────────────────────────────────────────────────────
class _DC {
  static const bg      = Color(0xFF0a0a0a);
  static const ink     = Color(0xFFf5f5f7);
  static const muted   = Color(0xFF636366);
  static const border  = Color(0x1AFFFFFF);
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
    colorScheme: ColorScheme.fromSeed(seedColor: _C.navy, brightness: b),
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
class SaessakApp extends StatelessWidget {
  const SaessakApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: _themeMode,
      builder: (_, mode, _) => MaterialApp(
        title: 'Saessak',
        debugShowCheckedModeBanner: false,
        themeMode: mode,
        theme: _buildTheme(Brightness.light),
        darkTheme: _buildTheme(Brightness.dark),
        home: const _IntroVideoScreen(),
      ),
    );
  }
}

// ─── intro video ──────────────────────────────────────────────────────────────
class _IntroVideoScreen extends StatefulWidget {
  const _IntroVideoScreen();
  @override
  State<_IntroVideoScreen> createState() => _IntroVideoScreenState();
}

class _IntroVideoScreenState extends State<_IntroVideoScreen> with WidgetsBindingObserver {
  late final VideoPlayerController _controller;
  bool _navigated = false;

  // 영상 재생 중에 앱이 백그라운드로 가면 iOS가 그 순간을 스냅샷으로 찍다가 검정 화면으로
  // 멈추는 경우가 있다 — 백그라운드로 갈 때 일시정지하고, 돌아오면 인트로를 이어보지 않고
  // 바로 앱으로 넘어가 이 문제를 피한다.
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state != AppLifecycleState.resumed) {
      if (_controller.value.isInitialized && _controller.value.isPlaying) {
        _controller.pause();
      }
    } else if (!_navigated && _controller.value.isInitialized) {
      _goToApp();
    }
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    // 영상 로딩이 실패하거나 오래 걸려도 검정 화면에 멈추지 않도록 안전장치를 둔다:
    // 초기화 실패 시 즉시, 그리고 몇 초 안에 초기화가 안 끝나면 타임아웃으로 강제 전환한다.
    Future.delayed(const Duration(seconds: 6), () {
      if (!_navigated && mounted && !_controller.value.isInitialized) _goToApp();
    });
    _controller = VideoPlayerController.asset('assets/videos/intro.mp4')
      ..initialize().then((_) {
        if (!mounted) return;
        setState(() {});
        _controller.play();
      }).catchError((_) {
        _goToApp();
      });
    _controller.addListener(_onTick);
  }

  void _onTick() {
    final value = _controller.value;
    if (value.isInitialized &&
        !value.isPlaying &&
        value.position >= value.duration &&
        value.duration > Duration.zero) {
      _goToApp();
    }
  }

  void _goToApp() {
    if (_navigated) return;
    _navigated = true;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const _MainShell()),
    );
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _controller.removeListener(_onTick);
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        fit: StackFit.expand,
        children: [
          if (_controller.value.isInitialized)
            FittedBox(
              fit: BoxFit.contain,
              child: SizedBox(
                width: _controller.value.size.width,
                height: _controller.value.size.height,
                child: VideoPlayer(_controller),
              ),
            ),
          Positioned(
            right: 16,
            bottom: 32,
            child: SafeArea(
              child: GestureDetector(
                onTap: _goToApp,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.4),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: const Text(
                    '건너뛰기',
                    style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── main shell ───────────────────────────────────────────────────────────────
class _MainShell extends StatefulWidget {
  const _MainShell();
  @override
  State<_MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<_MainShell> {
  int _tab = 0;
  static const _titles = ['Saessak', '진단', '마이플랜트', '케어일정', '시계'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.bg,
      appBar: AppBar(
        backgroundColor: context.bg.withAlpha(240),
        surfaceTintColor: Colors.transparent,
        title: Text(_titles[_tab]),
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
              MaterialPageRoute(builder: (_) => const ComingSoonScreen(title: '마이페이지')),
            ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: IndexedStack(
        index: _tab,
        children: const [
          HomeScreen(),
          DiagnosisUploadScreen(),
          MyPlantsScreen(),
          CareCalendarScreen(showAppBar: false),
          ClockScreen(),
        ],
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: context.bg,
          border: Border(top: BorderSide(color: context.dark ? _DC.border : _C.border, width: 0.5)),
        ),
        child: BottomNavigationBar(
          currentIndex: _tab,
          onTap: (i) => setState(() => _tab = i),
          backgroundColor: Colors.transparent,
          selectedItemColor: context.dark ? _DC.ink : _C.ink,
          unselectedItemColor: context.muted,
          type: BottomNavigationBarType.fixed,
          elevation: 0,
          selectedLabelStyle:
              const TextStyle(fontSize: 10, fontWeight: FontWeight.w500),
          unselectedLabelStyle: const TextStyle(fontSize: 10),
          items: const [
            BottomNavigationBarItem(
              icon: Icon(CupertinoIcons.house),
              activeIcon: Icon(CupertinoIcons.house_fill),
              label: '홈',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.local_florist_outlined),
              activeIcon: Icon(Icons.local_florist),
              label: '진단',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.eco_outlined),
              activeIcon: Icon(Icons.eco),
              label: '마이플랜트',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.calendar_month_outlined),
              activeIcon: Icon(Icons.calendar_month),
              label: '케어일정',
            ),
            BottomNavigationBarItem(
              icon: Icon(CupertinoIcons.time),
              activeIcon: Icon(CupertinoIcons.time_solid),
              label: '시계',
            ),
          ],
        ),
      ),
    );
  }
}
