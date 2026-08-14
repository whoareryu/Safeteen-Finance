// 마이페이지 — SafeTeen Finance 계정 관련 기능이 아직 없어 플레이스홀더로 둔다.

import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';

class MyPageScreen extends StatelessWidget {
  const MyPageScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('마이페이지')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(CupertinoIcons.person_crop_circle, size: 40, color: Theme.of(context).colorScheme.onSurfaceVariant),
              const SizedBox(height: 16),
              const Text('마이페이지', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              const SizedBox(height: 8),
              Text(
                '계정 관련 기능을 준비 중입니다.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13, color: Theme.of(context).colorScheme.onSurfaceVariant),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
