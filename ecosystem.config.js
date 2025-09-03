module.exports = {
  apps: [
    {
      name: "aisearch-rag-backend",
      script: "app/backend/app.py",
      interpreter: "python3",
      cwd: "/home/azureuser/aisearch-openai-rag-audio",
      env: {
        PYTHONPATH: "/home/azureuser/aisearch-openai-rag-audio",
        PORT: 8765,
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      error_file: "./logs/pm2-error.log",
      out_file: "./logs/pm2-out.log",
      log_file: "./logs/pm2-combined.log",
      time: true,
      env_production: {
        NODE_ENV: "production",
        RUNNING_IN_PRODUCTION: "true",
        PORT: 80, // Standard HTTP port for production
      },
    },
  ],
};
