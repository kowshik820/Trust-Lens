export default function InputTabs({ activeTab, onChange }) {
  const tabs = ['MESSAGE', 'URL', 'EMAIL', 'JOB OFFER'];

  return (
    <div className="input-tabs" role="tablist" aria-label="Input type selector">
      {tabs.map((tab) => (
        <button
          key={tab}
          type="button"
          role="tab"
          aria-selected={activeTab === tab}
          className={activeTab === tab ? 'tab active' : 'tab'}
          onClick={() => onChange(tab)}
        >
          {tab}
        </button>
      ))}
    </div>
  );
}
