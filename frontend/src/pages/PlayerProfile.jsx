import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS } from '../config';
import './PlayerProfile.css';

// Import Chart.js for heat maps
import { Chart, registerables } from 'chart.js';
import 'chartjs-adapter-date-fns';
import annotationPlugin from 'chartjs-plugin-annotation';
Chart.register(...registerables);

// Register the annotation plugin
Chart.register(annotationPlugin);

const PlayerProfile = () => {
  const { playerName, playerType } = useParams();
  const [playerData, setPlayerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [filters, setFilters] = useState({
    count: [],
    pitchType: [],
    result: 'all',
    minVelocity: '',
    maxVelocity: ''
  });
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPlayerData();
  }, [playerName, playerType]);

  const fetchPlayerData = async () => {
    try {
      // Build query parameters
      const params = new URLSearchParams({
        player_name: playerName,
        player_type: playerType,
        result: filters.result
      });
      
      // Only add count and pitch_type if they have values
      if (filters.count.length > 0) {
        params.append('count', filters.count.join(','));
        console.log('DEBUG: Adding count filter:', filters.count.join(','));
      }
      if (filters.pitchType.length > 0) {
        params.append('pitch_type', filters.pitchType.join(','));
        console.log('DEBUG: Adding pitch_type filter:', filters.pitchType.join(','));
      }
      
      if (filters.minVelocity) params.append('min_velocity', filters.minVelocity);
      if (filters.maxVelocity) params.append('max_velocity', filters.maxVelocity);
      
      console.log('DEBUG: API URL:', `${API_ENDPOINTS.PLAYER_PROFILE}?${params.toString()}`);
      
      const response = await fetch(`${API_ENDPOINTS.PLAYER_PROFILE}?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch player data');
      }

      const data = await response.json();
      console.log('DEBUG: Received player data:', data);
      console.log('DEBUG: Heat maps data:', data.heat_maps);
      setPlayerData(data);
    } catch (error) {
      console.error('Error fetching player data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToRoster = () => {
    navigate('/roster');
  };

  const renderOverview = () => {
    if (!playerData?.season_stats) return <div>No season data available</div>;

    const stats = playerData.season_stats;
    return (
      <div className="overview-section">
        <div className="stats-grid">
          <div className="stat-card">
            <h4>Games Played</h4>
            <div className="stat-value">{stats.games_played}</div>
          </div>
          <div className="stat-card">
            <h4>Total Events</h4>
            <div className="stat-value">{stats.total_events}</div>
          </div>
          {playerType === 'pitcher' && (
            <>
              <div className="stat-card">
                <h4>Strike Rate</h4>
                <div className="stat-value">{stats.strike_rate?.toFixed(1)}%</div>
              </div>
              <div className="stat-card">
                <h4>Avg Speed</h4>
                <div className="stat-value">{stats.avg_speed?.toFixed(1)} mph</div>
              </div>
              <div className="stat-card">
                <h4>Batting Average Against</h4>
                <div className="stat-value">{stats.batting_average_against?.toFixed(3)}</div>
              </div>
            </>
          )}
          {playerType === 'batter' && (
            <>
              <div className="stat-card">
                <h4>Batting Average</h4>
                <div className="stat-value">{stats.batting_average?.toFixed(3)}</div>
              </div>
              <div className="stat-card">
                <h4>Avg Exit Velocity</h4>
                <div className="stat-value">{stats.avg_exit_velocity?.toFixed(1)} mph</div>
              </div>
            </>
          )}
        </div>

        {stats.performance_metrics && (
          <div className="performance-metrics">
            <h3>Performance Metrics</h3>
            <div className="metrics-grid">
              {Object.entries(stats.performance_metrics).map(([key, value]) => (
                <div key={key} className="metric-item">
                  <span className="metric-label">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  <span className="metric-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderPitchAnalysis = () => {
    if (!playerData?.pitch_analysis?.pitch_types || playerType !== 'pitcher') {
      return <div>No pitch analysis available for this player type</div>;
    }

    const pitchTypes = playerData.pitch_analysis.pitch_types;
    return (
      <div className="pitch-analysis-section">
        <h3>Pitch Type Analysis</h3>
        <div className="pitch-types-grid">
          {Object.entries(pitchTypes).map(([pitchType, data]) => (
            <div key={pitchType} className="pitch-type-card">
              <h4>{pitchType}</h4>
              <div className="pitch-stats">
                <div className="pitch-stat">
                  <span>Count:</span>
                  <span>{data.count}</span>
                </div>
                <div className="pitch-stat">
                  <span>Success Rate:</span>
                  <span>{data.success_rate?.toFixed(1)}%</span>
                </div>
                <div className="pitch-stat">
                  <span>Avg Speed:</span>
                  <span>{data.avg_speed?.toFixed(1)} mph</span>
                </div>
                {data.spin_rate && (
                  <div className="pitch-stat">
                    <span>Spin Rate:</span>
                    <span>{data.spin_rate?.toFixed(0)} rpm</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderHeatMaps = () => {
    return (
      <div className="heat-maps-section">
        <h3>Heat Maps</h3>
        
        {/* Filter Controls */}
        <div className="filter-controls">
          <div className="filter-group">
            <label>Count:</label>
            <div className="checkbox-group">
              {['0-0', '1-0', '2-0', '3-0', '0-1', '1-1', '2-1', '3-1', '0-2', '1-2', '2-2', '3-2'].map(count => (
                <label key={count} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={filters.count.includes(count)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFilters({...filters, count: [...filters.count, count]});
                      } else {
                        setFilters({...filters, count: filters.count.filter(c => c !== count)});
                      }
                    }}
                  />
                  {count}
                </label>
              ))}
            </div>
          </div>
          
          <div className="filter-group">
            <label>Pitch Type:</label>
            <div className="checkbox-group">
              {(playerData?.available_pitch_types || []).map(type => (
                <label key={type} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={filters.pitchType.includes(type)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFilters({...filters, pitchType: [...filters.pitchType, type]});
                      } else {
                        setFilters({...filters, pitchType: filters.pitchType.filter(t => t !== type)});
                      }
                    }}
                  />
                  {type}
                </label>
              ))}
            </div>
          </div>
          
          <div className="filter-group">
            <label>Result:</label>
            <select 
              value={filters.result} 
              onChange={(e) => setFilters({...filters, result: e.target.value})}
              className="filter-select"
            >
              <option value="all">All Results</option>
              <option value="Strike">Strikes</option>
              <option value="Ball">Balls</option>
              <option value="InPlay">In Play</option>
              <option value="Foul">Foul</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>Velocity Range:</label>
            <div className="velocity-range">
              <input 
                type="number" 
                placeholder="Min" 
                value={filters.minVelocity || ''} 
                onChange={(e) => setFilters({...filters, minVelocity: e.target.value})}
                className="velocity-input"
              />
              <span>-</span>
              <input 
                type="number" 
                placeholder="Max" 
                value={filters.maxVelocity || ''} 
                onChange={(e) => setFilters({...filters, maxVelocity: e.target.value})}
                className="velocity-input"
              />
            </div>
          </div>
          
                      <button 
              onClick={() => setFilters({count: [], pitchType: [], result: 'all', minVelocity: '', maxVelocity: ''})}
              className="clear-filters-btn"
            >
              Clear Filters
            </button>
            <button 
              onClick={() => {
                // Don't set any filters - this means "show all data"
                setFilters({count: [], pitchType: [], result: 'all', minVelocity: '', maxVelocity: ''});
              }}
              className="clear-filters-btn"
              style={{marginLeft: '10px'}}
            >
              Show All Data
            </button>
        </div>
        
        <div className="heat-maps-container">
          <div className="heat-map-card">
            <h4>{playerType === 'batter' ? 'Batting Average Zones' : 'Pitch Success Zones'}</h4>
            <canvas id="pitchLocationHeatMap" width="400" height="400"></canvas>
          </div>
          <div className="heat-map-card">
            <h4>{playerType === 'batter' ? 'Average Exit Velocity Zones' : 'Average Velocity Zones'}</h4>
            <canvas id="velocityHeatMap" width="400" height="400"></canvas>
          </div>
        </div>
      </div>
    );
  };

  // Separate useEffect for chart creation
  React.useEffect(() => {
    if (playerData?.heat_maps && activeTab === 'heat-maps') {
      // Add a small delay to ensure DOM elements are ready
      const timer = setTimeout(() => {
        try {
          createPitchLocationHeatMap();
          createVelocityHeatMap();
        } catch (error) {
          console.error('Error creating heat maps:', error);
        }
      }, 100);

      return () => {
        clearTimeout(timer);
      };
    }
  }, [playerData, activeTab]); // Removed filters from dependency to prevent resize

  // Add resize handler for responsive canvas
  React.useEffect(() => {
    const handleResize = () => {
      if (activeTab === 'heat-maps' && playerData?.heat_maps) {
        createPitchLocationHeatMap();
        createVelocityHeatMap();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [activeTab, playerData]);

  // Separate effect for filter changes - only fetch new data, don't resize
  React.useEffect(() => {
    if (activeTab === 'heat-maps' && playerData?.heat_maps) {
      fetchPlayerData();
    }
  }, [filters]); // Only trigger on filter changes

  const createPitchLocationHeatMap = () => {
  const canvas = document.getElementById('pitchLocationHeatMap');
  if (!canvas) return;

  const container = canvas.parentElement;
  const size = Math.min(container.offsetWidth, container.offsetHeight);
  canvas.width = size;
  canvas.height = size;

  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, size, size);

  const heatMapData = playerData?.heat_maps?.pitch_locations;
  if (!heatMapData || heatMapData.length === 0) {
    ctx.fillStyle = '#666';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(`No ${playerType === 'batter' ? 'batting' : 'pitch'} location data available`, size / 2, size / 2);
    return;
  }

  const zones = [
    { x: -0.85, y: 3.6, w: 0.57, h: 0.6 }, { x: -0.28, y: 3.6, w: 0.57, h: 0.6 }, { x: 0.28, y: 3.6, w: 0.57, h: 0.6 },
    { x: -0.85, y: 3.0, w: 0.57, h: 0.6 }, { x: -0.28, y: 3.0, w: 0.57, h: 0.6 }, { x: 0.28, y: 3.0, w: 0.57, h: 0.6 },
    { x: -0.85, y: 2.4, w: 0.57, h: 0.6 }, { x: -0.28, y: 2.4, w: 0.57, h: 0.6 }, { x: 0.28, y: 2.4, w: 0.57, h: 0.6 },
  ];

  const xToCanvas = x => ((x + 3.0) / 6.0) * size;
  const yToCanvas = y => ((6.0 - y) / 4.5) * size;

  const zoneData = zones.map(zone => {
    const points = heatMapData.filter(p =>
      p.x >= zone.x && p.x < zone.x + zone.w &&
      p.y >= zone.y && p.y < zone.y + zone.h
    );
    
    if (playerType === 'batter') {
      // For batters, use batting average
      const total = points.reduce((sum, p) => sum + p.count, 0);
      const battingAvg = points.reduce((sum, p) => sum + (p.batting_avg * p.count), 0);
      const avgBattingAvg = total > 0 ? battingAvg / total : 0;
      return { ...zone, value: avgBattingAvg, isBatter: true };
    } else {
      // For pitchers, use success score
      const total = points.reduce((sum, p) => sum + p.total, 0);
      const successScore = points.reduce((sum, p) => sum + (p.success_score * p.total), 0);
      const avgSuccessScore = total > 0 ? successScore / total : 0;
      return { ...zone, value: avgSuccessScore, isBatter: false };
    }
  });

  const values = zoneData.map(z => z.value);
  const max = Math.max(...values);
  const min = Math.min(...values);

  const colorScale = (v) => {
    if (v === 0) return 'rgba(220,220,220,0.5)';
    const n = (v - min) / (max - min);
    // Simple red (0) to blue (240) transition for colorblind accessibility
    const hue = 240 - (n * 240); // 240 = blue, 0 = red
    return `hsl(${hue}, 80%, 50%)`;
  };

  // Draw grid
  zoneData.forEach(zone => {
    const x = xToCanvas(zone.x);
    const y = yToCanvas(zone.y + zone.h);
    const w = (zone.w / 6.0) * size;
    const h = (zone.h / 4.5) * size;

    ctx.fillStyle = colorScale(zone.value);
    ctx.fillRect(x, y, w, h);

    ctx.strokeStyle = '#444';
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, w, h);

    // Add value text in each zone
    if (zone.value > 0) {
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 12px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      if (zone.isBatter) {
        ctx.fillText(zone.value.toFixed(3), x + w / 2, y + h / 2);
      } else {
        ctx.fillText(zone.value.toFixed(3), x + w / 2, y + h / 2);
      }
    }
  });

  // Legend
  const legendW = size * 0.7;
  const legendH = 16;
  const lx = (size - legendW) / 2;
  const ly = size - 30;

  ctx.fillStyle = '#fff';
  ctx.fillRect(lx, ly, legendW, legendH);

  for (let i = 0; i < legendW; i++) {
    const n = i / legendW;
    const hue = 240 - (n * 240); // Red to blue transition
    ctx.fillStyle = `hsl(${hue}, 80%, 50%)`;
    ctx.fillRect(lx + i, ly + 2, 1, legendH - 4);
  }

  ctx.fillStyle = '#000';
  ctx.font = '10px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('poor', lx, ly + legendH + 10);
  ctx.fillText('excellent', lx + legendW, ly + legendH + 10);
  ctx.fillText(playerType === 'batter' ? 'batting average' : 'pitch success score', size / 2, ly - 5);
};
  

const createVelocityHeatMap = () => {
  const canvas = document.getElementById('velocityHeatMap');
  if (!canvas) return;

  const container = canvas.parentElement;
  const size = Math.min(container.offsetWidth, container.offsetHeight);
  canvas.width = size;
  canvas.height = size;

  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, size, size);

  const velocityData = playerData?.heat_maps?.velocities;
  if (!velocityData || velocityData.length === 0) {
    ctx.fillStyle = '#666';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(`No ${playerType === 'batter' ? 'exit velocity' : 'velocity'} data available`, size / 2, size / 2);
    return;
  }

  const zones = [
    { x: -0.85, y: 3.6, w: 0.57, h: 0.6 }, { x: -0.28, y: 3.6, w: 0.57, h: 0.6 }, { x: 0.28, y: 3.6, w: 0.57, h: 0.6 },
    { x: -0.85, y: 3.0, w: 0.57, h: 0.6 }, { x: -0.28, y: 3.0, w: 0.57, h: 0.6 }, { x: 0.28, y: 3.0, w: 0.57, h: 0.6 },
    { x: -0.85, y: 2.4, w: 0.57, h: 0.6 }, { x: -0.28, y: 2.4, w: 0.57, h: 0.6 }, { x: 0.28, y: 2.4, w: 0.57, h: 0.6 },
  ];

  const xToCanvas = x => ((x + 3.0) / 6.0) * size;
  const yToCanvas = y => ((6.0 - y) / 4.5) * size;

  const zoneData = zones.map(zone => {
    const points = velocityData.filter(p =>
      p.x >= zone.x && p.x < zone.x + zone.w &&
      p.y >= zone.y && p.y < zone.y + zone.h
    );
    
    if (playerType === 'batter') {
      // For batters, use exit velocity
      const sum = points.reduce((sum, p) => sum + p.avg_exit_velocity * p.count, 0);
      const count = points.reduce((sum, p) => sum + p.count, 0);
      const avgExitVel = count > 0 ? sum / count : 0;
      return { ...zone, avg_velocity: avgExitVel, isBatter: true };
    } else {
      // For pitchers, use pitch velocity
      const sum = points.reduce((sum, p) => sum + p.avg_velocity * p.count, 0);
      const count = points.reduce((sum, p) => sum + p.count, 0);
      const avgVel = count > 0 ? sum / count : 0;
      return { ...zone, avg_velocity: avgVel, isBatter: false };
    }
  });

  const values = zoneData.map(z => z.avg_velocity);
  const max = Math.max(...values);
  const min = Math.min(...values);

  const colorScale = (v) => {
    if (v === 0) return 'rgba(220,220,220,0.5)';
    const n = (v - min) / (max - min);
    const hue = 0; // solid red
    const saturation = 80 + n * 20;
    const lightness = 90 - n * 50;
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

  // Draw grid
  zoneData.forEach(zone => {
    const x = xToCanvas(zone.x);
    const y = yToCanvas(zone.y + zone.h);
    const w = (zone.w / 6.0) * size;
    const h = (zone.h / 4.5) * size;

    ctx.fillStyle = colorScale(zone.avg_velocity);
    ctx.fillRect(x, y, w, h);

    ctx.strokeStyle = '#444';
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, w, h);

    // Add velocity text in each zone
    if (zone.avg_velocity > 0) {
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 12px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(zone.avg_velocity.toFixed(1), x + w / 2, y + h / 2);
    }
  });

  // Draw legend
  const legendW = size * 0.7;
  const legendH = 16;
  const lx = (size - legendW) / 2;
  const ly = size - 30;

  ctx.fillStyle = '#fff';
  ctx.fillRect(lx, ly, legendW, legendH);

  for (let i = 0; i < legendW; i++) {
    const n = i / legendW;
    const saturation = 80 + n * 20;
    const lightness = 90 - n * 50;
    ctx.fillStyle = `hsl(0, ${saturation}%, ${lightness}%)`;
    ctx.fillRect(lx + i, ly + 2, 1, legendH - 4);
  }

  ctx.fillStyle = '#000';
  ctx.font = '10px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('low', lx, ly + legendH + 10);
  ctx.fillText('high', lx + legendW, ly + legendH + 10);
  ctx.fillText(playerType === 'batter' ? 'average exit velocity (mph)' : 'average velocity (mph)', size / 2, ly - 5);
};

  const renderRecentGames = () => {
    if (!playerData?.recent_games) return <div>No recent games data available</div>;

    return (
      <div className="recent-games-section">
        <h3>Recent Games</h3>
        <div className="games-list">
          {playerData.recent_games.map((game, index) => (
            <div key={index} className="game-card">
              <div className="game-date">{game.date}</div>
              <div className="game-opponent">vs {game.opponent}</div>
              <div className={`game-result ${game.result?.toLowerCase()}`}>
                {game.result || 'N/A'}
              </div>
              {game.performance_summary && (
                <div className="game-performance">{game.performance_summary}</div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'pitch-analysis':
        return renderPitchAnalysis();
      case 'heat-maps':
        return renderHeatMaps();
      case 'recent-games':
        return renderRecentGames();
      default:
        return renderOverview();
    }
  };

  if (loading) {
    return (
      <div className="player-profile-container">
        <div className="loading">Loading player data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="player-profile-container">
        <div className="error-message">{error}</div>
        <button onClick={handleBackToRoster} className="secondary-button">
          Back to Roster
        </button>
      </div>
    );
  }

  return (
    <div className="player-profile-container">
      <div className="player-profile-header">
        <h1>{playerName}</h1>
        <p className="player-type-badge">{playerType}</p>
        <button onClick={handleBackToRoster} className="back-button">
          ← Back to Roster
        </button>
      </div>

      {playerData?.season_stats && (
        <div className="player-summary">
          <div className="summary-stat">
            <span>Games Played:</span>
            <span>{playerData.season_stats.games_played}</span>
          </div>
          <div className="summary-stat">
            <span>Total {playerType === 'pitcher' ? 'Pitches' : 'At Bats'}:</span>
            <span>{playerData.season_stats.total_events}</span>
          </div>
          {playerType === 'pitcher' && (
            <>
              <div className="summary-stat">
                <span>Strike Rate:</span>
                <span>{playerData.season_stats.strike_rate?.toFixed(1)}%</span>
              </div>
              <div className="summary-stat">
                <span>Avg Speed:</span>
                <span>{playerData.season_stats.avg_speed?.toFixed(1)} mph</span>
              </div>
            </>
          )}
          {playerType === 'batter' && (
            <>
              <div className="summary-stat">
                <span>Batting Average:</span>
                <span>{playerData.season_stats.batting_average?.toFixed(3)}</span>
              </div>
              <div className="summary-stat">
                <span>Avg Exit Velocity:</span>
                <span>{playerData.season_stats.avg_exit_velocity?.toFixed(1)} mph</span>
              </div>
            </>
          )}
        </div>
      )}

      <div className="player-profile-content">
        <div className="tab-navigation">
          <button
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          {playerType === 'pitcher' && (
            <button
              className={`tab-button ${activeTab === 'pitch-analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('pitch-analysis')}
            >
              Pitch Analysis
            </button>
          )}
          <button
            className={`tab-button ${activeTab === 'heat-maps' ? 'active' : ''}`}
            onClick={() => setActiveTab('heat-maps')}
          >
            Heat Maps
          </button>
          <button
            className={`tab-button ${activeTab === 'recent-games' ? 'active' : ''}`}
            onClick={() => setActiveTab('recent-games')}
          >
            Recent Games
          </button>
        </div>

        <div className="tab-content">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default PlayerProfile; 