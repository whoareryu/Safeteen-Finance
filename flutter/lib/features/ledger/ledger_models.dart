class ReceiptItem {
  const ReceiptItem({
    required this.name,
    required this.quantity,
    required this.unitPrice,
    required this.amount,
  });

  final String name;
  final double quantity;
  final double unitPrice;
  final double amount;

  factory ReceiptItem.fromJson(Map<String, dynamic> json) => ReceiptItem(
        name: json['name'] as String,
        quantity: (json['quantity'] as num).toDouble(),
        unitPrice: (json['unit_price'] as num).toDouble(),
        amount: (json['amount'] as num).toDouble(),
      );
}

class Receipt {
  const Receipt({
    required this.id,
    required this.ownerUserId,
    required this.imageUrl,
    required this.storeName,
    required this.purchaseDate,
    required this.totalAmount,
    required this.category,
    required this.items,
    required this.createdAt,
  });

  final int id;
  final int ownerUserId;
  final String imageUrl;
  final String storeName;
  final String purchaseDate;
  final double totalAmount;
  final String category;
  final List<ReceiptItem> items;
  final String createdAt;

  factory Receipt.fromJson(Map<String, dynamic> json) => Receipt(
        id: json['id'] as int,
        ownerUserId: json['owner_user_id'] as int,
        imageUrl: json['image_url'] as String,
        storeName: json['store_name'] as String,
        purchaseDate: json['purchase_date'] as String,
        totalAmount: (json['total_amount'] as num).toDouble(),
        category: json['category'] as String,
        items: (json['items'] as List<dynamic>)
            .map((e) => ReceiptItem.fromJson(e as Map<String, dynamic>))
            .toList(),
        createdAt: json['created_at'] as String,
      );
}
