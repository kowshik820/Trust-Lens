import { CheckCircle2, ShieldAlert, ShieldCheck } from 'lucide-react';
import { getRiskPolicy } from '../services/riskPolicy';

export default function Recommendations({ items = [], result }) {
  const riskPolicy = result ? getRiskPolicy(result.risk_score ?? 0) : null;
  const recommendationItems = items.length ? items : [riskPolicy?.defaultRecommendation || 'Verify the sender independently before acting.'];

  return (
    <div className="recommendations glass-card">
      <h3>{riskPolicy ? riskPolicy.recommendationTitle : 'Safe next steps'}</h3>
      <ul>
        {recommendationItems.map((item, index) => (
          <li key={`${item}-${index}`}>
            {riskPolicy?.risk_level === 'HIGH' ? <ShieldAlert size={16} /> : <CheckCircle2 size={16} />}
            <span>{item}</span>
          </li>
        ))}
      </ul>
      {riskPolicy?.risk_level === 'LOW' && (
        <div className="low-risk-note">
          <ShieldCheck size={14} />
          <span>Low detected risk — always verify the source before proceeding.</span>
        </div>
      )}
    </div>
  );
}
