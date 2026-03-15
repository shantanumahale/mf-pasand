import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../models/fund.dart';
import '../theme.dart';
import '../widgets/metric_card.dart';

class FundDetailScreen extends StatelessWidget {
  final Fund fund;
  final bool showMatchScore;

  const FundDetailScreen({
    super.key,
    required this.fund,
    this.showMatchScore = false,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          fund.schemeName,
          style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 40),
        children: [
          // Hero section
          _HeroSection(fund: fund, showMatchScore: showMatchScore),
          const SizedBox(height: 24),

          // Returns section
          _SectionTitle(title: 'Returns'),
          const SizedBox(height: 12),
          _ReturnsGrid(fund: fund),
          const SizedBox(height: 24),

          // Returns chart
          if (_hasReturnsData(fund)) ...[
            _SectionTitle(title: 'Returns Comparison'),
            const SizedBox(height: 12),
            _ReturnsChart(fund: fund),
            const SizedBox(height: 24),
          ],

          // Fund Details section
          _SectionTitle(title: 'Fund Details'),
          const SizedBox(height: 12),
          _DetailsGrid(fund: fund),
          const SizedBox(height: 24),

          // Risk Metrics
          if (fund.volatility1y != null || fund.maxDrawdown1y != null) ...[
            _SectionTitle(title: 'Risk Metrics'),
            const SizedBox(height: 12),
            _RiskGrid(fund: fund),
            const SizedBox(height: 24),
          ],

          // Fund Manager
          if (fund.fundManager != null) ...[
            _SectionTitle(title: 'Fund Manager'),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.dividerColor),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withValues(alpha: 0.1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.person_rounded,
                      size: 20,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      fund.fundManager!,
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
          ],

          // Natural text description
          if (fund.naturalText != null &&
              fund.naturalText!.isNotEmpty) ...[
            _SectionTitle(title: 'About This Fund'),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.dividerColor),
              ),
              child: Text(
                fund.naturalText!,
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: AppTheme.textPrimary,
                  height: 1.6,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  bool _hasReturnsData(Fund fund) {
    return fund.returns1y != null ||
        fund.returns3y != null ||
        fund.returns5y != null;
  }
}

class _HeroSection extends StatelessWidget {
  final Fund fund;
  final bool showMatchScore;

  const _HeroSection({required this.fund, required this.showMatchScore});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.dividerColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            fund.schemeName,
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: AppTheme.textPrimary,
              height: 1.3,
            ),
          ),
          if (fund.fundHouse != null) ...[
            const SizedBox(height: 6),
            Text(
              fund.fundHouse!,
              style: GoogleFonts.inter(
                fontSize: 14,
                color: AppTheme.textSecondary,
              ),
            ),
          ],
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              if (fund.category != null)
                Chip(
                  label: Text(fund.category!),
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  visualDensity: VisualDensity.compact,
                ),
              if (fund.fundType != null)
                Chip(
                  label: Text(fund.fundType!),
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  visualDensity: VisualDensity.compact,
                ),
              if (showMatchScore && fund.similarityScore != null)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppTheme.secondaryColor.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.verified_rounded,
                        size: 16,
                        color: AppTheme.secondaryColor,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${(fund.similarityScore! * 100).round()}% Match',
                        style: GoogleFonts.inter(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.secondaryColor,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String title;

  const _SectionTitle({required this.title});

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: AppTheme.textPrimary,
      ),
    );
  }
}

class _ReturnsGrid extends StatelessWidget {
  final Fund fund;

  const _ReturnsGrid({required this.fund});

  Color _returnColor(double? value) {
    if (value == null) return AppTheme.textSecondary;
    return value >= 0 ? AppTheme.positiveReturn : AppTheme.negativeReturn;
  }

  String _returnString(double? value) {
    if (value == null) return 'N/A';
    return '${value >= 0 ? '+' : ''}${value.toStringAsFixed(1)}%';
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: MetricCard(
            label: '1Y RETURNS',
            value: _returnString(fund.returns1y),
            valueColor: _returnColor(fund.returns1y),
            compact: true,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: MetricCard(
            label: '3Y RETURNS',
            value: _returnString(fund.returns3y),
            valueColor: _returnColor(fund.returns3y),
            compact: true,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: MetricCard(
            label: '5Y RETURNS',
            value: _returnString(fund.returns5y),
            valueColor: _returnColor(fund.returns5y),
            compact: true,
          ),
        ),
      ],
    );
  }
}

class _ReturnsChart extends StatelessWidget {
  final Fund fund;

  const _ReturnsChart({required this.fund});

  @override
  Widget build(BuildContext context) {
    final entries = <_ChartEntry>[];
    if (fund.returns1y != null) {
      entries.add(_ChartEntry('1Y', fund.returns1y!));
    }
    if (fund.returns3y != null) {
      entries.add(_ChartEntry('3Y', fund.returns3y!));
    }
    if (fund.returns5y != null) {
      entries.add(_ChartEntry('5Y', fund.returns5y!));
    }

    if (entries.isEmpty) return const SizedBox.shrink();

    return Container(
      height: 200,
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.dividerColor),
      ),
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          maxY: entries
                  .map((e) => e.value.abs())
                  .reduce((a, b) => a > b ? a : b) *
              1.3,
          minY: entries.any((e) => e.value < 0)
              ? entries
                      .map((e) => e.value)
                      .reduce((a, b) => a < b ? a : b) *
                  1.3
              : 0,
          barTouchData: BarTouchData(
            touchTooltipData: BarTouchTooltipData(
              tooltipMargin: 8,
              getTooltipItem: (group, groupIndex, rod, rodIndex) {
                return BarTooltipItem(
                  '${entries[group.x].label}\n${entries[group.x].value.toStringAsFixed(1)}%',
                  GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                );
              },
            ),
          ),
          titlesData: FlTitlesData(
            show: true,
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  final idx = value.toInt();
                  if (idx < 0 || idx >= entries.length) {
                    return const SizedBox.shrink();
                  }
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      entries[idx].label,
                      style: GoogleFonts.inter(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color: AppTheme.textSecondary,
                      ),
                    ),
                  );
                },
                reservedSize: 30,
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return Text(
                    '${value.toInt()}%',
                    style: GoogleFonts.inter(
                      fontSize: 10,
                      color: AppTheme.textSecondary,
                    ),
                  );
                },
              ),
            ),
            topTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: _calcInterval(entries),
            getDrawingHorizontalLine: (value) => FlLine(
              color: AppTheme.dividerColor,
              strokeWidth: 1,
              dashArray: [5, 5],
            ),
          ),
          barGroups: entries.asMap().entries.map((entry) {
            final isPositive = entry.value.value >= 0;
            return BarChartGroupData(
              x: entry.key,
              barRods: [
                BarChartRodData(
                  toY: entry.value.value,
                  color: isPositive
                      ? AppTheme.primaryColor
                      : AppTheme.negativeReturn,
                  width: 32,
                  borderRadius: BorderRadius.vertical(
                    top: isPositive
                        ? const Radius.circular(6)
                        : Radius.zero,
                    bottom: isPositive
                        ? Radius.zero
                        : const Radius.circular(6),
                  ),
                ),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }

  double _calcInterval(List<_ChartEntry> entries) {
    final maxVal =
        entries.map((e) => e.value.abs()).reduce((a, b) => a > b ? a : b);
    if (maxVal > 50) return 20;
    if (maxVal > 20) return 10;
    if (maxVal > 10) return 5;
    return 2;
  }
}

class _ChartEntry {
  final String label;
  final double value;
  _ChartEntry(this.label, this.value);
}

class _DetailsGrid extends StatelessWidget {
  final Fund fund;

  const _DetailsGrid({required this.fund});

  String _formatAum(double? aum) {
    if (aum == null) return 'N/A';
    if (aum >= 10000) return '\u20B9${(aum / 1000).toStringAsFixed(0)}K Cr';
    return '\u20B9${aum.toStringAsFixed(0)} Cr';
  }

  String _formatAmount(double? amount) {
    if (amount == null) return 'N/A';
    if (amount >= 100000) return '\u20B9${(amount / 100000).toStringAsFixed(1)}L';
    if (amount >= 1000) return '\u20B9${(amount / 1000).toStringAsFixed(0)}K';
    return '\u20B9${amount.toStringAsFixed(0)}';
  }

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: [
        SizedBox(
          width: (MediaQuery.of(context).size.width - 50) / 2,
          child: MetricCard(
            label: 'EXPENSE RATIO',
            value: fund.expenseRatio != null
                ? '${fund.expenseRatio!.toStringAsFixed(2)}%'
                : 'N/A',
            compact: true,
            icon: Icons.percent,
          ),
        ),
        SizedBox(
          width: (MediaQuery.of(context).size.width - 50) / 2,
          child: MetricCard(
            label: 'AUM',
            value: _formatAum(fund.aumCr),
            compact: true,
            icon: Icons.account_balance,
          ),
        ),
        SizedBox(
          width: (MediaQuery.of(context).size.width - 50) / 2,
          child: MetricCard(
            label: 'CRISIL RATING',
            value: fund.crisilRating ?? 'N/A',
            compact: true,
            icon: Icons.star_outline,
          ),
        ),
        SizedBox(
          width: (MediaQuery.of(context).size.width - 50) / 2,
          child: MetricCard(
            label: 'MIN SIP',
            value: _formatAmount(fund.minSip),
            compact: true,
            icon: Icons.calendar_month,
          ),
        ),
        SizedBox(
          width: (MediaQuery.of(context).size.width - 50) / 2,
          child: MetricCard(
            label: 'MIN LUMPSUM',
            value: _formatAmount(fund.minLumpsum),
            compact: true,
            icon: Icons.payments_outlined,
          ),
        ),
      ],
    );
  }
}

class _RiskGrid extends StatelessWidget {
  final Fund fund;

  const _RiskGrid({required this.fund});

  @override
  Widget build(BuildContext context) {
    final halfWidth = (MediaQuery.of(context).size.width - 50) / 2;
    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: [
        if (fund.volatility1y != null)
          SizedBox(
            width: halfWidth,
            child: MetricCard(
              label: 'VOLATILITY (1Y)',
              value: '${fund.volatility1y!.toStringAsFixed(1)}%',
              compact: true,
              icon: Icons.show_chart,
              valueColor: fund.volatility1y! > 20
                  ? AppTheme.negativeReturn
                  : AppTheme.textPrimary,
            ),
          ),
        if (fund.maxDrawdown1y != null)
          SizedBox(
            width: halfWidth,
            child: MetricCard(
              label: 'MAX DRAWDOWN (1Y)',
              value: '${fund.maxDrawdown1y!.toStringAsFixed(1)}%',
              compact: true,
              icon: Icons.trending_down,
              valueColor: AppTheme.negativeReturn,
            ),
          ),
      ],
    );
  }
}
