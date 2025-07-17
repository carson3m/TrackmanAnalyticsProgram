import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './SelectTeam.css';

const SelectTeam = () => {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Get teams from sessionStorage (set during upload)
    const storedTeams = sessionStorage.getItem('teams');
    if (storedTeams) {
      setTeams(JSON.parse(storedTeams));
    } else {
      setError('No teams found. Please upload a CSV file first.');
    }
    setLoading(false);
  }, []);

  const handleTeamSelect = (team) => {
    setSelectedTeam(team);
  };

  const handleContinue = () => {
    if (selectedTeam) {
      // Store selected team for next page
      sessionStorage.setItem('selectedTeam', selectedTeam);
      navigate('/select-pitcher');
    }
  };

  const handleBack = () => {
    navigate('/upload');
  };

  if (loading) {
    return (
      <div className="select-container">
        <div className="select-card">
          <div className="loading">Loading teams...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="select-container">
      <div className="select-card">
        <div className="select-header">
          <h1>Select Team</h1>
          <p>Choose a team from your uploaded data</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        {teams.length > 0 && (
          <>
            <div className="teams-grid">
              {teams.map((team, index) => (
                <div
                  key={index}
                  className={`team-card ${selectedTeam === team ? 'selected' : ''}`}
                  onClick={() => handleTeamSelect(team)}
                >
                  <div className="team-icon">⚾</div>
                  <h3>{team}</h3>
                </div>
              ))}
            </div>

            <div className="select-actions">
              <button onClick={handleBack} className="secondary-button">
                Back to Upload
              </button>
              <button
                onClick={handleContinue}
                className="primary-button"
                disabled={!selectedTeam}
              >
                Continue to Pitcher Selection
              </button>
            </div>
          </>
        )}

        {teams.length === 0 && !error && (
          <div className="no-teams">
            <p>No teams found in the uploaded data.</p>
            <button onClick={handleBack} className="primary-button">
              Upload Different File
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SelectTeam; 