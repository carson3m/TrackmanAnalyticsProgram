import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS } from '../config';
import './RosterManagement.css';

const RosterManagement = () => {
  const [roster, setRoster] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('all');
  const { token, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchRoster();
  }, []);

  const fetchRoster = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.TEAM_ROSTER, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch roster');
      }

      const data = await response.json();
      setRoster(data);
    } catch (error) {
      console.error('Error fetching roster:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const StatCard = ({ title, value, color = 'primary' }) => {
    const getCardStyle = () => {
      switch (color) {
        case 'primary':
          return {
            background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)',
            color: 'white',
            padding: '28px 24px',
            borderRadius: '12px',
            textAlign: 'center',
            boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)',
            transition: 'transform 0.2s ease',
            position: 'relative',
            overflow: 'hidden'
          };
        case 'warning':
          return {
            background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)',
            color: 'white',
            padding: '28px 24px',
            borderRadius: '12px',
            textAlign: 'center',
            boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)',
            transition: 'transform 0.2s ease',
            position: 'relative',
            overflow: 'hidden'
          };
        case 'success':
          return {
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            color: '#1e3a8a',
            padding: '28px 24px',
            borderRadius: '12px',
            textAlign: 'center',
            boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)',
            transition: 'transform 0.2s ease',
            position: 'relative',
            overflow: 'hidden',
            border: '2px solid #1e3a8a'
          };
        default:
          return {};
      }
    };

    const getTitleStyle = () => ({
      fontSize: '1rem',
      fontWeight: '600',
      margin: '0 0 8px 0',
      color: color === 'success' ? '#1e3a8a' : 'rgba(255, 255, 255, 0.95)',
      textShadow: color === 'success' ? 'none' : '0 1px 2px rgba(0, 0, 0, 0.1)',
      position: 'relative',
      zIndex: 1
    });

    const getValueStyle = () => ({
      fontSize: '2.5rem',
      fontWeight: '800',
      margin: '0',
      color: color === 'success' ? '#1e3a8a' : 'white',
      textShadow: color === 'success' ? 'none' : '0 2px 4px rgba(0, 0, 0, 0.2)',
      position: 'relative',
      zIndex: 1
    });

    return (
      <div style={getCardStyle()}>
        <h3 style={getTitleStyle()}>{title}</h3>
        <div style={getValueStyle()}>{value}</div>
      </div>
    );
  };

  const PlayerCard = ({ player, type }) => {
    // Determine the actual player type based on which roster list they belong to
    const getPlayerType = () => {
      if (roster.pitchers && roster.pitchers.includes(player)) {
        return 'pitcher';
      } else if (roster.batters && roster.batters.includes(player)) {
        return 'batter';
      } else {
        // Fallback to the tab type if we can't determine
        return type === 'pitchers' ? 'pitcher' : type === 'batters' ? 'batter' : 'all';
      }
    };

    const getPlayerTypeStyle = (type) => {
      switch (type) {
        case 'pitcher':
          return {
            background: 'linear-gradient(135deg, #dc2626, #b91c1c)',
            color: 'white',
            border: '1px solid #dc2626',
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '0.8rem',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          };
        case 'batter':
          return {
            background: 'linear-gradient(135deg, #ffffff, #f8fafc)',
            color: '#1e3a8a',
            border: '1px solid #1e3a8a',
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '0.8rem',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          };
        default:
          return {
            background: 'linear-gradient(135deg, #1e3a8a, #1e40af)',
            color: 'white',
            border: '1px solid #1e3a8a',
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '0.8rem',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          };
      }
    };

    const playerType = getPlayerType();

    return (
      <div 
        className="player-card clickable"
        onClick={() => navigate(`/player-profile/${encodeURIComponent(player)}/${playerType}`)}
        style={{ cursor: 'pointer' }}
      >
        <div className="player-info">
          <h4>{player}</h4>
          <span style={getPlayerTypeStyle(playerType)}>{playerType}</span>
        </div>
        <div className="player-arrow">→</div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="roster-container">
        <div className="roster-card">
          <div className="loading">Loading roster...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="roster-container">
        <div className="roster-card">
          <div className="error-message">{error}</div>
          <button onClick={handleBackToDashboard} className="secondary-button">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!roster) {
    return (
      <div className="roster-container">
        <div className="roster-card">
          <div className="error-message">No roster data available</div>
          <button onClick={handleBackToDashboard} className="secondary-button">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const renderPlayers = (players, type) => {
    if (!players || players.length === 0) {
      return <p className="no-players">No {type} found</p>;
    }

    return (
      <div className="players-grid">
        {players.map((player, index) => (
          <PlayerCard key={index} player={player} type={type} />
        ))}
      </div>
    );
  };

  // Get deduplicated counts for stat cards
  const getDeduplicatedCounts = () => {
    const pitchers = roster.pitchers || [];
    const batters = roster.batters || [];
    const allPlayers = roster.all_players || [];
    
    const deduplicatedPitchers = deduplicatePlayers(pitchers);
    const deduplicatedBatters = deduplicatePlayers(batters);
    const deduplicatedAll = deduplicatePlayers(allPlayers);
    
    return {
      pitchers: deduplicatedPitchers.length,
      batters: deduplicatedBatters.length,
      all: deduplicatedAll.length
    };
  };

  // Function to calculate similarity between two names
  const calculateNameSimilarity = (name1, name2) => {
    const normalizeName = (name) => name.toLowerCase().replace(/[^a-z\s]/g, '').trim();
    const n1 = normalizeName(name1);
    const n2 = normalizeName(name2);
    
    // If names are identical after normalization, they're the same
    if (n1 === n2) return 1.0;
    
    // Handle common variations more aggressively
    const variations1 = generateNameVariations(n1);
    const variations2 = generateNameVariations(n2);
    
    // Check if any variations match
    for (const v1 of variations1) {
      for (const v2 of variations2) {
        if (v1 === v2) return 0.95; // High similarity for variation matches
      }
    }
    
    // Split into parts and compare
    const parts1 = n1.split(/\s+/);
    const parts2 = n2.split(/\s+/);
    
    // If both have same number of parts, compare each part
    if (parts1.length === parts2.length) {
      let matches = 0;
      for (let i = 0; i < parts1.length; i++) {
        if (parts1[i] === parts2[i]) {
          matches++;
        } else {
          // Check for common typos/variations with lower threshold
          const similarity = calculateStringSimilarity(parts1[i], parts2[i]);
          if (similarity > 0.7) matches++; // Lowered from 0.8
        }
      }
      return matches / parts1.length;
    }
    
    // If different number of parts, try to match longest parts
    const longer = parts1.length > parts2.length ? parts1 : parts2;
    const shorter = parts1.length > parts2.length ? parts2 : parts1;
    
    let bestMatch = 0;
    for (let i = 0; i <= longer.length - shorter.length; i++) {
      let matches = 0;
      for (let j = 0; j < shorter.length; j++) {
        if (longer[i + j] === shorter[j]) {
          matches++;
        } else {
          const similarity = calculateStringSimilarity(longer[i + j], shorter[j]);
          if (similarity > 0.7) matches++; // Lowered from 0.8
        }
      }
      const currentMatch = matches / shorter.length;
      if (currentMatch > bestMatch) bestMatch = currentMatch;
    }
    
    return bestMatch;
  };

  // Function to generate common name variations
  const generateNameVariations = (name) => {
    const variations = [name];
    
    // Common name variations
    const nameMap = {
      'john': ['johnny', 'jon', 'jonny'],
      'johnny': ['john', 'jon', 'jonny'],
      'jon': ['john', 'johnny', 'jonny'],
      'jonny': ['john', 'johnny', 'jon'],
      'josh': ['joshua'],
      'joshua': ['josh'],
      'ken': ['kenan', 'kenneth'],
      'kenan': ['ken', 'kenneth'],
      'kenneth': ['ken', 'kenan'],
      'connor': ['conner'],
      'conner': ['connor'],
      'tanner': ['tanar'],
      'tanar': ['tanner'],
      'evan': ['even'],
      'even': ['evan'],
      'dawson': ['dawsonl'],
      'dawsonl': ['dawson'],
      'williams': ['william'],
      'william': ['williams']
    };
    
    const parts = name.split(/\s+/);
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      if (nameMap[part]) {
        for (const variation of nameMap[part]) {
          const newParts = [...parts];
          newParts[i] = variation;
          variations.push(newParts.join(' '));
        }
      }
    }
    
    return variations;
  };

  // Function to calculate string similarity (Levenshtein distance based)
  const calculateStringSimilarity = (str1, str2) => {
    if (str1 === str2) return 1.0;
    if (str1.length === 0) return str2.length === 0 ? 1.0 : 0.0;
    if (str2.length === 0) return 0.0;
    
    const matrix = [];
    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i];
    }
    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j;
    }
    
    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    
    const maxLength = Math.max(str1.length, str2.length);
    return 1 - (matrix[str2.length][str1.length] / maxLength);
  };

  // Function to deduplicate players based on name similarity
  const deduplicatePlayers = (players) => {
    if (!players || players.length === 0) return [];
    
    console.log('DEBUG: Starting deduplication with', players.length, 'players');
    console.log('DEBUG: Original players:', players);
    
    const deduplicated = [];
    const processed = new Set();
    
    for (let i = 0; i < players.length; i++) {
      if (processed.has(i)) continue;
      
      const currentPlayer = players[i];
      const similarPlayers = [currentPlayer];
      processed.add(i);
      
      // Find similar players
      for (let j = i + 1; j < players.length; j++) {
        if (processed.has(j)) continue;
        
        const similarity = calculateNameSimilarity(currentPlayer, players[j]);
        console.log(`DEBUG: Comparing "${currentPlayer}" vs "${players[j]}" - similarity: ${similarity.toFixed(3)}`);
        
        if (similarity > 0.75) { // Lowered threshold from 0.85 to 0.75
          similarPlayers.push(players[j]);
          processed.add(j);
          console.log(`DEBUG: MERGED "${players[j]}" into "${currentPlayer}" (similarity: ${similarity.toFixed(3)})`);
        }
      }
      
      // Choose the best name (most complete, least typos)
      let bestName = currentPlayer;
      let bestScore = scoreNameQuality(currentPlayer);
      
      for (const player of similarPlayers) {
        const playerScore = scoreNameQuality(player);
        console.log(`DEBUG: Name quality - "${player}": ${playerScore}, "${bestName}": ${bestScore}`);
        if (playerScore > bestScore) {
          bestName = player;
          bestScore = playerScore;
        }
      }
      
      deduplicated.push(bestName);
      console.log(`DEBUG: Final name chosen: "${bestName}" from group: [${similarPlayers.join(', ')}]`);
    }
    
    console.log('DEBUG: Deduplication complete. Final count:', deduplicated.length);
    console.log('DEBUG: Deduplicated players:', deduplicated);
    
    return deduplicated;
  };

  // Function to score name quality (prefer properly formatted names)
  const scoreNameQuality = (name) => {
    let score = 0;
    
    // Prefer names with proper capitalization
    if (name.match(/^[A-Z][a-z]+,\s[A-Z][a-z]+$/)) score += 3;
    else if (name.match(/^[A-Z][a-z]+,\s[A-Z]/)) score += 2;
    else if (name.match(/^[A-Z]/)) score += 1;
    
    // Prefer names without numbers or special characters
    if (!name.match(/[0-9]/)) score += 2;
    if (!name.match(/[^A-Za-z\s,]/)) score += 1;
    
    // Prefer longer names (more complete)
    score += name.length * 0.1;
    
    return score;
  };

  const getFilteredPlayers = () => {
    let players = [];
    switch (activeTab) {
      case 'pitchers':
        players = roster.pitchers || [];
        break;
      case 'batters':
        players = roster.batters || [];
        break;
      case 'all':
      default:
        players = roster.all_players || [];
        break;
    }
    
    // Deduplicate players first, then sort alphabetically
    const deduplicatedPlayers = deduplicatePlayers(players);
    return deduplicatedPlayers.sort((a, b) => a.localeCompare(b));
  };

  return (
    <div className="roster-container">
      <div className="roster-card">
        <div className="roster-header">
          <h1>👥 Team Roster</h1>
          <p>Manage your team's players and view roster information</p>
        </div>

        {roster && (
          <div className="stats-section">
            <h2>📊 Roster Statistics</h2>
            <div className="stats-grid">
              <StatCard title="Total Players" value={getDeduplicatedCounts().all} color="primary" />
              <StatCard title="Pitchers" value={getDeduplicatedCounts().pitchers} color="warning" />
              <StatCard title="Batters" value={getDeduplicatedCounts().batters} color="success" />
            </div>
          </div>
        )}

        <div className="roster-content">
          <div className="tab-navigation">
            <button
              className={`tab-button ${activeTab === 'all' ? 'active' : ''}`}
              onClick={() => setActiveTab('all')}
            >
              All Players ({getDeduplicatedCounts().all})
            </button>
            <button
              className={`tab-button ${activeTab === 'pitchers' ? 'active' : ''}`}
              onClick={() => setActiveTab('pitchers')}
            >
              Pitchers ({getDeduplicatedCounts().pitchers})
            </button>
            <button
              className={`tab-button ${activeTab === 'batters' ? 'active' : ''}`}
              onClick={() => setActiveTab('batters')}
            >
              Batters ({getDeduplicatedCounts().batters})
            </button>
          </div>

          <div className="players-section">
            <h3>
              {activeTab === 'all' && 'All Players'}
              {activeTab === 'pitchers' && 'Pitchers'}
              {activeTab === 'batters' && 'Batters'}
            </h3>
            {renderPlayers(getFilteredPlayers(), activeTab)}
          </div>
        </div>

        <div className="roster-actions">
          <button onClick={handleBackToDashboard} className="secondary-button">
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default RosterManagement; 