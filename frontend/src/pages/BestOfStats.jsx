import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS } from '../config';
import './BestOfStats.css';
import Papa from 'papaparse';

const BestOfStats = () => {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [timePeriod, setTimePeriod] = useState('all');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [files, setFiles] = useState([]);
  const [parsing, setParsing] = useState(false);
  const { token } = useAuth();
  const navigate = useNavigate();

  // Parse CSVs and extract unique teams
  const handleFileChange = (e) => {
    setError('');
    setStats(null);
    setSelectedTeam('');
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    if (selectedFiles.length === 0) {
      setTeams([]);
      return;
    }
    setParsing(true);
    let allRows = [];
    let filesParsed = 0;
    selectedFiles.forEach((file) => {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          allRows = allRows.concat(results.data);
          filesParsed++;
          if (filesParsed === selectedFiles.length) {
            // Extract unique teams
            const uniqueTeams = Array.from(new Set(allRows.map(row => row.PitcherTeam).filter(Boolean)));
            setTeams(uniqueTeams);
            setParsing(false);
            if (uniqueTeams.length === 0) {
              setError('No teams found in the selected files.');
            }
          }
        },
        error: (err) => {
          setError('Failed to parse one or more files.');
          setParsing(false);
        }
      });
    });
  };

  const fetchBestOfStats = async () => {
    if (!selectedTeam) {
      setError('Please select a team first.');
      return;
    }
    if (files.length === 0) {
      setError('Please select at least one CSV file.');
      return;
    }
    setLoading(true);
    setError('');
    setStats(null);

    // Send files to backend for stat computation
    const formData = new FormData();
    files.forEach((file, idx) => {
      formData.append('files', file);
    });
    formData.append('team', selectedTeam);
    formData.append('time_period', timePeriod);

    try {
      const response = await fetch(API_ENDPOINTS.METRICS_BEST_OF, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch best of stats');
      }

      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching best of stats:', error);
      setError('Failed to load best of stats. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const StatCard = ({ title, data, error }) => {
    if (error) {
      return (
        <div className="stat-card error">
          <h3>{title}</h3>
          <p className="error-message">{error}</p>
        </div>
      );
    }

    if (!data || data.length === 0) {
      return (
        <div className="stat-card">
          <h3>{title}</h3>
          <p>No data available</p>
        </div>
      );
    }

    return (
      <div className="stat-card">
        <h3>{title}</h3>
        <div className="stat-list">
          {data.map((item, index) => (
            <div key={index} className="stat-item">
              <span className="player-name">{item.player}</span>
              <span className="stat-value">
                {item.value}{item.unit ? ` ${item.unit}` : ''}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="best-of-container">
      <div className="best-of-card">
        <div className="best-of-header">
          <h1>🏆 Best of Stats</h1>
          <p>Top performers across different metrics</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="controls-section">
          <div className="control-group">
            <label htmlFor="csv-files">Select CSV File(s):</label>
            <input
              id="csv-files"
              type="file"
              accept=".csv"
              multiple
              onChange={handleFileChange}
              disabled={loading || parsing}
            />
            {parsing && <span className="parsing-message">Parsing files...</span>}
          </div>
          <div className="control-group">
            <label htmlFor="team-select">Select Team:</label>
            <select
              id="team-select"
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
              className="team-select"
              disabled={teams.length === 0 || parsing}
            >
              <option value="">Choose a team...</option>
              {teams.map((team, index) => (
                <option key={index} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label htmlFor="time-period">Time Period:</label>
            <select
              id="time-period"
              value={timePeriod}
              onChange={(e) => setTimePeriod(e.target.value)}
              className="time-select"
            >
              <option value="all">All Time</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="season">This Season</option>
            </select>
          </div>

          <button
            onClick={fetchBestOfStats}
            disabled={!selectedTeam || loading || files.length === 0}
            className="fetch-button"
          >
            {loading ? 'Loading...' : 'Get Best of Stats'}
          </button>
        </div>

        {stats && (
          <div className="stats-section">
            <div className="stats-header">
              <h2>🏟️ {stats.team} - Best of {stats.time_period}</h2>
            </div>

            <div className="stats-grid">
              <div className="pitching-stats">
                <h3>⚾ Pitching Stats</h3>
                {stats.pitching_stats.map((stat, index) => (
                  <StatCard
                    key={index}
                    title={stat.label}
                    data={stat.data}
                    error={stat.error}
                  />
                ))}
              </div>

              <div className="hitting-stats">
                <h3>💥 Hitting Stats</h3>
                {stats.hitting_stats.map((stat, index) => (
                  <StatCard
                    key={index}
                    title={stat.label}
                    data={stat.data}
                    error={stat.error}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="best-of-actions">
          <button onClick={handleBackToDashboard} className="secondary-button">
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default BestOfStats; 