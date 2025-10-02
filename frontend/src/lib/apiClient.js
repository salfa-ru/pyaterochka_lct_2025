const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

export async function sendChatMessage({ message, history = [] }) {
  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  if (!res.ok) throw new Error(`Chat HTTP ${res.status}`);
  return res.json();
}

/** NER: POST /api/predict { input } -> SpanOut[] */
export async function predictEntities(input) {
  const res = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input }),
  });
  if (!res.ok) throw new Error(`NER HTTP ${res.status}`);
  return res.json();
}
