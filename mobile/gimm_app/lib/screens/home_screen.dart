import 'package:flutter/material.dart';

import 'socios_screen.dart';
import 'cobros_screen.dart';
import 'usuarios_screen.dart';

class HomeScreen extends StatelessWidget {
  final String token;

  const HomeScreen({super.key, required this.token});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6FA),

      appBar: AppBar(
        title: const Text(
          'GIMM - Panel principal',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
        elevation: 2,
      ),

      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),

        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,

          children: [
            // =====================================
            // ENCABEZADO
            // =====================================
            const Text(
              '¡Bienvenido a GIMM!',
              style: TextStyle(fontSize: 25, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 8),

            const Text(
              'Sistema de gestión integral de gimnasio.',
              style: TextStyle(fontSize: 15, color: Colors.grey),
            ),

            const SizedBox(height: 25),

            // =====================================
            // TARJETA PRINCIPAL
            // =====================================
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(22),

              decoration: BoxDecoration(
                color: const Color(0xFF1565C0),
                borderRadius: BorderRadius.circular(18),
              ),

              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,

                children: [
                  Icon(Icons.fitness_center, color: Colors.white, size: 40),

                  SizedBox(height: 15),

                  Text(
                    'GIMM MÓVIL',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 23,
                      fontWeight: FontWeight.bold,
                    ),
                  ),

                  SizedBox(height: 5),

                  Text(
                    'Administración y control de tu gimnasio.',
                    style: TextStyle(color: Colors.white, fontSize: 14),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 30),

            const Text(
              'MÓDULOS DEL SISTEMA',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 15),

            // =====================================
            // SOCIOS
            // =====================================
            _modulo(
              context,
              Icons.people,
              'Socios',
              'Registrar, consultar y editar socios',
              () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => SociosScreen(token: token),
                  ),
                );
              },
            ),

            // =====================================
            // COBROS
            // =====================================
            _modulo(
              context,
              Icons.payments,
              'Cobros',
              'Pagos e historial de cobros',
              () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => CobrosScreen(token: token),
                  ),
                );
              },
            ),

            // =====================================
            // INVENTARIO
            // =====================================
            _modulo(
              context,
              Icons.inventory,
              'Inventario',
              'Productos y existencias',
              () => _proximamente(context, 'Inventario'),
            ),

            // =====================================
            // MOVIMIENTOS
            // =====================================
            _modulo(
              context,
              Icons.swap_horiz,
              'Movimientos',
              'Entradas y salidas de inventario',
              () => _proximamente(context, 'Movimientos'),
            ),

            // =====================================
            // REPORTES
            // =====================================
            _modulo(
              context,
              Icons.bar_chart,
              'Reportes',
              'Consultas y estadísticas',
              () => _proximamente(context, 'Reportes'),
            ),

            // =====================================
            // USUARIOS
            // =====================================
            _modulo(
              context,
              Icons.manage_accounts,
              'Usuarios',
              'Administración de usuarios',

              () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => UsuariosScreen(token: token),
                  ),
                );
              },
            ),

            const SizedBox(height: 25),

            const Center(
              child: Text(
                'GIMM © 2026',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // =====================================
  // TARJETAS DE LOS MÓDULOS
  // =====================================

  Widget _modulo(
    BuildContext context,
    IconData icono,
    String nombre,
    String descripcion,
    VoidCallback accion,
  ) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 12),

      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),

      child: ListTile(
        contentPadding: const EdgeInsets.all(15),

        leading: CircleAvatar(
          backgroundColor: const Color(0xFFE3F2FD),

          child: Icon(icono, color: const Color(0xFF1565C0)),
        ),

        title: Text(
          nombre,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),

        subtitle: Text(descripcion),

        trailing: const Icon(Icons.arrow_forward_ios, size: 17),

        onTap: accion,
      ),
    );
  }

  // =====================================
  // MÓDULOS PENDIENTES
  // =====================================

  void _proximamente(BuildContext context, String modulo) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('El módulo $modulo está pendiente de desarrollo.'),
      ),
    );
  }
}
