import { useState } from 'react';
import { getRiskPolicy } from '../services/riskPolicy';

export default function ExplainSimple({ result }) {
  const [expanded, setExpanded] = useState(false);

  if (!result) return null;

  const signals = Array.isArray(result.signals) ? result.signals : [];
  const signalNames = signals.slice(0, 2).map((signal) => signal.type).join(' and ');
  const riskPolicy = getRiskPolicy(result.risk_score ?? 0);
  const simpleText = signals.length
    ? `TrustLens noticed ${signalNames}. In simple words, this message may be trying to make you act quickly or share something private before you check who sent it.`
    : 'TrustLens did not find clear warning signs. That does not prove the message is safe, so check the sender before you act.';

  return (
    <div className="explain-box glass-card">
      <div className="section-head">
        <h3>{riskPolicy.title}</h3>
        <button type="button" className="link-btn" onClick={() => setExpanded((value) => !value)}>
          {expanded ? 'Hide' : 'Explain Simply'}
        </button>
      </div>

      {expanded ? (
        <div>
          <p>
            <strong>Technical:</strong> {result.summary || 'No summary was returned by the analysis service.'}
          </p>
          <p>
            <strong>Simple:</strong> {simpleText}
          </p>
        </div>
      ) : (
        <p>{simpleText}</p>
      )}
    </div>
  );
}
