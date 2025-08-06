import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './LandingPage.css';
import pitchBreaksChart from '../assets/pitch_breaks_chart.png';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/login');
  };

  const handleContact = () => {
    window.location.href = 'mailto:cmorton@moundvision.com';
  };

  const handleLogin = () => {
    navigate('/login');
  };

  return (
    <div className="landing-page">
      {/* Navigation Header */}
      <nav className="landing-nav">
        <div className="nav-content">
          <div className="nav-logo">
            <span className="nav-brand">MoundVision Analytics</span>
          </div>
          <div className="nav-links">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/about" className="nav-link">About Us</Link>
            <button onClick={handleContact} className="nav-contact">Contact</button>
            <button onClick={handleLogin} className="nav-login">Login</button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-text">
            <h1>Transform Your Baseball Analytics</h1>
            <p className="hero-subtitle">
              Professional-grade data analysis for coaches, players, and teams. 
              Get insights that drive performance and winning strategies.
            </p>
            <div className="hero-cta">
              <button onClick={handleGetStarted} className="cta-primary">
                Get Started
              </button>
              <button onClick={handleContact} className="cta-secondary">
                Contact Us
              </button>
            </div>
          </div>
          <div className="hero-visual">
            <div className="hero-image-placeholder">
              <div className="mockup-dashboard">
                <div className="mockup-header">
                  <div className="mockup-logo">MV</div>
                  <div className="mockup-title">MoundVision Analytics</div>
                </div>
                <div className="mockup-content">
                  <div className="mockup-chart">
                    <img 
                      src={pitchBreaksChart} 
                      alt="Pitch Breaks Analysis Chart" 
                      className="chart-image"
                    />
                  </div>
                  <div className="mockup-stats">
                    <div className="mockup-stat">92.3 mph</div>
                    <div className="mockup-stat">2,450 rpm</div>
                    <div className="mockup-stat">85% strikes</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <h2>Professional Analytics Platform</h2>
          <p className="section-subtitle">
            Advanced tools that give you the insights you need to win
          </p>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔥</div>
              <h3>Interactive Heat Maps</h3>
              <p>
                Visualize pitch success zones and batting performance with professional heat maps. 
                See exactly where players excel and where they need improvement.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Comprehensive Reports</h3>
              <p>
                Generate detailed PDF reports with pitch-by-pitch analysis, 
                performance trends, and actionable insights for each player.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">👥</div>
              <h3>Smart Roster Management</h3>
              <p>
                Auto-populate rosters from game data with intelligent player deduplication. 
                Track both pitchers and batters with comprehensive statistics.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📅</div>
              <h3>Game Calendar & History</h3>
              <p>
                Visualize your season with an interactive game calendar. 
                Track wins/losses and access detailed game reports instantly.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🏆</div>
              <h3>Best of Stats</h3>
              <p>
                Identify top performers across different metrics and time periods. 
                Track progress and celebrate achievements with your team.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">⚖️</div>
              <h3>Umpire Accuracy Analysis</h3>
              <p>
                Analyze umpire performance and call accuracy to understand 
                strike zone consistency and game impact.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Social Media Graphics</h3>
              <p>
                Create professional social media posts with player stats and team highlights. 
                Perfect for recruiting and team promotion.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>Advanced Performance Tracking</h3>
              <p>
                Monitor player development with detailed metrics including velocity, 
                spin rate, command, exit velocity, and contact quality.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Enterprise Security</h3>
              <p>
                Your data stays private and secure with role-based access. 
                Only authorized users can view team information.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Platform Showcase Section */}
      <section className="platform-showcase">
        <div className="container">
          <h2>See MoundVision in Action</h2>
          <p className="section-subtitle">
            Professional analytics that transform raw data into winning insights
          </p>
          
          <div className="showcase-grid">
            <div className="showcase-item">
              <div className="showcase-visual">
                <div className="showcase-mockup heat-map-mockup">
                  <div className="mockup-header">
                    <span className="mockup-dot red"></span>
                    <span className="mockup-dot yellow"></span>
                    <span className="mockup-dot green"></span>
                  </div>
                  <div className="mockup-content">
                    <div className="heat-map-grid">
                      {[...Array(9)].map((_, i) => (
                        <div key={i} className={`heat-zone zone-${i % 3}`}></div>
                      ))}
                    </div>
                    <div className="mockup-label">Pitch Success Heat Map</div>
                  </div>
                </div>
              </div>
              <div className="showcase-content">
                <h3>Professional Heat Maps</h3>
                <p>
                  Visualize pitch success zones and batting performance with MLB-caliber heat maps. 
                  Identify strengths and weaknesses with precision.
                </p>
                <ul>
                  <li>Pitch success zones by location</li>
                  <li>Batting average heat maps</li>
                  <li>Exit velocity analysis</li>
                  <li>Contact quality visualization</li>
                </ul>
              </div>
            </div>
            
            <div className="showcase-item reverse">
              <div className="showcase-content">
                <h3>Comprehensive Player Profiles</h3>
                <p>
                  Deep dive into individual player performance with detailed statistics, 
                  trends, and actionable insights for development.
                </p>
                <ul>
                  <li>Season-long performance tracking</li>
                  <li>Pitch-by-pitch analysis</li>
                  <li>Velocity and spin rate trends</li>
                  <li>Game-by-game breakdowns</li>
                </ul>
              </div>
              <div className="showcase-visual">
                <div className="showcase-mockup profile-mockup">
                  <div className="mockup-header">
                    <span className="mockup-dot red"></span>
                    <span className="mockup-dot yellow"></span>
                    <span className="mockup-dot green"></span>
                  </div>
                  <div className="mockup-content">
                    <div className="profile-stats">
                      <div className="stat-row">
                        <span>Velocity:</span>
                        <span className="stat-value">92.3 mph</span>
                      </div>
                      <div className="stat-row">
                        <span>Spin Rate:</span>
                        <span className="stat-value">2,450 rpm</span>
                      </div>
                      <div className="stat-row">
                        <span>Strike %:</span>
                        <span className="stat-value">68.5%</span>
                      </div>
                    </div>
                    <div className="mockup-label">Player Analytics</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="showcase-item">
              <div className="showcase-visual">
                <div className="showcase-mockup calendar-mockup">
                  <div className="mockup-header">
                    <span className="mockup-dot red"></span>
                    <span className="mockup-dot yellow"></span>
                    <span className="mockup-dot green"></span>
                  </div>
                  <div className="mockup-content">
                    <div className="calendar-grid">
                      {[...Array(12)].map((_, i) => (
                        <div key={i} className={`calendar-day ${i % 3 === 0 ? 'win' : i % 3 === 1 ? 'loss' : 'no-game'}`}>
                          {i + 1}
                        </div>
                      ))}
                    </div>
                    <div className="mockup-label">Season Calendar</div>
                  </div>
                </div>
              </div>
              <div className="showcase-content">
                <h3>Season Management</h3>
                <p>
                  Track your entire season with an interactive game calendar. 
                  Access detailed reports and performance data for every game.
                </p>
                <ul>
                  <li>Visual game calendar</li>
                  <li>Win/loss tracking</li>
                  <li>Game-specific reports</li>
                  <li>Season trends analysis</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works">
        <div className="container">
          <h2>Get Started in Minutes</h2>
          <p className="section-subtitle">
            Simple 3-step process to transform your analytics
          </p>
          
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Upload Your Data</h3>
                <p>
                  Upload your Trackman CSV files directly to our secure platform. 
                  We support standard Trackman export formats with automatic processing.
                </p>
              </div>
            </div>
            
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>Explore & Analyze</h3>
                <p>
                  Choose the team and players you want to analyze. 
                  Generate comprehensive reports or explore specific metrics with our interactive tools.
                </p>
              </div>
            </div>
            
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Get Insights & Share</h3>
                <p>
                  Download detailed PDF reports, create social media graphics, 
                  and share insights with your team and recruits.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits">
        <div className="container">
          <h2>Built for Champions</h2>
          <p className="section-subtitle">
            Professional tools that give every level a competitive edge
          </p>
          
          <div className="benefits-grid">
            <div className="benefit-card">
              <h3>🏟️ Coaches & Programs</h3>
              <ul>
                <li>Make data-driven lineup and strategy decisions</li>
                <li>Track player development with precision</li>
                <li>Identify hidden strengths and improvement areas</li>
                <li>Create compelling recruiting materials</li>
                <li>Professional analytics that impress recruits</li>
                <li>Competitive advantage in scouting and development</li>
              </ul>
            </div>
            
            <div className="benefit-card">
              <h3>⚾ Players</h3>
              <ul>
                <li>Understand your performance with professional metrics</li>
                <li>Track improvement with detailed analytics</li>
                <li>Identify specific areas to focus training</li>
                <li>Showcase your stats to colleges and pro scouts</li>
                <li>Visual heat maps show your strengths</li>
                <li>Professional reports for your portfolio</li>
              </ul>
            </div>
            
            <div className="benefit-card">
              <h3>🏫 Programs & Organizations</h3>
              <ul>
                <li>Enterprise-level analytics for your program</li>
                <li>Enhanced recruiting with professional tools</li>
                <li>Data-backed player development strategies</li>
                <li>Competitive advantage in talent evaluation</li>
                <li>Professional branding and presentation</li>
                <li>Scalable solution for growing programs</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <h2>Ready to Gain the Competitive Edge?</h2>
          <p>
            Join coaches and programs who are already using MoundVision Analytics 
            to transform their player development and recruiting.
          </p>
          <div className="cta-buttons">
            <button onClick={handleGetStarted} className="cta-primary">
              Start Free Trial
            </button>
            <button onClick={handleContact} className="cta-secondary">
              Schedule a Demo
            </button>
          </div>
          <div className="cta-features">
            <div className="cta-feature">
              <span className="cta-icon">⚡</span>
              <span>Get started in minutes</span>
            </div>
            <div className="cta-feature">
              <span className="cta-icon">🔒</span>
              <span>Secure & private</span>
            </div>
            <div className="cta-feature">
              <span className="cta-icon">📊</span>
              <span>Professional analytics</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h4>MoundVision Analytics</h4>
              <p>Sharper vision. Better results.</p>
            </div>
            <div className="footer-section">
              <h4>Contact</h4>
              <p>Phone: (916) 250-9640</p>
              <p>Email: cmorton@moundvision.com</p>
            </div>
            <div className="footer-section">
              <h4>Features</h4>
              <ul>
                <li>Player Reports</li>
                <li>Best of Stats</li>
                <li>Umpire Analysis</li>
                <li>Social Media Graphics</li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 MoundVision Analytics. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage; 