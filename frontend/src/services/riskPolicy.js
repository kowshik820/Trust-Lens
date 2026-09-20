export const RISK_THRESHOLDS = {
  LOW: { min: 0, max: 30, riskLevel: 'LOW', status: 'Low Risk', action: 'ALLOW_WITH_NOTICE', actionLabel: 'Allow with notice', title: 'Low Risk', recommendationTitle: 'Safe next steps', defaultRecommendation: 'Low detected risk — always verify the source before proceeding.' },
  MEDIUM: { min: 31, max: 70, riskLevel: 'MEDIUM', status: 'Caution', action: 'REQUIRE_CONFIRMATION', actionLabel: 'Require confirmation', title: '⚠ Caution — Potential Risk Detected', recommendationTitle: 'Recommended safety actions', defaultRecommendation: 'Do not open or download until the sender is independently verified.' },
  HIGH: { min: 71, max: 100, riskLevel: 'HIGH', status: 'High Risk', action: 'BLOCK', actionLabel: 'Block', title: '🚨 High Risk — Suspicious Content Detected', recommendationTitle: 'High-risk actions', defaultRecommendation: 'Do not open this link or interact with this content unless you have independently verified the source.' },
};

export function getRiskPolicy(score = 0) {
  const normalizedScore = Math.max(0, Math.min(100, Number(score) || 0));

  if (normalizedScore >= 71) {
    return { ...RISK_THRESHOLDS.HIGH, risk_level: 'HIGH', risk_score: normalizedScore };
  }

  if (normalizedScore >= 31) {
    return { ...RISK_THRESHOLDS.MEDIUM, risk_level: 'MEDIUM', risk_score: normalizedScore };
  }

  return { ...RISK_THRESHOLDS.LOW, risk_level: 'LOW', risk_score: normalizedScore };
}
