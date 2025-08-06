import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS } from '../config';
import './CSVManagement.css';

const CSVManagement = () => {
  const [csvFiles, setCsvFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadFormData, setUploadFormData] = useState({
    game_date: '',
    opponent: '',
    game_result: '',
    notes: ''
  });
  const [editingFile, setEditingFile] = useState(null);
  const [editFormData, setEditFormData] = useState({
    game_date: '',
    opponent: '',
    game_result: '',
    notes: ''
  });
  const { token, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchCSVFiles();
  }, []);

  const fetchCSVFiles = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.LIST_CSV_FILES, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch CSV files');
      }

      const data = await response.json();
      
      // Sort by game date (newest first), then by upload date as fallback
      const sortedData = data.sort((a, b) => {
        // If both have game dates, sort by game date (newest first)
        if (a.game_date && b.game_date) {
          return new Date(b.game_date) - new Date(a.game_date);
        }
        // If only one has game date, prioritize the one with game date
        if (a.game_date && !b.game_date) return -1;
        if (!a.game_date && b.game_date) return 1;
        // If neither has game date, sort by upload date (newest first)
        return new Date(b.uploaded_at) - new Date(a.uploaded_at);
      });
      
      setCsvFiles(sortedData);
    } catch (error) {
      console.error('Error fetching CSV files:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'text/csv') {
      setSelectedFile(file);
      setError('');
    } else {
      setError('Please select a valid CSV file');
      setSelectedFile(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('game_date', uploadFormData.game_date);
      formData.append('opponent', uploadFormData.opponent);
      formData.append('game_result', uploadFormData.game_result);
      formData.append('notes', uploadFormData.notes);

      const response = await fetch(API_ENDPOINTS.UPLOAD_CSV_PERSISTENT, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload CSV');
      }

      const result = await response.json();
      setShowUploadForm(false);
      setSelectedFile(null);
      setUploadFormData({ game_date: '', opponent: '', game_result: '', notes: '' });
      fetchCSVFiles();
      alert('CSV uploaded successfully!');
    } catch (error) {
      console.error('Error uploading CSV:', error);
      setError(error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteFile = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this CSV file? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`${API_ENDPOINTS.DELETE_CSV_FILE}/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete CSV file');
      }

      fetchCSVFiles();
      alert('CSV file deleted successfully!');
    } catch (error) {
      console.error('Error deleting CSV file:', error);
      setError(error.message);
    }
  };

  const handleEditFile = (file) => {
    setEditingFile(file);
    setEditFormData({
      game_date: file.game_date || '',
      opponent: file.opponent || '',
      game_result: file.game_result || '',
      notes: file.notes || ''
    });
  };

  const handleUpdateMetadata = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('game_date', editFormData.game_date);
      formData.append('opponent', editFormData.opponent);
      formData.append('game_result', editFormData.game_result);
      formData.append('notes', editFormData.notes);

      const response = await fetch(`${API_ENDPOINTS.UPDATE_CSV_METADATA}/${editingFile.id}/metadata`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update metadata');
      }

      setEditingFile(null);
      setEditFormData({ game_date: '', opponent: '', game_result: '', notes: '' });
      fetchCSVFiles();
      alert('Metadata updated successfully!');
    } catch (error) {
      console.error('Error updating metadata:', error);
      setError(error.message);
    }
  };

  const handleCancelEdit = () => {
    setEditingFile(null);
    setEditFormData({ game_date: '', opponent: '', game_result: '', notes: '' });
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="csv-management-container">
        <div className="csv-management-card">
          <div className="loading">Loading CSV files...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="csv-management-container">
      <div className="csv-management-card">
        <div className="csv-management-header">
          <h1>📁 CSV File Management</h1>
          <p>Upload and manage your team's CSV data files</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="csv-management-actions">
          <button
            onClick={() => setShowUploadForm(true)}
            className="upload-button"
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : '+ Upload New CSV'}
          </button>
          <button onClick={handleBackToDashboard} className="secondary-button">
            Back to Dashboard
          </button>
        </div>

        {showUploadForm && (
          <div className="form-overlay">
            <div className="form-modal">
              <h3>Upload New CSV File</h3>
              <form onSubmit={handleUpload}>
                <div className="form-group">
                  <label>CSV File:</label>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileSelect}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Game Date:</label>
                  <input
                    type="date"
                    value={uploadFormData.game_date}
                    onChange={(e) => setUploadFormData({...uploadFormData, game_date: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Opponent:</label>
                  <input
                    type="text"
                    value={uploadFormData.opponent}
                    onChange={(e) => setUploadFormData({...uploadFormData, opponent: e.target.value})}
                    placeholder="e.g., Team Name"
                  />
                </div>
                <div className="form-group">
                  <label>Game Result:</label>
                  <select
                    value={uploadFormData.game_result}
                    onChange={(e) => setUploadFormData({...uploadFormData, game_result: e.target.value})}
                  >
                    <option value="">Select Result</option>
                    <option value="W">Win</option>
                    <option value="L">Loss</option>
                    <option value="T">Tie</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Notes:</label>
                  <textarea
                    value={uploadFormData.notes}
                    onChange={(e) => setUploadFormData({...uploadFormData, notes: e.target.value})}
                    placeholder="Optional notes about the game..."
                    rows="3"
                  />
                </div>
                <div className="form-actions">
                  <button type="submit" className="submit-button" disabled={uploading}>
                    {uploading ? 'Uploading...' : 'Upload CSV'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowUploadForm(false)}
                    className="cancel-button"
                    disabled={uploading}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {editingFile && (
          <div className="form-overlay">
            <div className="form-modal">
              <h3>Edit File Metadata: {editingFile.original_filename}</h3>
              <form onSubmit={handleUpdateMetadata}>
                <div className="form-group">
                  <label>Game Date:</label>
                  <input
                    type="date"
                    value={editFormData.game_date}
                    onChange={(e) => setEditFormData({...editFormData, game_date: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Opponent:</label>
                  <input
                    type="text"
                    value={editFormData.opponent}
                    onChange={(e) => setEditFormData({...editFormData, opponent: e.target.value})}
                    placeholder="e.g., Team Name"
                  />
                </div>
                <div className="form-group">
                  <label>Game Result:</label>
                  <select
                    value={editFormData.game_result}
                    onChange={(e) => setEditFormData({...editFormData, game_result: e.target.value})}
                  >
                    <option value="">Select Result</option>
                    <option value="W">Win</option>
                    <option value="L">Loss</option>
                    <option value="T">Tie</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Notes:</label>
                  <textarea
                    value={editFormData.notes}
                    onChange={(e) => setEditFormData({...editFormData, notes: e.target.value})}
                    placeholder="Optional notes about the game..."
                    rows="3"
                  />
                </div>
                <div className="form-actions">
                  <button type="submit" className="submit-button">
                    Update Metadata
                  </button>
                  <button
                    type="button"
                    onClick={handleCancelEdit}
                    className="cancel-button"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="csv-files-section">
          <h2>📊 Your CSV Files ({csvFiles.length})</h2>
          
          {csvFiles.length === 0 ? (
            <div className="no-files">
              <p>No CSV files uploaded yet.</p>
              <p>Click "Upload New CSV" to get started!</p>
            </div>
          ) : (
            <div className="csv-files-grid">
              {csvFiles.map((file) => (
                <div key={file.id} className="csv-file-card">
                  <div className="file-header">
                    <h4>{file.original_filename}</h4>
                    <span className={`status-badge ${file.is_processed ? 'processed' : 'pending'}`}>
                      {file.is_processed ? 'Processed' : 'Pending'}
                    </span>
                  </div>
                  
                  <div className="file-info">
                    <div className="info-row">
                      <span className="label">Uploaded:</span>
                      <span>{formatDate(file.uploaded_at)}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Size:</span>
                      <span>{formatFileSize(file.file_size)}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Rows:</span>
                      <span>{file.row_count.toLocaleString()}</span>
                    </div>
                    {file.game_date && (
                      <div className="info-row">
                        <span className="label">Game Date:</span>
                        <span>{file.game_date}</span>
                      </div>
                    )}
                    {file.opponent && (
                      <div className="info-row">
                        <span className="label">Opponent:</span>
                        <span>{file.opponent}</span>
                      </div>
                    )}
                    {file.game_result && (
                      <div className="info-row">
                        <span className="label">Result:</span>
                        <span className={`result-badge ${file.game_result}`}>
                          {file.game_result === 'W' ? 'Win' : file.game_result === 'L' ? 'Loss' : 'Tie'}
                        </span>
                      </div>
                    )}
                    {file.notes && (
                      <div className="info-row">
                        <span className="label">Notes:</span>
                        <span className="notes">{file.notes}</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="file-actions">
                    <button
                      onClick={() => {
                        // Store the selected file info for the report flow
                        sessionStorage.setItem('selectedCSVFile', JSON.stringify({
                          id: file.id,
                          filename: file.original_filename,
                          game_date: file.game_date,
                          opponent: file.opponent,
                          game_result: file.game_result
                        }));
                        navigate('/select-team');
                      }}
                      className="report-button"
                    >
                      Generate Report
                    </button>
                    <button
                      onClick={() => handleEditFile(file)}
                      className="edit-button"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteFile(file.id)}
                      className="delete-button"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CSVManagement; 