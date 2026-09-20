import { AlertCircle, ShieldAlert } from 'lucide-react';

const severityColors = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
};

export default function SignalList({ signals = [] }) {
  if (!signals.length) {
    return (
      <div className="empty-state glass-card">
        <ShieldAlert size={18} />
        <p>No risk signals were detected in the analyzed content.</p>
      </div>
    );
  }

  return (
    <div className="signal-list">
      {signals.map((signal, index) => (
        <div key={`${signal.type}-${index}`} className="signal-item glass-card">
          <div className="signal-icon">
            <AlertCircle size={16} />
          </div>
          <div className="signal-content">
            <div className="signal-head">
              <strong>{signal.type}</strong>
              <span className={`severity ${severityColors[signal.severity] || 'medium'}`}>{signal.severity}</span>
            </div>
            <p>{signal.explanation}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
