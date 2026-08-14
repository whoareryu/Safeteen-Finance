// 영수증 업로드 직후 Gemini Vision이 추출한 결과(상호명·금액·품목)를 보여준다.

import 'package:flutter/material.dart';

import '../../shared/app_style.dart';
import 'ledger_models.dart';

class ReceiptResultScreen extends StatelessWidget {
  const ReceiptResultScreen({super.key, required this.receipt});

  final Receipt receipt;

  String _won(double amount) => '${amount.round().toString().replaceAllMapped(
        RegExp(r'\B(?=(\d{3})+(?!\d))'),
        (m) => ',',
      )}원';

  @override
  Widget build(BuildContext context) {
    final dark = isDark(context);
    return Scaffold(
      appBar: AppBar(title: const Text('영수증 등록 완료')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.network(receipt.imageUrl, fit: BoxFit.contain),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: cardDecoration(context),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(receipt.storeName,
                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.accentBg(dark),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          receipt.category,
                          style: TextStyle(
                            fontSize: 12,
                            color: AppColors.accentForeground(dark),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(receipt.purchaseDate,
                      style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant)),
                  const SizedBox(height: 12),
                  Text(_won(receipt.totalAmount),
                      style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w700)),
                ],
              ),
            ),
            if (receipt.items.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: cardDecoration(context),
                child: Column(
                  children: [
                    for (final item in receipt.items)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                item.quantity > 1 ? '${item.name} × ${item.quantity.toStringAsFixed(0)}' : item.name,
                              ),
                            ),
                            Text(_won(item.amount)),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: () => Navigator.of(context).popUntil((r) => r.isFirst),
                style: FilledButton.styleFrom(
                  backgroundColor: AppColors.primary(dark),
                  foregroundColor: AppColors.primaryForeground(dark),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
                ),
                child: const Text('확인'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
