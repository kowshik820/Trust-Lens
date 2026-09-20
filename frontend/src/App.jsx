import { useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Analyzer from './components/Analyzer';
import LoadingState from './components/LoadingState';
import ResultCard from './components/ResultCard';
import SignalList from './components/SignalList';
import Recommendations from './components/Recommendations';
import ExplainSimple from './components/ExplainSimple';
import TrustReceipt from './components/TrustReceipt';
import SafetyActionEngine from './components/SafetyActionEngine';
import Footer from './components/Footer';

const stages = [
  'Reading content',
  'Extracting signals',
  'Checking URL characteristics',
  'Running AI analysis',
  'Building trust report',
];

export default function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async (payload, sourceText) => {
    setIsLoading(true);
    setError('');
    try {
      const result = await payload;
      setResult({
        ...result,
        source_text: sourceText,
        timestamp: result.timestamp || new Date().toISOString(),
      });
    } catch (err) {
      setError(err.message || 'Something went wrong while handling the result.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <Header />

      <main className="page">
        <Hero />

        <div className="content-grid">
          <Analyzer onAnalyze={handleAnalyze} isLoading={isLoading} />

          {isLoading && <LoadingState stages={stages} />}

          {error && (
            <div className="error-box full-width" role="alert">
              {error}
            </div>
          )}

          {result && (
            <>
              <ResultCard result={result} />
              <SignalList signals={result.signals || []} />
              <SafetyActionEngine result={result} />
              <Recommendations items={result.recommendations || []} result={result} />
              <ExplainSimple result={result} />
              <TrustReceipt result={result} />
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
