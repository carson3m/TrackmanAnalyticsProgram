import React, { useState } from 'react';
import Papa from 'papaparse';
import './SocialMediaGenerator.css';
import { API_ENDPOINTS } from '../config';

const DEFAULT_STATS = [
  'Exit Velocity',
  'Pitch Speed',
  'Strikeouts',
  'Home Runs',
  'Spin Rate',
  'Batting Average',
  'Innings Pitched',
  'Custom Stat',
];

const MODES = [
  { value: 'topN', label: 'Top N List' },
  { value: 'profile', label: 'Player Profile' },
];

const RECOMMENDED_STATS = [
  { label: 'Exit Velocity', column: 'ExitSpeed' },
  { label: 'Pitch Speed', column: 'RelSpeed' },
  { label: 'Spin Rate', column: 'SpinRate' },
  { label: 'Home Runs', column: 'PlayResult' },
  { label: 'Strikeouts', column: 'KorBB' },
  { label: 'Innings Pitched', column: 'Inning' },
  { label: 'Balls', column: 'Balls' },
  { label: 'Strikes', column: 'Strikes' },
  { label: 'Pitch Type', column: 'AutoPitchType' },
  { label: 'Batter', column: 'Batter' },
  { label: 'Pitcher', column: 'Pitcher' },
  { label: 'Distance', column: 'Distance' },
  { label: 'Angle', column: 'Angle' },
  { label: 'Direction', column: 'Direction' },
];

// Curated extended list (add more as needed, but exclude technical/ID/trajectory columns)
const EXTENDED_STATS = [
  ...RECOMMENDED_STATS,
  { label: 'Date', column: 'Date' },
  { label: 'Time', column: 'Time' },
  { label: 'Pitch Call', column: 'PitchCall' },
  { label: 'Play Result', column: 'PlayResult' },
  { label: 'Tagged Pitch Type', column: 'TaggedPitchType' },
  { label: 'Tagged Hit Type', column: 'TaggedHitType' },
  { label: 'Vert Break', column: 'VertBreak' },
  { label: 'Induced Vert Break', column: 'InducedVertBreak' },
  { label: 'Horz Break', column: 'HorzBreak' },
  { label: 'PlateLocHeight', column: 'PlateLocHeight' },
  { label: 'PlateLocSide', column: 'PlateLocSide' },
  { label: 'Zone Speed', column: 'ZoneSpeed' },
  { label: 'Hit Spin Rate', column: 'HitSpinRate' },
  { label: 'Max Height', column: 'MaxHeight' },
  { label: 'Hang Time', column: 'HangTime' },
  { label: 'Stadium', column: 'Stadium' },
  { label: 'Level', column: 'Level' },
  { label: 'League', column: 'League' },
  // ...add more as needed, but keep it under 60
];

// Stat definitions
const PITCHER_STATS = [
  { label: 'Pitch Speed', column: 'RelSpeed', auto: true },
  { label: 'Spin Rate', column: 'SpinRate', auto: true },
  { label: 'Innings Pitched', column: 'Inning', auto: false },
  { label: 'Strikeouts', column: 'KorBB', auto: false },
  { label: 'Pitch Type', column: 'AutoPitchType', auto: false },
  { label: 'Distance', column: 'Distance', auto: true },
];
const BATTER_STATS = [
  { label: 'Exit Velocity', column: 'ExitSpeed', auto: true },
  { label: 'Home Runs', column: 'PlayResult', auto: false },
  { label: 'Batting Average', column: 'BattingAverage', auto: false },
  { label: 'Distance', column: 'Distance', auto: true },
];
const SHARED_STATS = [
  { label: 'Spin Rate', column: 'SpinRate', auto: true },
  { label: 'Pitch Speed', column: 'RelSpeed', auto: true },
  { label: 'Exit Velocity', column: 'ExitSpeed', auto: true },
  { label: 'Distance', column: 'Distance', auto: true },
];

const SocialMediaGenerator = () => {
  const [mode, setMode] = useState('topN');
  const [csvData, setCsvData] = useState(null);
  const [columns, setColumns] = useState([]);
  const [fileName, setFileName] = useState('');
  const [manualStats, setManualStats] = useState([{ stat: '', value: '' }]);
  const [selectedStat, setSelectedStat] = useState('Exit Velocity');
  const [topN, setTopN] = useState(5);
  const [team, setTeam] = useState('');
  const [player, setPlayer] = useState('');
  const [players, setPlayers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [timeFrame, setTimeFrame] = useState('all');
  const [logo, setLogo] = useState(null);
  const [accentColor, setAccentColor] = useState('');
  const [aspect, setAspect] = useState('square');
  const [hashtag, setHashtag] = useState('');
  const [customStat, setCustomStat] = useState('');
  const [showAllStats, setShowAllStats] = useState(false);
  const [profileType, setProfileType] = useState('pitcher'); // 'pitcher' or 'batter'
  const [batters, setBatters] = useState([]);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [playerImage, setPlayerImage] = useState(null);
  const [logoFile, setLogoFile] = useState(null);
  const [formDataDebug, setFormDataDebug] = useState('');
  const [selectedStats, setSelectedStats] = useState([]); // [{label, column, manualValue}]
  // Add to state
  const [customStatLabel, setCustomStatLabel] = useState('');
  const [customStatValue, setCustomStatValue] = useState('');
  const [validationErrors, setValidationErrors] = useState({});

  // CSV upload and parsing
  const handleCsvUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(file.name);
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        setCsvData(results.data);
        setColumns(Object.keys(results.data[0] || {}));
        // Extract teams and players for dropdowns
        const uniqueTeams = Array.from(new Set(results.data.map(row => row.PitcherTeam || row.Team).filter(Boolean)));
        setTeams(uniqueTeams);
        const uniquePitchers = Array.from(new Set(results.data.map(row => row.Pitcher).filter(Boolean)));
        setPlayers(uniquePitchers);
        const uniqueBatters = Array.from(new Set(results.data.map(row => row.Batter).filter(Boolean)));
        setBatters(uniqueBatters);
      },
      error: () => {
        setCsvData(null);
        setColumns([]);
        setTeams([]);
        setPlayers([]);
      },
    });
  };

  // Logo upload
  const handleLogoUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    // Only allow image files
    if (!file.type.startsWith('image/')) {
      alert('Please upload a valid image file for the logo (PNG, JPG, etc.)');
      return;
    }
    setLogoFile(file);
    setLogo(URL.createObjectURL(file));
  };

  // Player image upload
  const handlePlayerImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    // Only allow image files
    if (!file.type.startsWith('image/')) {
      alert('Please upload a valid image file for the player image (PNG, JPG, etc.)');
      return;
    }
    setPlayerImage(file);
  };

  // Manual stat entry for fallback
  const handleManualStatChange = (idx, field, value) => {
    setManualStats((prev) => {
      const updated = [...prev];
      updated[idx][field] = value;
      return updated;
    });
  };
  const addManualStat = () => setManualStats([...manualStats, { stat: '', value: '' }]);
  const removeManualStat = (idx) => setManualStats(manualStats.filter((_, i) => i !== idx));

  // Helper to get highest value from CSV for a stat/column
  const getMaxStatValue = (column) => {
    if (!csvData || !player) return '';
    const playerRows = csvData.filter(row => row.Pitcher === player || row.Batter === player);
    const values = playerRows.map(row => parseFloat(row[column])).filter(v => !isNaN(v));
    if (!values.length) return '';
    return Math.max(...values).toFixed(2);
  };

  // Helper to check if a stat requires manual entry and is missing
  const isManualRequiredAndMissing = (stat) => {
    return !stat.auto && (!stat.manualValue || stat.manualValue.trim() === '');
  };

  // Instead of demo: hardcoded stat labels/values, use selected and manual stats
  let statLabels = [];
  let statValues = [];
  if (mode === 'topN') {
    statLabels = [selectedStat === 'custom' ? customStat : selectedStat];
    statValues = [manualStats[0]?.value || ''];
  } else if (mode === 'profile') {
    statLabels = selectedStats.map(s => s.label);
    statValues = selectedStats.map(s => s.manualValue || (s.auto ? getMaxStatValue(s.column) : ''));
  }

  // When generating, validate required manual fields
  const handleGenerate = async () => {
    // Validation: require at least one stat label and value
    if (!statLabels.length || !statValues.length || statLabels.some(l => !l) || statValues.some(v => !v)) {
      alert('Please enter at least one stat and value before generating.');
      return;
    }
    setGenerating(true);
    setGeneratedImage(null);
    const formData = new FormData();
    // Title and subtitle logic
    let title = mode === 'topN' ? 'DATA ROUNDUP' : `${profileType === 'pitcher' ? 'Pitcher' : 'Batter'} Profile`;
    let subtitle = '';
    if (mode === 'topN') {
      subtitle = `${selectedStat === 'custom' ? customStat : selectedStat} Leader`;
    } else if (mode === 'profile') {
      subtitle = player;
    }
    formData.append('mode', mode);
    formData.append('title', title);
    formData.append('subtitle', subtitle);
    formData.append('accent_color', accentColor);
    formData.append('aspect', aspect);
    if (hashtag) formData.append('hashtag', hashtag);
    if (logoFile) formData.append('logo', logoFile);
    if (playerImage) formData.append('player_image', playerImage);
    // Add selected stats
    statLabels.forEach(label => formData.append('stat_labels', label));
    statValues.forEach(value => formData.append('stat_values', value));
    try {
      const resp = await fetch(API_ENDPOINTS.SOCIAL_GENERATE_GRAPHIC, {
        method: 'POST',
        body: formData,
      });
      if (resp.ok) {
        const blob = await resp.blob();
        setGeneratedImage(URL.createObjectURL(blob));
      } else {
        const errorText = await resp.text();
        alert('Error generating graphic: ' + errorText);
      }
    } catch (err) {
      alert('Error generating graphic: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  // UI
  return (
    <div className="smg-container">
      <h1>📱 Social Media Generator</h1>
      <p>Create a shareable stat graphic for your team or player!</p>

      {/* Mode selection */}
      <div className="smg-section">
        <label>Mode:</label>
        <select value={mode} onChange={e => setMode(e.target.value)}>
          {MODES.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
        </select>
      </div>

      {/* CSV upload */}
      <div className="smg-section">
        <label>Upload CSV (optional):</label>
        <input type="file" accept=".csv" onChange={handleCsvUpload} />
        {fileName && <span className="smg-filename">{fileName}</span>}
      </div>

      {/* Stat/category selection */}
      {mode === 'topN' && (
        <>
          <div className="smg-section">
            <label>Stat Category:</label>
            <select value={selectedStat} onChange={e => setSelectedStat(e.target.value)}>
              {(showAllStats ? EXTENDED_STATS : RECOMMENDED_STATS).map(stat => (
                columns.includes(stat.column) && (
                  <option key={stat.column} value={stat.column}>{stat.label}</option>
                )
              ))}
              <option value="custom">Custom Stat</option>
            </select>
            {selectedStat === 'custom' && (
              <input
                type="text"
                placeholder="Enter custom stat name"
                value={customStat}
                onChange={e => setCustomStat(e.target.value)}
                style={{ marginLeft: '0.5rem' }}
              />
            )}
            <button type="button" onClick={() => setShowAllStats(s => !s)} style={{ marginLeft: '1rem' }}>
              {showAllStats ? 'Show Recommended' : 'Show All Stats'}
            </button>
          </div>
          <div className="smg-section">
            <label>Top N:</label>
            <input type="number" min={1} max={20} value={topN} onChange={e => setTopN(Number(e.target.value))} style={{ width: '60px' }} />
          </div>
          <div className="smg-section">
            <label>Team:</label>
            <select value={team} onChange={e => setTeam(e.target.value)}>
              <option value="">All Teams</option>
              {teams.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="smg-section">
            <label>Time Frame:</label>
            <select value={timeFrame} onChange={e => setTimeFrame(e.target.value)}>
              <option value="all">All Time</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="season">This Season</option>
              <option value="custom">Custom</option>
            </select>
          </div>
        </>
      )}

      {mode === 'profile' && (
        <>
          <div className="smg-section">
            <label>Profile Type:</label>
            <select value={profileType} onChange={e => { setProfileType(e.target.value); setSelectedStats([]); }}>
              <option value="pitcher">Pitcher</option>
              <option value="batter">Batter</option>
            </select>
          </div>
          <div className="smg-section">
            <label>{profileType === 'pitcher' ? 'Pitcher' : 'Batter'}:</label>
            <select value={player} onChange={e => setPlayer(e.target.value)}>
              <option value="">Select {profileType === 'pitcher' ? 'Pitcher' : 'Batter'}</option>
              {(profileType === 'pitcher' ? players : batters).map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div className="smg-section">
            <label>Stats to Display:</label>
            {((profileType === 'pitcher' ? PITCHER_STATS : BATTER_STATS).concat(SHARED_STATS.filter(s => !(profileType === 'pitcher' ? PITCHER_STATS : BATTER_STATS).some(ps => ps.column === s.column)))).map(stat => {
              const selected = selectedStats.find(s => s.column === stat.column);
              const error = validationErrors[stat.column];
              return (
                <div key={stat.column} style={{ display: 'inline-block', marginRight: '1rem', marginBottom: '0.5rem' }}>
                  <input
                    type="checkbox"
                    id={`stat-${stat.column}`}
                    checked={!!selected}
                    onChange={e => {
                      if (e.target.checked) {
                        setSelectedStats([...selectedStats, { ...stat, manualValue: '' }]);
                      } else {
                        setSelectedStats(selectedStats.filter(s => s.column !== stat.column));
                      }
                    }}
                  />
                  <label htmlFor={`stat-${stat.column}`}>{stat.label}</label>
                  {selected && (
                    <span title={stat.auto ? 'Leave blank to use highest value from CSV' : 'Manual entry required'} style={{ marginLeft: 4, color: stat.auto ? '#888' : '#d00', fontWeight: stat.auto ? 'normal' : 'bold' }}>
                      {stat.auto ? '(auto or manual)' : '*'}
                    </span>
                  )}
                  {selected && (
                    <input
                      type="text"
                      placeholder={stat.auto ? `Auto: ${getMaxStatValue(stat.column)}` : 'Manual entry required'}
                      value={selected.manualValue || ''}
                      onChange={e => {
                        setSelectedStats(selectedStats.map(s =>
                          s.column === stat.column ? { ...s, manualValue: e.target.value } : s
                        ));
                      }}
                      style={{ marginLeft: '0.5rem', width: '80px', borderColor: error ? '#d00' : undefined, background: error ? '#ffeaea' : undefined }}
                    />
                  )}
                  {error && <span style={{ color: '#d00', fontSize: 12, marginLeft: 4 }}>{error}</span>}
                </div>
              );
            })}
            {/* Custom stat adder */}
            <div style={{ marginTop: '1rem' }}>
              <input
                type="text"
                placeholder="Custom stat label"
                value={customStatLabel}
                onChange={e => setCustomStatLabel(e.target.value)}
                style={{ width: '120px', marginRight: '0.5rem' }}
              />
              <input
                type="text"
                placeholder="Value"
                value={customStatValue}
                onChange={e => setCustomStatValue(e.target.value)}
                style={{ width: '80px', marginRight: '0.5rem' }}
              />
              <button type="button" onClick={() => {
                if (customStatLabel && customStatValue) {
                  setSelectedStats([...selectedStats, { label: customStatLabel, column: `custom_${Date.now()}`, auto: false, manualValue: customStatValue }]);
                  setCustomStatLabel('');
                  setCustomStatValue('');
                }
              }}>Add Custom Stat</button>
            </div>
          </div>
        </>
      )}

      {/* Customization options */}
      <div className="smg-section">
        <label>Player Image (optional):</label>
        <input type="file" accept="image/*" onChange={handlePlayerImageUpload} />
        {playerImage && <img src={URL.createObjectURL(playerImage)} alt="Player preview" style={{ height: '60px', marginLeft: '1rem' }} />}
      </div>
      <div className="smg-section">
        <label>Logo (optional):</label>
        <input type="file" accept="image/*" onChange={handleLogoUpload} />
        {logo && <img src={logo} alt="Logo preview" style={{ height: '40px', marginLeft: '1rem' }} />}
      </div>
      <div className="smg-section">
        <label>Accent Color (optional):</label>
        <input type="color" value={accentColor} onChange={e => setAccentColor(e.target.value)} />
      </div>
      <div className="smg-section">
        <label>Aspect Ratio:</label>
        <select value={aspect} onChange={e => setAspect(e.target.value)}>
          <option value="square">Square (1:1)</option>
          <option value="portrait">Portrait (4:5)</option>
          <option value="landscape">Landscape (16:9)</option>
        </select>
      </div>
      <div className="smg-section">
        <label>Hashtags/Social Handles (optional):</label>
        <input type="text" value={hashtag} onChange={e => setHashtag(e.target.value)} placeholder="#GoTeam @YourHandle" style={{ width: '220px' }} />
      </div>

      {/* Visible debug output for FormData */}
      {/* Placeholder for generated image */}
      <div className="smg-section">
        <button className="smg-generate-btn" onClick={handleGenerate} disabled={generating}>
          {generating ? 'Generating...' : 'Generate Graphic'}
        </button>
      </div>
      {generatedImage && (
        <div className="smg-section">
          <h3>Preview:</h3>
          <img src={generatedImage} alt="Generated Social Graphic" style={{ maxWidth: '100%', borderRadius: '12px', boxShadow: '0 2px 12px rgba(0,0,0,0.08)' }} />
          <a href={generatedImage} download="social-graphic.png" className="smg-generate-btn" style={{ marginTop: '1rem', display: 'inline-block' }}>Download</a>
        </div>
      )}
    </div>
  );
};

export default SocialMediaGenerator; 