import { useMemo, useState } from 'react';
import { AlertTriangle, ArrowLeft, CheckCircle2, ExternalLink, Lock, ShieldAlert } from 'lucide-react';
import { getRiskPolicy } from '../services/riskPolicy';

export default function SafetyActionEngine({ result }) {
  const [showModal, setShowModal] = useState(false);
  const [isVerified, setIsVerified] = useState(false);

  if (!result) {
    return null;
  }

  const policy = getRiskPolicy(result.risk_score ?? 0);
  const urlExamples = useMemo(
    () => (Array.isArray(result?.rule_analysis?.url_examples) ? result.rule_analysis.url_examples : []),
    [result]
  );

  const actionText = policy.risk_level === 'HIGH'
    ? 'Blocked — View Safety Report'
    : policy.risk_level === 'MEDIUM'
      ? 'Continue to link'
      : 'Continue normally';

  const isBlocking = policy.risk_level === 'HIGH';

  const handlePrimaryAction = () => {
    if (policy.risk_level === 'LOW') {
      return;
    }

    setShowModal(true);
  };

  const handleConfirmedContinue = () => {
    setIsVerified(true);
    setShowModal(false);

    if (urlExamples.length > 0) {
      const targetUrl = urlExamples[0];
      if (typeof window !== 'undefined') {
        window.open(targetUrl, '_blank', 'noopener,noreferrer');
      }
    }
  };

  const handleGoBack = () => {
    setShowModal(false);
    setIsVerified(false);
  };

  return (
    <div className="safety-action-engine glass-card">
      <div className="section-head">
        <h3>Risk-Based Safety Action Engine</h3>
      </div>

      <div className={`safety-status ${policy.risk_level.toLowerCase()}`}>
        <span>{policy.status}</span>
        <strong>{policy.action}</strong>
      </div>

      <p className="safety-message">
        {policy.message}
      </p>

      {policy.risk_level === 'LOW' && (
        <div className="low-risk-callout">
          <CheckCircle2 size={16} />
          <span>Low detected risk — always verify the source before proceeding.</span>
        </div>
      )}

      {policy.risk_level === 'MEDIUM' && (
        <div className="medium-risk-callout">
          <AlertTriangle size={16} />
          <span>Potentially suspicious content detected. Our analyzer found several warning signs.</span>
        </div>
      )}

      {policy.risk_level === 'HIGH' && (
        <div className="high-risk-callout">
          <ShieldAlert size={16} />
          <span>Do not open this link or interact with this content unless you have independently verified the source.</span>
        </div>
      )}

      {urlExamples.length > 0 && (
        <div className="link-action-row">
          <button
            type="button"
            className={isBlocking ? 'primary-btn blocked-btn' : 'secondary-btn'}
            onClick={handlePrimaryAction}
            aria-label={isBlocking ? 'Open blocked link flow' : 'Open the detected URL'}
          >
            {isBlocking ? <Lock size={16} /> : <ExternalLink size={16} />}
            {actionText}
          </button>
        </div>
      )}

      {showModal && (
        <div className="action-modal-backdrop" role="dialog" aria-modal="true" aria-label="Risk confirmation dialogue">
          <div className="action-modal">
            <div className="action-modal-header">
              <ShieldAlert size={18} />
              <h4>{isBlocking ? 'Access blocked because this URL has been classified as high risk.' : 'Potentially suspicious content detected.'}</h4>
            </div>

            <p>
              {isBlocking
                ? 'Do not open this link unless you have independently verified the source.'
                : 'Our analyzer found several warning signs. Do you want to continue?'}
            </p>

            <div className="modal-actions">
              <button type="button" className="secondary-btn" onClick={handleGoBack}>
                <ArrowLeft size={16} />
                Go Back
              </button>

              <button type="button" className="primary-btn" onClick={handleConfirmedContinue}>
                {isBlocking ? 'I\'ve independently verified this source — Continue' : 'Continue Anyway'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
