# BloomAI — Frontend

Vue 3 + Vite single-page app for BloomAI. Three routes: upload a PDF (`/`),
answer the generated questions (`/test`), review graded results (`/results`).
State lives in a Pinia store (`src/stores/testStore.js`); every backend call
goes through `src/services/apiService.js`.

## Setup

```sh
npm install
cp .env.example .env   # optional: point VITE_API_BASE_URL at your backend
npm run dev            # http://localhost:5173
```

`npm run build` produces a static bundle in `dist/`. The Django backend must be
running for uploads and grading to work — see the root README.
