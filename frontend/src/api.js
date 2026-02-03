const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function getAuthHeader() {
  const credentials = localStorage.getItem('equipment_auth');
  if (!credentials) return {};
  return { Authorization: `Basic ${credentials}` };
}

export async function login(username, password) {
  const credentials = btoa(`${username}:${password}`);
  const res = await fetch(`${API_BASE}/history/`, {
    headers: { Authorization: `Basic ${credentials}` },
  });
  if (!res.ok) throw new Error('Invalid credentials');
  localStorage.setItem('equipment_auth', credentials);
  return { ok: true };
}

export function logout() {
  localStorage.removeItem('equipment_auth');
}

export function isAuthenticated() {
  return !!localStorage.getItem('equipment_auth');
}

export async function uploadCSV(file, name) {
  const formData = new FormData();
  formData.append('file', file);
  if (name) formData.append('name', name);
  const res = await fetch(`${API_BASE}/upload/`, {
    method: 'POST',
    headers: getAuthHeader(),
    body: formData,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Upload failed');
  return data;
}

export async function getHistory() {
  const res = await fetch(`${API_BASE}/history/`, { headers: getAuthHeader() });
  if (!res.ok) throw new Error('Failed to load history');
  return res.json();
}

export async function getSummary(datasetId) {
  const res = await fetch(`${API_BASE}/summary/${datasetId}/`, { headers: getAuthHeader() });
  if (!res.ok) throw new Error('Failed to load summary');
  return res.json();
}

export async function downloadReportPdf(datasetId) {
  const res = await fetch(
    `${API_BASE}/report/${datasetId}/pdf/`,
    { headers: getAuthHeader() }
  );
  if (!res.ok) throw new Error('Failed to generate PDF');
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `equipment_report_${datasetId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}
