import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS } from '../config';
import './UmpireAccuracy.css';
import { useRef } from 'react';

const UmpireAccuracy = () => {
  const [file, setFile] = useState(null);
  const [accuracyData, setAccuracyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [plotUrl, setPlotUrl] = useState(null);
  const plotRef = useRef(null);
  const { token } = useAuth();
  const navigate = useNavigate();

  const handleFileChange = async (e) => {
    setError('');
    setAccuracyData(null);
    setPlotUrl(null);
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    if (!selectedFile) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      // Fetch stats
      const response = await fetch(API_ENDPOINTS.METRICS_UMPIRE_ACCURACY, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch umpire accuracy');
      }
      const data = await response.json();
      setAccuracyData(data);

      // Fetch plot image
      const plotResp = await fetch(API_ENDPOINTS.METRICS_UMPIRE_ACCURACY_PLOT, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });
      if (plotResp.ok) {
        const blob = await plotResp.blob();
        setPlotUrl(URL.createObjectURL(blob));
      } else {
        setPlotUrl(null);
      }
    } catch (error) {
      console.error('Error fetching umpire accuracy:', error);
      setError('Failed to load umpire accuracy data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const MetricCard = ({ title, value, color = 'primary' }) => (
    <div className={`metric-card ${color}`}>
      <h3>{title}</h3>
      <div className="metric-value">{value}</div>
    </div>
  );

  return (
    <div className="umpire-container">
      <div className="umpire-card">
        <div className="umpire-header">
          <h1>⚖️ Umpire Accuracy Analysis</h1>
          <p>Analyze umpire performance and call accuracy</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="file-upload-section">
          <label htmlFor="umpire-csv">Select CSV File:</label>
          <input
            id="umpire-csv"
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            disabled={loading}
          />
          {file && <span className="file-name">Selected: {file.name}</span>}
        </div>

        {accuracyData && (
          <div className="accuracy-section">
            <div className="accuracy-header">
              <h2>📊 Umpire Accuracy Results</h2>
              {accuracyData.filters.team && (
                <p className="filter-info">Team: {accuracyData.filters.team}</p>
              )}
              {accuracyData.filters.pitcher && (
                <p className="filter-info">Pitcher: {accuracyData.filters.pitcher}</p>
              )}
            </div>

            <div className="metrics-grid screenshot-metrics-grid">
              {accuracyData.metrics['Total Called Pitches'] && (
                <MetricCard
                  title="Total Called Pitches"
                  value={accuracyData.metrics['Total Called Pitches']}
                  color="primary"
                />
              )}
              {accuracyData.metrics['Correct Strikes'] && (
                <MetricCard
                  title="Correct Strikes"
                  value={accuracyData.metrics['Correct Strikes']}
                  color="success"
                />
              )}
              {accuracyData.metrics['Correct Balls'] && (
                <MetricCard
                  title="Correct Balls"
                  value={accuracyData.metrics['Correct Balls']}
                  color="success"
                />
              )}
              {accuracyData.metrics['Missed Strikes'] && (
                <MetricCard
                  title="Missed Strikes"
                  value={accuracyData.metrics['Missed Strikes']}
                  color="warning"
                />
              )}
              {accuracyData.metrics['Missed Balls'] && (
                <MetricCard
                  title="Missed Balls"
                  value={accuracyData.metrics['Missed Balls']}
                  color="warning"
                />
              )}
              {accuracyData.metrics['Overall Accuracy'] && (
                <MetricCard
                  title="Overall Accuracy"
                  value={accuracyData.metrics['Overall Accuracy']}
                  color="primary"
                />
              )}
            </div>

            {/* Show the plot image */}
            {plotUrl && (
              <div className="umpire-plot-section screenshot-plot-section">
                <h3 style={{ textAlign: 'center', marginBottom: '1rem' }}>Strike Zone & Critical Misses</h3>
                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <img
                    ref={plotRef}
                    src={plotUrl}
                    alt="Umpire Call Accuracy Plot"
                    style={{ width: '600px', height: '600px', border: '2px solid #888', background: '#fff', boxShadow: '0 2px 12px rgba(0,0,0,0.07)', borderRadius: '12px' }}
                  />
                </div>
              </div>
            )}

            {/* Export as PDF button (placeholder) */}
            <div style={{ textAlign: 'center', margin: '1rem 0' }}>
              <button className="export-pdf-button" disabled>
                Export as PDF (coming soon)
              </button>
            </div>
          </div>
        )}

        <div className="umpire-actions">
          <button onClick={handleBackToDashboard} className="secondary-button">
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default UmpireAccuracy; 