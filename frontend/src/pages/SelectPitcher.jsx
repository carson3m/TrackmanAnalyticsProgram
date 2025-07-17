import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS, FALLBACK_API_URL } from '../config';
import './SelectPitcher.css';

const SelectPitcher = () => {
  const [pitchers, setPitchers] = useState([]);
  const [selectedPitcher, setSelectedPitcher] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPitchers = async () => {
      const selectedTeam = sessionStorage.getItem('selectedTeam');
      if (!selectedTeam) {
        setError('No team selected. Please go back and select a team.');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `${API_ENDPOINTS.TEAM_PITCHERS}?team=${encodeURIComponent(selectedTeam)}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch pitchers');
        }

        const data = await response.json();
        setPitchers(data.pitchers || []);
      } catch (error) {
        console.error('Error fetching pitchers:', error);
        setError('Failed to load pitchers. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchPitchers();
  }, [token]);

  const handlePitcherSelect = (pitcher) => {
    setSelectedPitcher(pitcher);
  };

  const handleContinue = () => {
    if (selectedPitcher) {
      // Store selected pitcher for next page
      sessionStorage.setItem('selectedPitcher', selectedPitcher);
      navigate('/report');
    }
  };

  const handleBack = () => {
    navigate('/select-team');
  };

  const selectedTeam = sessionStorage.getItem('selectedTeam');

  if (loading) {
    return (
      <div className="select-container">
        <div className="select-card">
          <div className="loading">Loading pitchers...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="select-container">
      <div className="select-card">
        <div className="select-header">
          <h1>Select Pitcher</h1>
          <p>Choose a pitcher from {selectedTeam}</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        {pitchers.length > 0 && (
          <>
            <div className="pitchers-grid">
              {pitchers.map((pitcher, index) => (
                <div
                  key={index}
                  className={`pitcher-card ${selectedPitcher === pitcher ? 'selected' : ''}`}
                  onClick={() => handlePitcherSelect(pitcher)}
                >
                  <div className="pitcher-icon">🎯</div>
                  <h3>{pitcher}</h3>
                </div>
              ))}
            </div>

            <div className="select-actions">
              <button onClick={handleBack} className="secondary-button">
                Back to Team Selection
              </button>
              <button
                onClick={handleContinue}
                className="primary-button"
                disabled={!selectedPitcher}
              >
                View Report
              </button>
            </div>
          </>
        )}

        {pitchers.length === 0 && !error && (
          <div className="no-pitchers">
            <p>No pitchers found for {selectedTeam}.</p>
            <button onClick={handleBack} className="primary-button">
              Select Different Team
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SelectPitcher; 