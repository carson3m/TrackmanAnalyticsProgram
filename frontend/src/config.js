// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://moundvision-backend-prod.eba-pqeztud4.us-west-2.elasticbeanstalk.com';

// API Endpoints
export const API_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/api/auth/login`,
  UPLOAD_CSV: `${API_BASE_URL}/api/csv/upload`,
  TEAM_PITCHERS: `${API_BASE_URL}/api/csv/team_pitchers`,
  METRICS_SUMMARY: `${API_BASE_URL}/api/metrics/summary`,
  METRICS_PITCHES: `${API_BASE_URL}/api/metrics/pitches`,
  METRICS_DOWNLOAD_PDF: `${API_BASE_URL}/api/metrics/download_pdf`,
};

// Fallback URL for development (update this with your actual EB environment URL)
// You can find this in your AWS Console under Elastic Beanstalk > Environments
export const FALLBACK_API_URL = 'http://moundvision-backend-prod.eba-pqeztud4.us-west-2.elasticbeanstalk.com';

// For development, you can also use:
// export const FALLBACK_API_URL = http://localhost:8000'; 