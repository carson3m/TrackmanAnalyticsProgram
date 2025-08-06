import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS } from '../config';
import './GameReport.css';

const GameReport = () => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('summary');
  const { fileId, pitcherName } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchGameReport();
  }, [fileId]);

  const fetchGameReport = async () => {
    try {
      let apiEndpoint;
      if (pitcherName) {
        // Pitcher-specific report
        console.log('Fetching pitcher-specific game report for fileId:', fileId, 'pitcher:', pitcherName);
        apiEndpoint = `${API_ENDPOINTS.GAME_REPORT}/${fileId}/pitcher/${pitcherName}`;
      } else {
        // Regular game report
        console.log('Fetching game report for fileId:', fileId);
        apiEndpoint = `${API_ENDPOINTS.GAME_REPORT}/${fileId}`;
      }
      
      console.log('API endpoint:', apiEndpoint);
      console.log('Token available:', !!token);
      
      const response = await fetch(apiEndpoint, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
        credentials: 'include',
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', errorData);
        throw new Error(errorData.detail || 'Failed to fetch game report');
      }

      const data = await response.json();
      console.log('Game report data:', data);
      setReport(data);
    } catch (error) {
      console.error('Error fetching game report:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const formatPercentage = (value) => {
    return value ? `${value.toFixed(1)}%` : '0.0%';
  };

  const formatAverage = (value) => {
    return value ? value.toFixed(3) : '0.000';
  };

  const formatSpeed = (value) => {
    return value ? `${value.toFixed(1)} mph` : 'N/A';
  };

  if (loading) {
    return <div className="game-report-container">Loading game report...</div>;
  }

  if (error) {
    return <div className="game-report-container">Error: {error}</div>;
  }

  if (!report) {
    return <div className="game-report-container">No report data available</div>;
  }

  console.log('Rendering GameReport with data:', report);
  console.log('fileId:', fileId);
  console.log('pitcherName:', pitcherName);

  // Handle both regular game reports and pitcher-specific reports
  const { game_summary, pitchers, batters, pitches, pitcher_stats } = report;
  
  // For pitcher-specific reports, we only have one pitcher
  const isPitcherSpecific = !!pitcher_stats;
  const displayPitchers = isPitcherSpecific ? [pitcher_stats] : (pitchers || []);
  const displayBatters = batters || [];
  const displayPitches = pitches || [];

  try {
    return (
      <div className="game-report-container">
        <div className="report-header">
          <button onClick={() => navigate(-1)} className="back-button">
            ← Back
          </button>
          <h1>Game Report</h1>
        </div>

      {/* Game Summary Card */}
      <div className="game-summary-card">
        <div className="summary-header">
          <h2>{game_summary.opponent || 'Unknown Opponent'}</h2>
          <div className={`result-badge ${game_summary.result?.toLowerCase().includes('w') ? 'win' : game_summary.result?.toLowerCase().includes('l') ? 'loss' : 'neutral'}`}>
            {game_summary.result || 'N/A'}
          </div>
        </div>
        <div className="summary-details">
          <div className="detail-item">
            <span className="label">Date:</span>
            <span className="value">{formatDate(game_summary.game_date)}</span>
          </div>
          <div className="detail-item">
            <span className="label">Total Pitches:</span>
            <span className="value">{game_summary.total_pitches}</span>
          </div>
          <div className="detail-item">
            <span className="label">Innings:</span>
            <span className="value">{game_summary.total_innings}</span>
          </div>
          {game_summary.notes && (
            <div className="detail-item">
              <span className="label">Notes:</span>
              <span className="value">{game_summary.notes}</span>
            </div>
          )}
        </div>
        
        {/* Generate Pitcher Report Button */}
        <div className="summary-actions">
          <button
            onClick={() => {
              // Store the selected file info for the pitcher report flow
              sessionStorage.setItem('selectedCSVFile', JSON.stringify({
                id: fileId,
                filename: game_summary.filename || 'Unknown',
                game_date: game_summary.game_date,
                opponent: game_summary.opponent,
                game_result: game_summary.result
              }));
              navigate('/select-team');
            }}
            className="generate-report-button"
          >
            📊 Generate Pitcher Report
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          Summary
        </button>
        <button 
          className={`tab-button ${activeTab === 'pitching' ? 'active' : ''}`}
          onClick={() => setActiveTab('pitching')}
        >
          {isPitcherSpecific ? 'Pitcher Performance' : `Pitching (${displayPitchers.length})`}
        </button>
        <button 
          className={`tab-button ${activeTab === 'batting' ? 'active' : ''}`}
          onClick={() => setActiveTab('batting')}
        >
          Batting ({displayBatters.length})
        </button>
        <button 
          className={`tab-button ${activeTab === 'pitches' ? 'active' : ''}`}
          onClick={() => setActiveTab('pitches')}
        >
          Pitch-by-Pitch
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'summary' && (
          <div className="summary-tab">
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Pitching Summary</h3>
                              <div className="stat-item">
                <span>Total Pitchers:</span>
                <span>{displayPitchers.length}</span>
              </div>
                <div className="stat-item">
                  <span>Total Strikeouts:</span>
                  <span>{displayPitchers.reduce((sum, p) => sum + (p.strikeouts || 0), 0)}</span>
                </div>
                <div className="stat-item">
                  <span>Total Walks:</span>
                  <span>{displayPitchers.reduce((sum, p) => sum + (p.walks || 0), 0)}</span>
                </div>
                <div className="stat-item">
                  <span>Total Hits Allowed:</span>
                  <span>{displayPitchers.reduce((sum, p) => sum + (p.hits || 0), 0)}</span>
                </div>
              </div>

              <div className="stat-card">
                <h3>Batting Summary</h3>
                              <div className="stat-item">
                <span>Total Batters:</span>
                <span>{displayBatters.length}</span>
              </div>
                <div className="stat-item">
                  <span>Total Hits:</span>
                  <span>{displayBatters.reduce((sum, b) => sum + (b.hits || 0), 0)}</span>
                </div>
                <div className="stat-item">
                  <span>Total Walks:</span>
                  <span>{displayBatters.reduce((sum, b) => sum + (b.walks || 0), 0)}</span>
                </div>
                <div className="stat-item">
                  <span>Total Strikeouts:</span>
                  <span>{displayBatters.reduce((sum, b) => sum + (b.strikeouts || 0), 0)}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'pitching' && (
          <div className="pitching-tab">
            <div className="pitchers-grid">
              {displayPitchers.map((pitcher, index) => (
                <div key={index} className="pitcher-card">
                  <div className="pitcher-header">
                    <h3>{pitcher.name}</h3>
                    <span className="team-badge">{pitcher.team}</span>
                  </div>
                  <div className="pitcher-stats">
                    <div className="stat-row">
                      <span>Pitches:</span>
                      <span>{pitcher.pitches || 0}</span>
                    </div>
                    <div className="stat-row">
                      <span>Strikes:</span>
                      <span>{pitcher.strikes || 0} ({formatPercentage(pitcher.strike_percentage || 0)})</span>
                    </div>
                    <div className="stat-row">
                      <span>Balls:</span>
                      <span>{pitcher.balls || 0} ({formatPercentage(pitcher.ball_percentage || 0)})</span>
                    </div>
                    <div className="stat-row">
                      <span>Strikeouts:</span>
                      <span>{pitcher.strikeouts || 0}</span>
                    </div>
                    <div className="stat-row">
                      <span>Walks:</span>
                      <span>{pitcher.walks || 0}</span>
                    </div>
                    <div className="stat-row">
                      <span>Hits Allowed:</span>
                      <span>{pitcher.hits || 0}</span>
                    </div>
                    <div className="stat-row">
                      <span>Runs Allowed:</span>
                      <span>{pitcher.runs || 0}</span>
                    </div>
                    <div className="stat-row">
                      <span>Avg Speed:</span>
                      <span>{formatSpeed(pitcher.avg_speed || 0)}</span>
                    </div>
                  </div>
                  {pitcher.pitch_types && Object.keys(pitcher.pitch_types).length > 0 && (
                    <div className="pitch-types">
                      <h4>Pitch Types:</h4>
                      <div className="pitch-type-list">
                        {Object.entries(pitcher.pitch_types).map(([type, count]) => (
                          <div key={type} className="pitch-type-item">
                            <span>{type}:</span>
                            <span>{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'batting' && (
          <div className="batting-tab">
            <div className="batters-grid">
              {displayBatters.map((batter, index) => (
                <div key={index} className="batter-card">
                  <div className="batter-header">
                    <h3>{batter.name}</h3>
                    <span className="team-badge">{batter.team}</span>
                  </div>
                  <div className="batter-stats">
                    <div className="stat-row">
                      <span>At Bats:</span>
                      <span>{batter.at_bats || 0}</span>
                    </div>
                    <div className="stat-row">
                      <span>Hits:</span>
                      <span>{batter.hits || 0}</span>
                    </div>
                    <div className="stat-row">
                      <span>Batting Average:</span>
                      <span>{formatAverage(batter.batting_average || 0)}</span>
                    </div>
                    <div className="stat-row">
                      <span>Walks:</span>
                      <span>{batter.walks || 0}</span>
                    </div>
                    <div className="stat-row">
                      <span>Strikeouts:</span>
                      <span>{batter.strikeouts || 0}</span>
                    </div>
                    <div className="stat-row">
                      <span>Runs:</span>
                      <span>{batter.runs || 0}</span>
                    </div>
                    <div className="stat-row">
                      <span>Avg Exit Velocity:</span>
                      <span>{formatSpeed(batter.avg_exit_velocity || 0)}</span>
                    </div>
                  </div>
                  {batter.hit_types && Object.keys(batter.hit_types).length > 0 && (
                    <div className="hit-types">
                      <h4>Hit Types:</h4>
                      <div className="hit-type-list">
                        {Object.entries(batter.hit_types).map(([type, count]) => (
                          <div key={type} className="hit-type-item">
                            <span>{type}:</span>
                            <span>{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'pitches' && (
          <div className="pitches-tab">
            <div className="pitches-table">
              <table>
                <thead>
                  <tr>
                    <th>Pitch #</th>
                    <th>Pitcher</th>
                    <th>Batter</th>
                    <th>Type</th>
                    <th>Call</th>
                    <th>Speed</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {displayPitches.map((pitch, index) => (
                    <tr key={index}>
                      <td>{pitch.PitchNo || index + 1}</td>
                      <td>{pitch.Pitcher || 'N/A'}</td>
                      <td>{pitch.Batter || 'N/A'}</td>
                      <td>{pitch.AutoPitchType || 'N/A'}</td>
                      <td>{pitch.PitchCall || 'N/A'}</td>
                      <td>{formatSpeed(pitch.RelSpeed)}</td>
                      <td>{pitch.PlayResult || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
    );
  } catch (error) {
    console.error('Error rendering GameReport:', error);
    return (
      <div className="game-report-container">
        <div className="report-header">
          <button onClick={() => navigate(-1)} className="back-button">
            ← Back
          </button>
          <h1>Game Report</h1>
        </div>
        <div style={{ padding: '20px', color: 'red' }}>
          <h2>Error Rendering Report</h2>
          <p>There was an error rendering the game report:</p>
          <pre>{error.message}</pre>
          <p>Please try refreshing the page or going back.</p>
        </div>
      </div>
    );
  }
};

export default GameReport; 