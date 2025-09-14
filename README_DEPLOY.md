deploy_production.sh — README

This repository includes a simple, safe deploy script: `deploy_production.sh`.

Purpose

- Build the frontend production bundle
- Copy frontend artifacts into `backend/static` (the backend serves those files)
- Optionally create a timestamped backup of the previous `backend/static`
- Optionally restart a named service (systemd or pm2)

Basic usage

From the repo root:

```bash
./deploy_production.sh
```

To skip backup:

```bash
./deploy_production.sh --no-backup
```

To restart a systemd service after deploy (requires sudo):

```bash
./deploy_production.sh --restart converse-backend
```

Notes

- The script will run `npm ci` in the `frontend` directory; ensure the machine has network access and Node installed.
- The script creates backups in `backups/static.YYYYMMDDTHHMMSSZ` and keeps the last 5 backups by default.
- The script will not force-restart services by default; use the `--restart` flag to request a restart.

Example systemd service

Save the following as `/etc/systemd/system/converse-backend.service` and adapt paths:

```ini
[Unit]
Description=Converse Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/azureuser/aisearch-openai-rag-audio/backend
ExecStart=/usr/bin/node dist/main.js
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

After creating the unit file:

```bash
sudo systemctl daemon-reload
sudo systemctl enable converse-backend
sudo systemctl start converse-backend
```

Security

- The script uses `sudo systemctl restart` if `--restart` is provided; ensure the user has appropriate sudo privileges.

Contact

- If you want automatic zero-downtime deploys, consider using a more advanced deploy tool (pm2, capistrano, or Kubernetes) and a CI pipeline.

CI/CD from GitHub
-----------------

This repository includes a GitHub Actions workflow at `.github/workflows/ci-cd-deploy.yml` which builds `frontend-next` and `backend/nestjs`, copies artifacts to the server via SCP, and restarts processes via SSH.

Required repository secrets (GitHub → Settings → Secrets):

- `SSH_HOST` — server IP or hostname
- `SSH_PORT` — SSH port (usually 22)
- `SSH_USER` — SSH username (e.g., `azureuser`)
- `SSH_PRIVATE_KEY` — private key contents (PEM)
- `REMOTE_PATH` — absolute path on the server where the repo is deployed (e.g., `/home/azureuser/aisearch-openai-rag-audio`)

What the workflow does:
- Checks out code and sets up Node.js
- Builds `frontend-next` (Tailwind prebuild + Next build)
- Builds `backend/nestjs` (TypeScript compile)
- Copies build artifacts to `REMOTE_PATH`
- Runs remote commands to install production deps and restart `pm2` processes for the frontend and backend

Notes:
- You must install `pm2` and configure it on the server. The workflow uses `pm2 restart` / `pm2 start` commands; you can adapt the remote script to use systemd instead.
- For increased safety use rsync with atomic symlink swaps and health checks.

