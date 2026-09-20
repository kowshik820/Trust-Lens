import { ArrowRight, ShieldAlert, Sparkles } from 'lucide-react';

export default function Hero() {
  const scrollToAnalyzer = () => {
    document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <section className="hero">
      <div className="hero-copy">
        <div className="eyebrow">
          <Sparkles size={14} />
          AI-assisted digital trust monitoring
        </div>
        <h1>Can you trust this?</h1>
        <p>
          Detect scam patterns in URLs, emails, messages, and fake job offers before they lead to fraud.
        </p>
        <div className="hero-actions">
          <button type="button" className="primary-btn" onClick={scrollToAnalyzer}>
            Analyze Now <ArrowRight size={16} />
          </button>
        </div>

        <div className="hero-stats">
          <div>
            <strong>360°</strong>
            <span>content scan</span>
          </div>
          <div>
            <strong>AI</strong>
            <span>risk engine</span>
          </div>
          <div>
            <strong>1-click</strong>
            <span>safety action</span>
          </div>
        </div>
      </div>

      <div className="hero-panel glass-card" aria-label="TrustLens overview">
        <div className="panel-header">
          <ShieldAlert size={18} />
          <span>live assessment</span>
        </div>

        <div className="mini-score">
          <strong>HIGH</strong>
          <span>risk level</span>
        </div>

        <div className="mini-meter">
          <div className="meter-fill high" style={{ width: '72%' }} />
        </div>

        <ul>
          <li>Urgency patterns</li>
          <li>URL risk review</li>
          <li>Credential attack cues</li>
        </ul>
      </div>
    </section>
  );
}
