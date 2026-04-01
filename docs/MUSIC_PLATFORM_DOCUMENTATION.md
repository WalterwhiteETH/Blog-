# Music Platform Documentation

## 1. Project Overview

Music Platform is a local development workspace that combines:

- A FastAPI backend for device registration, subscription rules, marketplace flows, holiday-aware recommendations, Ethiopian calendar conversion, and audio analysis.
- A Feishin-based React frontend for the user experience, playback shell, routing, device-aware UI behavior, and future integration with marketplace, payments, and recommendation flows.
- Local infrastructure for Navidrome, Postgres, and backend containers via Docker Compose.

Current local URLs:

- Frontend web UI: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Backend Swagger docs: `http://localhost:8000/docs`
- Backend health check: `http://localhost:8000/health`
- Navidrome: `http://localhost:4533`

## 2. Repository Layout

Main folders:

- `backend/`: Python backend and tests
- `backend/app/`: canonical FastAPI application
- `backend/app/api/routers/`: route definitions
- `backend/app/services/`: backend business logic
- `backend/app/core/`: settings and recommendation catalogs
- `backend/app/models.py`: SQLAlchemy models
- `backend/app/schemas.py`: Pydantic request and response schemas
- `feishin/`: frontend application and web build tooling
- `feishin/src/renderer/`: canonical frontend app code
- `docs/`: project documentation and exported PDF files
- `docker-compose.yml`: local infrastructure orchestration

Runtime-only folders intentionally excluded from Git:

- `postgres-data/`
- `navidrome-data/`
- `music/`

## 3. Architecture Summary

### Backend architecture

The backend runs as a FastAPI app defined in `backend/app/main.py`. It registers routers for core platform logic, marketplace, payments, calendar conversion, recommendations, holiday administration, and audio analysis.

The database layer is defined in `backend/app/db.py` and uses SQLAlchemy. The app supports:

- SQLite for local fallback development
- Postgres when `DATABASE_URL` is provided, including in Docker

On startup, the backend creates tables automatically through SQLAlchemy metadata.

### Frontend architecture

The frontend is a React application bootstrapped from `feishin/src/renderer/main.tsx`. It uses:

- React
- Mantine UI
- TanStack React Query with IndexedDB persistence
- A Feishin renderer architecture
- MemoryRouter-based in-app routing

The app shell in `feishin/src/renderer/app.tsx` initializes:

- theme and notifications
- player providers and audio layers
- settings synchronization
- Telegram Mini App behavior
- device registration with the backend
- bitrate policy selection based on backend device classification

### Infrastructure

`docker-compose.yml` defines three services:

- `postgres`
- `navidrome`
- `backend`

The frontend is started separately through Vite from the `feishin` directory.

## 4. Backend Documentation

### 4.1 Runtime model

Backend startup entrypoints:

- `backend/main.py`: compatibility entrypoint
- `backend/app/main.py`: canonical application

Configuration comes from `backend/app/core/settings.py`. Important settings include:

- `APP_ENV`
- `APP_TITLE`
- `APP_VERSION`
- `ADMIN_API_KEY`
- `DATABASE_URL`
- `DATABASE_ECHO`

Default local behavior:

- `DATABASE_URL` defaults to `sqlite:///./music_platform.db`
- This means the backend can run locally without Docker if needed

Docker behavior:

- Docker Compose passes a Postgres `DATABASE_URL`
- Backend container exposes port `8000`

### 4.2 Core routes

#### `GET /`

Purpose:
- basic service sanity check

Returns:
- running message

#### `GET /health`

Purpose:
- health endpoint for local verification and monitoring

Returns:
- `{"status":"ok"}`

#### `POST /register-device`

Purpose:
- create a user/device record and classify the device capability

Request body:
- `user_agent: string`
- `telegram: boolean = false`
- `telegram_id: string | null`
- `email: string | null`

Response:
- `user_id: int`
- `device_class: "lite" | "standard" | "high"`

Business rules:
- device class is inferred from `user_agent`
- Telegram detection uses request payload plus request headers

#### `GET /can-play/{song_id}/{user_id}`

Purpose:
- determine if a user may play a premium song

Response:
- `allowed: boolean`

Behavior:
- non-premium songs are always allowed
- premium songs require an active subscription

#### `GET /premium-songs`

Purpose:
- list premium Navidrome song ids

Response:
- list of string song ids

#### `GET /stream-policy/{user_id}`

Purpose:
- return the bitrate policy for a user based on device class

Response:
- `device_class`
- `maxBitrate`

Bitrate policy:

- `lite`: `96`
- `standard`: `192`
- `high`: `320`

### 4.3 Marketplace routes

Routes are registered under `/marketplace`.

#### `POST /marketplace/sell-playlist`

Purpose:
- create a public or private marketplace listing for a playlist

Request body:
- `playlist_id: string`
- `seller_id: int`
- `price: float > 0`
- `currency: string = "ETB"`
- `is_public: boolean = true`

Response:
- marketplace listing record

#### `GET /marketplace`

Purpose:
- list public marketplace entries

Response:
- list of marketplace records

#### `POST /marketplace/buy-playlist`

Purpose:
- record a purchase for a public playlist listing

Request body:
- `playlist_id: string`
- `buyer_id: int`

Response:
- `playlist_id`
- `buyer_id`
- `sales_count`
- `purchased: true`

Behavior:
- validates buyer existence
- validates public listing existence
- creates purchase record
- increments `sales_count`

### 4.4 Payment and subscription routes

Routes are registered under `/payment`.

#### `POST /payment/create`

Purpose:
- create a pending payment row for a user

Request body:
- `user_id: int`
- `amount: float > 0`
- `method: "telebirr" | "cbe"`

Response:
- payment record

#### `POST /payment/confirm`

Purpose:
- confirm a payment and activate a 30-day subscription

Request body:
- `payment_id: int`

Response:
- `payment_id`
- `status`
- `subscription_status`
- `expires_at`

Behavior:
- marks payment as confirmed
- creates or updates a subscription
- extends subscription expiration by 30 days from current time

### 4.5 Calendar routes

Routes are registered under `/calendar`.

#### `GET /calendar/ethiopian-now`

Purpose:
- convert the current UTC date into Ethiopian calendar format

Response:
- `year`
- `month`
- `day`

#### `POST /calendar/to-ethiopian`

Purpose:
- convert a Gregorian date into Ethiopian date

Request body:
- `year`
- `month`
- `day`

#### `POST /calendar/to-gregorian`

Purpose:
- convert an Ethiopian date into Gregorian date

Request body:
- `year`
- `month`
- `day`

Implementation notes:

- conversion uses Julian Day Number math
- invalid month/day combinations return HTTP 400

### 4.6 Recommendation routes

Routes are registered under `/recommendations`.

#### `GET /recommendations/playlists`

Purpose:
- return playlist recommendations based on date and Ethiopian holiday rules

Query params:
- `date` optional, format `YYYY-MM-DD`

Response:
- `date`
- `holiday`
- `recommendations`

Behavior:
- checks built-in holiday rules plus active DB rules
- falls back to default recommendations when no holiday matches

#### `GET /recommendations/hybrid-feed`

Purpose:
- return ranked songs from a static catalog with holiday-aware recommendation logic

Query params:
- `date` optional, format `YYYY-MM-DD`
- `location` optional
- `limit` default `10`, min `1`, max `50`

Response:
- `date`
- `holiday`
- `location`
- `model_backend`
- `recommendations`

Behavior:
- builds candidates from the configured song catalog
- ranks them through `HybridRecommender`

### 4.7 Admin holiday routes

Routes are registered under `/admin/holidays`.

All admin holiday routes require header:

- `x-admin-key`

Default local key:

- `admin123`

#### `GET /admin/holidays`

Purpose:
- list all holiday rules

#### `POST /admin/holidays`

Purpose:
- create a holiday rule

Request body:
- `key`
- `name`
- `eth_month`
- `eth_day`
- `recommendations`
- `is_active`

#### `PUT /admin/holidays/{rule_id}`

Purpose:
- update an existing holiday rule

Request body:
- partial update fields

Validation behavior:

- duplicate holiday key returns `409`
- missing rule returns `404`
- invalid admin key returns `401`

### 4.8 Audio analysis route

#### `POST /analyze-audio`

Purpose:
- upload a music file, extract audio features, and classify Qenet mode

Accepted file types:

- `.mp3`
- `.wav`

Optional form fields:

- `artist`

Response:
- `Genre`
- `Qenet Mode`
- `Tempo`

Current operational caveat:

- this route depends on optional audio-analysis dependencies such as `numpy` and `librosa`
- the route now fails gracefully with HTTP `503` if the required audio modules are not installed
- this protects overall backend startup from failing

### 4.9 Data model

Main SQLAlchemy entities:

- `User`
- `Subscription`
- `PremiumContent`
- `PlaylistMarketplace`
- `PlaylistPurchase`
- `Payment`
- `HolidayRule`
- `MusicMetadata`
- `UserPlaybackLog`

Relationship summary:

- `User` owns subscriptions, payments, marketplace listings, and purchases
- `PlaylistMarketplace` owns related purchases
- `MusicMetadata` stores extracted audio features and metadata for analyzed files

### 4.10 Business logic currently implemented

Implemented backend rules include:

- user/device creation
- Telegram request detection
- device capability classification based on user agent
- premium playback gating through active subscriptions
- marketplace listing and purchase recording
- payment confirmation and 30-day subscription activation
- Ethiopian date conversion
- holiday-driven playlist recommendations
- hybrid song recommendation ranking
- holiday rule management for admins

### 4.11 Backend testing and operation

Useful backend URLs:

- `http://localhost:8000/`
- `http://localhost:8000/health`
- `http://localhost:8000/docs`

Local backend run command:

```powershell
cd c:\Users\u\Music\music-platform\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Backend checks:

```powershell
cd c:\Users\u\Music\music-platform\backend
python -m pytest
ruff check .
black --check .
mypy .
```

## 5. Frontend Documentation

### 5.1 Frontend runtime model

The frontend is a web/dev build of the Feishin renderer app. It starts from:

- `feishin/src/renderer/main.tsx`

It creates a React root, wires up React Query persistence through IndexedDB, and renders the top-level `App`.

### 5.2 App provider tree

The app in `feishin/src/renderer/app.tsx` wraps the UI with:

- `MantineProvider`
- `Notifications`
- `WebAudioContext.Provider`
- `PlayerProvider`
- `AudioPlayers`
- `AppRouter`

It also lazy-loads a release notes modal.

### 5.3 Device-aware frontend behavior

Current frontend behavior includes:

- detection of Telegram Mini App mode
- detection of low-RAM mode
- toggling CSS body classes for Telegram and low-RAM experiences
- calling backend `register-device`
- mapping backend device class to transcoding bitrate

Current bitrate mapping:

- `lite`: `96`
- `high`: `320`
- fallback/default: `192`

If backend registration fails, the frontend keeps the current bitrate settings.

### 5.4 Telegram behavior

When Telegram Mini App mode is detected, the frontend:

- extracts Telegram user id
- stores Telegram state in local storage
- attempts a backend login request through `telegramLogin`

Current note:

- the frontend expects a Telegram login API, but that route is not currently present in the backend router set

### 5.5 Routing model

Routing is handled through:

- `feishin/src/renderer/router/app-router.tsx`
- `feishin/src/renderer/router/modules/consumer-routes.tsx`

The router uses:

- `MemoryRouter`
- authentication outlet
- titlebar outlet
- app outlet
- modal provider
- router error boundary

Current consumer routes include:

- home
- search
- library
- now playing
- favorites
- settings
- marketplace
- payments
- profile

Initial landing behavior:

- Telegram mode defaults to home
- mobile widths default to home
- non-mobile defaults to now playing

### 5.6 Current route implementation status

Some frontend route paths are already present as navigation targets, but not all have dedicated screens yet.

At the moment:

- `home`, `search`, `library`, and `now playing` have dedicated route components
- `favorites`, `settings`, `marketplace`, `payments`, and `profile` currently route to the home screen component

That means route structure exists, but part of the product surface is still placeholder or shared-screen backed.

### 5.7 Frontend API client

The backend integration client lives in:

- `feishin/src/renderer/api/client.ts`

Base URL resolution:

- `BACKEND_API` env var, if present
- `VITE_BACKEND_API` env var, if present
- otherwise `http://localhost:8000`

Current exported frontend API helpers:

- `getUserProfile`
- `checkSubscription`
- `getMarketplacePlaylists`
- `purchasePlaylist`
- `createPayment`
- `getRecommendations`
- `registerDevice`
- `telegramLogin`

### 5.8 Frontend operational command

Run the frontend locally with:

```powershell
cd c:\Users\u\Music\music-platform\feishin
npx vite dev --config web.vite.config.ts --host 0.0.0.0 --port 5173
```

Open:

- `http://localhost:5173`

### 5.9 Frontend quality checks

```powershell
cd c:\Users\u\Music\music-platform\feishin
npx eslint src
npx tsc --noEmit -p tsconfig.node.json --composite false
npx tsc --noEmit -p tsconfig.web.json --composite false
npx prettier --check .
```

## 6. Current Backend and Frontend Integration Status

The frontend and backend are only partially aligned right now.

Confirmed mismatches:

- backend exposes `/payment/create`, while frontend calls `/payments/create`
- backend exposes `/marketplace`, while frontend calls `/marketplace/playlists`
- backend exposes `/marketplace/buy-playlist`, while frontend calls `/marketplace/buy`
- backend exposes `/recommendations/playlists` and `/recommendations/hybrid-feed`, while frontend calls `/recommendations`
- frontend references `/telegram/login`, but the backend router set does not currently expose that route
- frontend references `/users/{id}/profile`, but the backend router set does not currently expose that route
- frontend references `/subscription/check`, but the backend router set does not currently expose that route

What is aligned today:

- frontend device registration uses `/register-device`
- backend stream-policy logic exists for future frontend use
- frontend bitrate policy behavior is conceptually aligned with backend device classes

Recommended next integration step:

- either update frontend API calls to match the backend routes
- or add compatibility routes in the backend that match the frontend expectations

## 7. Local Run, Test, and Debug Guide

### 7.1 Start backend services with Docker

```powershell
cd c:\Users\u\Music\music-platform
docker compose up -d
```

This starts:

- `postgres`
- `navidrome`
- `backend`

### 7.2 Start frontend

```powershell
cd c:\Users\u\Music\music-platform\feishin
npx vite dev --config web.vite.config.ts --host 0.0.0.0 --port 5173
```

### 7.3 Check service status

```powershell
cd c:\Users\u\Music\music-platform
docker compose ps
docker compose logs --tail=200 backend
docker compose logs --tail=200 navidrome
docker compose logs --tail=200 postgres
```

### 7.4 Backend smoke tests

Browser:

- `http://localhost:8000/`
- `http://localhost:8000/health`
- `http://localhost:8000/docs`

PowerShell:

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/
```

### 7.5 Frontend smoke tests

- confirm Vite starts without errors
- open `http://localhost:5173`
- inspect browser console and network tabs

### 7.6 Port checklist

Expected ports:

- `5173`: frontend
- `8000`: backend
- `4533`: Navidrome

Port check:

```powershell
netstat -ano | Select-String ':5173|:8000|:4533'
```

### 7.7 Stop services

Frontend:

- press `Ctrl+C` in the frontend terminal

Docker:

```powershell
cd c:\Users\u\Music\music-platform
docker compose down
```

## 8. Current Limitations

Known limitations in the current state:

- frontend and backend API contracts are not fully synchronized
- some frontend routes still reuse the home screen as placeholders
- Telegram login flow is not fully backed by a server route
- profile and subscription-check APIs referenced by the frontend are missing in the backend
- audio-analysis requires optional dependencies that are not guaranteed to be installed locally
- Docker availability depends on the local Docker engine being active

## 9. Recommended Next Work

Recommended near-term engineering tasks:

- align frontend API client paths with backend routes
- add missing backend endpoints expected by the frontend, or refactor the frontend to use existing routes
- build real marketplace, profile, payment, and settings screens instead of placeholder routes
- define end-to-end auth and Telegram user handling
- formalize DB migrations instead of relying only on SQLAlchemy auto-create
- decide whether audio-analysis is optional or required for baseline local development

## 10. Quick Reference

Backend only:

```powershell
cd c:\Users\u\Music\music-platform\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Frontend only:

```powershell
cd c:\Users\u\Music\music-platform\feishin
npx vite dev --config web.vite.config.ts --host 0.0.0.0 --port 5173
```

Docker stack:

```powershell
cd c:\Users\u\Music\music-platform
docker compose up -d
docker compose ps
docker compose down
```
