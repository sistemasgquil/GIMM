import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

class ApiService {
  // Iniciar sesión en Django
  static Future<String> login(String username, String password) async {
    try {
      // Buscar primero el servidor Django
      final servidor = await ApiConfig.buscarServidor();

      final url = Uri.parse('$servidor/api/token/');

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
