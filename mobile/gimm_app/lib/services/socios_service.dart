import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/socio.dart';

class SociosService {
  final String token;

  SociosService({required this.token});

  // =====================================
  // CABECERAS DE AUTENTICACIÓN
  // =====================================

  Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Authorization': 'Token $token',
  };

  // =====================================
  // LISTAR SOCIOS
  // =====================================

  Future<List<Socio>> listarSocios() async {
    final baseUrl = await ApiConfig.sociosUrl;

    final response = await http.get(Uri.parse(baseUrl), headers: headers);

    if (response.statusCode == 200) {
      final decoded = jsonDecode(utf8.decode(response.bodyBytes));

      final List datos = decoded is List ? decoded : decoded['results'];

      return datos.map((item) => Socio.fromJson(item)).toList();
    }

    throw Exception('Error al consultar socios: ${response.statusCode}');
  }

  // =====================================
  // REGISTRAR SOCIO
  // =====================================

  Future<void> crearSocio(Socio socio) async {
    final baseUrl = await ApiConfig.sociosUrl;

    final response = await http.post(
      Uri.parse(baseUrl),
      headers: headers,
      body: jsonEncode(socio.toJson()),
    );

    if (response.statusCode != 201) {
      throw Exception('No se pudo registrar el socio: ${response.body}');
    }
  }

  // =====================================
  // EDITAR SOCIO
  // =====================================

  Future<void> editarSocio(Socio socio) async {
    final baseUrl = await ApiConfig.sociosUrl;

    final url = '$baseUrl${socio.id}/';

    final response = await http.put(
      Uri.parse(url),
      headers: headers,
      body: jsonEncode(socio.toJson()),
    );

    if (response.statusCode != 200) {
      throw Exception('No se pudo actualizar el socio: ${response.body}');
    }
  }

  // =====================================
  // ACTIVAR / DESACTIVAR SOCIO
  // =====================================

  Future<void> cambiarEstado(int id, bool activo) async {
    final baseUrl = await ApiConfig.sociosUrl;

    final url = '$baseUrl$id/';

    final response = await http.patch(
      Uri.parse(url),
      headers: headers,
      body: jsonEncode({'activo': activo}),
    );

    if (response.statusCode != 200) {
      throw Exception(
        'No se pudo cambiar el estado del socio: ${response.body}',
      );
    }
  }
}
