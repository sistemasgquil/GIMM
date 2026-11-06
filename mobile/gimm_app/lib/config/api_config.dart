class ApiConfig {
  // Dirección del servidor Django para emulador Android
  static const String baseUrl = 'http://10.0.2.2:8000';

  // Dirección para teléfono físico:
  // static const String baseUrl = 'http://192.168.1.104:8000';

  static const String tokenUrl = '$baseUrl/api/token/';

  static const String sociosUrl = '$baseUrl/api/socios/';
}
