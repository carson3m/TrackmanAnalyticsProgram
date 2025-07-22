import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS, FALLBACK_API_URL } from '../config';
import './UploadCSV.css';

const UploadCSV = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [teams, setTeams] = useState([]);
  const { token } = useAuth();
  const navigate = useNavigate();

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid CSV file');
      setFile(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'text/csv') {
      setFile(droppedFile);
      setError('');
    } else {
      setError('Please drop a valid CSV file');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(API_ENDPOINTS.UPLOAD_CSV, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setTeams(data.teams || []);
      setSuccess(true);
      
      // Store teams in sessionStorage for next page
      sessionStorage.setItem('teams', JSON.stringify(data.teams || []));
      
      // Navigate to team selection after a brief delay
      setTimeout(() => {
        navigate('/select-team');
      }, 1500);

    } catch (error) {
      console.error('Upload error:', error);
      setError('Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        <div className="upload-header">
          <h1>Upload CSV Data</h1>
          <p>Upload your CSV file to begin analysis</p>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && (
          <div className="success-message">
            ✅ File uploaded successfully! Redirecting to team selection...
          </div>
        )}

        <div 
          className={`upload-area ${file ? 'has-file' : ''}`}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="upload-icon">📁</div>
          <h3>Drop your CSV file here</h3>
          <p>or</p>
          <label className="file-input-label">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="file-input"
            />
            Choose File
          </label>
          {file && (
            <div className="file-info">
              <p>Selected: {file.name}</p>
              <p>Size: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}
        </div>

        <div className="upload-actions">
          <button
            onClick={() => navigate('/dashboard')}
            className="secondary-button"
            disabled={uploading}
          >
            Back to Dashboard
          </button>
          <button
            onClick={handleUpload}
            className="upload-button"
            disabled={!file || uploading}
          >
            {uploading ? 'Uploading...' : 'Upload & Continue'}
          </button>
        </div>

        <div className="upload-help">
          <h4>File Requirements:</h4>
          <ul>
            <li>File must be in CSV format</li>
            <li>Should contain data in the Trackman CSV format (columns like Pitcher, PitcherTeam, etc. are supported)</li>
            <li>Maximum file size: 50MB</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default UploadCSV; 