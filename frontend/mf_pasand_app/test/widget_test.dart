import 'package:flutter_test/flutter_test.dart';

import 'package:mf_pasand/main.dart';

void main() {
  testWidgets('App renders persona screen', (WidgetTester tester) async {
    await tester.pumpWidget(const MfPasandApp());
    expect(find.text('MF Pasand'), findsOneWidget);
  });
}
