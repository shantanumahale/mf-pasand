class Fund {
  final String schemeCode;
  final String schemeName;
  final String? isin;
  final String? fundHouse;
  final String? category;
  final String? fundType;
  final String? crisilRating;
  final double? expenseRatio;
  final double? aumCr;
  final double? returns1y;
  final double? returns3y;
  final double? returns5y;
  final double? volatility1y;
  final double? maxDrawdown1y;
  final double? minSip;
  final double? minLumpsum;
  final String? fundManager;
  final String? naturalText;
  final double? similarityScore;

  Fund({
    required this.schemeCode,
    required this.schemeName,
    this.isin,
    this.fundHouse,
    this.category,
    this.fundType,
    this.crisilRating,
    this.expenseRatio,
    this.aumCr,
    this.returns1y,
    this.returns3y,
    this.returns5y,
    this.volatility1y,
    this.maxDrawdown1y,
    this.minSip,
    this.minLumpsum,
    this.fundManager,
    this.naturalText,
    this.similarityScore,
  });

  factory Fund.fromJson(Map<String, dynamic> json) {
    return Fund(
      schemeCode: (json['scheme_code'] ?? json['schemeCode'] ?? '').toString(),
      schemeName: json['scheme_name'] ?? json['schemeName'] ?? 'Unknown Fund',
      isin: json['isin'] as String?,
      fundHouse: json['fund_house'] ?? json['fundHouse'] as String?,
      category: json['category'] as String?,
      fundType: json['fund_type'] ?? json['fundType'] as String?,
      crisilRating: json['crisil_rating'] ?? json['crisilRating'] as String?,
      expenseRatio: _toDouble(json['expense_ratio'] ?? json['expenseRatio']),
      aumCr: _toDouble(json['aum_cr'] ?? json['aumCr']),
      returns1y: _toDouble(json['returns_1y'] ?? json['returns1y']),
      returns3y: _toDouble(json['returns_3y'] ?? json['returns3y']),
      returns5y: _toDouble(json['returns_5y'] ?? json['returns5y']),
      volatility1y: _toDouble(json['volatility_1y'] ?? json['volatility1y']),
      maxDrawdown1y:
          _toDouble(json['max_drawdown_1y'] ?? json['maxDrawdown1y']),
      minSip: _toDouble(json['min_sip'] ?? json['minSip']),
      minLumpsum: _toDouble(json['min_lumpsum'] ?? json['minLumpsum']),
      fundManager: json['fund_manager'] ?? json['fundManager'] as String?,
      naturalText: json['natural_text'] ?? json['naturalText'] as String?,
      similarityScore:
          _toDouble(json['similarity_score'] ?? json['similarityScore']),
    );
  }

  static double? _toDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }
}
