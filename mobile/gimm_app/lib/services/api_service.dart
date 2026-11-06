import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config/api_config.dart';

class ApiService {
  // ==================================================
  // AUTENTICACIÓN DE USUARIOS
  // ==================================================

  static Future<String> login(String username, String password) async {
    final url = Uri.parse(ApiConfig.tokenUrl);

    try {
      final response = await http
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'username': username, 'password': password}),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        return data['token'];
      } else if (response.statusCode == 400 || response.statusCode == 401) {
        throw Exception('Usuario o contraseña incorrectos.');
      } else {
        throw Exception('Error del servidor: ${response.statusCode}');
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }

      throw Exception('No se pudo conectar con el servidor Django.');
    }
  }
}
