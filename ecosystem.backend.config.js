/**
 * PM2 ecosystem for backend
 * Runs the Python backend (backend/app.py) with the configured BACKEND_PORT.
 */
module.exports = {
  apps: [
    {
      name: "converse-backend",
      script: "backend/app.py",
      interpreter: "python3",
      cwd: __dirname,
      env: {
        NODE_ENV: "development",
        BACKEND_PORT: process.env.BACKEND_PORT || 2355,
        FRONTEND_ORIGIN: process.env.FRONTEND_ORIGIN || "http://localhost:2357",
      },
    },
  ],
};
