class Usuario {
  final int id;
  final String username;
  final String nombres;
  final String apellidos;
  final String email;
  final String telefono;
  final String rol;
  final String estado;
  final DateTime? fechaRegistro;
  final DateTime? ultimoAcceso;

  Usuario({
    required this.id,
    required this.username,
    required this.nombres,
    required this.apellidos,
    required this.email,
    required this.telefono,
    required this.rol,
    required this.estado,
    this.fechaRegistro,
    this.ultimoAcceso,
  });

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: int.tryParse('${json['id']}') ?? 0,
      username: json['username']?.toString() ?? '',
      nombres: json['nombres']?.toString() ?? '',
      apellidos: json['apellidos']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      telefono: json['telefono']?.toString() ?? '',
      rol: json['rol']?.toString() ?? 'SIN PERFIL',
      estado: json['estado']?.toString() ?? 'DESCONOCIDO',
      fechaRegistro: json['fecha_registro'] != null
          ? DateTime.tryParse(json['fecha_registro'].toString())
          : null,
      ultimoAcceso: json['ultimo_acceso'] != null
          ? DateTime.tryParse(json['ultimo_acceso'].toString())
          : null,
    ); // COBROS
  }

  String get nombreCompleto {
    final nombre = '$nombres $apellidos'.trim();

    return nombre.isEmpty ? username : nombre;
  }
}
