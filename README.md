# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## FastAPI Backend

Backend lives in `backend/main.py` and exposes:

- `GET /api/health`
- `GET /api/playlists`
- `POST /api/playlists`
- `POST /api/checkout-session`
- `GET /api/auth/google/url`
- `GET /api/auth/google/callback`
- `POST /api/auth/google/verify`
- `GET /api/auth/me`

State persistence:

- Runtime data is persisted to `backend/data/state.json` (playlists, purchases, artist support).
- Seed data is used only when no persisted state exists.

Run backend + frontend together:

```bash
pip install -r backend/requirements.txt
npm run dev:fastapi
```
