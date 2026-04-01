# Music Platform Operation and Debug Guide

## 1. What this project runs

This workspace has two main things you will use during development:

1. Backend services with Docker:
   - Postgres database
   - Navidrome music server
   - FastAPI backend on port `8000`
2. Frontend web server with Vite:
   - Feishin web UI on port `5173`

Main local URLs:

- Frontend: `http://localhost:5173`
- Backend health check: `http://localhost:8000/health`
- Navidrome: `http://localhost:4533`

## 2. Project folders you should know

- `backend/app`: main FastAPI application code
- `backend/tests`: backend tests
- `feishin/src/renderer`: frontend UI code
- `docker-compose.yml`: backend service definitions
- `music`: local music library mounted into Navidrome
- `navidrome-data`: Navidrome data
- `postgres-data`: Postgres data

## 3. Start everything

Open PowerShell in:

```powershell
cd c:\Users\u\Music\music-platform
```

### Step 1: Start Docker services

```powershell
docker compose up -d
```

This starts:

- `postgres`
- `navidrome`
- `backend`

### Step 2: Check Docker services

```powershell
docker compose ps
```

You want to see the containers running, especially:

- `music-postgres`
- `navidrome`
- `music-backend`

### Step 3: Start the frontend dev server

Open a second PowerShell window:

```powershell
cd c:\Users\u\Music\music-platform\feishin
npx vite dev --config web.vite.config.ts --host 0.0.0.0 --port 5173
```

### Step 4: Open the app

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Backend health: `http://localhost:8000/health`
- Navidrome: `http://localhost:4533`

## 4. Stop everything

Stop the frontend by pressing `Ctrl+C` in the frontend terminal.

Stop Docker services:

```powershell
cd c:\Users\u\Music\music-platform
docker compose down
```

## 5. Daily workflow

1. Run `docker compose up -d`
2. Run the frontend Vite command in `feishin`
3. Open `http://localhost:5173`
4. Make code changes
5. Refresh the browser after frontend changes
6. Rebuild or restart services only when needed

## 6. How to debug the backend

### Quick backend checks

Run:

```powershell
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### See backend logs

```powershell
cd c:\Users\u\Music\music-platform
docker compose logs --tail=200 backend
```

### Follow backend logs live

```powershell
docker compose logs -f backend
```

### Common backend debug steps

1. Check whether backend container is running with `docker compose ps`
2. Check `/health`
3. Read backend logs
4. Confirm Postgres is healthy
5. Restart backend if needed:

```powershell
docker compose restart backend
```

### Run backend tests

```powershell
cd c:\Users\u\Music\music-platform\backend
python -m pytest
```

### Run backend static checks

```powershell
cd c:\Users\u\Music\music-platform\backend
ruff check .
black --check .
mypy .
```

## 7. How to debug the frontend

### Start the web UI

```powershell
cd c:\Users\u\Music\music-platform\feishin
npx vite dev --config web.vite.config.ts --host 0.0.0.0 --port 5173
```

### Common frontend debug steps

1. Watch the terminal where Vite is running
2. Open browser developer tools
3. Check the Network tab for failed API calls
4. Check the Console tab for React or JavaScript errors
5. Confirm requests are going to the correct backend URL

### Run frontend checks

```powershell
cd c:\Users\u\Music\music-platform\feishin
npx eslint src
npx tsc --noEmit -p tsconfig.node.json --composite false
npx tsc --noEmit -p tsconfig.web.json --composite false
npx prettier --check .
```

## 8. How to debug Docker services

### Check all service status

```powershell
cd c:\Users\u\Music\music-platform
docker compose ps
```

### See logs for all services

```powershell
docker compose logs --tail=200
```

### See logs for Navidrome

```powershell
docker compose logs --tail=200 navidrome
```

### See logs for Postgres

```powershell
docker compose logs --tail=200 postgres
```

### Restart a single service

```powershell
docker compose restart backend
docker compose restart navidrome
docker compose restart postgres
```

## 9. Port checklist

If something does not open, check these ports:

- `5173`: frontend Vite server
- `8000`: FastAPI backend
- `4533`: Navidrome

Check listening ports:

```powershell
netstat -ano | Select-String ':5173|:8000|:4533'
```

## 10. If something fails

### Frontend does not open

- Confirm Vite is running
- Confirm port `5173` is not blocked
- Read the frontend terminal errors

### Backend does not respond

- Check `docker compose ps`
- Check `docker compose logs --tail=200 backend`
- Check `http://localhost:8000/health`

### Database problems

- Check Postgres logs
- Confirm the `postgres` container is healthy
- Restart backend after Postgres becomes healthy

### Navidrome problems

- Check `docker compose logs --tail=200 navidrome`
- Confirm `http://localhost:4533` opens
- Confirm music files exist under `music`

## 11. Most useful commands

```powershell
cd c:\Users\u\Music\music-platform
docker compose up -d
docker compose ps
docker compose logs --tail=200 backend
docker compose logs --tail=200 navidrome
docker compose down
```

```powershell
cd c:\Users\u\Music\music-platform\feishin
npx vite dev --config web.vite.config.ts --host 0.0.0.0 --port 5173
```

```powershell
cd c:\Users\u\Music\music-platform\backend
python -m pytest
ruff check .
black --check .
mypy .
```

## 12. Recommended order when debugging

1. Check whether the service is running
2. Check the health endpoint or UI URL
3. Read logs
4. Check ports
5. Run tests or type checks
6. Restart only the broken service
7. Re-test after each change
