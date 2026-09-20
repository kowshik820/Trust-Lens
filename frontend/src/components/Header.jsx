import { ShieldCheck, Menu } from 'lucide-react';

export default function Header() {
  return (
    <header className="topbar">
      <div className="brand-wrap">
        <div className="brand-icon">
          <ShieldCheck size={18} />
        </div>
        <div>
          <div className="brand-name">TRUSTLENS</div>
          <div className="brand-subtitle">Threat intelligence</div>
        </div>
      </div>

      <nav className="topnav" aria-label="Main navigation">
        <span>Assessment</span>
        <span>URL defense</span>
        <span>Controls</span>
      </nav>

      <button className="mobile-menu" aria-label="Open menu">
        <Menu size={18} />
      </button>
    </header>
  );
}
