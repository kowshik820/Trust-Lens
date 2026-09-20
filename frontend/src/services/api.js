const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export async function analyzeContent(text) {
  const trimmed = typeof text === 'string' ? text.trim() : '';

  if (!trimmed) {
    throw new Error('Please enter content to analyze.');
  }

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: trimmed }),
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = data?.detail || 'The analysis request failed. Please try again.';
    throw new Error(message);
  }

  if (!data || typeof data !== 'object') {
    throw new Error('The backend returned an invalid response.');
  }

  return data;
}
