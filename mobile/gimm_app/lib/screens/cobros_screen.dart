import 'package:flutter/material.dart';
import '../models/cobro.dart';
import '../models/socio.dart';
import '../services/cobros_service.dart';
import '../services/socios_service.dart';

class CobrosScreen extends StatefulWidget {
  final String token;

  const CobrosScreen({super.key, required this.token});

  @override
  State<CobrosScreen> createState() => _CobrosScreenState();
}

class _CobrosScreenState extends State<CobrosScreen> {
  late final CobrosService cobrosService;
  late final SociosService sociosService;

  List<Cobro> cobros = [];

  bool cargando = true;
  bool formularioAbierto = false;

  String? error;

  static const Color azul = Color(0xFF1565C0);
  static const Color azulOscuro = Color(0xFF0D47A1);
  static const Color fondo = Color(0xFFF4F7FB);

  @override
  void initState() {
    super.initState();

    cobrosService = CobrosService(token: widget.token);
    sociosService = SociosService(token: widget.token);

    cargarCobros();
  }

  // =====================================
  // MOSTRAR MENSAJES
  // =====================================

  void mostrarMensaje(
    BuildContext contexto,
    String mensaje, {
    bool correcto = false,
  }) {
    if (!contexto.mounted) return;

    final messenger = ScaffoldMessenger.maybeOf(contexto);

    if (messenger == null) return;

    messenger
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(mensaje),
          backgroundColor: correcto ? Colors.green : Colors.red,
          behavior: SnackBarBehavior.floating,
        ),
      );
  }

  // =====================================
  // CARGAR COBROS
  // =====================================

  Future<void> cargarCobros() async {
    if (!mounted) return;

    setState(() {
      cargando = true;
      error = null;
    });

    try {
      final resultado = await cobrosService.listarCobros();

      if (!mounted) return;

      setState(() {
        cobros = resultado;
        cargando = false;
        error = null;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        error = e.toString();
        cargando = false;
      });
    }
  }

  // =====================================
  // REGISTRAR COBRO
  // =====================================

  Future<void> mostrarFormulario() async {
    if (formularioAbierto || !mounted) return;

    final contextoPrincipal = context;

    setState(() {
      formularioAbierto = true;
    });

    String? mensajeError;

    try {
      // CARGAR SOCIOS ACTIVOS

      final List<Socio> socios = await sociosService.listarSocios();

      if (!contextoPrincipal.mounted) return;

      final sociosActivos = socios
          .where((socio) => socio.activo && socio.id != null)
          .toList();

      if (sociosActivos.isEmpty) {
        mostrarMensaje(
          contextoPrincipal,
          'No existen socios activos para registrar cobros.',
        );
        return;
      }

      // CONTROLADORES

      final conceptoController = TextEditingController();
      final valorController = TextEditingController();
      final observacionController = TextEditingController();

      int? socioSeleccionado = sociosActivos.first.id;

      String metodoPago = 'EFECTIVO';
      String estado = 'PAGADO';

      DateTime? fechaVencimiento;

      bool guardando = false;
      bool registrado = false;

      try {
        // COMPROBAR CONTEXTO ANTES DE ABRIR EL DIÁLOGO

        if (!contextoPrincipal.mounted) return;

        final resultado = await showDialog<bool>(
          context: contextoPrincipal,
          barrierDismissible: false,
          builder: (dialogContext) {
            return StatefulBuilder(
              builder: (contextoDialogo, actualizarDialogo) {
                return AlertDialog(
                  title: const Text(
                    'Registrar nuevo cobro',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: azulOscuro,
                    ),
                  ),

                  content: SizedBox(
                    width: 450,
                    child: SingleChildScrollView(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // SOCIO
                          DropdownButtonFormField<int>(
                            initialValue: socioSeleccionado,
                            isExpanded: true,
                            decoration: const InputDecoration(
                              labelText: 'Socio',
                              prefixIcon: Icon(Icons.person),
                              border: OutlineInputBorder(),
                            ),
                            items: sociosActivos.map((socio) {
                              return DropdownMenuItem<int>(
                                value: socio.id,
                                child: Text(
                                  '${socio.nombres} ${socio.apellidos}',
                                  overflow: TextOverflow.ellipsis,
                                ),
                              );
                            }).toList(),
                            onChanged: guardando
                                ? null
                                : (valor) {
                                    actualizarDialogo(() {
                                      socioSeleccionado = valor;
                                    });
                                  },
                          ),

                          const SizedBox(height: 15),

                          // CONCEPTO
                          TextField(
                            controller: conceptoController,
                            enabled: !guardando,
                            maxLength: 150,
                            decoration: const InputDecoration(
                              labelText: 'Concepto',
                              prefixIcon: Icon(Icons.description),
                              border: OutlineInputBorder(),
                            ),
                          ),

                          const SizedBox(height: 15),

                          // VALOR
                          TextField(
                            controller: valorController,
                            enabled: !guardando,
                            keyboardType: const TextInputType.numberWithOptions(
                              decimal: true,
                            ),
                            decoration: const InputDecoration(
                              labelText: 'Valor',
                              prefixIcon: Icon(Icons.attach_money),
                              border: OutlineInputBorder(),
                            ),
                          ),

                          const SizedBox(height: 15),

                          // MÉTODO DE PAGO
                          DropdownButtonFormField<String>(
                            initialValue: metodoPago,
                            decoration: const InputDecoration(
                              labelText: 'Método de pago',
                              prefixIcon: Icon(Icons.payment),
                              border: OutlineInputBorder(),
                            ),
                            items: Cobro.metodosPago.map((metodo) {
                              return DropdownMenuItem<String>(
                                value: metodo['valor'],
                                child: Text(metodo['nombre']!),
                              );
                            }).toList(),
                            onChanged: guardando
                                ? null
                                : (valor) {
                                    if (valor != null) {
                                      actualizarDialogo(() {
                                        metodoPago = valor;
                                      });
                                    }
                                  },
                          ),

                          const SizedBox(height: 15),

                          // ESTADO
                          DropdownButtonFormField<String>(
                            initialValue: estado,
                            decoration: const InputDecoration(
                              labelText: 'Estado',
                              prefixIcon: Icon(Icons.flag),
                              border: OutlineInputBorder(),
                            ),
                            items: Cobro.estados.map((item) {
                              return DropdownMenuItem<String>(
                                value: item['valor'],
                                child: Text(item['nombre']!),
                              );
                            }).toList(),
                            onChanged: guardando
                                ? null
                                : (valor) {
                                    if (valor != null) {
                                      actualizarDialogo(() {
                                        estado = valor;
                                      });
                                    }
                                  },
                          ),

                          const SizedBox(height: 15),

                          // FECHA DE VENCIMIENTO
                          OutlinedButton.icon(
                            onPressed: guardando
                                ? null
                                : () async {
                                    final fecha = await showDatePicker(
                                      context: dialogContext,
                                      initialDate:
                                          fechaVencimiento ?? DateTime.now(),
                                      firstDate: DateTime(2020),
                                      lastDate: DateTime(2100),
                                    );

                                    if (!dialogContext.mounted) return;

                                    if (fecha != null) {
                                      actualizarDialogo(() {
                                        fechaVencimiento = fecha;
                                      });
                                    }
                                  },
                            icon: const Icon(Icons.calendar_month),
                            label: Text(
                              fechaVencimiento == null
                                  ? 'Seleccionar vencimiento (opcional)'
                                  : 'Vence: ${formatearFecha(fechaVencimiento!.toIso8601String())}',
                            ),
                          ),

                          const SizedBox(height: 15),

                          // OBSERVACIONES
                          TextField(
                            controller: observacionController,
                            enabled: !guardando,
                            maxLines: 3,
                            maxLength: 500,
                            decoration: const InputDecoration(
                              labelText: 'Observaciones',
                              prefixIcon: Icon(Icons.notes),
                              border: OutlineInputBorder(),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  actions: [
                    // CANCELAR
                    TextButton(
                      onPressed: guardando
                          ? null
                          : () {
                              Navigator.of(dialogContext).pop(false);
                            },
                      child: const Text('Cancelar'),
                    ),

                    // GUARDAR
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: azul,
                        foregroundColor: Colors.white,
                      ),
                      icon: guardando
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.save),
                      label: Text(guardando ? 'Guardando...' : 'Guardar'),
                      onPressed: guardando
                          ? null
                          : () async {
                              final concepto = conceptoController.text.trim();

                              final valorTexto = valorController.text
                                  .trim()
                                  .replaceAll(',', '.');

                              final valor = double.tryParse(valorTexto);

                              // VALIDAR SOCIO

                              if (socioSeleccionado == null) {
                                mostrarMensaje(
                                  contextoPrincipal,
                                  'Seleccione un socio.',
                                );
                                return;
                              }

                              // VALIDAR CONCEPTO

                              if (concepto.isEmpty) {
                                mostrarMensaje(
                                  contextoPrincipal,
                                  'Ingrese el concepto del cobro.',
                                );
                                return;
                              }

                              if (concepto.length > 150) {
                                mostrarMensaje(
                                  contextoPrincipal,
                                  'El concepto supera los 150 caracteres.',
                                );
                                return;
                              }

                              // VALIDAR VALOR

                              if (valor == null ||
                                  !valor.isFinite ||
                                  valor <= 0) {
                                mostrarMensaje(
                                  contextoPrincipal,
                                  'Ingrese un valor válido mayor que cero.',
                                );
                                return;
                              }

                              if (valor > 99999999.99) {
                                mostrarMensaje(
                                  contextoPrincipal,
                                  'El valor supera el máximo permitido.',
                                );
                                return;
                              }

                              // CREAR OBJETO COBRO

                              final cobro = Cobro(
                                socio: socioSeleccionado!,
                                concepto: concepto,
                                valor: valor,
                                metodoPago: metodoPago,
                                estado: estado,
                                fechaVencimiento: fechaVencimiento
                                    ?.toIso8601String()
                                    .split('T')
                                    .first,
                                observacion: observacionController.text.trim(),
                              );

                              // BLOQUEAR DOBLE ENVÍO

                              actualizarDialogo(() {
                                guardando = true;
                              });

                              try {
                                await cobrosService.crearCobro(cobro);

                                if (!dialogContext.mounted) return;

                                // CERRAR DIÁLOGO UNA SOLA VEZ

                                Navigator.of(dialogContext).pop(true);
                              } catch (e) {
                                if (!dialogContext.mounted ||
                                    !contextoPrincipal.mounted) {
                                  return;
                                }

                                actualizarDialogo(() {
                                  guardando = false;
                                });

                                mostrarMensaje(
                                  contextoPrincipal,
                                  'No se pudo registrar el cobro: $e',
                                );
                              }
                            },
                    ),
                  ],
                );
              },
            );
          },
        );

        registrado = resultado == true;
      } finally {
        // LIBERAR CONTROLADORES

        conceptoController.dispose();
        valorController.dispose();
        observacionController.dispose();
      }

      // ACTUALIZAR LISTA DESPUÉS DEL REGISTRO

      if (registrado && contextoPrincipal.mounted) {
        await cargarCobros();

        if (!contextoPrincipal.mounted) return;

        if (error == null) {
          mostrarMensaje(
            contextoPrincipal,
            'Cobro registrado correctamente.',
            correcto: true,
          );
        } else {
          mostrarMensaje(
            contextoPrincipal,
            'El cobro fue enviado, pero no se pudo actualizar la lista.',
          );
        }
      }
    } catch (e) {
      mensajeError = e.toString();
    } finally {
      // LIBERAR CONTROL DEL FORMULARIO

      if (mounted) {
        setState(() {
          formularioAbierto = false;
        });
      }

      if (mensajeError != null && contextoPrincipal.mounted) {
        mostrarMensaje(
          contextoPrincipal,
          'Error al abrir el formulario: $mensajeError',
        );
      }
    }
  }

  // =====================================
  // FORMATEAR FECHAS
  // =====================================

  String formatearFecha(String? fecha) {
    if (fecha == null || fecha.isEmpty) {
      return 'No registrada';
    }

    final resultado = DateTime.tryParse(fecha);

    if (resultado == null) {
      return fecha;
    }

    final dia = resultado.day.toString().padLeft(2, '0');
    final mes = resultado.month.toString().padLeft(2, '0');

    return '$dia/$mes/${resultado.year}';
  }

  // =====================================
  // COLOR DEL ESTADO
  // =====================================

  Color colorEstado(String estado) {
    switch (estado) {
      case 'PAGADO':
        return Colors.green;
      case 'PENDIENTE':
        return Colors.orange;
      case 'ANULADO':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  // =====================================
  // NOMBRE DEL ESTADO
  // =====================================

  String nombreEstado(String estado) {
    switch (estado) {
      case 'PAGADO':
        return 'Pagado';
      case 'PENDIENTE':
        return 'Pendiente';
      case 'ANULADO':
        return 'Anulado';
      default:
        return estado;
    }
  }

  // =====================================
  // INTERFAZ PRINCIPAL
  // =====================================

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: fondo,

      appBar: AppBar(
        title: const Text(
          'GIMM - Cobros',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: azulOscuro,
        foregroundColor: Colors.white,
      ),

      floatingActionButton: FloatingActionButton.extended(
        onPressed: formularioAbierto ? null : mostrarFormulario,
        backgroundColor: azul,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text('Nuevo cobro'),
      ),

      body: RefreshIndicator(
        onRefresh: cargarCobros,
        child: _construirContenido(),
      ),
    );
  }

  // =====================================
  // CONTENIDO
  // =====================================

  Widget _construirContenido() {
    if (cargando) {
      return const Center(child: CircularProgressIndicator());
    }

    if (error != null) {
      return ListView(
        children: [
          const SizedBox(height: 100),

          const Icon(Icons.error_outline, size: 65, color: Colors.red),

          const SizedBox(height: 15),

          Center(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'No se pudieron cargar los cobros.\n$error',
                textAlign: TextAlign.center,
              ),
            ),
          ),

          Center(
            child: ElevatedButton.icon(
              onPressed: cargarCobros,
              icon: const Icon(Icons.refresh),
              label: const Text('Reintentar'),
            ),
          ),
        ],
      );
    }

    if (cobros.isEmpty) {
      return ListView(
        children: const [
          SizedBox(height: 130),

          Icon(Icons.receipt_long, size: 75, color: azul),

          SizedBox(height: 15),

          Center(
            child: Text(
              'No existen cobros registrados.',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w600),
            ),
          ),

          SizedBox(height: 8),

          Center(child: Text('Utilice el botón para registrar uno nuevo.')),
        ],
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(12, 15, 12, 90),
      itemCount: cobros.length,

      itemBuilder: (context, index) {
        final cobro = cobros[index];

        final nombreSocio = cobro.socioNombre?.trim();

        final socioMostrar = nombreSocio != null && nombreSocio.isNotEmpty
            ? nombreSocio
            : 'Socio #${cobro.socio}';

        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),

          child: Padding(
            padding: const EdgeInsets.all(15),

            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,

              children: [
                Row(
                  children: [
                    const CircleAvatar(
                      backgroundColor: Color(0xFFE3F2FD),
                      child: Icon(Icons.receipt_long, color: azulOscuro),
                    ),

                    const SizedBox(width: 12),

                    Expanded(
                      child: Text(
                        cobro.concepto,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),

                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 5,
                      ),

                      decoration: BoxDecoration(
                        color: colorEstado(
                          cobro.estado,
                        ).withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(20),
                      ),

                      child: Text(
                        nombreEstado(cobro.estado),
                        style: TextStyle(
                          color: colorEstado(cobro.estado),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),

                const Divider(height: 25),

                // NOMBRE DEL SOCIO
                _dato(Icons.person, 'Socio', socioMostrar),

                // CÉDULA DEL SOCIO
                if (cobro.socioCedula?.trim().isNotEmpty == true)
                  _dato(Icons.badge, 'Cédula', cobro.socioCedula!.trim()),

                _dato(
                  Icons.attach_money,
                  'Valor',
                  '\$${cobro.valor.toStringAsFixed(2)}',
                ),

                _dato(Icons.payment, 'Método de pago', cobro.metodoPago),

                _dato(
                  Icons.calendar_today,
                  'Fecha de cobro',
                  formatearFecha(cobro.fechaCobro),
                ),

                _dato(
                  Icons.event,
                  'Vencimiento',
                  formatearFecha(cobro.fechaVencimiento),
                ),

                if (cobro.observacion.isNotEmpty)
                  _dato(Icons.notes, 'Observación', cobro.observacion),
              ],
            ),
          ),
        );
      },
    );
  }

  // =====================================
  // FILAS DE INFORMACIÓN
  // =====================================

  Widget _dato(IconData icono, String titulo, String valor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 9),

      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,

        children: [
          Icon(icono, size: 19, color: azul),

          const SizedBox(width: 10),

          SizedBox(
            width: 115,
            child: Text(titulo, style: const TextStyle(color: Colors.black54)),
          ),

          Expanded(
            child: Text(
              valor,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }
}
