export default function RiskMeter({ score = 0, level = 'LOW' }) {
  const safeScore = Math.min(100, Math.max(0, Number(score) || 0));

  return (
    <div className="meter-wrap">
      <div className="meter-labels">
        <span>Low</span>
        <span aria-label={`Risk score ${safeScore} out of 100`}>{safeScore}/100</span>
        <span>High</span>
      </div>
      <div className="risk-meter">
        <div
          className={`meter-fill ${String(level).toLowerCase()}`}
          style={{ '--meter-score': `${safeScore}%` }}
          role="progressbar"
          aria-valuemin="0"
          aria-valuemax="100"
          aria-valuenow={safeScore}
          aria-label="TrustLens risk score"
        />
      </div>
    </div>
  );
}
