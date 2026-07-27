const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options)
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.error?.message || data.error || 'The backend request failed.')
  }
  return data
}

export const api = {
  upload: (file) => {
    const form = new FormData()
    form.append('file', file)
    return request('/datasets/upload/', { method: 'POST', body: form })
  },
  startRun: (configuration) => request('/runs/start/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(configuration),
  }),
  status: (id) => request(`/runs/${id}/status/`),
  results: (id) => request(`/runs/${id}/results/`),
  artifacts: (id) => request(`/runs/${id}/artifacts/`),
  modelSchema: (id) => request(`/models/${id}/predict/`),
  predict: (id, features) => request(`/models/${id}/predict/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ features }),
  }),
}
