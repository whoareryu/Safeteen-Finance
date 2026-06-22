import 'dart:convert';
import 'dart:math';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(const GourmetMateApp());

// ─── constants ────────────────────────────────────────────────────────────────
// iOS 시뮬레이터에서 호스트 localhost 접근 (Next.js dev server)
const _kApiBase = 'http://localhost:3000';

// ─── global state ─────────────────────────────────────────────────────────────
final _themeMode         = ValueNotifier<ThemeMode>(ThemeMode.light);
final _authUser          = ValueNotifier<_User?>(null);
final _titanicPassengers = ValueNotifier<List<_Passenger>>([]);

class _User {
  const _User({required this.username, required this.nickname});
  final String username, nickname;
}

class _Passenger {
  const _Passenger({
    required this.id,
    required this.pclass,
    required this.name,
    required this.gender,
    required this.survived,
    this.age,
  });
  final int id, pclass, survived;
  final String name, gender;
  final double? age;
}

class _ChatMsg {
  _ChatMsg.user(this.text) : isUser = true;
  _ChatMsg.assistant(this.text) : isUser = false;
  final String text;
  final bool isUser;
}

// ─── palette · light ──────────────────────────────────────────────────────────
class _C {
  static const bg      = Color(0xFFfbfbfd);
  static const ink     = Color(0xFF1d1d1f);
  static const sub     = Color(0xFF6e6e73);
  static const muted   = Color(0xFF86868b);
  static const surface = Color(0xFFf5f5f7);
  static const border  = Color(0x1A1d1d1f);
  static const amber   = Color(0xFFF59E0B);
  static const navy    = Color(0xFF1e3a5f);
}

// ─── palette · dark ───────────────────────────────────────────────────────────
class _DC {
  static const bg      = Color(0xFF0a0a0a);
  static const ink     = Color(0xFFf5f5f7);
  static const sub     = Color(0xFF98989d);
  static const muted   = Color(0xFF636366);
  static const surface = Color(0xFF1c1c1e);
  static const card    = Color(0xFF111111);
  static const border  = Color(0x1AFFFFFF);
}

// ─── adaptive color extension ─────────────────────────────────────────────────
extension _Adp on BuildContext {
  bool  get dark    => Theme.of(this).brightness == Brightness.dark;
  Color get bg      => dark ? _DC.bg      : _C.bg;
  Color get ink     => dark ? _DC.ink     : _C.ink;
  Color get sub     => dark ? _DC.sub     : _C.sub;
  Color get muted   => dark ? _DC.muted   : _C.muted;
  Color get surface => dark ? _DC.surface : _C.surface;
  Color get card    => dark ? _DC.card    : Colors.white;
  Color get border  => dark ? _DC.border  : _C.border;
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

// ─── shared data ──────────────────────────────────────────────────────────────
class _Cat {
  const _Cat(this.label, this.emoji, this.lightBg, this.darkBg);
  final String label, emoji;
  final Color lightBg, darkBg;
}

const _kCats = [
  _Cat('한식',         '🍚', Color(0xFFfef2f2), Color(0xFF2d1515)),
  _Cat('일식',         '🍣', Color(0xFFf8f9fa), Color(0xFF1a1a1a)),
  _Cat('중식',         '🥟', Color(0xFFFFFBEB), Color(0xFF2d2510)),
  _Cat('양식',         '🍝', Color(0xFFFAF5EB), Color(0xFF251f10)),
  _Cat('아시안',       '🍜', Color(0xFFF0FDF4), Color(0xFF0f2d18)),
  _Cat('분식',         '🌶️', Color(0xFFFFF7ED), Color(0xFF2d1a0a)),
  _Cat('카페·디저트', '☕', Color(0xFFFDF4FF), Color(0xFF1f0d2d)),
  _Cat('바·주점',     '🍸', Color(0xFFEEF2FF), Color(0xFF0d1229)),
];

class _Step {
  const _Step(this.no, this.title, this.sub);
  final int no;
  final String title, sub;
}

const _kSteps = [
  _Step(1, '데이터 수집',        '타이타닉 CSV 업로드·확인 단계'),
  _Step(2, '탑승자 목록',        '승객 데이터 확인 — 20명씩 페이지'),
  _Step(3, '스미스 선장과 대화', '선장 AI와 타이타닉에 대해 대화'),
];

// ─── CSV parser (Kaggle Titanic 형식) ─────────────────────────────────────────
List<_Passenger> _parseCsvTitanic(String text) {
  final lines =
      text.replaceAll('\r\n', '\n').replaceAll('\r', '\n').split('\n');
  if (lines.isEmpty) return [];

  final header =
      lines[0].split(',').map((s) => s.trim().toLowerCase()).toList();

  int idx(String name) =>
      header.indexWhere((h) => h == name.toLowerCase());

  final iId       = idx('passengerid');
  final iSurvived = idx('survived');
  final iPclass   = idx('pclass');
  final iName     = idx('name');
  final iGender   = idx('gender') >= 0 ? idx('gender') : idx('sex');
  final iAge      = idx('age');

  if ([iId, iPclass, iName, iGender].any((i) => i < 0)) {
    throw Exception(
        'CSV 헤더가 Titanic 형식이 아닙니다.\n(PassengerId, Pclass, Name, Gender/Sex 필요)');
  }

  final rows = <_Passenger>[];
  for (final raw in lines.skip(1)) {
    final line = raw.trim();
    if (line.isEmpty) continue;

    // 따옴표 안 콤마 처리 (이름 필드에 콤마 포함 가능)
    final cells = <String>[];
    var cur = '';
    var inQ = false;
    for (final ch in line.split('')) {
      if (ch == '"') {
        inQ = !inQ;
      } else if (ch == ',' && !inQ) {
        cells.add(cur);
        cur = '';
      } else {
        cur += ch;
      }
    }
    cells.add(cur);

    String cell(int i) =>
        (i >= 0 && i < cells.length) ? cells[i].trim() : '';

    final id = int.tryParse(cell(iId));
    if (id == null) continue;

    rows.add(_Passenger(
      id:       id,
      pclass:   int.tryParse(cell(iPclass)) ?? 0,
      name:     cell(iName),
      gender:   cell(iGender),
      age:      double.tryParse(cell(iAge)),
      survived: int.tryParse(cell(iSurvived)) ?? -1,
    ));
  }
  return rows;
}

// ─── app ──────────────────────────────────────────────────────────────────────
class GourmetMateApp extends StatelessWidget {
  const GourmetMateApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: _themeMode,
      builder: (_, mode, _) => MaterialApp(
        title: 'GourmetMate',
        debugShowCheckedModeBanner: false,
        themeMode: mode,
        theme: _buildTheme(Brightness.light),
        darkTheme: _buildTheme(Brightness.dark),
        home: const _MainShell(),
      ),
    );
  }
}

// ─── login sheet helper ───────────────────────────────────────────────────────
void _showLoginSheet(BuildContext context) => showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => const _LoginSheet(),
    );

// ─── main shell ───────────────────────────────────────────────────────────────
class _MainShell extends StatefulWidget {
  const _MainShell();
  @override
  State<_MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<_MainShell> {
  int _tab = 0;
  static const _titles = ['GourmetMate', '카테고리', '레슨', '마이페이지'];

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
          // 다크모드 토글
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
          // 로그인 / 닉네임
          ValueListenableBuilder<_User?>(
            valueListenable: _authUser,
            builder: (_, user, _) => user == null
                ? TextButton(
                    onPressed: () => _showLoginSheet(context),
                    style: TextButton.styleFrom(
                      foregroundColor: context.ink,
                      textStyle: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    child: const Text('로그인'),
                  )
                : GestureDetector(
                    onTap: () => setState(() => _tab = 3),
                    child: Padding(
                      padding: const EdgeInsets.only(right: 12),
                      child: Row(
                        children: [
                          Icon(CupertinoIcons.person_circle_fill,
                              size: 18, color: context.muted),
                          const SizedBox(width: 4),
                          Text(
                            user.nickname,
                            style: TextStyle(
                              color: context.ink,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: IndexedStack(
        index: _tab,
        children: const [
          _HomeTab(),
          _CategoryTab(),
          _LessonTab(),
          _MyPageTab(),
        ],
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: context.bg,
          border: Border(top: BorderSide(color: context.border, width: 0.5)),
        ),
        child: BottomNavigationBar(
          currentIndex: _tab,
          onTap: (i) => setState(() => _tab = i),
          backgroundColor: Colors.transparent,
          selectedItemColor: context.ink,
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
              icon: Icon(CupertinoIcons.square_grid_2x2),
              activeIcon: Icon(CupertinoIcons.square_grid_2x2_fill),
              label: '카테고리',
            ),
            BottomNavigationBarItem(
              icon: Icon(CupertinoIcons.book),
              activeIcon: Icon(CupertinoIcons.book_fill),
              label: '레슨',
            ),
            BottomNavigationBarItem(
              icon: Icon(CupertinoIcons.person),
              activeIcon: Icon(CupertinoIcons.person_fill),
              label: '마이페이지',
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 0 · 홈
// ═══════════════════════════════════════════════════════════════════════════════
class _HomeTab extends StatefulWidget {
  const _HomeTab();
  @override
  State<_HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<_HomeTab> {
  final _search = TextEditingController();
  final _chat   = TextEditingController();

  @override
  void dispose() {
    _search.dispose();
    _chat.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      physics: const BouncingScrollPhysics(
        parent: AlwaysScrollableScrollPhysics(),
      ),
      keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
      slivers: [
        SliverToBoxAdapter(child: _SearchBar(controller: _search)),
        SliverToBoxAdapter(child: _HeroSection()),
        SliverToBoxAdapter(child: _AiChatSection(controller: _chat)),
        const SliverToBoxAdapter(child: _HomeCategoryGrid()),
        const SliverToBoxAdapter(child: _SocialFooter()),
        const SliverToBoxAdapter(child: SizedBox(height: 16)),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 1 · 카테고리
// ═══════════════════════════════════════════════════════════════════════════════
class _CategoryTab extends StatelessWidget {
  const _CategoryTab();

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      physics: const BouncingScrollPhysics(),
      slivers: [
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
          sliver: SliverGrid.builder(
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1.5,
            ),
            itemCount: _kCats.length,
            itemBuilder: (_, i) => _CatCard(_kCats[i], large: true),
          ),
        ),
        const SliverToBoxAdapter(child: SizedBox(height: 24)),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 2 · 레슨
// ═══════════════════════════════════════════════════════════════════════════════
class _LessonTab extends StatelessWidget {
  const _LessonTab();

  void _push(BuildContext context, Widget screen) {
    Navigator.push(
      context,
      CupertinoPageRoute<void>(builder: (_) => screen),
    );
  }

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      physics: const BouncingScrollPhysics(),
      slivers: [
        // 타이타닉 모듈 헤더 카드
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
            child: _TitanicHeroCard(),
          ),
        ),
        // 단계 목록
        SliverPadding(
          padding: const EdgeInsets.all(16),
          sliver: SliverList.separated(
            itemCount: _kSteps.length,
            separatorBuilder: (_, _) => const SizedBox(height: 10),
            itemBuilder: (ctx, i) {
              final onTaps = [
                () => _push(ctx, const _DataCollectionScreen()),
                () => _push(ctx, const _PassengerListScreen()),
                () => _push(ctx, const _SmithChatScreen()),
              ];
              return _StepCard(_kSteps[i], onTap: onTaps[i]);
            },
          ),
        ),
        const SliverToBoxAdapter(child: SizedBox(height: 24)),
      ],
    );
  }
}

// ─── titanic hero card ────────────────────────────────────────────────────────
class _TitanicHeroCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 180,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF0c1929), Color(0xFF1e3a5f), Color(0xFF0a1628)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Stack(
        children: [
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                gradient: RadialGradient(
                  center: const Alignment(0, 1.8),
                  radius: 1.0,
                  colors: [
                    const Color(0xFF38BDF8).withAlpha(90),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          const Positioned(
            right: 12, top: 12,
            child: Text('🚢', style: TextStyle(fontSize: 72)),
          ),
          const Padding(
            padding: EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Text('생존 예측 · 데이터 분석',
                    style: TextStyle(color: Colors.white70, fontSize: 12)),
                SizedBox(height: 4),
                Text('타이타닉',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.w600,
                      letterSpacing: -0.5,
                    )),
                SizedBox(height: 4),
                Text('승객 데이터 수집 → 생존 예측 모델',
                    style: TextStyle(color: Colors.white70, fontSize: 13)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─── step card ────────────────────────────────────────────────────────────────
class _StepCard extends StatelessWidget {
  const _StepCard(this.step, {required this.onTap});
  final _Step step;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: context.card,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: context.border),
          boxShadow: context.dark
              ? null
              : [
                  const BoxShadow(
                    color: Color(0x06000000),
                    blurRadius: 12,
                    offset: Offset(0, 2),
                  ),
                ],
        ),
        child: Row(
          children: [
            Container(
              width: 36, height: 36,
              decoration: BoxDecoration(
                color: _C.navy,
                borderRadius: BorderRadius.circular(10),
              ),
              alignment: Alignment.center,
              child: Text(
                '${step.no}',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(step.title,
                      style: TextStyle(
                        color: context.ink,
                        fontWeight: FontWeight.w500,
                        fontSize: 15,
                      )),
                  const SizedBox(height: 2),
                  Text(step.sub,
                      style: TextStyle(color: context.sub, fontSize: 12)),
                ],
              ),
            ),
            Icon(CupertinoIcons.chevron_right,
                color: context.muted, size: 16),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// LESSON STEP 1 · 데이터 수집
// ═══════════════════════════════════════════════════════════════════════════════
class _DataCollectionScreen extends StatefulWidget {
  const _DataCollectionScreen();
  @override
  State<_DataCollectionScreen> createState() => _DataCollectionScreenState();
}

class _DataCollectionScreenState extends State<_DataCollectionScreen> {
  PlatformFile? _picked;
  bool _uploading = false;
  String? _error;
  String? _successMsg;

  Future<void> _pick() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['csv'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) return;
    setState(() {
      _picked = result.files.first;
      _error = null;
      _successMsg = null;
    });
  }

  Future<void> _upload() async {
    final file = _picked;
    if (file == null || _uploading) return;
    setState(() {
      _uploading = true;
      _error = null;
      _successMsg = null;
    });

    try {
      final bytes = file.bytes!;
      final text = utf8.decode(bytes);
      final rows = _parseCsvTitanic(text);

      if (rows.isEmpty) {
        setState(() {
          _error = 'CSV에서 유효한 행을 찾지 못했습니다.';
          _uploading = false;
        });
        return;
      }

      // 백엔드 업로드 시도 (서버가 꺼져 있으면 로컬 저장만)
      try {
        final req = http.MultipartRequest(
          'POST',
          Uri.parse('$_kApiBase/api/titanic/james/upload'),
        );
        req.files.add(
          http.MultipartFile.fromBytes('file', bytes, filename: file.name),
        );
        await req.send().timeout(const Duration(seconds: 15));
      } catch (_) {
        // 서버 연결 실패 시 로컬 데이터만 저장하고 계속 진행
      }

      _titanicPassengers.value = rows;
      setState(() {
        _uploading = false;
        _picked = null;
        _successMsg =
            '${rows.length}건을 저장했습니다.\n2. 탑승자 목록에서 확인할 수 있습니다.';
      });
    } catch (e) {
      setState(() {
        _error = e is Exception ? e.toString().replaceFirst('Exception: ', '') : '오류가 발생했습니다.';
        _uploading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.bg,
      appBar: AppBar(
        title: const Text('1. 데이터 수집'),
        backgroundColor: context.bg,
        foregroundColor: context.ink,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              '타이타닉 CSV 업로드',
              style: TextStyle(
                color: context.ink,
                fontSize: 20,
                fontWeight: FontWeight.w600,
                letterSpacing: -0.4,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Kaggle Titanic CSV를 선택해 저장합니다.\n'
              '새 파일을 올리면 기존 데이터는 교체됩니다.',
              style: TextStyle(color: context.sub, fontSize: 14, height: 1.6),
            ),
            const SizedBox(height: 24),

            // 파일 선택 영역
            GestureDetector(
              onTap: _uploading ? null : _pick,
              child: Container(
                height: 180,
                decoration: BoxDecoration(
                  color: context.card,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: context.dark
                        ? _DC.border
                        : const Color(0x26000000),
                    width: 1.5,
                  ),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(CupertinoIcons.arrow_up_doc,
                        size: 44, color: context.muted),
                    const SizedBox(height: 12),
                    Text(
                      'CSV 파일 선택',
                      style: TextStyle(
                        color: context.ink,
                        fontSize: 15,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'PassengerId · Survived · Pclass · Name · Gender · Age',
                      style: TextStyle(color: context.muted, fontSize: 11),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),

            // 선택된 파일 정보
            if (_picked != null) ...[
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                decoration: BoxDecoration(
                  color: context.surface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: context.border),
                ),
                child: Row(
                  children: [
                    Icon(CupertinoIcons.doc_text, color: context.sub, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _picked!.name,
                            style: TextStyle(color: context.ink, fontSize: 14),
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            '${(_picked!.size / 1024).toStringAsFixed(1)} KB',
                            style: TextStyle(color: context.muted, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
              FilledButton(
                onPressed: _uploading ? null : _upload,
                style: FilledButton.styleFrom(
                  backgroundColor: _C.navy,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
                child: _uploading
                    ? const SizedBox(
                        height: 18, width: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text('저장하기',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.w500)),
              ),
            ],

            // 결과 메시지
            if (_successMsg != null) ...[
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: context.dark
                      ? const Color(0xFF0f2d1a)
                      : const Color(0xFFecfdf5),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(CupertinoIcons.checkmark_circle_fill,
                        color: Color(0xFF22c55e), size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(_successMsg!,
                          style: const TextStyle(
                            color: Color(0xFF166534),
                            fontSize: 13,
                            height: 1.5,
                          )),
                    ),
                  ],
                ),
              ),
            ],
            if (_error != null) ...[
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: context.dark
                      ? const Color(0xFF2d0a0a)
                      : const Color(0xFFfef2f2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(CupertinoIcons.exclamationmark_circle_fill,
                        color: Color(0xFFef4444), size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(_error!,
                          style: const TextStyle(
                            color: Color(0xFF991b1b),
                            fontSize: 13,
                            height: 1.5,
                          )),
                    ),
                  ],
                ),
              ),
            ],

            // 형식 안내
            const SizedBox(height: 32),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: context.surface,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('필수 헤더 컬럼',
                      style: TextStyle(
                        color: context.ink,
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      )),
                  const SizedBox(height: 8),
                  for (final col in [
                    'PassengerId',
                    'Survived (0/1)',
                    'Pclass (1/2/3)',
                    'Name',
                    'Gender (또는 Sex)',
                    'Age',
                  ])
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Row(
                        children: [
                          Icon(CupertinoIcons.circle_fill,
                              size: 5, color: context.muted),
                          const SizedBox(width: 8),
                          Text(col,
                              style: TextStyle(
                                  color: context.sub, fontSize: 12)),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// LESSON STEP 2 · 탑승자 목록
// ═══════════════════════════════════════════════════════════════════════════════
class _PassengerListScreen extends StatefulWidget {
  const _PassengerListScreen();
  @override
  State<_PassengerListScreen> createState() => _PassengerListScreenState();
}

class _PassengerListScreenState extends State<_PassengerListScreen> {
  static const _pageSize = 20;
  int _page = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.bg,
      appBar: AppBar(
        title: const Text('2. 탑승자 목록'),
        backgroundColor: context.bg,
        foregroundColor: context.ink,
      ),
      body: ValueListenableBuilder<List<_Passenger>>(
        valueListenable: _titanicPassengers,
        builder: (_, passengers, _) {
          if (passengers.isEmpty) {
            return _LessonEmptyState(
              icon: CupertinoIcons.person_2,
              message: '저장된 승객 데이터가 없습니다.',
              detail: '1. 데이터 수집에서\nKaggle Titanic CSV를 먼저 업로드해 주세요.',
            );
          }

          final totalPages = max(1, (passengers.length / _pageSize).ceil());
          final page = _page.clamp(0, totalPages - 1);
          final start = page * _pageSize;
          final end = min(start + _pageSize, passengers.length);
          final slice = passengers.sublist(start, end);

          return Column(
            children: [
              // 페이지 헤더
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: context.card,
                  border: Border(bottom: BorderSide(color: context.border, width: 0.5)),
                ),
                child: Row(
                  children: [
                    Text(
                      '전체 ${passengers.length}명',
                      style: TextStyle(
                        color: context.ink, fontSize: 13, fontWeight: FontWeight.w500,
                      ),
                    ),
                    const Spacer(),
                    _PageButton(
                      icon: CupertinoIcons.chevron_left,
                      onTap: page > 0 ? () => setState(() => _page = page - 1) : null,
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      child: Text(
                        '${page + 1} / $totalPages',
                        style: TextStyle(color: context.sub, fontSize: 13),
                      ),
                    ),
                    _PageButton(
                      icon: CupertinoIcons.chevron_right,
                      onTap: page < totalPages - 1
                          ? () => setState(() => _page = page + 1)
                          : null,
                    ),
                  ],
                ),
              ),
              // 테이블
              Expanded(
                child: SingleChildScrollView(
                  scrollDirection: Axis.vertical,
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // 헤더 행
                        _TableRow(
                          cells: const ['#', '이름', '성별', '등급', '생존', '나이'],
                          isHeader: true,
                          context: context,
                        ),
                        Container(height: 1, color: context.border, width: 600),
                        // 데이터 행
                        for (final p in slice)
                          _TableRow(
                            cells: [
                              '${p.id}',
                              p.name,
                              p.gender,
                              '${p.pclass}등급',
                              p.survived == 1 ? '✓ 생존' : p.survived == 0 ? '✗ 사망' : '-',
                              p.age != null ? '${p.age!.toStringAsFixed(0)}세' : '-',
                            ],
                            isHeader: false,
                            context: context,
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _PageButton extends StatelessWidget {
  const _PageButton({required this.icon, required this.onTap});
  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(6),
        decoration: BoxDecoration(
          border: Border.all(color: context.border),
          borderRadius: BorderRadius.circular(6),
        ),
        child: Icon(
          icon,
          size: 14,
          color: onTap != null ? context.ink : context.muted,
        ),
      ),
    );
  }
}

class _TableRow extends StatelessWidget {
  const _TableRow({
    required this.cells,
    required this.isHeader,
    required this.context,
  });
  final List<String> cells;
  final bool isHeader;
  final BuildContext context;

  static const _widths = [50.0, 200.0, 60.0, 70.0, 70.0, 60.0];

  @override
  Widget build(BuildContext ctx) {
    return Container(
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: context.border, width: 0.5)),
        color: isHeader ? context.surface : null,
      ),
      child: Row(
        children: [
          for (var i = 0; i < cells.length; i++)
            Container(
              width: _widths[i],
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
              child: Text(
                cells[i],
                style: TextStyle(
                  color: isHeader ? context.sub : context.ink,
                  fontSize: isHeader ? 11 : 13,
                  fontWeight:
                      isHeader ? FontWeight.w600 : FontWeight.normal,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// LESSON STEP 3 · 스미스 선장과 대화
// ═══════════════════════════════════════════════════════════════════════════════
class _SmithChatScreen extends StatefulWidget {
  const _SmithChatScreen();
  @override
  State<_SmithChatScreen> createState() => _SmithChatScreenState();
}

class _SmithChatScreenState extends State<_SmithChatScreen> {
  final _scrollCtrl = ScrollController();
  final _inputCtrl  = TextEditingController();
  final _messages   = <_ChatMsg>[
    _ChatMsg.assistant(
      '안녕하십니까. 저는 RMS 타이타닉의 선장 에드워드 존 스미스입니다.\n'
      '타이타닉에 관해 궁금한 것이 있으시면 무엇이든 물어보십시오.',
    ),
  ];
  bool _loading = false;

  static const _suggestions = [
    '타이타닉은 어떤 배인가요?',
    '빙산과 충돌한 날 무슨 일이 있었나요?',
    '승객들은 어떻게 구조됐나요?',
    '타이타닉의 속도는 얼마였나요?',
  ];

  @override
  void dispose() {
    _scrollCtrl.dispose();
    _inputCtrl.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollCtrl.hasClients) return;
      _scrollCtrl.animateTo(
        _scrollCtrl.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  Future<void> _send([String? preset]) async {
    final text = (preset ?? _inputCtrl.text).trim();
    if (text.isEmpty || _loading) return;
    _inputCtrl.clear();

    setState(() {
      _messages.add(_ChatMsg.user(text));
      _loading = true;
    });
    _scrollToBottom();

    try {
      final res = await http
          .post(
            Uri.parse('$_kApiBase/api/titanic/smith-chat'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({'message': text}),
          )
          .timeout(const Duration(seconds: 30));

      final data = json.decode(res.body) as Map<String, dynamic>;
      final reply =
          (data['reply'] as String?) ??
          (data['error'] as String?) ??
          '응답을 받지 못했습니다.';

      setState(() {
        _messages.add(_ChatMsg.assistant(reply));
        _loading = false;
      });
    } catch (_) {
      setState(() {
        _messages.add(_ChatMsg.assistant(
            '서버에 연결할 수 없습니다.\nNext.js 서버(localhost:3000)가 실행 중인지 확인해 주세요.'));
        _loading = false;
      });
    }
    _scrollToBottom();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.bg,
      appBar: AppBar(
        title: const Text('스미스 선장과 대화'),
        backgroundColor: context.bg,
        foregroundColor: context.ink,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(0.5),
          child: Divider(height: 0.5, color: context.border),
        ),
      ),
      body: Column(
        children: [
          // 선장 프로필 배너
          Container(
            color: context.card,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: [
                Container(
                  width: 36, height: 36,
                  decoration: BoxDecoration(
                    color: _C.navy,
                    borderRadius: BorderRadius.circular(18),
                  ),
                  alignment: Alignment.center,
                  child: const Text('S',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                        fontSize: 16,
                      )),
                ),
                const SizedBox(width: 10),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Captain Edward J. Smith',
                        style: TextStyle(
                          color: context.ink,
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        )),
                    Text('RMS Titanic · 1912',
                        style: TextStyle(color: context.muted, fontSize: 12)),
                  ],
                ),
              ],
            ),
          ),
          Divider(height: 0.5, color: context.border),

          // 추천 질문 칩
          Container(
            color: context.bg,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: _suggestions
                    .map((q) => Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: GestureDetector(
                            onTap: _loading ? null : () => _send(q),
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 6),
                              decoration: BoxDecoration(
                                color: context.surface,
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(color: context.border),
                              ),
                              child: Text(q,
                                  style: TextStyle(
                                    color: context.sub, fontSize: 12)),
                            ),
                          ),
                        ))
                    .toList(),
              ),
            ),
          ),
          Divider(height: 0.5, color: context.border),

          // 메시지 목록
          Expanded(
            child: ListView.builder(
              controller: _scrollCtrl,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              itemCount: _messages.length + (_loading ? 1 : 0),
              itemBuilder: (_, i) {
                if (_loading && i == _messages.length) {
                  return _ChatBubble(
                    isUser: false,
                    child: const _TypingDots(),
                  );
                }
                final msg = _messages[i];
                return _ChatBubble(
                  isUser: msg.isUser,
                  child: Text(
                    msg.text,
                    style: TextStyle(
                      fontSize: 14,
                      height: 1.5,
                      color: msg.isUser ? context.ink : Colors.white,
                    ),
                  ),
                );
              },
            ),
          ),

          // 입력창
          Container(
            decoration: BoxDecoration(
              color: context.bg,
              border: Border(top: BorderSide(color: context.border, width: 0.5)),
            ),
            padding: EdgeInsets.only(
              left: 16, right: 12, top: 10,
              bottom: MediaQuery.viewInsetsOf(context).bottom > 0
                  ? 10
                  : MediaQuery.paddingOf(context).bottom + 10,
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(
                  child: CupertinoTextField(
                    controller: _inputCtrl,
                    placeholder: '스미스 선장에게 질문하기…',
                    placeholderStyle:
                        TextStyle(color: context.muted, fontSize: 14),
                    style: TextStyle(color: context.ink, fontSize: 14),
                    minLines: 1,
                    maxLines: 4,
                    padding:
                        const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: context.surface,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _send(),
                  ),
                ),
                const SizedBox(width: 8),
                ListenableBuilder(
                  listenable: _inputCtrl,
                  builder: (_, _) {
                    final active =
                        _inputCtrl.text.trim().isNotEmpty && !_loading;
                    return GestureDetector(
                      onTap: active ? _send : null,
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 150),
                        width: 38, height: 38,
                        decoration: BoxDecoration(
                          color: active ? _C.navy : context.surface,
                          borderRadius: BorderRadius.circular(19),
                        ),
                        child: Icon(
                          CupertinoIcons.arrow_up,
                          size: 18,
                          color: active ? Colors.white : context.muted,
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  const _ChatBubble({required this.isUser, required this.child});
  final bool isUser;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            Container(
              width: 28, height: 28,
              margin: const EdgeInsets.only(right: 6),
              decoration: BoxDecoration(
                color: _C.navy,
                borderRadius: BorderRadius.circular(14),
              ),
              alignment: Alignment.center,
              child: const Text('S',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                  )),
            ),
          ],
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.sizeOf(context).width * 0.72,
            ),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: isUser
                  ? context.surface
                  : _C.navy,
              borderRadius: BorderRadius.circular(18).copyWith(
                bottomLeft: isUser ? null : const Radius.circular(4),
                bottomRight: isUser ? const Radius.circular(4) : null,
              ),
            ),
            child: child,
          ),
        ],
      ),
    );
  }
}

class _TypingDots extends StatefulWidget {
  const _TypingDots();
  @override
  State<_TypingDots> createState() => _TypingDotsState();
}

class _TypingDotsState extends State<_TypingDots>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, _) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: List.generate(3, (i) {
            final delay = i / 3;
            final val = ((_ctrl.value - delay) % 1.0).clamp(0.0, 1.0);
            final opacity = val < 0.5 ? val * 2 : (1 - val) * 2;
            return Container(
              width: 6, height: 6,
              margin: const EdgeInsets.symmetric(horizontal: 2),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.4 + opacity * 0.6),
                shape: BoxShape.circle,
              ),
            );
          }),
        );
      },
    );
  }
}

// ─── lesson empty state ───────────────────────────────────────────────────────
class _LessonEmptyState extends StatelessWidget {
  const _LessonEmptyState({
    required this.icon,
    required this.message,
    required this.detail,
  });
  final IconData icon;
  final String message, detail;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 64, color: context.muted),
            const SizedBox(height: 16),
            Text(message,
                style: TextStyle(
                  color: context.ink,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                )),
            const SizedBox(height: 8),
            Text(detail,
                style: TextStyle(
                  color: context.sub,
                  fontSize: 13,
                  height: 1.6,
                ),
                textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 3 · 마이페이지
// ═══════════════════════════════════════════════════════════════════════════════
class _MyPageTab extends StatelessWidget {
  const _MyPageTab();

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<_User?>(
      valueListenable: _authUser,
      builder: (ctx, user, _) => CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  if (user == null)
                    _LoginPromptCard(onTap: () => _showLoginSheet(ctx))
                  else
                    _ProfileCard(user: user),
                  const SizedBox(height: 16),
                  _MenuItem(icon: CupertinoIcons.star, label: '즐겨찾기', onTap: () {}),
                  const SizedBox(height: 8),
                  _MenuItem(icon: CupertinoIcons.creditcard, label: '식비 플랜 (버짓)', onTap: () {}),
                  const SizedBox(height: 8),
                  _MenuItem(icon: CupertinoIcons.person_badge_plus, label: '고객 관리', onTap: () {}),
                  const SizedBox(height: 8),
                  _MenuItem(icon: CupertinoIcons.building_2_fill, label: '매점 관리', onTap: () {}),
                  if (user != null) ...[
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton(
                        onPressed: () => _authUser.value = null,
                        style: OutlinedButton.styleFrom(
                          foregroundColor: Colors.red,
                          side: const BorderSide(color: Colors.red),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        child: const Text('로그아웃'),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SliverToBoxAdapter(child: SizedBox(height: 24)),
        ],
      ),
    );
  }
}

class _LoginPromptCard extends StatelessWidget {
  const _LoginPromptCard({required this.onTap});
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 28),
      decoration: BoxDecoration(
        color: context.card,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: context.border),
      ),
      child: Column(
        children: [
          Icon(CupertinoIcons.person_circle, size: 60, color: context.muted),
          const SizedBox(height: 14),
          Text('로그인이 필요합니다',
              style: TextStyle(
                color: context.ink, fontSize: 16, fontWeight: FontWeight.w500,
              )),
          const SizedBox(height: 6),
          Text(
            '로그인하면 즐겨찾기·식비 플랜을\n이용할 수 있습니다',
            style: TextStyle(color: context.sub, fontSize: 13, height: 1.55),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: onTap,
              style: FilledButton.styleFrom(
                backgroundColor: context.ink,
                foregroundColor: context.bg,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: const Text('로그인',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w500)),
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfileCard extends StatelessWidget {
  const _ProfileCard({required this.user});
  final _User user;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: context.card,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: context.border),
      ),
      child: Row(
        children: [
          Container(
            width: 52, height: 52,
            decoration: BoxDecoration(
              color: _C.navy,
              borderRadius: BorderRadius.circular(26),
            ),
            alignment: Alignment.center,
            child: Text(
              user.nickname.isNotEmpty
                  ? user.nickname[0].toUpperCase()
                  : '?',
              style: const TextStyle(
                color: Colors.white, fontSize: 22, fontWeight: FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(width: 14),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(user.nickname,
                  style: TextStyle(
                    color: context.ink, fontSize: 16, fontWeight: FontWeight.w600,
                  )),
              const SizedBox(height: 2),
              Text('@${user.username}',
                  style: TextStyle(color: context.sub, fontSize: 13)),
            ],
          ),
        ],
      ),
    );
  }
}

class _MenuItem extends StatelessWidget {
  const _MenuItem({required this.icon, required this.label, required this.onTap});
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: context.card,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: context.border),
        ),
        child: Row(
          children: [
            Icon(icon, size: 20, color: context.sub),
            const SizedBox(width: 12),
            Text(label, style: TextStyle(color: context.ink, fontSize: 15)),
            const Spacer(),
            Icon(CupertinoIcons.chevron_right, size: 14, color: context.muted),
          ],
        ),
      ),
    );
  }
}

// ─── login sheet ──────────────────────────────────────────────────────────────
class _LoginSheet extends StatefulWidget {
  const _LoginSheet();
  @override
  State<_LoginSheet> createState() => _LoginSheetState();
}

class _LoginSheetState extends State<_LoginSheet> {
  final _usernameCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _usernameCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final u = _usernameCtrl.text.trim();
    final p = _passwordCtrl.text.trim();
    if (u.isEmpty || p.isEmpty) {
      setState(() => _error = '아이디와 비밀번호를 입력해 주세요.');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    await Future.delayed(const Duration(milliseconds: 800));
    _authUser.value = _User(username: u, nickname: u);
    if (mounted) Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: context.bg,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: EdgeInsets.only(
        left: 24, right: 24, top: 20,
        bottom: MediaQuery.viewInsetsOf(context).bottom + 32,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Center(
            child: Container(
              width: 36, height: 4,
              decoration: BoxDecoration(
                color: context.border,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text('로그인',
              style: TextStyle(
                color: context.ink, fontSize: 22, fontWeight: FontWeight.w600,
                letterSpacing: -0.4,
              )),
          const SizedBox(height: 20),
          CupertinoTextField(
            controller: _usernameCtrl,
            placeholder: '아이디',
            placeholderStyle: TextStyle(color: context.muted, fontSize: 15),
            style: TextStyle(color: context.ink, fontSize: 15),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
            decoration: BoxDecoration(
              color: context.surface,
              borderRadius: BorderRadius.circular(12),
            ),
            textInputAction: TextInputAction.next,
          ),
          const SizedBox(height: 10),
          CupertinoTextField(
            controller: _passwordCtrl,
            placeholder: '비밀번호',
            obscureText: true,
            placeholderStyle: TextStyle(color: context.muted, fontSize: 15),
            style: TextStyle(color: context.ink, fontSize: 15),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
            decoration: BoxDecoration(
              color: context.surface,
              borderRadius: BorderRadius.circular(12),
            ),
            textInputAction: TextInputAction.done,
            onSubmitted: (_) => _submit(),
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: Colors.red, fontSize: 13)),
          ],
          const SizedBox(height: 20),
          FilledButton(
            onPressed: _loading ? null : _submit,
            style: FilledButton.styleFrom(
              backgroundColor: context.ink,
              foregroundColor: context.bg,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
            child: Text(
              _loading ? '로그인 중...' : '로그인',
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500),
            ),
          ),
          const SizedBox(height: 8),
          OutlinedButton(
            onPressed: () => Navigator.pop(context),
            style: OutlinedButton.styleFrom(
              foregroundColor: context.sub,
              side: BorderSide(color: context.border),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
            child: const Text('취소'),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// 공용 위젯
// ═══════════════════════════════════════════════════════════════════════════════

class _SearchBar extends StatelessWidget {
  const _SearchBar({required this.controller});
  final TextEditingController controller;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: context.bg,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: CupertinoTextField(
          controller: controller,
          placeholder: '맛집·메뉴·지역 검색',
          placeholderStyle: TextStyle(color: context.muted, fontSize: 15),
          style: TextStyle(color: context.ink, fontSize: 15),
          prefix: Padding(
            padding: const EdgeInsets.only(left: 12),
            child: Icon(CupertinoIcons.search, color: context.muted, size: 18),
          ),
          clearButtonMode: OverlayVisibilityMode.editing,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 13),
          decoration: BoxDecoration(
            color: context.surface,
            borderRadius: BorderRadius.circular(12),
          ),
          textInputAction: TextInputAction.search,
        ),
      ),
    );
  }
}

class _HeroSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final titleSize = w < 400 ? 44.0 : w < 430 ? 48.0 : 52.0;

    return ColoredBox(
      color: context.bg,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(24, 36, 24, 12),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.auto_awesome_rounded,
                    size: 13, color: _C.amber),
                const SizedBox(width: 6),
                Text(
                  'SEOUL DINING · AI GUIDE',
                  style: TextStyle(
                    color: context.muted,
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                    letterSpacing: 2.2,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Text(
              'GourmetMate',
              style: TextStyle(
                color: context.ink,
                fontSize: titleSize,
                fontWeight: FontWeight.w700,
                letterSpacing: -2.0,
                height: 1.05,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 14),
            Text(
              '서울 맛집, AI가 주제별로 찾아드립니다',
              style: TextStyle(
                color: context.ink, fontSize: 17, fontWeight: FontWeight.w500,
                height: 1.45,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              '"오늘 뭐 먹지?" 고민은 이제 끝,\n내 입맛을 가장 잘 아는 인공지능\n미식 파트너 gourmetmate를 만나보세요!',
              style:
                  TextStyle(color: context.sub, fontSize: 15, height: 1.65),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 28),
          ],
        ),
      ),
    );
  }
}

class _AiChatSection extends StatefulWidget {
  const _AiChatSection({required this.controller});
  final TextEditingController controller;
  @override
  State<_AiChatSection> createState() => _AiChatSectionState();
}

class _AiChatSectionState extends State<_AiChatSection> {
  bool _sending = false;
  static const _suggestions = [
    '강남 분위기 맛집',
    '혼밥하기 좋은 곳',
    '가성비 점심',
    '데이트 식당 추천',
  ];

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: context.bg,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 36),
        child: Column(
          children: [
            Text('AI에게 바로 물어보기',
                style: TextStyle(
                  color: context.muted,
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  letterSpacing: 2.0,
                )),
            const SizedBox(height: 16),
            Container(
              decoration: BoxDecoration(
                color: context.card,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: context.border),
                boxShadow: context.dark
                    ? null
                    : [
                        const BoxShadow(
                          color: Color(0x0A000000),
                          blurRadius: 20,
                          offset: Offset(0, 4),
                        ),
                      ],
              ),
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    children: _suggestions
                        .map((s) => _Chip(
                              label: s,
                              onTap: () {
                                widget.controller.text = s;
                                widget.controller.selection =
                                    TextSelection.collapsed(
                                        offset: s.length);
                              },
                            ))
                        .toList(),
                  ),
                  const SizedBox(height: 12),
                  Divider(height: 1, color: context.border),
                  const SizedBox(height: 12),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Expanded(
                        child: CupertinoTextField(
                          controller: widget.controller,
                          placeholder: '맛집·메뉴·분위기를 AI에게 물어보기',
                          placeholderStyle:
                              TextStyle(color: context.muted, fontSize: 14),
                          style: TextStyle(color: context.ink, fontSize: 14),
                          minLines: 1,
                          maxLines: 4,
                          decoration:
                              const BoxDecoration(color: Colors.transparent),
                          padding: EdgeInsets.zero,
                          textInputAction: TextInputAction.send,
                          onSubmitted: (_) => _sendChat(),
                        ),
                      ),
                      const SizedBox(width: 10),
                      ListenableBuilder(
                        listenable: widget.controller,
                        builder: (_, _) {
                          final active =
                              widget.controller.text.trim().isNotEmpty &&
                                  !_sending;
                          return GestureDetector(
                            onTap: active ? _sendChat : null,
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 150),
                              width: 36, height: 36,
                              decoration: BoxDecoration(
                                color: active ? context.ink : context.surface,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Icon(
                                _sending
                                    ? CupertinoIcons.ellipsis
                                    : CupertinoIcons.arrow_up,
                                size: 16,
                                color: active ? context.bg : context.muted,
                              ),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _sendChat() {
    final text = widget.controller.text.trim();
    if (text.isEmpty || _sending) return;
    setState(() => _sending = true);
    Future.delayed(const Duration(milliseconds: 800), () {
      if (mounted) {
        setState(() => _sending = false);
        widget.controller.clear();
      }
    });
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.label, required this.onTap});
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 6),
        decoration: BoxDecoration(
          color: context.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: context.border),
        ),
        child: Text(label,
            style: TextStyle(color: context.sub, fontSize: 12)),
      ),
    );
  }
}

class _HomeCategoryGrid extends StatelessWidget {
  const _HomeCategoryGrid();

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: context.surface,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 28, 16, 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.only(left: 4, bottom: 16),
              child: Text('카테고리',
                  style: TextStyle(
                    color: context.ink,
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    letterSpacing: -0.4,
                  )),
            ),
            GridView.builder(
              physics: const NeverScrollableScrollPhysics(),
              shrinkWrap: true,
              gridDelegate:
                  const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 4,
                mainAxisSpacing: 10,
                crossAxisSpacing: 10,
                childAspectRatio: 0.88,
              ),
              itemCount: _kCats.length,
              itemBuilder: (_, i) => _CatCard(_kCats[i]),
            ),
          ],
        ),
      ),
    );
  }
}

class _CatCard extends StatelessWidget {
  const _CatCard(this.cat, {this.large = false});
  final _Cat cat;
  final bool large;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {},
      child: Container(
        decoration: BoxDecoration(
          color: context.dark ? cat.darkBg : cat.lightBg,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: context.border),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(cat.emoji,
                style: TextStyle(fontSize: large ? 30 : 24)),
            const SizedBox(height: 6),
            Text(
              cat.label,
              style: TextStyle(
                color: context.ink,
                fontSize: large ? 13 : 11,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
            ),
          ],
        ),
      ),
    );
  }
}

class _SocialFooter extends StatelessWidget {
  const _SocialFooter();

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: context.bg,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: _SocialCard(
                    icon: Icons.code_rounded,
                    platform: 'GitHub',
                    handle: '@Whoareryu',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _SocialCard(
                    icon: CupertinoIcons.at,
                    platform: 'X (Twitter)',
                    handle: '@Who_are_ryu__',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 14),
              decoration: BoxDecoration(
                color: context.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: context.border),
              ),
              child: Text(
                '문의사항  fbwns1234@gmail.com',
                style: TextStyle(color: context.sub, fontSize: 13),
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SocialCard extends StatelessWidget {
  const _SocialCard({
    required this.icon,
    required this.platform,
    required this.handle,
  });
  final IconData icon;
  final String platform, handle;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      decoration: BoxDecoration(
        color: context.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: context.border),
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: context.sub),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(platform,
                    style: TextStyle(color: context.muted, fontSize: 11)),
                const SizedBox(height: 2),
                Text(handle,
                    style: TextStyle(
                      color: context.ink, fontSize: 12, fontWeight: FontWeight.w500,
                    ),
                    overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
