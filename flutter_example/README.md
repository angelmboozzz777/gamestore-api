# Ejemplo Flutter

1. Agrega la dependencia en tu `pubspec.yaml`:

```yaml
dependencies:
  http: ^1.2.0
```

2. Copia `lib/models/game.dart` y `lib/services/api_service.dart` a tu proyecto.
3. Ajusta `ApiService.baseUrl` segun donde corras la app (ver comentarios en el archivo).
4. Android con HTTP (sin https) en desarrollo: en `android/app/src/main/AndroidManifest.xml`
   agrega `android:usesCleartextTraffic="true"` dentro de `<application ...>`.
5. Uso:

```dart
final games = await ApiService.getGames(limit: 10);
final user  = await ApiService.login('demo', 'demo123');
await ApiService.createCart([{'gameId': 1, 'quantity': 2}]);
```
