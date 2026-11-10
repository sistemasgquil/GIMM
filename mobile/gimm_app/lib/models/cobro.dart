class Cobro {
  final int? id;
  final int socio;
  final String? socioNombre;
  final String? socioCedula;
  final String concepto;
  final String? fechaCobro;
  final String? fechaVencimiento;
  final double valor;
  final String metodoPago;
  final String estado;
  final String observacion;

  const Cobro({
    this.id,
    required this.socio,
    this.socioNombre,
    this.socioCedula,
    required this.concepto,
    this.fechaCobro,
    this.fechaVencimiento,
    required this.valor,
    this.metodoPago = 'EFECTIVO',
    this.estado = 'PAGADO',
    this.observacion = '',
  });

  // =====================================
  // CONVERTIR JSON A OBJETO COBRO
  // =====================================

  factory Cobro.fromJson(Map<String, dynamic> json) {
    final socioJson = json['socio'];

    return Cobro(
      id: json['id'] as int?,
      socio: socioJson is Map ? socioJson['id'] as int : socioJson as int,
      socioNombre: json['socio_nombre']?.toString(),
      socioCedula: json['socio_cedula']?.toString(),
      concepto: json['concepto']?.toString() ?? '',
      fechaCobro: json['fecha_cobro']?.toString(),
      fechaVencimiento: json['fecha_vencimiento']?.toString(),
      valor: double.tryParse(json['valor']?.toString() ?? '') ?? 0.0,
      metodoPago: json['metodo_pago']?.toString() ?? 'EFECTIVO',
      estado: json['estado']?.toString() ?? 'PAGADO',
      observacion: json['observacion']?.toString() ?? '',
    );
  }

  // =====================================
  // CONVERTIR OBJETO COBRO A JSON
  // =====================================

  Map<String, dynamic> toJson() {
    return {
      'socio': socio,
      'concepto': concepto,
      'fecha_vencimiento': fechaVencimiento,
      'valor': valor.toStringAsFixed(2),
      'metodo_pago': metodoPago,
      'estado': estado,
      'observacion': observacion,
    };
  }

  // =====================================
  // OPCIONES DE MÉTODOS DE PAGO
  // =====================================

  static const List<Map<String, String>> metodosPago = [
    {'valor': 'EFECTIVO', 'nombre': 'Efectivo'},
    {'valor': 'TRANSFERENCIA', 'nombre': 'Transferencia'},
    {'valor': 'TARJETA', 'nombre': 'Tarjeta'},
    {'valor': 'OTRO', 'nombre': 'Otro'},
  ];

  // =====================================
  // OPCIONES DE ESTADOS
  // =====================================

  static const List<Map<String, String>> estados = [
    {'valor': 'PAGADO', 'nombre': 'Pagado'},
    {'valor': 'PENDIENTE', 'nombre': 'Pendiente'},
    {'valor': 'ANULADO', 'nombre': 'Anulado'},
  ];
}
