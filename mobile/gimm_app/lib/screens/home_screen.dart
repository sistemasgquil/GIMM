import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  final String token;

  const HomeScreen({super.key, required this.token});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('GIMM - Panel principal'),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
      ),

      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),

          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,

            children: [
              const Icon(Icons.check_circle, size: 80, color: Colors.green),

              const SizedBox(height: 20),

              const Text(
                '¡Bienvenido a GIMM!',
                style: TextStyle(fontSize: 25, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 12),

              const Text(
                'Autenticación realizada correctamente.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),

              const SizedBox(height: 30),

              const Text(
                'Próximamente tendremos aquí los módulos:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 20),

              _modulo(Icons.people, 'Socios'),

              _modulo(Icons.payments, 'Cobros'),

              _modulo(Icons.inventory, 'Inventario'),

              _modulo(Icons.bar_chart, 'Reportes'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _modulo(IconData icono, String nombre) {
    return Card(
      child: ListTile(
        leading: Icon(icono, color: const Color(0xFF1565C0)),
        title: Text(nombre),
        trailing: const Icon(Icons.arrow_forward_ios),
      ),
    );
  }
}
