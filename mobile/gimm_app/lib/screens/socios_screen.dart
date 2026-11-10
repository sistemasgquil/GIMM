import 'package:flutter/material.dart';

import '../models/socio.dart';
import '../services/socios_service.dart';

class SociosScreen extends StatefulWidget {
  final String token;

  const SociosScreen({super.key, required this.token});

  @override
  State<SociosScreen> createState() => _SociosScreenState();
}

class _SociosScreenState extends State<SociosScreen> {
  late SociosService service;

  List<Socio> socios = [];

  bool cargando = true;

  String busqueda = '';

  @override
  void initState() {
    super.initState();

    service = SociosService(token: widget.token);

    cargarSocios();
  }

  // =====================================
  // CONSULTAR SOCIOS
  // =====================================

  Future<void> cargarSocios() async {
    setState(() => cargando = true);

    try {
      final resultado = await service.listarSocios();

      if (!mounted) return;

      setState(() {
        socios = resultado;
        cargando = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() => cargando = false);

      mostrarMensaje(e.toString());
    }
  }

  // =====================================
  // MENSAJES
  // =====================================

  void mostrarMensaje(String mensaje) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(mensaje)));
  }

  // =====================================
  // FORMULARIO
  // =====================================

  void formularioSocio({Socio? socio}) {
    final formKey = GlobalKey<FormState>();

    final nombres = TextEditingController(text: socio?.nombres ?? '');

    final apellidos = TextEditingController(text: socio?.apellidos ?? '');

    final cedula = TextEditingController(text: socio?.cedula ?? '');

    final telefono = TextEditingController(text: socio?.telefono ?? '');

    final email = TextEditingController(text: socio?.email ?? '');

    final fecha = TextEditingController(text: socio?.fechaNacimiento ?? '');

    showDialog(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: Text(socio == null ? 'Registrar socio' : 'Editar socio'),

          content: SizedBox(
            width: 400,

            child: SingleChildScrollView(
              child: Form(
                key: formKey,

                child: Column(
                  mainAxisSize: MainAxisSize.min,

                  children: [
                    campo(nombres, 'Nombres'),

                    campo(apellidos, 'Apellidos'),

                    campo(
                      cedula,
                      'Cédula',
                      teclado: TextInputType.number,
                      longitud: 10,
                    ),

                    campo(telefono, 'Teléfono', teclado: TextInputType.phone),

                    campo(
                      email,
                      'Correo electrónico',
                      requerido: false,
                      teclado: TextInputType.emailAddress,
                    ),

                    campo(
                      fecha,
                      'Fecha nacimiento (AAAA-MM-DD)',
                      requerido: false,
                    ),
                  ],
                ),
              ),
            ),
          ),

          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Cancelar'),
            ),

            ElevatedButton(
              onPressed: () async {
                if (!formKey.currentState!.validate()) {
                  return;
                }

                final nuevoSocio = Socio(
                  id: socio?.id,

                  nombres: nombres.text.trim(),

                  apellidos: apellidos.text.trim(),

                  cedula: cedula.text.trim(),

                  telefono: telefono.text.trim(),

                  email: email.text.trim(),

                  fechaNacimiento: fecha.text.trim().isEmpty
                      ? null
                      : fecha.text.trim(),

                  activo: socio?.activo ?? true,
                );

                try {
                  if (socio == null) {
                    await service.crearSocio(nuevoSocio);
                  } else {
                    await service.editarSocio(nuevoSocio);
                  }
                  if (!mounted || !dialogContext.mounted) return;

                  Navigator.pop(dialogContext);

                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        socio == null
                            ? 'Socio registrado correctamente'
                            : 'Socio actualizado correctamente',
                      ),
                    ),
                  );

                  await cargarSocios();
                } catch (e) {
                  if (!mounted) return;

                  mostrarMensaje(e.toString());
                }
              },

              child: const Text('Guardar'),
            ),
          ],
        );
      },
    );
  }

  // =====================================
  // CAMPOS DEL FORMULARIO
  // =====================================

  Widget campo(
    TextEditingController controller,
    String etiqueta, {
    bool requerido = true,
    TextInputType teclado = TextInputType.text,
    int? longitud,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),

      child: TextFormField(
        controller: controller,

        keyboardType: teclado,

        maxLength: longitud,

        decoration: InputDecoration(
          labelText: etiqueta,

          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),

          counterText: '',
        ),

        validator: (value) {
          if (requerido && (value == null || value.trim().isEmpty)) {
            return 'Campo obligatorio';
          }

          if (etiqueta == 'Cédula' &&
              value != null &&
              !RegExp(r'^\d{10}$').hasMatch(value.trim())) {
            return 'La cédula debe tener 10 dígitos';
          }

          if (etiqueta == 'Correo electrónico' &&
              value != null &&
              value.trim().isNotEmpty &&
              !RegExp(r'^[^@]+@[^@]+\.[^@]+$').hasMatch(value.trim())) {
            return 'Correo electrónico inválido';
          }

          if (etiqueta == 'Fecha nacimiento (AAAA-MM-DD)' &&
              value != null &&
              value.trim().isNotEmpty &&
              !RegExp(r'^\d{4}-\d{2}-\d{2}$').hasMatch(value.trim())) {
            return 'Utiliza el formato AAAA-MM-DD';
          }

          return null;
        },
      ),
    );
  }

  // =====================================
  // CAMBIAR ESTADO
  // =====================================

  Future<void> cambiarEstado(Socio socio) async {
    try {
      await service.cambiarEstado(socio.id!, !socio.activo);

      mostrarMensaje(socio.activo ? 'Socio desactivado' : 'Socio activado');

      await cargarSocios();
    } catch (e) {
      mostrarMensaje(e.toString());
    }
  }

  // =====================================
  // INTERFAZ PRINCIPAL
  // =====================================

  @override
  Widget build(BuildContext context) {
    final filtrados = socios.where((socio) {
      final texto = '${socio.nombres} ${socio.apellidos} ${socio.cedula}'
          .toLowerCase();

      return texto.contains(busqueda.toLowerCase());
    }).toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF4F6FA),

      appBar: AppBar(
        title: const Text('Gestión de socios'),

        backgroundColor: const Color(0xFF1565C0),

        foregroundColor: Colors.white,

        actions: [
          IconButton(onPressed: cargarSocios, icon: const Icon(Icons.refresh)),
        ],
      ),

      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: const Color(0xFF1565C0),

        foregroundColor: Colors.white,

        onPressed: () => formularioSocio(),

        icon: const Icon(Icons.person_add),

        label: const Text('Nuevo socio'),
      ),

      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),

            child: TextField(
              decoration: InputDecoration(
                hintText: 'Buscar por nombre o cédula',

                prefixIcon: const Icon(Icons.search),

                filled: true,

                fillColor: Colors.white,

                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),

              onChanged: (value) {
                setState(() => busqueda = value);
              },
            ),
          ),

          Expanded(
            child: cargando
                ? const Center(child: CircularProgressIndicator())
                : filtrados.isEmpty
                ? const Center(child: Text('No hay socios registrados'))
                : RefreshIndicator(
                    onRefresh: cargarSocios,

                    child: ListView.builder(
                      padding: const EdgeInsets.all(12),

                      itemCount: filtrados.length,

                      itemBuilder: (context, index) {
                        final socio = filtrados[index];

                        return Card(
                          elevation: 2,

                          margin: const EdgeInsets.only(bottom: 12),

                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),

                          child: ListTile(
                            contentPadding: const EdgeInsets.all(12),

                            leading: CircleAvatar(
                              backgroundColor: const Color(0xFF1565C0),

                              child: Text(
                                socio.nombres.isNotEmpty
                                    ? socio.nombres[0].toUpperCase()
                                    : '?',
                                style: const TextStyle(color: Colors.white),
                              ),
                            ),

                            title: Text(
                              '${socio.nombres} ${socio.apellidos}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),

                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,

                              children: [
                                Text('Cédula: ${socio.cedula}'),

                                Text('Teléfono: ${socio.telefono}'),

                                Text(
                                  socio.activo ? 'ACTIVO' : 'INACTIVO',
                                  style: TextStyle(
                                    color: socio.activo
                                        ? Colors.green
                                        : Colors.red,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),

                            trailing: PopupMenuButton<String>(
                              onSelected: (accion) {
                                if (accion == 'editar') {
                                  formularioSocio(socio: socio);
                                }

                                if (accion == 'estado') {
                                  cambiarEstado(socio);
                                }
                              },

                              itemBuilder: (context) => [
                                const PopupMenuItem(
                                  value: 'editar',
                                  child: Text('Editar'),
                                ),

                                PopupMenuItem(
                                  value: 'estado',
                                  child: Text(
                                    socio.activo ? 'Desactivar' : 'Activar',
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}
