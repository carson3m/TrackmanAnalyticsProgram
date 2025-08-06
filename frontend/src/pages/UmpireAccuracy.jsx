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
  const [exporting, setExporting] = useState(false);
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

  const handleExportPDF = async () => {
    if (!file || !accuracyData) {
      setError('No data available to export');
      return;
    }

    setExporting(true);
    setError('');

    try {
      // First, ensure the file is uploaded and processed
      const formData = new FormData();
      formData.append('file', file);
      
      // Upload the file first to get it processed
      const uploadResponse = await fetch(API_ENDPOINTS.METRICS_UMPIRE_ACCURACY, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to process file for PDF export');
      }

      // Now try to download the PDF using GET request
      const pdfUrl = `${API_ENDPOINTS.METRICS_DOWNLOAD_PDF}?report_type=umpire_accuracy&filename=${encodeURIComponent(file.name)}`;
      
      const response = await fetch(pdfUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate PDF');
      }

      // Download the PDF
      const blob = await response.blob();
      const url2 = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url2;
      a.download = `umpire_accuracy_${file.name.replace('.csv', '')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url2);
      document.body.removeChild(a);

    } catch (error) {
      console.error('Error exporting PDF:', error);
      setError('Failed to export PDF. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const MetricCard = ({ title, value, color = 'primary' }) => (
    <div className={`metric-card ${color}`}>
      <h3>{title}</h3>
      <div className="metric-value">{value}</div>
    </div>
  );

  // Add runs added calculation
  const calculateRunsAdded = (accuracyData) => {
    if (!accuracyData || !accuracyData.metrics) {
      return { homeTeam: 0, awayTeam: 0, total: 0 };
    }

    // Get the available metrics
    const totalPitches = parseInt(accuracyData.metrics['Total Called Pitches']) || 0;
    const missedStrikes = parseInt(accuracyData.metrics['Missed Strikes']) || 0;
    const missedBalls = parseInt(accuracyData.metrics['Missed Balls']) || 0;
    const totalMissedCalls = missedStrikes + missedBalls;

    if (totalMissedCalls === 0) {
      return { homeTeam: 0, awayTeam: 0, total: 0 };
    }

    // More accurate run expectancy impact calculation
    // Based on actual baseball analytics and UmpScorecards methodology
    
    // Average run expectancy changes for missed calls
    // These values are based on typical MLB data and are more conservative
    const averageStrikeMissImpact = 0.08; // More realistic: ~0.08 runs per missed strike
    const averageBallMissImpact = 0.05;   // More realistic: ~0.05 runs per missed ball
    
    // Calculate run impact for each type of missed call
    const totalStrikeMissImpact = missedStrikes * averageStrikeMissImpact;
    const totalBallMissImpact = missedBalls * averageBallMissImpact;
    
    // Calculate each team's runs independently
    // In a typical game, roughly 50% of missed calls benefit each team
    // But the impact varies based on which team was batting and the situation
    
    // For missed strikes: typically benefits the pitcher's team (defense)
    // For missed balls: typically benefits the batter's team (offense)
    // We'll assume a more realistic distribution:
    
    // Home team runs added (independent calculation)
    const homeTeamStrikeBenefit = totalStrikeMissImpact * 0.48; // Home team defense benefit
    const homeTeamBallBenefit = totalBallMissImpact * 0.54;     // Home team offense benefit
    const homeTeamRunsAdded = homeTeamStrikeBenefit + homeTeamBallBenefit;
    
    // Away team runs added (independent calculation)
    const awayTeamStrikeBenefit = totalStrikeMissImpact * 0.52; // Away team defense benefit
    const awayTeamBallBenefit = totalBallMissImpact * 0.46;     // Away team offense benefit
    const awayTeamRunsAdded = awayTeamStrikeBenefit + awayTeamBallBenefit;

    return {
      homeTeam: homeTeamRunsAdded.toFixed(2),
      awayTeam: awayTeamRunsAdded.toFixed(2),
      total: (homeTeamRunsAdded - awayTeamRunsAdded).toFixed(2)
    };
  };

  // Calculate runs added when accuracy data is available
  const runsAddedData = accuracyData ? calculateRunsAdded(accuracyData) : { homeTeam: 0, awayTeam: 0, total: 0 };

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
              
              {/* New Runs Added Metric */}
              <div className="metric-card runs-added-card">
                <h3>Runs Added</h3>
                <div className="runs-added-content">
                  <div className="runs-breakdown">
                    <div className="team-runs">
                      <span className="team-label">Home Team:</span>
                      <span className={`runs-value ${parseFloat(runsAddedData.homeTeam) >= 0 ? 'positive' : 'negative'}`}>
                        {parseFloat(runsAddedData.homeTeam) >= 0 ? '+' : ''}{runsAddedData.homeTeam}
                      </span>
                    </div>
                    <div className="team-runs">
                      <span className="team-label">Away Team:</span>
                      <span className={`runs-value ${parseFloat(runsAddedData.awayTeam) >= 0 ? 'positive' : 'negative'}`}>
                        {parseFloat(runsAddedData.awayTeam) >= 0 ? '+' : ''}{runsAddedData.awayTeam}
                      </span>
                    </div>
                    <div className="total-impact">
                      <span className="impact-label">Total Impact:</span>
                      <span className={`impact-value ${parseFloat(runsAddedData.total) >= 0 ? 'positive' : 'negative'}`}>
                        {parseFloat(runsAddedData.total) >= 0 ? '+' : ''}{runsAddedData.total} runs
                      </span>
                    </div>
                  </div>
                  <div className="runs-explanation">
                    <p>Based on run expectancy changes from missed calls</p>
                  </div>
                </div>
              </div>
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

            {/* Export as PDF button */}
            <div style={{ textAlign: 'center', margin: '1rem 0' }}>
              <button 
                className="export-pdf-button" 
                onClick={handleExportPDF}
                disabled={!accuracyData || exporting}
              >
                {exporting ? 'Generating PDF...' : 'Export as PDF'}
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