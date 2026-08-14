// SafeTeen Finance 공용 스타일. www/app/globals.css의 --primary(인디고, oklch 265°)와
// .content-card(반경 1.25rem, 은은한 섀도) 톤을 Flutter 색상으로 옮긴 값이다.
// main.dart의 다크네이비 테마(_C/_DC)는 건드리지 않고, 카드형 화면(가계부 등)만 이 액센트를 쓴다.

import 'package:flutter/material.dart';

class AppColors {
  const AppColors._();

  static Color primary(bool dark) => dark ? const Color(0xFF8B85F0) : const Color(0xFF4F46E5);
  static Color primaryForeground(bool dark) => dark ? const Color(0xFF1B1B3A) : Colors.white;
  static Color accentBg(bool dark) => dark ? const Color(0xFF241F3D) : const Color(0xFFE6E4FB);
  static Color accentForeground(bool dark) =>
      dark ? const Color(0xFFEDECFB) : const Color(0xFF332F78);
  static Color destructiveBg(bool dark) =>
      dark ? const Color(0xFF3A211F) : const Color(0xFFFBEAE9);
  static Color destructive(bool dark) => dark ? const Color(0xFFE8877E) : const Color(0xFFB3382D);
}

bool isDark(BuildContext context) => Theme.of(context).brightness == Brightness.dark;

BoxDecoration cardDecoration(BuildContext context) {
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
