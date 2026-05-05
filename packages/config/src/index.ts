// Configuration
export const config = {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  environment: process.env.NODE_ENV || 'development',
  debug: process.env.DEBUG === 'true',
};

export default config;
