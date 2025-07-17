import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleUploadCSV = () => {
    navigate('/upload');
  };

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <h2>Trackman Analytics</h2>
        </div>
        <div className="nav-user">
          <span>Welcome, {user?.username}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </nav>

      <main className="dashboard-main">
        <div className="dashboard-header">
          <h1>Analytics Dashboard</h1>
          <p>Upload your Trackman data and generate comprehensive reports</p>
        </div>

        <div className="dashboard-cards">
          <div className="dashboard-card">
            <div className="card-icon">📊</div>
            <h3>Upload CSV Data</h3>
            <p>Upload your Trackman CSV file to begin analysis</p>
            <button onClick={handleUploadCSV} className="card-button">
              Start Analysis
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">📈</div>
            <h3>View Reports</h3>
            <p>Access previously generated reports and analytics</p>
            <button className="card-button" disabled>
              Coming Soon
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">⚙️</div>
            <h3>Settings</h3>
            <p>Manage your account and preferences</p>
            <button className="card-button" disabled>
              Coming Soon
            </button>
          </div>
        </div>

        <div className="dashboard-info">
          <h3>Getting Started</h3>
          <ol>
            <li>Click "Start Analysis" to upload your Trackman CSV file</li>
            <li>Select the team and pitcher you want to analyze</li>
            <li>View comprehensive metrics and download PDF reports</li>
          </ol>
        </div>
      </main>
    </div>
  );
};

export default Dashboard; 