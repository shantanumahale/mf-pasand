class UserPersona {
  final int age;
  final double? annualIncome;
  final String investmentHorizon;
  final String riskAppetite;
  final String investmentGoal;
  final double? monthlySipBudget;
  final double? lumpsumAvailable;
  final String? existingInvestments;
  final String? preferences;

  UserPersona({
    required this.age,
    this.annualIncome,
    required this.investmentHorizon,
    required this.riskAppetite,
    required this.investmentGoal,
    this.monthlySipBudget,
    this.lumpsumAvailable,
    this.existingInvestments,
    this.preferences,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'age': age,
      'investment_horizon': investmentHorizon,
      'risk_appetite': riskAppetite,
      'investment_goal': investmentGoal,
    };
    if (annualIncome != null) map['annual_income'] = annualIncome;
    if (monthlySipBudget != null) map['monthly_sip_budget'] = monthlySipBudget;
    if (lumpsumAvailable != null) map['lumpsum_available'] = lumpsumAvailable;
    if (existingInvestments != null && existingInvestments!.isNotEmpty) {
      map['existing_investments'] = existingInvestments;
    }
    if (preferences != null && preferences!.isNotEmpty) {
      map['preferences'] = preferences;
    }
    return map;
  }
}
