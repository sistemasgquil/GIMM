import 'package:flutter/material.dart';

import '../models/usuario.dart';
import '../services/usuarios_service.dart';

class UsuariosScreen extends StatefulWidget {
  final String token;

  const UsuariosScreen({super.key, required this.token});

  @override
  State<UsuariosScreen> createState() => _UsuariosScreenState();
}

class _UsuariosScreenState extends State<UsuariosScreen> {
  late final UsuariosService _service;

  final TextEditingController _buscarController = TextEditingController();

  ReporteUsuarios? _reporte;

  bool _cargando = true;
  String? _error;

  @override
  void initState() {
    super.initState();

    _service = UsuariosService(token: widget.token);

    _cargarReporte();
  }

  @override
  void dispose() {
    _buscarController.dispose();
    super.dispose();
  }

  // =====================================
  // CONSULTAR REPORTE
  // =====================================

  Future<void> _cargarReporte() async {
    setState(() {
      _cargando = true;
      _error = null;
    });

    try {
      final resultado = await _service.obtenerReporte();

      if (!mounted) return;

      setState(() {
        _reporte = resultado;
        _cargando = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _cargando = false;
      });
    }
  }

  // =====================================
  // BUSCADOR
  // =====================================

  List<Usuario> get _usuariosFiltrados {
    if (_reporte == null) return [];

    final texto = _buscarController.text.trim().toLowerCase();

    if (texto.isEmpty) {
      return _reporte!.usuarios;
    }

    return _reporte!.usuarios.where((usuario) {
      return usuario.username.toLowerCase().contains(texto) ||
          usuario.nombres.toLowerCase().contains(texto) ||
          usuario.apellidos.toLowerCase().contains(texto) ||
          usuario.email.toLowerCase().contains(texto) ||
          usuario.telefono.toLowerCase().contains(texto) ||
          usuario.rol.toLowerCase().contains(texto);
    }).toList();
  }

  // =====================================
  // FORMATEAR FECHAS
  // =====================================

  String _formatearFecha(DateTime? fecha) {
    if (fecha == null) return 'Sin información';

    final f = fecha.toLocal();

    final dia = f.day.toString().padLeft(2, '0');
    final mes = f.month.toString().padLeft(2, '0');
    final anio = f.year;

    return '$dia/$mes/$anio';
  }

  // =====================================
  // INTERFAZ PRINCIPAL
  // =====================================

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6FA),

      appBar: AppBar(
        title: const Text(
          'Reporte de usuarios',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
        elevation: 2,
        actions: [
          IconButton(
            tooltip: 'Actualizar reporte',
            onPressed: _cargando ? null : _cargarReporte,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),

      body: RefreshIndicator(
        onRefresh: _cargarReporte,

        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(18),

          children: [
            const Text(
              'Administración de usuarios',
              style: TextStyle(
                fontSize: 23,
                fontWeight: FontWeight.bold,
                color: Color(0xFF263238),
              ),
            ),

            const SizedBox(height: 6),

            const Text(
              'Consulta los usuarios registrados en GIMM.',
              style: TextStyle(fontSize: 14, color: Colors.grey),
            ),

            const SizedBox(height: 22),

            if (_cargando)
              const Padding(
                padding: EdgeInsets.all(45),
                child: Center(
                  child: CircularProgressIndicator(color: Color(0xFF1565C0)),
                ),
              )
            else if (_error != null)
              _mostrarError()
            else if (_reporte != null) ...[
              _indicadores(),

              const SizedBox(height: 25),

              _buscador(),

              const SizedBox(height: 18),

              const Text(
                'LISTADO DE USUARIOS',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 12),

              if (_usuariosFiltrados.isEmpty)
                const Padding(
                  padding: EdgeInsets.all(30),
                  child: Center(
                    child: Text(
                      'No se encontraron usuarios.',
                      style: TextStyle(color: Colors.grey),
                    ),
                  ),
                )
              else
                ..._usuariosFiltrados.map(
                  (usuario) => _tarjetaUsuario(usuario),
                ),
            ],
          ],
        ),
      ),
    );
  }

  // =====================================
  // INDICADORES
  // =====================================

  Widget _indicadores() {
    final reporte = _reporte!;

    return LayoutBuilder(
      builder: (context, constraints) {
        final ancho = (constraints.maxWidth - 12) / 2;

        return Wrap(
          spacing: 12,
          runSpacing: 12,

          children: [
            SizedBox(
              width: ancho,
              child: _indicador(
                'Total usuarios',
                reporte.totalUsuarios,
                Icons.people,
                const Color(0xFF1565C0),
              ),
            ),

            SizedBox(
              width: ancho,
              child: _indicador(
                'Activos',
                reporte.usuariosActivos,
                Icons.check_circle,
                Colors.green,
              ),
            ),

            SizedBox(
              width: ancho,
              child: _indicador(
                'Inactivos',
                reporte.usuariosInactivos,
                Icons.cancel,
                Colors.red,
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _indicador(String titulo, int cantidad, IconData icono, Color color) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),

      child: Padding(
        padding: const EdgeInsets.all(15),

        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,

          children: [
            Icon(icono, color: color, size: 28),

            const SizedBox(height: 10),

            Text(
              cantidad.toString(),
              style: TextStyle(
                fontSize: 25,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),

            Text(
              titulo,
              style: const TextStyle(fontSize: 13, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  // =====================================
  // BUSCADOR
  // =====================================

  Widget _buscador() {
    return TextField(
      controller: _buscarController,

      onChanged: (_) {
        setState(() {});
      },

      decoration: InputDecoration(
        hintText: 'Buscar usuario...',
        prefixIcon: const Icon(Icons.search),

        suffixIcon: IconButton(
          icon: const Icon(Icons.clear),
          onPressed: () {
            _buscarController.clear();
            setState(() {});
          },
        ),

        filled: true,
        fillColor: Colors.white,

        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
      ),
    );
  }

  // =====================================
  // TARJETA DE USUARIO
  // =====================================

  Widget _tarjetaUsuario(Usuario usuario) {
    final activo = usuario.estado == 'ACTIVO';

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 12),

      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),

      child: Padding(
        padding: const EdgeInsets.all(15),

        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,

          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 23,
                  backgroundColor: const Color(0xFFE3F2FD),
                  child: Text(
                    usuario.username.isNotEmpty
                        ? usuario.username[0].toUpperCase()
                        : '?',
                    style: const TextStyle(
                      color: Color(0xFF1565C0),
                      fontWeight: FontWeight.bold,
                      fontSize: 19,
                    ),
                  ),
                ),

                const SizedBox(width: 12),

                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,

                    children: [
                      Text(
                        usuario.nombreCompleto,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),

                      Text(
                        '@${usuario.username}',
                        style: const TextStyle(
                          color: Colors.grey,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const Divider(height: 25),

            if (usuario.email.isNotEmpty)
              _datoUsuario(Icons.email_outlined, usuario.email),

            if (usuario.telefono.isNotEmpty)
              _datoUsuario(Icons.phone_outlined, usuario.telefono),

            _datoUsuario(
              Icons.admin_panel_settings_outlined,
              'Rol: ${usuario.rol}',
            ),

            _datoUsuario(
              Icons.calendar_today_outlined,
              'Registro: ${_formatearFecha(usuario.fechaRegistro)}',
            ),

            _datoUsuario(
              Icons.access_time,
              'Último acceso: ${_formatearFecha(usuario.ultimoAcceso)}',
            ),

            const SizedBox(height: 12),

            Align(
              alignment: Alignment.centerRight,

              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 13,
                  vertical: 6,
                ),

                decoration: BoxDecoration(
                  color: activo ? Colors.green.shade50 : Colors.red.shade50,

                  borderRadius: BorderRadius.circular(20),
                ),

                child: Text(
                  usuario.estado,
                  style: TextStyle(
                    color: activo ? Colors.green : Colors.red,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // =====================================
  // DATOS DEL USUARIO
  // =====================================

  Widget _datoUsuario(IconData icono, String texto) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 9),

      child: Row(
        children: [
          Icon(icono, size: 17, color: Colors.grey),

          const SizedBox(width: 9),

          Expanded(child: Text(texto, style: const TextStyle(fontSize: 13))),
        ],
      ),
    );
  }

  // =====================================
  // MOSTRAR ERRORES
  // =====================================

  Widget _mostrarError() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(22),

        child: Column(
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 45),

            const SizedBox(height: 12),

            const Text(
              'No se pudo cargar el reporte',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 10),

            Text(
              _error ?? 'Error desconocido.',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.grey),
            ),

            const SizedBox(height: 18),

            ElevatedButton.icon(
              onPressed: _cargarReporte,
              icon: const Icon(Icons.refresh),
              label: const Text('Reintentar'),
            ),
          ],
        ),
      ),
    );
  }
}
