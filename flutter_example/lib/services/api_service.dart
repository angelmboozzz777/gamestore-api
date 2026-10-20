import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/game.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class ApiService {
  // Emulador Android: 10.0.2.2 | iOS simulator / web: localhost
  // Celular fisico: IP de tu PC (ej. 192.168.1.50) | Produccion: tu URL https
  static const String baseUrl = 'http://10.0.2.2:8000';

  // En una app real guarda el token con shared_preferences o flutter_secure_storage.
  static String? token;

  static Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  static dynamic _decode(http.Response r) {
    final body = utf8.decode(r.bodyBytes);
    if (r.statusCode >= 200 && r.statusCode < 300) {
      return body.isEmpty ? null : jsonDecode(body);
    }
    String msg = body;
    try {
      msg = jsonDecode(body)['detail'].toString();
    } catch (_) {}
    throw ApiException(r.statusCode, msg);
  }

  // ---------- Auth ----------
  static Future<Map<String, dynamic>> login(String username, String password) async {
    final r = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: _headers,
      body: jsonEncode({'username': username, 'password': password}),
    );
    final data = _decode(r) as Map<String, dynamic>;
    token = data['token'] as String;
    return data['user'] as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> register({
    required String email,
    required String username,
    required String password,
    String firstname = '',
    String lastname = '',
  }) async {
    final r = await http.post(
      Uri.parse('$baseUrl/users'),
      headers: _headers,
      body: jsonEncode({
        'email': email,
        'username': username,
        'password': password,
        'name': {'firstname': firstname, 'lastname': lastname},
      }),
    );
    return _decode(r) as Map<String, dynamic>;
  }

  // ---------- Games ----------
  static Future<List<Game>> getGames({int? limit, String sort = 'asc', String? q}) async {
    final uri = Uri.parse('$baseUrl/games').replace(queryParameters: {
      if (limit != null) 'limit': '$limit',
      'sort': sort,
      if (q != null && q.isNotEmpty) 'q': q,
    });
    final list = _decode(await http.get(uri, headers: _headers)) as List;
    return list.map((e) => Game.fromJson(e)).toList();
  }

  static Future<Game> getGame(int id) async {
    final r = await http.get(Uri.parse('$baseUrl/games/$id'), headers: _headers);
    return Game.fromJson(_decode(r));
  }

  static Future<List<String>> getCategories() async {
    final r = await http.get(Uri.parse('$baseUrl/games/categories'), headers: _headers);
    return List<String>.from(_decode(r) as List);
  }

  static Future<List<Game>> getGamesByCategory(String category) async {
    final r = await http.get(
      Uri.parse('$baseUrl/games/category/${Uri.encodeComponent(category)}'),
      headers: _headers,
    );
    return (_decode(r) as List).map((e) => Game.fromJson(e)).toList();
  }

  // ---------- Carts (requieren login) ----------
  /// items: [{'gameId': 1, 'quantity': 2}, ...]
  static Future<Map<String, dynamic>> createCart(List<Map<String, int>> items) async {
    final r = await http.post(
      Uri.parse('$baseUrl/carts'),
      headers: _headers,
      body: jsonEncode({'products': items}),
    );
    return _decode(r) as Map<String, dynamic>;
  }

  static Future<List<dynamic>> getMyCarts() async {
    final r = await http.get(Uri.parse('$baseUrl/carts'), headers: _headers);
    return _decode(r) as List;
  }
}
