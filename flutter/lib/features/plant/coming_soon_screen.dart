// 소셜(관리자 전용 메일/디스코드/텔레그램 도구), 마이페이지(실제 로그인 필요)처럼
// 진짜 로그인 시스템이 있어야 동작하는 화면의 자리표시자. 웹의 소셜/디스코드 페이지가
// 이미 "준비 중입니다" 스텁으로 되어 있는 것과 같은 패턴이다.

import 'package:flutter/material.dart';

class ComingSoonScreen extends StatelessWidget {
  const ComingSoonScreen({super.key, required this.title, this.detail});

  final String title;
  final String? detail;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.hourglass_empty,
                  size: 48, color: Theme.of(context).colorScheme.onSurfaceVariant),
              const SizedBox(height: 16),
              const Text('준비 중입니다', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              if (detail != null) ...[
                const SizedBox(height: 8),
                Text(
                  detail!,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      fontSize: 13, color: Theme.of(context).colorScheme.onSurfaceVariant),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
