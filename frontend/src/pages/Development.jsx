import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS } from '../config';
import './Development.css';

const Development = () => {
  const { user, token } = useAuth();
  const [developmentData, setDevelopmentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('overall');
  const [selectedTimeframe, setSelectedTimeframe] = useState('season');

  useEffect(() => {
    console.log('Development component mounted, fetching data...');
    fetchDevelopmentData();
  }, []);

  const fetchDevelopmentData = async () => {
    try {
      console.log('Starting fetchDevelopmentData...');
      setLoading(true);
      setError(null);
      
      const response = await fetch(API_ENDPOINTS.DEVELOPMENT_ANALYSIS, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Response received:', response.status, response.statusText);

      if (!response.ok) {
        if (response.status === 404) {
          // No data available - show helpful message instead of error
          setDevelopmentData({
            team_overview: {
              total_players: 0,
              pitchers: 0,
              batters: 0,
              overall_improvement_score: 0,
              key_areas: []
            },
            improvement_areas: [],
            player_insights: [],
            practice_recommendations: [],
            no_data: true
          });
          return;
        }
        
        const errorText = await response.text();
        console.error('Development API Error:', response.status, errorText);
        throw new Error(`Failed to fetch development data: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('Development data received:', data);
      setDevelopmentData(data);
    } catch (err) {
      console.error('Error in fetchDevelopmentData:', err);
      setError(err.message || 'Load failed');
    } finally {
      setLoading(false);
    }
  };

  const getMetricColor = (value, threshold) => {
    if (value >= threshold) return '#22c55e'; // Green for good
    if (value >= threshold * 0.8) return '#f59e0b'; // Yellow for needs improvement
    return '#dc2626'; // Red for needs significant work
  };

  const getImprovementPriority = (current, target) => {
    const gap = target - current;
    if (gap <= 0) return 'Maintain';
    if (gap <= target * 0.1) return 'Low Priority';
    if (gap <= target * 0.2) return 'Medium Priority';
    return 'High Priority';
  };

  if (loading) {
    return (
      <div className="development-container">
        <div className="loading-spinner">Loading development analysis...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="development-container">
        <div className="error-message">
          <h2>Error Loading Development Data</h2>
          <p>{error}</p>
          <button onClick={fetchDevelopmentData} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Mock data for demonstration - replace with actual API data
  const mockData = {
    team_overview: {
      total_players: 25,
      pitchers: 12,
      batters: 13,
      overall_improvement_score: 72,
      key_areas: ['Chase Rate', 'Command', 'Exit Velocity']
    },
    improvement_areas: [
      {
        metric: 'Chase Rate',
        current: 28.5,
        target: 22.0,
        priority: 'High',
        description: 'Reducing chase rate will improve on-base percentage',
        drills: ['Plate discipline drills', 'Zone recognition', 'Two-strike approach']
      },
      {
        metric: 'Command',
        current: 65.2,
        target: 70.0,
        priority: 'Medium',
        description: 'Improving command will reduce walks and increase strike percentage',
        drills: ['Bullpen sessions', 'Target practice', 'Mechanical adjustments']
      },
      {
        metric: 'Exit Velocity',
        current: 82.3,
        target: 88.0,
        priority: 'High',
        description: 'Higher exit velocity correlates with better hitting outcomes',
        drills: ['Strength training', 'Bat speed drills', 'Swing mechanics']
      },
      {
        metric: 'Spin Rate',
        current: 2100,
        target: 2300,
        priority: 'Medium',
        description: 'Higher spin rates create more movement and deception',
        drills: ['Grip adjustments', 'Release point work', 'Pitch-specific training']
      },
      {
        metric: 'First Pitch Strike %',
        current: 58.4,
        target: 65.0,
        priority: 'High',
        description: 'Getting ahead in counts improves overall pitching success',
        drills: ['First pitch mentality', 'Strike zone work', 'Confidence building']
      }
    ],
    player_insights: [
      {
        name: 'Johnny Alkire',
        position: 'Pitcher',
        top_strength: 'Velocity (92.3 mph)',
        improvement_area: 'Command (58% strikes)',
        recommendation: 'Focus on mechanical consistency and strike zone command'
      },
      {
        name: 'Connor Doucet',
        position: 'Batter',
        top_strength: 'Exit Velocity (89.2 mph)',
        improvement_area: 'Chase Rate (32%)',
        recommendation: 'Work on plate discipline and zone recognition'
      }
    ],
    practice_recommendations: [
      {
        category: 'Pitching',
        focus: 'Command & Control',
        drills: [
          'Bullpen sessions with target practice',
          'Mechanical video analysis',
          'Strike zone visualization drills'
        ],
        frequency: '3x per week',
        duration: '45 minutes'
      },
      {
        category: 'Hitting',
        focus: 'Plate Discipline',
        drills: [
          'Zone recognition drills',
          'Two-strike approach practice',
          'Pitch recognition training'
        ],
        frequency: '4x per week',
        duration: '30 minutes'
      }
    ]
  };

  // const data = mockData; // Replace with actual data when API is ready
  const data = developmentData || mockData; // Use API data if available, otherwise fallback to mock

  console.log('Rendering with data:', data);

  // Check if no data is available
  if (data.no_data) {
    return (
      <div className="development-container">
        <div className="development-header">
          <h1>Player Development Center</h1>
          <p>Identify improvement areas and get actionable training recommendations</p>
        </div>
        
        <div className="no-data-message">
          <div className="no-data-icon">📊</div>
          <h2>No Development Data Available</h2>
          <p>To see player development analysis, you'll need to upload some Trackman CSV files first.</p>
          <div className="no-data-actions">
            <button onClick={() => window.location.href = '/csv-management'} className="upload-button">
              Upload CSV Files
            </button>
            <button onClick={() => window.location.href = '/dashboard'} className="dashboard-button">
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="development-container">
      <div className="development-header">
        <h1>Player Development Center</h1>
        <p>Identify improvement areas and get actionable training recommendations</p>
      </div>

      {/* Team Overview */}
      <div className="overview-section">
        <h2>Team Development Overview</h2>
        <div className="overview-cards">
          <div className="overview-card">
            <div className="overview-icon">📊</div>
            <h3>Overall Improvement Score</h3>
            <div className="score-display">
              <span className="score-value">{data.team_overview.overall_improvement_score}</span>
              <span className="score-label">/ 100</span>
            </div>
            <p>Based on current performance vs. targets</p>
          </div>
          
          <div className="overview-card">
            <div className="overview-icon">🎯</div>
            <h3>Key Focus Areas</h3>
            <div className="focus-areas">
              {data.team_overview.key_areas.map((area, index) => (
                <span key={index} className="focus-tag">{area}</span>
              ))}
            </div>
          </div>
          
          <div className="overview-card">
            <div className="overview-icon">👥</div>
            <h3>Team Composition</h3>
            <div className="team-stats">
              <div className="stat-item">
                <span className="stat-label">Total Players:</span>
                <span className="stat-value">{data.team_overview.total_players}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Pitchers:</span>
                <span className="stat-value">{data.team_overview.pitchers}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Batters:</span>
                <span className="stat-value">{data.team_overview.batters}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Improvement Areas */}
      <div className="improvement-section">
        <h2>Priority Improvement Areas</h2>
        <div className="improvement-grid">
          {data.improvement_areas.map((area, index) => (
            <div key={index} className="improvement-card">
              <div className="improvement-header">
                <h3>{area.metric}</h3>
                <span className={`priority-badge ${area.priority.toLowerCase()}`}>
                  {area.priority} Priority
                </span>
              </div>
              
              <div className="metric-display">
                <div className="current-value">
                  <span className="value-label">Current:</span>
                  <span 
                    className="value-number"
                    style={{ color: getMetricColor(area.current, area.target) }}
                  >
                    {area.current}
                  </span>
                </div>
                <div className="target-value">
                  <span className="value-label">Target:</span>
                  <span className="value-number target">{area.target}</span>
                </div>
                <div className="gap-indicator">
                  <span className="gap-label">Gap:</span>
                  <span className="gap-value">
                    {Math.abs(area.target - area.current).toFixed(1)}
                  </span>
                </div>
              </div>
              
              <p className="improvement-description">{area.description}</p>
              
              <div className="drill-recommendations">
                <h4>Recommended Drills:</h4>
                <ul>
                  {area.drills.map((drill, drillIndex) => (
                    <li key={drillIndex}>{drill}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Individual Player Insights */}
      <div className="player-insights-section">
        <h2>Individual Player Insights</h2>
        <div className="player-insights-grid">
          {data.player_insights.map((player, index) => (
            <div key={index} className="player-insight-card">
              <div className="player-header">
                <h3>{player.name}</h3>
                <span className="position-badge">{player.position}</span>
              </div>
              
              <div className="player-metrics">
                <div className="strength-metric">
                  <span className="metric-label">Top Strength:</span>
                  <span className="metric-value strength">{player.top_strength}</span>
                </div>
                <div className="improvement-metric">
                  <span className="metric-label">Focus Area:</span>
                  <span className="metric-value improvement">{player.improvement_area}</span>
                </div>
              </div>
              
              <div className="player-recommendation">
                <h4>Recommendation:</h4>
                <p>{player.recommendation}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Practice Recommendations */}
      <div className="practice-section">
        <h2>Structured Practice Plans</h2>
        <div className="practice-grid">
          {data.practice_recommendations.map((plan, index) => (
            <div key={index} className="practice-card">
              <div className="practice-header">
                <h3>{plan.category}</h3>
                <span className="focus-badge">{plan.focus}</span>
              </div>
              
              <div className="practice-details">
                <div className="practice-info">
                  <div className="info-item">
                    <span className="info-label">Frequency:</span>
                    <span className="info-value">{plan.frequency}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Duration:</span>
                    <span className="info-value">{plan.duration}</span>
                  </div>
                </div>
                
                <div className="drill-list">
                  <h4>Key Drills:</h4>
                  <ul>
                    {plan.drills.map((drill, drillIndex) => (
                      <li key={drillIndex}>{drill}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Items */}
      <div className="action-section">
        <h2>Next Steps</h2>
        <div className="action-items">
          <div className="action-item">
            <div className="action-icon">📋</div>
            <div className="action-content">
              <h3>Create Practice Schedule</h3>
              <p>Implement the recommended practice plans into your weekly schedule</p>
            </div>
          </div>
          
          <div className="action-item">
            <div className="action-icon">📊</div>
            <div className="action-content">
              <h3>Track Progress</h3>
              <p>Monitor improvement in key metrics over the next 4-6 weeks</p>
            </div>
          </div>
          
          <div className="action-item">
            <div className="action-icon">🎯</div>
            <div className="action-content">
              <h3>Set Individual Goals</h3>
              <p>Work with each player to set specific, measurable improvement targets</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Development; 