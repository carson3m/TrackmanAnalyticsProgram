import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS } from '../config';
import './BestOfStats.css';

const BestOfStats = () => {
  const { token } = useAuth();
  const [csvFiles, setCsvFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [seasons, setSeasons] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState('all');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStoredCSVFiles();
  }, []);

  const fetchStoredCSVFiles = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.LIST_CSV_FILES, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        if (response.status === 401) {
          setError('Your session has expired. Please log out and log back in.');
          return;
        }
        throw new Error('Failed to fetch CSV files');
      }
      const data = await response.json();
      setCsvFiles(data);
      
      // Get available teams from the CSV data
      const teamsResponse = await fetch(`${API_ENDPOINTS.METRICS_BASE}/available-teams`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      if (teamsResponse.ok) {
        const teamsData = await teamsResponse.json();
        setTeams(teamsData.teams);
        console.log('Available teams from CSV data:', teamsData.teams);
      } else if (teamsResponse.status === 401) {
        setError('Your session has expired. Please log out and log back in.');
        return;
      } else {
        console.warn('Failed to get teams from CSV data, falling back to file metadata');
        // Fallback to team names from file metadata
        const uniqueTeams = Array.from(new Set(data.map(file => file.team_name).filter(Boolean)));
        setTeams(uniqueTeams);
      }
      
      const uniqueSeasons = Array.from(new Set(
        data.map(file => new Date(file.game_date || file.uploaded_at).getFullYear())
      )).sort((a, b) => b - a);
      setSeasons(uniqueSeasons);
    } catch (error) {
      console.error('Error fetching CSV files:', error);
      setError('Failed to load stored CSV files.');
    }
  };

  const handleFileToggle = (fileId) => {
    setSelectedFiles(prev => 
      prev.includes(fileId) 
        ? prev.filter(id => id !== fileId)
        : [...prev, fileId]
    );
    setError('');
    setStats(null);
  };

  const handleSelectAll = () => {
    setSelectedFiles(csvFiles.map(file => file.id));
    setError('');
    setStats(null);
  };

  const handleSelectNone = () => {
    setSelectedFiles([]);
    setError('');
    setStats(null);
  };

  const fetchBestOfStats = async () => {
    if (!selectedTeam) { setError('Please select a team first.'); return; }
    setLoading(true); setError(''); setStats(null);
    try {
      const response = await fetch(API_ENDPOINTS.METRICS_BEST_OF, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team: selectedTeam,
          season: selectedSeason,
          file_ids: selectedFiles.length > 0 ? selectedFiles : undefined
        }),
      });
      if (!response.ok) {
        if (response.status === 401) {
          setError('Your session has expired. Please log out and log back in.');
          return;
        }
        const errorData = await response.json(); 
        throw new Error(errorData.detail || 'Failed to fetch best of stats');
      }
      const data = await response.json();
      console.log('Best of stats data received:', data);
      console.log('Home runs data:', data.batting?.top_home_runs);
      setStats(data);
    } catch (error) {
      console.error('Error fetching best of stats:', error);
      setError('Failed to load best of stats. Please try again.');
    } finally { setLoading(false); }
  };

  const StatCard = ({ title, data, icon }) => {
    console.log(`StatCard ${title}:`, data);
    console.log(`StatCard ${title} data length:`, data?.length);
    return (
    <div className="stat-card">
      <div className="stat-header">
        <span className="stat-icon">{icon}</span>
        <h3>{title}</h3>
      </div>
      <div className="stat-content">
        {data && data.length > 0 ? (
          data.map((item, index) => (
            <div key={index} className="stat-item">
              <div className="stat-main">
                <span className="player-name">{item.player}</span>
                <span className="stat-value">
                  {item.value}
                  {item.unit && <span className="unit"> {item.unit}</span>}
                </span>
              </div>
              {item.pitch_type && (
                <div className="pitch-details">
                  <span className="pitch-type">{item.pitch_type}</span>
                  {item.date && <span className="pitch-date">{item.date}</span>}
                  {item.pitch_no && <span className="pitch-number">Pitch #{item.pitch_no}</span>}
                </div>
              )}
            </div>
          ))
        ) : (
          <p className="no-data">No data available</p>
        )}
      </div>
    </div>
  );
  };

  return (
    <div className="best-of-stats">
      <div className="stats-header">
        <h1>🏆 Best of Stats</h1>
        <p>Top performers across different metrics</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="controls-section">
        <div className="file-selection">
          <h3>Select CSV Files</h3>
          <div className="file-controls">
            <button onClick={handleSelectAll} className="select-btn">Select All</button>
            <button onClick={handleSelectNone} className="select-btn">Select None</button>
          </div>
          <div className="file-list">
            {csvFiles.map(file => (
              <label key={file.id} className="file-checkbox">
                                 <input
                   type="checkbox"
                   checked={selectedFiles.includes(file.id)}
                   onChange={() => handleFileToggle(file.id)}
                 />
                <span className="file-name">{file.original_filename}</span>
                <span className="file-date">
                  {new Date(file.game_date || file.uploaded_at).toLocaleDateString()}
                </span>
              </label>
            ))}
          </div>
          <p className="file-hint">
            {selectedFiles.length === 0 
              ? "All files will be used (no specific files selected)" 
              : `${selectedFiles.length} file(s) selected`
            }
          </p>
        </div>

        <div className="filter-controls">
          <div className="control-group">
            <label>Select Team:</label>
            <select 
              value={selectedTeam} 
              onChange={(e) => setSelectedTeam(e.target.value)}
            >
              <option value="">Choose a team...</option>
              {teams.map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label>Season:</label>
            <select 
              value={selectedSeason} 
              onChange={(e) => setSelectedSeason(e.target.value)}
            >
              <option value="all">All Seasons</option>
              {seasons.map(season => (
                <option key={season} value={season}>{season}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="action-buttons">
          <button 
            onClick={fetchBestOfStats} 
            disabled={loading || !selectedTeam}
            className="fetch-btn"
          >
            {loading ? 'Loading...' : 'Get Best of Stats'}
          </button>
        </div>
      </div>

      {stats && (
        <div className="stats-grid">
          <StatCard 
            title="Top Velocity" 
            data={stats.pitching?.top_velocity?.data} 
            icon="⚡"
          />
          <StatCard 
            title="Top Spin Rate" 
            data={stats.pitching?.top_spin_rate?.data} 
            icon="🌀"
          />
          <StatCard 
            title="Top Induced Vertical Break" 
            data={stats.pitching?.top_induced_vertical_break?.data} 
            icon="📈"
          />
          <StatCard 
            title="Top Horizontal Break" 
            data={stats.pitching?.top_horizontal_break?.data} 
            icon="↔️"
          />
          <StatCard 
            title="Top Total Break" 
            data={stats.pitching?.top_total_break?.data} 
            icon="🎯"
          />
          <StatCard 
            title="Top Exit Velocity" 
            data={stats.batting?.top_exit_velocity?.data} 
            icon="💥"
          />
          <StatCard 
            title="Top Home Runs" 
            data={stats.batting?.top_home_runs?.data} 
            icon="🏠"
          />
        </div>
      )}

      <div className="navigation">
        <button onClick={() => window.history.back()} className="back-btn">
          Back to Dashboard
        </button>
      </div>
    </div>
  );
};

export default BestOfStats; 