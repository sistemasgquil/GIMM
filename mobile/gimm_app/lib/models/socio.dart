class Socio {
  final int? id;
  final String nombres;
  final String apellidos;
  final String cedula;
  final String telefono;
  final String email;
  final String? fechaNacimiento;
  final bool activo;

  Socio({
    this.id,
    required this.nombres,
    required this.apellidos,
    required this.cedula,
    required this.telefono,
    required this.email,
    this.fechaNacimiento,
    this.activo = true,
  });

  factory Socio.fromJson(Map<String, dynamic> json) {
    return Socio(
      id: json['id'],
      nombres: json['nombres'] ?? '',
      apellidos: json['apellidos'] ?? '',
      cedula: json['cedula'] ?? '',
      telefono: json['telefono'] ?? '',
      email: json['email'] ?? '',
      fechaNacimiento: json['fecha_nacimiento'],
      activo: json['activo'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'nombres': nombres,
      'apellidos': apellidos,
      'cedula': cedula,
      'telefono': telefono,
      'email': email,
      'fecha_nacimiento': fechaNacimiento,
      'activo': activo,
    };
  }
}
