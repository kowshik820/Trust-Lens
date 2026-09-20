const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'https://trust-lens-f1nt.onrender.com'
).replace(/\/$/, '');

export async function analyzeContent(text) {
  const trimmed = typeof text === 'string' ? text.trim() : '';

  if (!trimmed) {
    throw new Error('Please enter content to analyze.');
  }

  if (!API_BASE_URL) {
    throw new Error('The analysis service is not configured. Set VITE_API_BASE_URL in the deployment settings.');
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: trimmed }),
    });
  } catch {
    throw new Error('Unable to reach the analysis service. Check the deployed backend URL and CORS settings.');
  }

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
