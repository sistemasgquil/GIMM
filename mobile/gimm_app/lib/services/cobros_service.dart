import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/cobro.dart';

class CobrosService {
  final String token;

  CobrosService({required this.token});

  // =====================================
  // CABECERAS DE AUTENTICACIÓN
  // =====================================

  Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Authorization': 'Token $token',
  };

  // =====================================
  // LISTAR COBROS
  // =====================================

  Future<List<Cobro>> listarCobros() async {
    final baseUrl = await ApiConfig.cobrosUrl;

    final response = await http.get(Uri.parse(baseUrl), headers: headers);

    if (response.statusCode == 200) {
      final decoded = jsonDecode(utf8.decode(response.bodyBytes));

      final List datos = decoded is List ? decoded : decoded['results'];

      return datos.map((item) => Cobro.fromJson(item)).toList();
    }

    throw Exception('Error al consultar cobros: ${response.statusCode}');
  }

  // =====================================
  // REGISTRAR COBRO
  // =====================================

  Future<void> crearCobro(Cobro cobro) async {
    if (cobro.valor <= 0) {
      throw Exception('El valor del cobro debe ser mayor que cero.');
    }

    if (cobro.concepto.trim().isEmpty) {
      throw Exception('El concepto del cobro es obligatorio.');
    }

    if (cobro.socio <= 0) {
      throw Exception('Debe seleccionar un socio válido.');
    }

    final baseUrl = await ApiConfig.cobrosUrl;

    final response = await http.post(
      Uri.parse(baseUrl),
      headers: headers,
      body: jsonEncode(cobro.toJson()),
    );

    if (response.statusCode != 201) {
      throw Exception('No se pudo registrar el cobro: ${response.body}');
    }
  }
}
