class Game {
  final int id;
  final String title;
  final double price;
  final String description;
  final String category;
  final String image;
  final String platform;
  final int stock;
  final double rate;
  final int ratingCount;

  Game({
    required this.id,
    required this.title,
    required this.price,
    required this.description,
    required this.category,
    required this.image,
    required this.platform,
    required this.stock,
    required this.rate,
    required this.ratingCount,
  });

  factory Game.fromJson(Map<String, dynamic> json) => Game(
        id: json['id'] as int,
        title: json['title'] as String,
        price: (json['price'] as num).toDouble(),
        description: (json['description'] ?? '') as String,
        category: json['category'] as String,
        image: (json['image'] ?? '') as String,
        platform: (json['platform'] ?? '') as String,
        stock: (json['stock'] ?? 0) as int,
        rate: ((json['rating']?['rate'] ?? 0) as num).toDouble(),
        ratingCount: (json['rating']?['count'] ?? 0) as int,
      );

  Map<String, dynamic> toJson() => {
        'title': title,
        'price': price,
        'description': description,
        'category': category,
        'image': image,
        'platform': platform,
        'stock': stock,
      };
}
