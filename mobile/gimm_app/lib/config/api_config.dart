import 'package:http/http.dart' as http;

class ApiConfig {
  static const int port = 8000;

  // Rango de búsqueda de la laptop
  static const int primeraIp = 101;
  static const int ultimaIp = 110;

  static String? _servidorEncontrado;

  // =====================================
  // BUSCAR AUTOMÁTICAMENTE EL SERVIDOR
  // =====================================

  static Future<String> buscarServidor() async {
    if (_servidorEncontrado != null) {
      return _servidorEncontrado!;
    }

    for (int ip = primeraIp; ip <= ultimaIp; ip++) {
      final servidor = 'http://192.168.1.$ip:$port';

      try {
        final respuesta = await http
            .get(Uri.parse('$servidor/api/token/'))
            .timeout(const Duration(milliseconds: 800));

        if (respuesta.statusCode == 405) {
          _servidorEncontrado = servidor;
          return servidor;
        }
      } catch (_) {
        // Continuar buscando el servidor.
      }
    }

    throw Exception('No se encontró el servidor GIMM en la red Wi-Fi.');
  }

  // =====================================
  // AUTENTICACIÓN
  // =====================================

  static Future<String> get tokenUrl async {
    return '${await buscarServidor()}/api/token/';
  }

  // =====================================
  // SOCIOS
  // =====================================

  static Future<String> get sociosUrl async {
    return '${await buscarServidor()}/api/socios/';
  }

  // =====================================
  // COBROS
  // =====================================

  static Future<String> get cobrosUrl async {
    return '${await buscarServidor()}/api/cobros/';
  }

  // =====================================
  // REPORTE DE USUARIOS
  // =====================================

  static Future<String> get reporteUsuariosUrl async {
    return '${await buscarServidor()}/api/reportes/usuarios/';
  }
}
