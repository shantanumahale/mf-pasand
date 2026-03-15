import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../models/fund.dart';
import '../theme.dart';

class FundCard extends StatelessWidget {
  final Fund fund;
  final VoidCallback onTap;

  const FundCard({
    super.key,
    required this.fund,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.dividerColor),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Fund name and match score
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        fund.schemeName,
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.textPrimary,
                          height: 1.3,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (fund.fundHouse != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          fund.fundHouse!,
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            color: AppTheme.textSecondary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ],
                  ),
                ),
                if (fund.similarityScore != null) ...[
                  const SizedBox(width: 12),
                  _MatchBadge(score: fund.similarityScore!),
                ],
              ],
            ),

            const SizedBox(height: 12),

            // Category chip
            if (fund.category != null)
              Wrap(
                spacing: 8,
                children: [
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppTheme.chipBackground,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      fund.category!,
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                        color: AppTheme.primaryColor,
                      ),
                    ),
                  ),
                  if (fund.crisilRating != null)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFF8E1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        fund.crisilRating!,
                        style: GoogleFonts.inter(
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                          color: const Color(0xFFFF8F00),
                        ),
                      ),
                    ),
                ],
              ),

            const SizedBox(height: 12),

            // Metrics row
            Row(
              children: [
                if (fund.returns3y != null)
                  _MetricChip(
                    label: '3Y',
                    value: '${fund.returns3y!.toStringAsFixed(1)}%',
                    color: fund.returns3y! >= 0
                        ? AppTheme.positiveReturn
                        : AppTheme.negativeReturn,
                  ),
                if (fund.returns3y != null) const SizedBox(width: 16),
                if (fund.expenseRatio != null)
                  _MetricChip(
                    label: 'Exp.',
                    value: '${fund.expenseRatio!.toStringAsFixed(2)}%',
                    color: AppTheme.textSecondary,
                  ),
                const Spacer(),
                Icon(
                  Icons.chevron_right_rounded,
                  size: 20,
                  color: AppTheme.textSecondary.withValues(alpha: 0.5),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _MatchBadge extends StatelessWidget {
  final double score;

  const _MatchBadge({required this.score});

  @override
  Widget build(BuildContext context) {
    final percentage = (score * 100).round();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: AppTheme.primaryColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              value: score,
              strokeWidth: 2.5,
              backgroundColor: AppTheme.primaryColor.withValues(alpha: 0.2),
              valueColor:
                  const AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
            ),
          ),
          const SizedBox(width: 6),
          Text(
            '$percentage%',
            style: GoogleFonts.inter(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: AppTheme.primaryColor,
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _MetricChip({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          '$label ',
          style: GoogleFonts.inter(
            fontSize: 12,
            color: AppTheme.textSecondary,
          ),
        ),
        Text(
          value,
          style: GoogleFonts.inter(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: color,
          ),
        ),
      ],
    );
  }
}
