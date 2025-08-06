import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS, FALLBACK_API_URL } from '../config';
import './ViewReport.css';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

const ViewReport = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);
  const { token } = useAuth();
  const navigate = useNavigate();
  const [pitchData, setPitchData] = useState([]);
  const [pitchDataLoading, setPitchDataLoading] = useState(true);
  const [pitchDataError, setPitchDataError] = useState('');

  const selectedTeam = sessionStorage.getItem('selectedTeam');
  const selectedPitcher = sessionStorage.getItem('selectedPitcher');
  const selectedCSVFile = sessionStorage.getItem('selectedCSVFile');

  useEffect(() => {
    const fetchMetrics = async () => {
      if (!selectedTeam || !selectedPitcher) {
        setError('No team or pitcher selected. Please start over.');
        setLoading(false);
        return;
      }

      try {
        // Check if we have a selected CSV file (new flow) or not (old flow)
        if (selectedCSVFile) {
          const csvFile = JSON.parse(selectedCSVFile);
          console.log('Using file-specific report for:', {
            fileId: csvFile.id,
            team: selectedTeam,
            pitcher: selectedPitcher,
          });
          
          // Use the file-specific game report endpoint
          const response = await fetch(
            `${API_ENDPOINTS.GAME_REPORT}/${csvFile.id}/pitcher/${encodeURIComponent(selectedPitcher)}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            }
          );

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch metrics');
          }

          const data = await response.json();
          console.log('Received file-specific metrics data:', data);
          
          // Transform the data to match the expected format
          if (data.pitcher_stats) {
            console.log('DEBUG: Received pitcher_stats:', data.pitcher_stats);
            
            const pitcher_stats = data.pitcher_stats;
            
            // Use the detailed per-pitch metrics from the backend if available
            let per_pitch_metrics = [];
            if (pitcher_stats.per_pitch_metrics && pitcher_stats.per_pitch_metrics.length > 0) {
              console.log('DEBUG: Using detailed per-pitch metrics from backend');
              per_pitch_metrics = pitcher_stats.per_pitch_metrics;
            } else if (pitcher_stats.pitch_types) {
              console.log('DEBUG: Using basic pitch type counts');
              // Fallback to basic pitch type counts
              per_pitch_metrics = Object.entries(pitcher_stats.pitch_types).map(([pitch_type, count]) => ({
                'Pitch Type': pitch_type,
                'Count': count,
                'Avg Velo': 'N/A',
                'Spin Rate': 'N/A',
                'Vert. Break': 'N/A',
                'Horz. Break': 'N/A',
                'Strike %': 'N/A',
                'Whiff %': 'N/A',
                'Chase %': 'N/A',
                'Contact %': 'N/A',
                'Hard Hit %': 'N/A',
                'Barrel %': 'N/A',
                'PutAway %': 'N/A',
                'In-Zone %': 'N/A',
                'Avg Extension': 'N/A'
              }));
            }
            
            setMetrics({
              whiff_rate: 0, // Will be calculated from pitch data
              strike_rate: pitcher_stats.strike_percentage || 0,
              zone_rate: 0, // Will be calculated from pitch data
              per_pitch_metrics: per_pitch_metrics
            });
          } else {
            throw new Error('Invalid data format received');
          }
        } else {
          // Fallback to old metrics endpoint
          console.log('Using old metrics endpoint for:', {
            team: selectedTeam,
            pitcher: selectedPitcher,
          });
          
          const response = await fetch(
            API_ENDPOINTS.METRICS_SUMMARY,
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
              },
              body: JSON.stringify({
                team: selectedTeam,
                pitcher: selectedPitcher,
              }),
            }
          );

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch metrics');
          }

          const data = await response.json();
          console.log('Received old metrics data:', data);
          
          if (data.detail) {
            throw new Error(data.detail);
          }
          
          setMetrics(data);
        }
      } catch (error) {
        console.error('Error fetching metrics:', error);
        setError('Failed to load metrics. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [token, selectedTeam, selectedPitcher, selectedCSVFile]);

  // Fetch pitch-level data for plots
  useEffect(() => {
    const fetchPitchData = async () => {
      if (!selectedTeam || !selectedPitcher) {
        setPitchDataError('No team or pitcher selected.');
        setPitchDataLoading(false);
        return;
      }
      setPitchDataLoading(true);
      setPitchDataError('');
      try {
        // Check if we have a selected CSV file (new flow) or not (old flow)
        if (selectedCSVFile) {
          const csvFile = JSON.parse(selectedCSVFile);
          console.log('Using file-specific pitch data for:', {
            fileId: csvFile.id,
            team: selectedTeam,
            pitcher: selectedPitcher,
          });
          
          // Use the file-specific game report endpoint to get pitch data
          const response = await fetch(
            `${API_ENDPOINTS.GAME_REPORT}/${csvFile.id}/pitcher/${encodeURIComponent(selectedPitcher)}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            }
          );
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch pitch data');
          }
          
          const data = await response.json();
          console.log('Received file-specific pitch data:', data.pitches);
          setPitchData(data.pitches || []);
        } else {
          // Fallback to old pitch data endpoint
          console.log('Using old pitch data endpoint for:', {
            team: selectedTeam,
            pitcher: selectedPitcher,
          });
          
          const response = await fetch(
            `${API_ENDPOINTS.METRICS_PITCHES}?team=${encodeURIComponent(selectedTeam)}&pitcher=${encodeURIComponent(selectedPitcher)}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            }
          );
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch pitch data');
          }
          const data = await response.json();
          console.log('Received old pitch data:', data.pitches);
          setPitchData(data.pitches || []);
        }
      } catch (error) {
        console.error('Error fetching pitch data:', error);
        setPitchDataError('Failed to load pitch data.');
      } finally {
        setPitchDataLoading(false);
      }
    };
    fetchPitchData();
  }, [token, selectedTeam, selectedPitcher, selectedCSVFile]);

  const handleDownloadPDF = async () => {
    setDownloading(true);
    try {
      // Check if we have a selected CSV file (new flow) or not (old flow)
      if (selectedCSVFile) {
        const csvFile = JSON.parse(selectedCSVFile);
        console.log('Using file-specific PDF download for:', {
          fileId: csvFile.id,
          pitcher: selectedPitcher,
        });
        
        // Use the file-specific PDF endpoint
        const response = await fetch(
          `${API_ENDPOINTS.GAME_REPORT}/${csvFile.id}/pitcher/${encodeURIComponent(selectedPitcher)}/pdf`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to download PDF');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedPitcher}_${csvFile.game_date}_report.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        // Fallback to old PDF endpoint
        console.log('Using old PDF endpoint for:', {
          team: selectedTeam,
          pitcher: selectedPitcher,
        });
        
        const response = await fetch(
          `${API_ENDPOINTS.METRICS_DOWNLOAD_PDF}?team=${encodeURIComponent(selectedTeam)}&pitcher=${encodeURIComponent(selectedPitcher)}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to download PDF');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedPitcher}_${selectedTeam}_report.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading PDF:', error);
      setError('Failed to download PDF. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  const handleNewAnalysis = () => {
    // Clear session storage and go back to upload
    sessionStorage.clear();
    navigate('/upload');
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  if (loading) {
    return (
      <div className="report-container">
        <div className="report-card">
          <div className="loading">Loading report...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="report-container">
      <div className="report-card">
        <div className="report-header">
          <h1>Pitcher Analysis Report</h1>
          <p>{selectedPitcher} - {selectedTeam}</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        {metrics && (
          <>
            {/* Per-pitch metrics table (already present) */}
            {Array.isArray(metrics.per_pitch_metrics) && metrics.per_pitch_metrics.length > 0 && (
              <div className="per-pitch-metrics-table-container">
                <h2>Per-Pitch Type Metrics</h2>
                <div className="table-scroll">
                  <table className="per-pitch-metrics-table">
                    <thead>
                      <tr>
                        {Object.keys(metrics.per_pitch_metrics[0]).map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {metrics.per_pitch_metrics.map((row, idx) => (
                        <tr key={idx}>
                          {Object.values(row).map((val, i) => (
                            <td key={i}>{typeof val === 'number' ? val.toFixed(2) : val}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Pitch Breaks Plot */}
            <div className="plot-section">
              <h2>Pitch Breaks</h2>
              {pitchDataLoading ? (
                <div>Loading pitch data...</div>
              ) : pitchDataError ? (
                <div className="error-message">{pitchDataError}</div>
              ) : (
                <ResponsiveContainer width="100%" height={350}>
                  <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid />
                    <XAxis type="number" dataKey="HorzBreak" name="Horizontal Break (in)" label={{ value: 'Horizontal Break (in)', position: 'insideBottom', offset: -5 }} domain={[-25, 25]} />
                    <YAxis type="number" dataKey="InducedVertBreak" name="Vertical Break (in)" label={{ value: 'Vertical Break (in)', angle: -90, position: 'insideLeft' }} domain={[-25, 25]} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Legend />
                    {/* Add 0" axis lines */}
                    <ReferenceLine x={0} stroke="black" strokeWidth={1} strokeOpacity={0.7} />
                    <ReferenceLine y={0} stroke="black" strokeWidth={1} strokeOpacity={0.7} />
                    {Array.from(new Set(pitchData.map(p => p.AutoPitchType || 'Unknown'))).map((type, idx) => (
                      <Scatter
                        key={type}
                        name={type}
                        data={pitchData.filter(p => p.AutoPitchType === type)}
                        fill={['#8884d8', '#82ca9d', '#ff7300', '#ff0000', '#0088FE', '#00C49F', '#FFBB28', '#FF8042'][idx % 8]}
                        line={false}
                      />
                    ))}
                  </ScatterChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Release Points Plot */}
            <div className="plot-section">
              <h2>Release Points</h2>
              {pitchDataLoading ? (
                <div>Loading pitch data...</div>
              ) : pitchDataError ? (
                <div className="error-message">{pitchDataError}</div>
              ) : (
                <ResponsiveContainer width="100%" height={350}>
                  <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid />
                    <XAxis type="number" dataKey="RelSide" name="Horizontal Release Side (ft)" label={{ value: 'Horizontal Release Side (ft)', position: 'insideBottom', offset: -5 }} domain={[-3.5, 3.5]} />
                    <YAxis type="number" dataKey="RelHeight" name="Vertical Release Height (ft)" label={{ value: 'Vertical Release Height (ft)', angle: -90, position: 'insideLeft' }} domain={[1, 7]} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Legend />
                    {/* Add 0" axis lines */}
                    <ReferenceLine x={0} stroke="black" strokeWidth={1} strokeOpacity={0.7} />
                    <ReferenceLine y={0} stroke="black" strokeWidth={1} strokeOpacity={0.7} />
                    {Array.from(new Set(pitchData.map(p => p.AutoPitchType || 'Unknown'))).map((type, idx) => (
                      <Scatter
                        key={type}
                        name={type}
                        data={pitchData.filter(p => p.AutoPitchType === type)}
                        fill={['#8884d8', '#82ca9d', '#ff7300', '#ff0000', '#0088FE', '#00C49F', '#FFBB28', '#FF8042'][idx % 8]}
                        line={false}
                      />
                    ))}
                  </ScatterChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="report-actions">
              <button onClick={handleBackToDashboard} className="secondary-button">
                Back to Dashboard
              </button>
              <button onClick={handleNewAnalysis} className="secondary-button">
                New Analysis
              </button>
              <button
                onClick={handleDownloadPDF}
                className="download-button"
                disabled={downloading}
              >
                {downloading ? 'Downloading...' : '\ud83d\udcc4 Download PDF Report'}
              </button>
            </div>
          </>
        )}

        {!metrics && !error && (
          <div className="no-metrics">
            <p>No metrics available for this pitcher.</p>
            <button onClick={handleNewAnalysis} className="primary-button">
              Start New Analysis
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ViewReport; 