import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../models/user_persona.dart';
import '../providers/recommendation_provider.dart';
import '../theme.dart';
import 'recommendations_screen.dart';

class PersonaScreen extends StatefulWidget {
  const PersonaScreen({super.key});

  @override
  State<PersonaScreen> createState() => _PersonaScreenState();
}

class _PersonaScreenState extends State<PersonaScreen> {
  final _formKey = GlobalKey<FormState>();
  final _ageController = TextEditingController();
  final _incomeController = TextEditingController();
  final _sipController = TextEditingController();
  final _lumpsumController = TextEditingController();
  final _existingController = TextEditingController();
  final _preferencesController = TextEditingController();

  String _investmentHorizon = 'medium';
  String _riskAppetite = 'moderate';
  String _investmentGoal = 'wealth_creation';

  @override
  void dispose() {
    _ageController.dispose();
    _incomeController.dispose();
    _sipController.dispose();
    _lumpsumController.dispose();
    _existingController.dispose();
    _preferencesController.dispose();
    super.dispose();
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final persona = UserPersona(
      age: int.parse(_ageController.text.trim()),
      annualIncome: _incomeController.text.trim().isNotEmpty
          ? double.tryParse(_incomeController.text.trim())
          : null,
      investmentHorizon: _investmentHorizon,
      riskAppetite: _riskAppetite,
      investmentGoal: _investmentGoal,
      monthlySipBudget: _sipController.text.trim().isNotEmpty
          ? double.tryParse(_sipController.text.trim())
          : null,
      lumpsumAvailable: _lumpsumController.text.trim().isNotEmpty
          ? double.tryParse(_lumpsumController.text.trim())
          : null,
      existingInvestments: _existingController.text.trim().isNotEmpty
          ? _existingController.text.trim()
          : null,
      preferences: _preferencesController.text.trim().isNotEmpty
          ? _preferencesController.text.trim()
          : null,
    );

    final provider =
        Provider.of<RecommendationProvider>(context, listen: false);
    provider.fetchRecommendations(persona);

    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const RecommendationsScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'MF Pasand',
              style: GoogleFonts.inter(
                fontSize: 22,
                fontWeight: FontWeight.w700,
                color: AppTheme.primaryColor,
              ),
            ),
            Text(
              'Find mutual funds that match your profile',
              style: GoogleFonts.inter(
                fontSize: 12,
                fontWeight: FontWeight.w400,
                color: AppTheme.textSecondary,
              ),
            ),
          ],
        ),
        toolbarHeight: 64,
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 40),
          children: [
            // Age
            _SectionLabel(label: 'Age'),
            const SizedBox(height: 8),
            TextFormField(
              controller: _ageController,
              keyboardType: TextInputType.number,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              decoration: const InputDecoration(
                hintText: 'Enter your age',
                prefixIcon: Icon(Icons.person_outline, size: 20),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'Age is required';
                final age = int.tryParse(v.trim());
                if (age == null || age < 18 || age > 100) {
                  return 'Enter a valid age (18-100)';
                }
                return null;
              },
            ),

            const SizedBox(height: 24),

            // Annual Income
            _SectionLabel(label: 'Annual Income (\u20B9 Lakhs)', optional: true),
            const SizedBox(height: 8),
            TextFormField(
              controller: _incomeController,
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
              ],
              decoration: const InputDecoration(
                hintText: 'e.g., 12',
                prefixIcon: Icon(Icons.currency_rupee, size: 20),
              ),
            ),

            const SizedBox(height: 24),

            // Investment Horizon
            _SectionLabel(label: 'Investment Horizon'),
            const SizedBox(height: 10),
            _ChoiceChipGroup(
              options: const {
                'short': 'Short (<3 yrs)',
                'medium': 'Medium (3-7 yrs)',
                'long': 'Long (7+ yrs)',
              },
              selected: _investmentHorizon,
              onSelected: (v) => setState(() => _investmentHorizon = v),
            ),

            const SizedBox(height: 24),

            // Risk Appetite
            _SectionLabel(label: 'Risk Appetite'),
            const SizedBox(height: 10),
            _ChoiceChipGroup(
              options: const {
                'low': 'Low',
                'moderate': 'Moderate',
                'high': 'High',
                'very_high': 'Very High',
              },
              selected: _riskAppetite,
              onSelected: (v) => setState(() => _riskAppetite = v),
            ),

            const SizedBox(height: 24),

            // Investment Goal
            _SectionLabel(label: 'Investment Goal'),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              initialValue: _investmentGoal,
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.flag_outlined, size: 20),
              ),
              borderRadius: BorderRadius.circular(12),
              items: const [
                DropdownMenuItem(
                    value: 'wealth_creation', child: Text('Wealth Creation')),
                DropdownMenuItem(
                    value: 'tax_saving', child: Text('Tax Saving')),
                DropdownMenuItem(
                    value: 'retirement', child: Text('Retirement')),
                DropdownMenuItem(
                    value: 'child_education', child: Text('Child Education')),
                DropdownMenuItem(
                    value: 'emergency_fund', child: Text('Emergency Fund')),
                DropdownMenuItem(
                    value: 'regular_income', child: Text('Regular Income')),
              ],
              onChanged: (v) {
                if (v != null) setState(() => _investmentGoal = v);
              },
            ),

            const SizedBox(height: 24),

            // Monthly SIP Budget
            _SectionLabel(label: 'Monthly SIP Budget (\u20B9)', optional: true),
            const SizedBox(height: 8),
            TextFormField(
              controller: _sipController,
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
              ],
              decoration: const InputDecoration(
                hintText: 'e.g., 5000',
                prefixIcon: Icon(Icons.calendar_month_outlined, size: 20),
              ),
            ),

            const SizedBox(height: 24),

            // Lumpsum Available
            _SectionLabel(label: 'Lumpsum Available (\u20B9)', optional: true),
            const SizedBox(height: 8),
            TextFormField(
              controller: _lumpsumController,
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
              ],
              decoration: const InputDecoration(
                hintText: 'e.g., 100000',
                prefixIcon: Icon(Icons.account_balance_wallet_outlined, size: 20),
              ),
            ),

            const SizedBox(height: 24),

            // Existing Investments
            _SectionLabel(label: 'Existing Investments', optional: true),
            const SizedBox(height: 8),
            TextFormField(
              controller: _existingController,
              maxLines: 3,
              decoration: const InputDecoration(
                hintText:
                    'e.g., SBI Blue Chip, HDFC Index Fund Nifty 50...',
                alignLabelWithHint: true,
              ),
            ),

            const SizedBox(height: 24),

            // Preferences
            _SectionLabel(label: 'Preferences', optional: true),
            const SizedBox(height: 8),
            TextFormField(
              controller: _preferencesController,
              maxLines: 3,
              decoration: const InputDecoration(
                hintText:
                    'e.g., I prefer index funds, no sectoral funds',
                alignLabelWithHint: true,
              ),
            ),

            const SizedBox(height: 32),

            // Submit button
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: _submit,
                child: const Text('Get Recommendations'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String label;
  final bool optional;

  const _SectionLabel({required this.label, this.optional = false});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimary,
          ),
        ),
        if (optional) ...[
          const SizedBox(width: 6),
          Text(
            '(optional)',
            style: GoogleFonts.inter(
              fontSize: 12,
              color: AppTheme.textSecondary,
            ),
          ),
        ],
      ],
    );
  }
}

class _ChoiceChipGroup extends StatelessWidget {
  final Map<String, String> options;
  final String selected;
  final ValueChanged<String> onSelected;

  const _ChoiceChipGroup({
    required this.options,
    required this.selected,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: options.entries.map((entry) {
        final isSelected = entry.key == selected;
        return ChoiceChip(
          label: Text(entry.value),
          selected: isSelected,
          onSelected: (_) => onSelected(entry.key),
          selectedColor: AppTheme.primaryColor,
          backgroundColor: Colors.white,
          labelStyle: GoogleFonts.inter(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: isSelected ? Colors.white : AppTheme.textPrimary,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
            side: BorderSide(
              color:
                  isSelected ? AppTheme.primaryColor : AppTheme.dividerColor,
            ),
          ),
          showCheckmark: false,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        );
      }).toList(),
    );
  }
}
