import React, { useState, useEffect } from 'react';
import { login, logout, isAuthenticated, uploadCSV, getHistory, getSummary, downloadReportPdf } from './api';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import './App.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function LoginForm({ onSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(username, password);
      onSuccess();
    } catch {
      setError('Invalid username or password');
    }
  };

  return (
    <div className="auth-card">
      <h1>Chemical Equipment Parameter Visualizer</h1>
      <p className="subtitle">Sign in to continue</p>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          autoComplete="username"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="current-password"
        />
        {error && <p className="error">{error}</p>}
        <button type="submit">Sign In</button>
      </form>
    </div>
  );
}

function AppContent() {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [selectedHistoryId, setSelectedHistoryId] = useState(null);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const loadHistory = async () => {
    setLoadingHistory(true);
    try {
      const list = await getHistory();
      setHistory(list);
      if (list.length && !selectedHistoryId) setSelectedHistoryId(list[0].id);
    } catch {
      setHistory([]);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    if (!selectedHistoryId) return;
    let cancelled = false;
    getSummary(selectedHistoryId).then((s) => {
      if (!cancelled) setData({ summary: s.summary, records: [], fromHistory: true });
    }).catch(() => {});
    return () => { cancelled = true; };
  }, [selectedHistoryId]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadError('');
    setUploading(true);
    try {
      const result = await uploadCSV(file, file.name);
      setData({ summary: result.summary, records: result.records || [], fromHistory: false, dataset_id: result.dataset_id });
      loadHistory();
    } catch (err) {
      setUploadError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDownloadPdf = async () => {
    const id = data?.dataset_id || selectedHistoryId;
    if (!id) return;
    try {
      await downloadReportPdf(id);
    } catch {
      alert('Failed to generate PDF');
    }
  };

  const summary = data?.summary;
  const records = data?.records;
  const typeDist = summary?.equipment_type_distribution || {};
  const averages = summary?.averages || {};

  const doughnutData = {
    labels: Object.keys(typeDist),
    datasets: [{
      data: Object.values(typeDist),
      backgroundColor: COLORS.slice(0, Object.keys(typeDist).length),
      borderWidth: 1,
    }],
  };

  const barData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [{
      label: 'Average',
      data: [averages.Flowrate, averages.Pressure, averages.Temperature],
      backgroundColor: COLORS[0],
    }],
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Chemical Equipment Parameter Visualizer</h1>
        <div className="header-actions">
          <label className="btn btn-primary">
            Upload CSV
            <input type="file" accept=".csv" onChange={handleFileUpload} disabled={uploading} hidden />
          </label>
          <button type="button" className="btn btn-secondary" onClick={handleDownloadPdf} disabled={!summary}>
            Generate PDF Report
          </button>
          <button type="button" className="btn btn-outline" onClick={() => { logout(); window.location.reload(); }}>
            Sign Out
          </button>
        </div>
      </header>

      {uploadError && <div className="banner error">{uploadError}</div>}

      <section className="history-section">
        <h2>History (last 5 datasets)</h2>
        {loadingHistory ? (
          <p>Loading...</p>
        ) : history.length === 0 ? (
          <p>No uploads yet. Upload a CSV to get started.</p>
        ) : (
          <div className="history-tabs">
            {history.map((h) => (
              <button
                key={h.id}
                type="button"
                className={`tab ${selectedHistoryId === h.id ? 'active' : ''}`}
                onClick={() => setSelectedHistoryId(h.id)}
              >
                {h.name} ({h.row_count} rows)
              </button>
            ))}
          </div>
        )}
      </section>

      {summary && (
        <>
          <section className="summary-cards">
            <div className="card">
              <span className="card-label">Total Count</span>
              <span className="card-value">{summary.total_count}</span>
            </div>
            <div className="card">
              <span className="card-label">Avg Flowrate</span>
              <span className="card-value">{summary.averages?.Flowrate ?? '-'}</span>
            </div>
            <div className="card">
              <span className="card-label">Avg Pressure</span>
              <span className="card-value">{summary.averages?.Pressure ?? '-'}</span>
            </div>
            <div className="card">
              <span className="card-label">Avg Temperature</span>
              <span className="card-value">{summary.averages?.Temperature ?? '-'}</span>
            </div>
          </section>

          <section className="charts">
            <div className="chart-box">
              <h3>Equipment Type Distribution</h3>
              <div className="chart-container">
                <Doughnut data={doughnutData} options={{ responsive: true, maintainAspectRatio: false }} />
              </div>
            </div>
            <div className="chart-box">
              <h3>Parameter Averages</h3>
              <div className="chart-container">
                <Bar
                  data={barData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { y: { beginAtZero: true } },
                  }}
                />
              </div>
            </div>
          </section>
        </>
      )}

      {records && records.length > 0 && (
        <section className="table-section">
          <h2>Data Table</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Equipment Name</th>
                  <th>Type</th>
                  <th>Flowrate</th>
                  <th>Pressure</th>
                  <th>Temperature</th>
                </tr>
              </thead>
              <tbody>
                {records.map((row, i) => (
                  <tr key={i}>
                    <td>{row['Equipment Name']}</td>
                    <td>{row.Type}</td>
                    <td>{row.Flowrate}</td>
                    <td>{row.Pressure}</td>
                    <td>{row.Temperature}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {summary && (!records || records.length === 0) && (
        <section className="table-section">
          <p>Summary only (no row data). Upload a new CSV to see the full table.</p>
        </section>
      )}
    </div>
  );
}

function App() {
  const [auth, setAuth] = useState(isAuthenticated());

  if (!auth) {
    return (
      <div className="auth-page">
        <LoginForm onSuccess={() => setAuth(true)} />
      </div>
    );
  }

  return <AppContent />;
}

export default App;
