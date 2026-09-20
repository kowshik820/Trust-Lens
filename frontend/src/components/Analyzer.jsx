import { useMemo, useState } from 'react';
import Tesseract from 'tesseract.js';
import { AlertCircle, ArrowRight, ImageUp, Trash2 } from 'lucide-react';
import InputTabs from './InputTabs';
import { analyzeContent } from '../services/api';

const EXAMPLES = [
  {
    label: 'Demo: Fake job offer',
    value:
      'URGENT! We are hiring immediately. Pay a training fee of $250 and we will send the onboarding details after your payment is received.',
  },
  {
    label: 'Demo: Suspicious banking message',
    value:
      'Your account has been suspended. Verify your account now and send your OTP immediately to restore access.https://bit.ly/account-verify',
  },
  {
    label: 'Demo: Investment scam',
    value:
      'Guaranteed 3x returns in 7 days. Invest now with a small upfront payment and double your money safely.',
  },
  {
    label: 'Demo: Safe legitimate-looking message',
    value:
      'Hi team, the project review meeting is scheduled for tomorrow at 3 PM. Please share your updates before the call.',
  },
];

export default function Analyzer({ onAnalyze, isLoading }) {
  const [activeTab, setActiveTab] = useState('MESSAGE');
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [isUploadingScreenshot, setIsUploadingScreenshot] = useState(false);

  const remainingChars = useMemo(() => 10000 - text.length, [text]);

  const handleAnalyze = async () => {
    const trimmed = text.trim();
    if (!trimmed) {
      setError('Please enter content to analyze.');
      return;
    }

    setError('');
    try {
      const result = await analyzeContent(trimmed);
      onAnalyze(result, trimmed);
    } catch (err) {
      setError(err.message || 'The analysis could not be completed.');
    }
  };

  const handleLoadExample = (exampleText) => {
    setText(exampleText);
    setError('');
  };

  const handleScreenshotUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    if (!file.type.startsWith('image/')) {
      setError('Please upload a valid image screenshot.');
      event.target.value = '';
      return;
    }

    setError('');
    setIsUploadingScreenshot(true);

    try {
      const result = await Tesseract.recognize(file, 'eng', {
        logger: (message) => {
          if (message.status === 'recognizing text') {
            setError(`Reading screenshot... ${Math.round(message.progress * 100)}%`);
          }
        },
      });

      const extractedText = (result?.data?.text || '').replace(/\s+/g, ' ').trim();
      if (!extractedText) {
        throw new Error('No readable text was detected in the screenshot.');
      }

      setText(extractedText);
      const analysis = await analyzeContent(extractedText);
      onAnalyze(analysis, extractedText);
    } catch (err) {
      setError(err.message || 'The screenshot could not be analyzed.');
    } finally {
      setIsUploadingScreenshot(false);
      event.target.value = '';
    }
  };

  return (
    <section id="analyzer" className="analyzer-panel glass-card">
      <div className="panel-topline">
        <h2>Analyze suspicious content</h2>
        <span className="tag">AI-assisted risk assessment</span>
      </div>

      <InputTabs activeTab={activeTab} onChange={setActiveTab} />

      <label className="sr-only" htmlFor="message-input">
        Paste a suspicious message, email, job offer or URL
      </label>
      <textarea
        id="message-input"
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="Paste a suspicious message, email, job offer or URL..."
        maxLength={10000}
        aria-label="Content to analyze"
      />

      <div className="field-row">
        <span className="char-counter">{remainingChars} chars left</span>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <label className="primary-btn" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', cursor: 'pointer', margin: 0 }}>
            <input type="file" accept="image/*" capture="environment" onChange={handleScreenshotUpload} hidden />
            <ImageUp size={14} />
            {isUploadingScreenshot ? 'Reading...' : 'Upload screenshot'}
          </label>
          <button type="button" className="clear-btn" onClick={() => setText('')}>
            <Trash2 size={14} />
            Clear
          </button>
        </div>
      </div>

      {error && (
        <div className="error-box" role="alert">
          <AlertCircle size={14} />
          <span>{error}</span>
        </div>
      )}

      <div className="example-list" aria-label="Demo examples">
        {EXAMPLES.map((example) => (
          <button key={example.label} type="button" className="example-btn" onClick={() => handleLoadExample(example.value)}>
            {example.label}
          </button>
        ))}
      </div>

      <button type="button" className="primary-btn submit-btn" onClick={handleAnalyze} disabled={isLoading}>
        {isLoading ? 'Analyzing...' : 'Analyze Now'}
        <ArrowRight size={16} />
      </button>
    </section>
  );
}
