import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/usuario.dart';

class UsuariosService {
  final String token;

  UsuariosService({required this.token});

  // =====================================
  // CABECERAS DE AUTENTICACIÓN
  // =====================================

  Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Authorization': 'Token $token',
  };

  // =====================================
  // CONSULTAR REPORTE DE USUARIOS
  // =====================================

  Future<ReporteUsuarios> obtenerReporte() async {
    final url = await ApiConfig.reporteUsuariosUrl;

    final response = await http
        .get(Uri.parse(url), headers: headers)
        .timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      final decoded = jsonDecode(utf8.decode(response.bodyBytes));

      if (decoded is! Map<String, dynamic>) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (decoded['success'] != true) {
        throw Exception(decoded['mensaje'] ?? 'No se pudo obtener el reporte.');
      }

      final List datos = decoded['usuarios'] ?? [];

      final usuarios = datos.map((item) {
        return Usuario.fromJson(Map<String, dynamic>.from(item));
      }).toList();

      return ReporteUsuarios(
        totalUsuarios: _convertirNumero(decoded['total_usuarios']),
        usuariosActivos: _convertirNumero(decoded['usuarios_activos']),
        usuariosInactivos: _convertirNumero(decoded['usuarios_inactivos']),
        usuarios: usuarios,
      );
    }

    if (response.statusCode == 401) {
      throw Exception('Sesión no válida. Inicie sesión nuevamente.');
    }

    if (response.statusCode == 403) {
      throw Exception(
        'Acceso denegado. Este reporte requiere permisos de administrador.',
      );
    }

    throw Exception('Error al consultar usuarios: ${response.statusCode}');
  }

  // =====================================
  // CONVERTIR VALORES NUMÉRICOS
  // =====================================

  int _convertirNumero(dynamic valor) {
    return int.tryParse(valor.toString()) ?? 0;
  }
}

// =====================================
// RESULTADO DEL REPORTE
// =====================================

class ReporteUsuarios {
  final int totalUsuarios;
  final int usuariosActivos;
  final int usuariosInactivos;
  final List<Usuario> usuarios;

  ReporteUsuarios({
    required this.totalUsuarios,
    required this.usuariosActivos,
    required this.usuariosInactivos,
    required this.usuarios,
  });
}
