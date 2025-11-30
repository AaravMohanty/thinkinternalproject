import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import '../styles/landing.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);
  const [activeFeature, setActiveFeature] = useState(0);

  const features = [
    {
      icon: (
        <svg width="60" height="30" viewBox="0 0 60 30" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M5 15 Q 15 5, 25 15 T 45 15 T 55 15" strokeLinecap="round"/>
          <circle cx="15" cy="10" r="2" fill="currentColor" stroke="none"/>
          <circle cx="35" cy="20" r="2" fill="currentColor" stroke="none"/>
        </svg>
      ),
      title: "BUILD CONNECTIONS",
      description: "Network with alumni who share\nyour interests and career goals."
    },
    {
      icon: (
        <svg width="60" height="30" viewBox="0 0 60 30" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="8" y="5" width="18" height="22" rx="2" />
          <rect x="34" y="5" width="18" height="22" rx="2" />
          <path d="M26 15 L34 15" strokeLinecap="round"/>
          <circle cx="17" cy="12" r="4" />
          <path d="M12 22 Q17 18, 22 22" strokeLinecap="round"/>
          <circle cx="43" cy="12" r="4" />
          <path d="M38 22 Q43 18, 48 22" strokeLinecap="round"/>
        </svg>
      ),
      title: "AI-POWERED MATCHING",
      description: "Get personalized alumni\nrecommendations based on your goals."
    },
    {
      icon: (
        <svg width="60" height="30" viewBox="0 0 60 30" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M10 25 L10 10 L25 10" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M10 10 L30 25" strokeLinecap="round"/>
          <circle cx="35" cy="8" r="6" />
          <path d="M41 14 L50 23" strokeLinecap="round"/>
          <circle cx="50" cy="23" r="4" />
        </svg>
      ),
      title: "GROW YOUR CAREER",
      description: "Access mentorship opportunities\nand insider industry insights."
    }
  ];

  useEffect(() => {
    // Trigger animations after mount
    setTimeout(() => setIsVisible(true), 100);
  }, []);

  const handlePrevFeature = () => {
    setActiveFeature((prev) => (prev === 0 ? features.length - 1 : prev - 1));
  };

  const handleNextFeature = () => {
    setActiveFeature((prev) => (prev === features.length - 1 ? 0 : prev + 1));
  };

  return (
    <div className={`landing-page ${isVisible ? 'visible' : ''}`}>
      {/* Background with light rays */}
      <div className="landing-bg">
        <div className="light-ray ray-1"></div>
        <div className="light-ray ray-2"></div>
      </div>

      {/* Top Navigation */}
      <nav className="landing-nav">
        <div className="landing-nav-left">
          <img
            src="/assets/Copy of P logo for medium or dark background (1).png"
            alt="PurdueTHINK"
            className="landing-logo"
          />
        </div>
        <div className="landing-nav-right">
          <button className="landing-nav-btn" onClick={() => navigate('/auth')}>
            Get Started
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="landing-main">
        {/* Left Content */}
        <div className="landing-left">
          <span className="landing-label">PURDUE THINK</span>
          <h1 className="landing-title">THINKedIn</h1>
          <div className="landing-divider"></div>
          <p className="landing-description">
            The exclusive alumni networking platform<br />
            for Purdue THINK members. Connect, learn,<br />
            and grow your professional network.
          </p>
          <button className="landing-cta-btn" onClick={() => navigate('/auth')}>
            Get Started
          </button>
        </div>

        {/* Center 3D Sphere */}
        <div className="landing-sphere-container">
          <div className="sphere-3d">
            <div className="sphere-layer layer-1"></div>
            <div className="sphere-layer layer-2"></div>
            <div className="sphere-layer layer-3"></div>
            <div className="sphere-layer layer-4"></div>
            <div className="sphere-layer layer-5"></div>
            <div className="sphere-layer layer-6"></div>
            <div className="sphere-layer layer-7"></div>
            <div className="sphere-layer layer-8"></div>
          </div>
        </div>

        {/* Right Content - Feature Carousel */}
        <div className="landing-right">
          <div className="feature-icon">
            {features[activeFeature].icon}
          </div>
          <span className="feature-count">{activeFeature + 1} / {features.length}</span>
          <h3 className="feature-title">{features[activeFeature].title}</h3>
          <p className="feature-description">
            {features[activeFeature].description.split('\n').map((line, i) => (
              <span key={i}>{line}<br /></span>
            ))}
          </p>
          <div className="feature-nav">
            <button className="nav-arrow" onClick={handlePrevFeature}>‹</button>
            <button className="nav-arrow" onClick={handleNextFeature}>›</button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default LandingPage;
