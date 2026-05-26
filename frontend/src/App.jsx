import { useEffect, useState } from 'react';
import './index.css';

const SOURCE_OPTIONS = [
  { value: 'sap-fuel', label: 'SAP fuel/procurement export' },
  { value: 'utility-electricity', label: 'Utility electricity bill CSV' },
  { value: 'travel-corporate', label: 'Corporate travel export' },
];

// ✅ FIXED: must be string
const API_BASE = "https://breathe-backend-78xx.onrender.com";

function App() {
  const [tenant, setTenant] = useState('acme');
  const [sourceType, setSourceType] = useState('sap-fuel');
  const [file, setFile] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  const [statusFilter, setStatusFilter] = useState('pending_review');
  const [typeFilter, setTypeFilter] = useState('');
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    fetchRecords();
  }, []);

  // ✅ FETCH RECORDS (UPDATED)
  const fetchRecords = async () => {
    setLoading(true);
    try {
      let url = `${API_BASE}/api/records/?status=${statusFilter}`;

      if (typeFilter) {
        url += `&record_type=${typeFilter}`;
      }

      const response = await fetch(url);
      const data = await response.json();
      const recordList = Array.isArray(data) ? data : data.results || [];

      setRecords(recordList);
    } catch (error) {
      showToast('Failed to load records', 'error');
    } finally {
      setLoading(false);
    }
  };

  // ✅ UPLOAD
  const handleUpload = async (event) => {
    event.preventDefault();

    if (!file) {
      showToast('Please choose a file first', 'error');
      return;
    }

    const formData = new FormData();
    formData.append('tenant', tenant);
    formData.append('source_type', sourceType);
    formData.append('file', file);

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/imports/upload/`, {
        method: 'POST',
        body: formData,
      });

      const result = await res.json();

      if (!res.ok) {
        showToast(result.detail || 'Import failed', 'error');
      } else {
        showToast(`Imported ${result.imported} rows`, 'success');
        fetchRecords();
      }
    } catch (error) {
      showToast('Upload failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  // ✅ REJECT
  const rejectRecord = async (id) => {
    const reason = prompt("Enter rejection reason:");
    if (!reason) return;

    try {
      const res = await fetch(`${API_BASE}/api/records/${id}/reject/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      });

      if (res.ok) {
        showToast('Record rejected', 'success');
        fetchRecords();
      }
    } catch {
      showToast('Reject failed', 'error');
    }
  };

  // ✅ APPROVE
  const approveRecord = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/records/${id}/approve/`, {
        method: 'POST',
      });

      if (res.ok) {
        showToast('Record approved', 'success');
        fetchRecords();
      }
    } catch {
      showToast('Approve failed', 'error');
    }
  };

  // ✅ TOAST
  const showToast = (message, type = 'success') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  };

  return (
    <div className="shell">
      <header className="header">
        <h1>Breathe ESG import review</h1>
      </header>

      {/* Upload */}
      <section className="upload-panel">
        <h2>Import source data</h2>

        <form onSubmit={handleUpload}>
          <input value={tenant} onChange={(e) => setTenant(e.target.value)} />

          <select value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
            {SOURCE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>

          <input type="file" onChange={(e) => setFile(e.target.files?.[0])} />

          <button type="submit">Upload</button>
        </form>
      </section>

      {/* Filters */}
      <section className="review-panel">
        <div className="filters">
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="pending_review">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="">All</option>
          </select>

          <input
            placeholder="type filter"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          />

          <button onClick={fetchRecords}>Apply</button>
        </div>

        {/* Table */}
        {loading ? <p>Loading...</p> : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Scope</th>
                <th>Approve</th>
                <th>Reject</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {records.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.record_type}</td>
                  <td>{r.emission_scope}</td>

                  <td>
                    {r.status === 'pending_review'
                      ? <button onClick={() => approveRecord(r.id)}>Approve</button>
                      : '—'}
                  </td>

                  <td>
                    {r.status === 'pending_review'
                      ? <button onClick={() => rejectRecord(r.id)}>Reject</button>
                      : '—'}
                  </td>

                  <td>{r.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* Toast UI */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.type}`}>
            {t.message}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;