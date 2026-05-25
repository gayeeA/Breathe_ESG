import { useEffect, useState } from 'react';
import './index.css';

const SOURCE_OPTIONS = [
  { value: 'sap-fuel', label: 'SAP fuel/procurement export' },
  { value: 'utility-electricity', label: 'Utility electricity bill CSV' },
  { value: 'travel-corporate', label: 'Corporate travel export' },
];

function App() {
  const [tenant, setTenant] = useState('acme');
  const [sourceType, setSourceType] = useState('sap-fuel');
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/records/?status=pending_review');
      const data = await response.json();
      const recordList = Array.isArray(data) ? data : data.results || [];
      setRecords(recordList);
    } catch (error) {
      setMessage('Unable to load records.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!file) {
      setMessage('Please choose a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('tenant', tenant);
    formData.append('source_type', sourceType);
    formData.append('file', file);

    setLoading(true);
    setMessage('Uploading...');
    try {
      const res = await fetch('/api/imports/upload/', {
        method: 'POST',
        body: formData,
      });
      const result = await res.json();
      if (!res.ok) {
        setMessage(result.detail || 'Import failed.');
      } else {
        setMessage(`Imported ${result.imported} rows, ${result.failed} failed.`);
        fetchRecords();
      }
    } catch (error) {
      setMessage('Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  const approveRecord = async (id) => {
    try {
      const res = await fetch(`/api/records/${id}/approve/`, { method: 'POST' });
      if (res.ok) {
        fetchRecords();
      }
    } catch (error) {
      setMessage('Approve failed.');
    }
  };

  return (
    <div className="shell">
      <header>
        <h1>Breathe ESG import review</h1>
        <p>Upload realistic SAP, electricity, or travel exports and review the normalized rows before audit.</p>
      </header>

      <section className="upload-panel">
        <h2>Import source data</h2>
        <form onSubmit={handleUpload}>
          <label>
            Tenant slug
            <input value={tenant} onChange={(e) => setTenant(e.target.value)} />
          </label>
          <label>
            Source type
            <select value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
              {SOURCE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            File upload
            <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          </label>
          <button type="submit" disabled={loading}>Upload to ingest</button>
          <div className="message">{message}</div>
        </form>
      </section>

      <section className="review-panel">
        <h2>Pending review</h2>
        {loading ? (
          <p>Loading...</p>
        ) : records.length ? (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Scope</th>
                <th>Period</th>
                <th>Quantity</th>
                <th>Emissions</th>
                <th>Suspicious</th>
                <th>Approve</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.id} className={record.suspicious_reason ? 'suspicious' : ''}>
                  <td>{record.id}</td>
                  <td>{record.record_type}</td>
                  <td>{record.emission_scope}</td>
                  <td>{record.activity_start} → {record.activity_end}</td>
                  <td>{record.normalized_quantity} {record.normalized_unit}</td>
                  <td>{record.emissions_kg_co2e.toFixed(1)} kg CO₂e</td>
                  <td>{record.suspicious_reason || '—'}</td>
                  <td><button onClick={() => approveRecord(record.id)}>Approve</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No pending records yet.</p>
        )}
      </section>
    </div>
  );
}

export default App;
