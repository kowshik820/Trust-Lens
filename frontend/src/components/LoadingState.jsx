export default function LoadingState({ stages = [] }) {
  return (
    <div className="loading-state glass-card" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <h3>Analyzing content</h3>
      <ul>
        {stages.map((stage, index) => (
          <li key={index}>{stage}</li>
        ))}
      </ul>
    </div>
  );
}
