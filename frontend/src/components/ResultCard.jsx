import { AlertTriangle, Gauge, ShieldCheck } from 'lucide-react';
import RiskMeter from './RiskMeter';
import { getRiskPolicy } from '../services/riskPolicy';

export default function ResultCard({ result }) {
  if (!result) {
    return null;
  }

  const riskClass = String(result.risk_level || 'LOW').toLowerCase();
  const policy = getRiskPolicy(result.risk_score ?? 0);

  return (
    <section className="result-card glass-card">
      <div className="result-header">
        <div>
          <p className="section-kicker">TrustLens assessment</p>
          <h2>{policy.status}</h2>
        </div>
        <div className={`risk-pill ${riskClass}`}>
          {result.risk_level}
        </div>
      </div>

      <div className="score-row">
        <div className="score-box">
          <Gauge size={18} />
          <div>
            <span>Risk score</span>
            <strong>{result.risk_score ?? 0}/100</strong>
          </div>
        </div>

        <div className="score-box">
          <ShieldCheck size={18} />
          <div>
            <span>Action</span>
            <strong>{policy.actionLabel}</strong>
          </div>
        </div>
      </div>

      <RiskMeter score={result.risk_score} level={result.risk_level} />

      <div className="summary-box">
        <AlertTriangle size={16} />
        <p>{policy.message}</p>
      </div>
    </section>
  );
}
