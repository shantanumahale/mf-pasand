import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/fund_provider.dart';
import 'providers/recommendation_provider.dart';
import 'screens/persona_screen.dart';
import 'theme.dart';

void main() {
  runApp(const MfPasandApp());
}

class MfPasandApp extends StatelessWidget {
  const MfPasandApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => RecommendationProvider()),
        ChangeNotifierProvider(create: (_) => FundProvider()),
      ],
      child: MaterialApp(
        title: 'MF Pasand',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        home: const PersonaScreen(),
      ),
    );
  }
}
