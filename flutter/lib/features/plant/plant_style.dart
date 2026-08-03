// 새싹(Saessak) 브랜드 스타일. www/app/globals.css의 --primary/--accent(oklch 145° 그린)와
// .saessak-card(반경 1.25rem, 은은한 섀도) 톤을 Flutter 색상으로 옮긴 값이다.
// main.dart의 기존 다크네이비 테마(_C/_DC)는 건드리지 않고, 이 플랜트 화면군만 별도 그린 악센트를 쓴다.

import 'package:flutter/material.dart';

class PlantColors {
  const PlantColors._();

  static Color primary(bool dark) => dark ? const Color(0xFF6CBF80) : const Color(0xFF3F8C52);
  static Color primaryForeground(bool dark) => dark ? const Color(0xFF10241A) : Colors.white;
  static Color accentBg(bool dark) => dark ? const Color(0xFF1E3324) : const Color(0xFFDCEEDF);
  static Color accentForeground(bool dark) =>
      dark ? const Color(0xFFE9F3EA) : const Color(0xFF294B31);
  static Color destructiveBg(bool dark) =>
      dark ? const Color(0xFF3A211F) : const Color(0xFFFBEAE9);
  static Color destructive(bool dark) => dark ? const Color(0xFFE8877E) : const Color(0xFFB3382D);
}

bool isDark(BuildContext context) => Theme.of(context).brightness == Brightness.dark;

BoxDecoration plantCardDecoration(BuildContext context) {
  final dark = isDark(context);
  final scheme = Theme.of(context).colorScheme;
  return BoxDecoration(
    color: scheme.surface,
    borderRadius: BorderRadius.circular(20),
    border: Border.all(color: scheme.outlineVariant),
    boxShadow: dark
        ? null
        : [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              blurRadius: 24,
              offset: const Offset(0, 8),
            ),
          ],
  );
}

/// 서브페이지 히어로 배너(웹의 .saessak-photo-hero--banner) — 사진 위 그린-톤 스크림 + 흰 타이틀.
class PlantHeroBanner extends StatelessWidget {
  const PlantHeroBanner({
    super.key,
    required this.title,
    required this.subtitle,
    required this.imageUrl,
  });

  final String title;
  final String subtitle;
  final String imageUrl;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 180,
      width: double.infinity,
      child: Stack(
        fit: StackFit.expand,
        children: [
          Image.network(imageUrl, fit: BoxFit.cover),
          DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.black.withValues(alpha: 0.35),
                  Colors.black.withValues(alpha: 0.55),
                ],
              ),
            ),
          ),
          Positioned(
            left: 20,
            right: 20,
            bottom: 20,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: TextStyle(color: Colors.white.withValues(alpha: 0.85), fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
