// 마이페이지 — 로그인 여부를 확인한 뒤, 로그인 상태면 탭(현재 "가계부") 화면을 보여준다.
// 로그인 없이는 볼 수 없는 개인 데이터(영수증)라 여기서 게이트를 건다.

import 'package:flutter/material.dart';

import '../auth/auth_session_store.dart';
import '../ledger/receipt_upload_screen.dart';
import '../../auth.dart' show KakaoLoginScreen;

class MyPageScreen extends StatefulWidget {
  const MyPageScreen({super.key});

  @override
  State<MyPageScreen> createState() => _MyPageScreenState();
}

class _MyPageScreenState extends State<MyPageScreen> {
  bool? _hasSession;

  @override
  void initState() {
    super.initState();
    AuthSessionStore.hasRefreshToken().then((has) {
      if (mounted) setState(() => _hasSession = has);
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_hasSession == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (!_hasSession!) {
      return Scaffold(
        appBar: AppBar(title: const Text('마이페이지')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('로그인이 필요해요', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                Text(
                  '가계부 등 마이페이지 기능은 로그인 후 이용할 수 있어요.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 13, color: Theme.of(context).colorScheme.onSurfaceVariant),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const KakaoLoginScreen()),
                  ),
                  child: const Text('로그인하기'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return DefaultTabController(
      length: 1,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('마이페이지'),
          bottom: const TabBar(
            tabs: [Tab(text: '가계부 영수증 업로드')],
          ),
        ),
        body: const TabBarView(
          children: [ReceiptUploadScreen()],
        ),
      ),
    );
  }
}
