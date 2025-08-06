import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './AboutUs.css';
import carsonPhoto from '../assets/carson_optimized.png';
import kathrynPhoto from '../assets/Kathryn_optimized.png';

const AboutUs = () => {
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
    <div className="about-page">
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
      <section className="about-hero">
        <div className="about-hero-content">
          <h1>About MoundVision Analytics</h1>
          <p className="hero-subtitle">
            Transforming baseball analytics through innovative technology and deep understanding of the game
          </p>
        </div>
      </section>

      {/* Mission Section */}
      <section className="mission-section">
        <div className="container">
          <div className="mission-content">
            <div className="mission-text">
              <h2>Our Mission</h2>
              <p>
                At MoundVision Analytics, we believe that every pitch tells a story. Our mission is to 
                provide coaches, players, and teams with the most advanced analytics tools to unlock 
                the full potential of their performance data.
              </p>
              <p>
                We combine cutting-edge technology with deep baseball expertise to deliver insights 
                that drive winning strategies and player development. From pitch-by-pitch analysis 
                to comprehensive team reports, we're committed to helping you make data-driven 
                decisions that lead to success on the field.
              </p>
            </div>
            <div className="mission-visual">
              <div className="mission-card">
                <div className="mission-icon">🎯</div>
                <h3>Data-Driven Decisions</h3>
                <p>Transform raw data into actionable insights</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Story Section */}
      <section className="story-section">
        <div className="container">
          <h2>Our Story</h2>
          <div className="story-content">
            <div className="story-text">
              <p>
                MoundVision Analytics was born from a passion for baseball and a recognition that 
                the game was evolving. As technology advanced and radar systems became more 
                prevalent, we saw an opportunity to bridge the gap between raw data and practical 
                coaching insights.
              </p>
              <p>
                What started as a solution for local teams has grown into a comprehensive analytics 
                platform trusted by coaches. Our team combines technical expertise with real-world 
                baseball experience, ensuring that every feature we build serves a practical purpose
                in player development and team strategy.
              </p>
              <p>
                Today, we're proud to support teams, helping them harness the power of data to achieve 
                their goals on the diamond.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="values-section">
        <div className="container">
          <h2>Our Values</h2>
          <div className="values-grid">
            <div className="value-card">
              <div className="value-icon">🔬</div>
              <h3>Innovation</h3>
              <p>
                We continuously push the boundaries of what's possible in baseball analytics, 
                developing new tools and insights that give teams a competitive edge.
              </p>
            </div>
            
            <div className="value-card">
              <div className="value-icon">🤝</div>
              <h3>Partnership</h3>
              <p>
                We believe in building lasting relationships with our clients, working closely 
                with coaches and teams to understand their unique needs and challenges.
              </p>
            </div>
            
            <div className="value-card">
              <div className="value-icon">📈</div>
              <h3>Excellence</h3>
              <p>
                Every feature we build, every report we generate, and every insight we provide 
                is crafted with the highest standards of quality and accuracy.
              </p>
            </div>
            
            <div className="value-card">
              <div className="value-icon">🎓</div>
              <h3>Education</h3>
              <p>
                We're committed to helping teams understand not just what the data shows, 
                but why it matters and how to use it effectively in their programs.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="team-section">
        <div className="container">
          <h2>Our Team</h2>
          <div className="team-content">
            <div className="team-member">
              <div className="member-avatar">
                <img src={carsonPhoto} alt="Carson Morton" className="member-photo" />
              </div>
              <div className="member-info">
                <h3>Carson Morton</h3>
                <p className="member-title">Founder & Lead Developer</p>
                <p className="member-bio">
                  Carson brings together a deep understanding of baseball and software development 
                  to create innovative analytics solutions. Starting as an intern with the
                  Lincoln Potters, he realized missed potential with the data created each game.
                  As a senior in college at Colorado State University, he decided to create a tool
                  that would help coaches and players understand the data and use it to their advantage.
                </p>
              </div>
            </div>
            
            <div className="team-member">
              <div className="member-avatar">
                <img src={kathrynPhoto} alt="Kathryn Prerost" className="member-photo" style={{ objectPosition: 'top' }} />
              </div>
              <div className="member-info">
                <h3>Kathryn Prerost</h3>
                <p className="member-title">Social Media Director</p>
                <p className="member-bio">
                  Kathryn is a sophomore at Colorado State University majoring in Journalism and Media Communication. 
                  As our Social Media Director, she brings her creative vision and media expertise to help teams 
                  showcase their achievements through compelling content. Kathryn also works with CSU Lacrosse as 
                  one of their media creators, bringing valuable experience in sports media and content creation 
                  to the MoundVision team.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="about-cta">
        <div className="container">
          <h2>Ready to Transform Your Analytics?</h2>
          <p>
            Join the teams using MoundVision Analytics to gain a competitive edge. 
            Start your journey toward data-driven success today.
          </p>
          <div className="cta-buttons">
            <button onClick={handleGetStarted} className="cta-primary">
              Get Started
            </button>
            <button onClick={handleContact} className="cta-secondary">
              Contact Us
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutUs; 