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

  const handleBestOfStats = () => {
    navigate('/best-of');
  };

  const handleUmpireAccuracy = () => {
    navigate('/umpire-accuracy');
  };

  const handleAdminPanel = () => {
    navigate('/admin');
  };

  const isAdmin = user?.role === 'admin';

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <h2>MoundVision Analytics</h2>
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
          <p>Upload your CSV data and generate comprehensive reports</p>
        </div>

        <div className="dashboard-cards">
          <div className="dashboard-card">
            <div className="card-icon">📊</div>
            <h3>Upload CSV Data</h3>
            <p>Upload your CSV file to begin analysis</p>
            <button onClick={handleUploadCSV} className="card-button">
              Start Analysis
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🏆</div>
            <h3>Best of Stats</h3>
            <p>View top performers across different metrics and time periods</p>
            <button onClick={handleBestOfStats} className="card-button">
              View Best of Stats
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">⚖️</div>
            <h3>Umpire Accuracy</h3>
            <p>Analyze umpire performance and call accuracy</p>
            <button onClick={handleUmpireAccuracy} className="card-button">
              Analyze Umpire Accuracy
            </button>
          </div>

          {isAdmin && (
            <div className="dashboard-card admin-card">
              <div className="card-icon">👑</div>
              <h3>Admin Panel</h3>
              <p>Manage users and system settings</p>
              <button onClick={handleAdminPanel} className="card-button admin-button">
                Access Admin Panel
              </button>
            </div>
          )}

          <div className="dashboard-card">
            <div className="card-icon">📱</div>
            <h3>Social Media Generator</h3>
            <p>Create a shareable stat graphic for your team or player</p>
            <button onClick={() => navigate('/social-media-generator')} className="card-button">
              Create Social Post
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
            <li>Click "Start Analysis" to upload your CSV file (Trackman format supported)</li>
            <li>Select the team and pitcher you want to analyze</li>
            <li>View comprehensive metrics and download PDF reports</li>
            <li>Use "Best of Stats" to see top performers across metrics</li>
            <li>Analyze umpire accuracy with the Umpire Accuracy tool</li>
            {isAdmin && <li>Access the Admin Panel to manage users and system settings</li>}
          </ol>
        </div>
      </main>
    </div>
  );
};

export default Dashboard; 