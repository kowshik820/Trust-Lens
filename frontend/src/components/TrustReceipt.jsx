import { useState } from 'react';
import { Check, Copy, Download } from 'lucide-react';

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function buildPlainReport(report) {
  const riskMeaning = report.risk_level === 'HIGH'
    ? 'High risk: do not click, reply, pay, or share private codes.'
    : report.risk_level === 'MEDIUM'
      ? 'Be careful: check the sender using an official contact before acting.'
      : 'No clear warning signs were found, but still check the sender before acting.';
  const signals = report.signals.length
    ? report.signals.map((signal) => `- ${signal.type}: ${signal.explanation}`).join('\n')
    : '- No clear warning signs were detected.';
  const recommendations = report.recommendations.length
    ? report.recommendations.map((item) => `- ${item}`).join('\n')
    : '- Verify the sender independently before acting.';

  return [
    'TRUSTLENS - SIMPLE SAFETY REPORT',
    '=================================',
    `Risk: ${report.risk_level} (${report.risk_score}/100)`,
    riskMeaning,
    '',
    'WHAT WAS CHECKED',
    report.source_text || 'The original message was not included in this report.',
    '',
    'WHY THIS MAY BE A SCAM',
    report.summary || 'The analyzer found warning signs that need checking.',
    signals,
    '',
    'WHAT TO DO NOW',
    recommendations,
    '',
    `Report ID: ${report.analysis_id}`,
    `Created: ${new Date(report.timestamp).toLocaleString()}`,
    '',
    'TrustLens is decision support, not proof of fraud.',
  ].join('\n');
}

function buildHtmlReport(report) {
  const riskClass = report.risk_level.toLowerCase();
  const riskMeaning = report.risk_level === 'HIGH'
    ? 'Do not click, reply, pay, or share private codes.'
    : report.risk_level === 'MEDIUM'
      ? 'Check the sender using an official contact before acting.'
      : 'No clear warning signs were found. Still check the sender before acting.';
  const signals = report.signals.length
    ? report.signals.map((signal) => `<li><strong>${escapeHtml(signal.type)}</strong><span>${escapeHtml(signal.explanation)}</span></li>`).join('')
    : '<li><strong>No clear warning signs found</strong><span>Stay careful and verify the sender.</span></li>';
  const recommendations = report.recommendations.length
    ? report.recommendations.map((item) => `<li>${escapeHtml(item)}</li>`).join('')
    : '<li>Verify the sender independently before acting.</li>';

  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TrustLens Simple Safety Report</title>
<style>
body{margin:0;background:#eef3f8;color:#142033;font:16px/1.55 Arial,sans-serif}.report{max-width:760px;margin:32px auto;background:#fff;border:1px solid #d6e0ea;border-radius:18px;overflow:hidden;box-shadow:0 12px 35px #17324d18}.top{padding:28px 30px;background:#10243b;color:#fff}.brand{font-size:13px;letter-spacing:3px;font-weight:700;color:#9ed0ff}.top h1{margin:20px 0 4px;font-size:30px}.top p{margin:0;color:#c9d8e8}.risk{margin:24px 30px 0;padding:22px;border-radius:14px;background:${riskClass === 'high' ? '#fff0f0' : riskClass === 'medium' ? '#fff8e7' : '#edfbf4'};border:2px solid ${riskClass === 'high' ? '#e36b6b' : riskClass === 'medium' ? '#e4b341' : '#52b788'}}.risk strong{display:block;font-size:28px;color:${riskClass === 'high' ? '#b42318' : riskClass === 'medium' ? '#8a5b00' : '#157347'}}.risk span{display:block;margin-top:6px}.section{padding:24px 30px;border-top:1px solid #e3eaf1}.section h2{font-size:19px;margin:0 0 12px}.message{padding:16px;background:#f5f8fb;border-left:4px solid #72a7d6;border-radius:8px;white-space:pre-wrap;word-break:break-word}.signals,.steps{padding:0;margin:0;list-style:none;display:grid;gap:12px}.signals li{padding:14px;background:#f7f9fb;border-radius:10px}.signals strong{display:block}.signals span{display:block;color:#526174;margin-top:4px}.steps li{padding-left:24px;position:relative}.steps li:before{content:'OK';position:absolute;left:0;color:#157347;font-size:11px;font-weight:bold}.meta{font-size:13px;color:#64748b}.footer{padding:20px 30px;background:#f5f8fb;color:#64748b;font-size:13px}@media(max-width:600px){.report{margin:0;border-radius:0}.top,.section,.footer{padding-left:20px;padding-right:20px}.risk{margin-left:20px;margin-right:20px}}
</style></head><body><main class="report"><header class="top"><div class="brand">TRUSTLENS</div><h1>Simple Safety Report</h1><p>Understand the message before you act.</p></header><section class="risk"><strong>${escapeHtml(report.risk_level)} RISK - ${escapeHtml(report.risk_score)}/100</strong><span>${escapeHtml(riskMeaning)}</span></section><section class="section"><h2>Message Checked</h2><div class="message">${escapeHtml(report.source_text || 'Original message not included.')}</div></section><section class="section"><h2>Why It May Be Unsafe</h2><p>${escapeHtml(report.summary || 'The analyzer found warning signs that need checking.')}</p><ul class="signals">${signals}</ul></section><section class="section"><h2>What To Do Now</h2><ul class="steps">${recommendations}</ul></section><footer class="footer"><div class="meta">Report ID: ${escapeHtml(report.analysis_id)}<br>Created: ${escapeHtml(new Date(report.timestamp).toLocaleString())}</div><p>TrustLens gives safety guidance. It does not prove that a message is fraudulent.</p></footer></main></body></html>`;
}

export default function TrustReceipt({ result }) {
  const [status, setStatus] = useState('');

  if (!result) return null;

  const timestamp = result.timestamp || new Date().toISOString();

  const report = {
    trustlens: 'TrustLens',
    message: 'Digital Trust Assessment',
    analysis_id: result.analysis_id || 'unknown',
    timestamp,
    risk_level: result.risk_level,
    risk_score: result.risk_score,
    source_text: result.source_text || '',
    summary: result.summary || '',
    signals: result.signals || [],
    recommendations: result.recommendations || [],
    rule_analysis: result.rule_analysis || {},
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(buildPlainReport(report));
      setStatus('Copied');
    } catch {
      setStatus('Copy unavailable');
    }
  };

  const handleDownload = () => {
    const blob = new Blob([buildHtmlReport(report)], { type: 'text/html' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'trustlens-simple-safety-report.html';
    link.click();
    URL.revokeObjectURL(link.href);
    setStatus('Downloaded');
  };

  return (
    <div className="receipt glass-card">
      <div className="section-head">
        <h3>Trust Receipt</h3>
      </div>

      <div className="receipt-grid">
        <div>
          <span>Analysis ID</span>
          <strong>{report.analysis_id}</strong>
        </div>
        <div>
          <span>Timestamp</span>
          <strong>{new Date(timestamp).toLocaleString()}</strong>
        </div>
        <div>
          <span>Risk level</span>
          <strong>{report.risk_level}</strong>
        </div>
        <div>
          <span>Risk score</span>
          <strong>{report.risk_score}</strong>
        </div>
      </div>

      <div className="receipt-actions">
        <button type="button" className="secondary-btn" onClick={handleCopy}>
          {status === 'Copied' ? <Check size={16} /> : <Copy size={16} />}
          {status === 'Copied' ? 'Copied' : 'Copy Report'}
        </button>
        <button type="button" className="secondary-btn" onClick={handleDownload}>
          <Download size={16} />
          Download Report
        </button>
        {status && <span className="receipt-status" role="status">{status}</span>}
      </div>
    </div>
  );
}
