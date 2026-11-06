import 'package:flutter/material.dart';

import 'screens/login_screen.dart';

void main() {
  runApp(const GimmApp());
}

class GimmApp extends StatelessWidget {
  const GimmApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,

      title: 'GIMM',

      theme: ThemeData(
        useMaterial3: true,
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: const Color(0xFFF3F5F9),
      ),

      home: const LoginScreen(),
    );
  }
}
