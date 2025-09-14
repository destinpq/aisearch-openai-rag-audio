module.exports = {
  apps: [
    {
      name: "converse-frontend",
      script: "npm",
      args: "start",
      cwd: __dirname + "/../frontend-next",
      env: {
        NODE_ENV: "production",
        PORT: 45533,
      },
    },
  ],
};

// Backend (Nest) process
module.exports.apps.push({
  name: "converse-backend",
  script: "npm",
  args: "run start:dev",
  cwd: __dirname + "/../backend/nestjs",
  env: {
    NODE_ENV: "development",
    PORT: 3001,
  },
});
