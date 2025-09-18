/**
 * PM2 ecosystem for frontend
 * Starts Next.js using npm start or npm run dev and ensures PORT env is set.
 */
module.exports = {
  apps: [
    {
      name: "converse-frontend",
      script: "npm",
      args: "run start",
      cwd: __dirname + "/frontend-next",
      env: {
        NODE_ENV: "production",
        PORT: process.env.FRONTEND_PORT || 2357,
      },
      // Pre-start hook to kill any process listening on the port
      interpreter: "/bin/bash",
      post_update: [],
    },
  ],
};
