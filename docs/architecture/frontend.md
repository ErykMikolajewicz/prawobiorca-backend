# Frontend

## 1. Introduction

The frontend is the user-facing layer of Prawobiorca. It is a single-page application (SPA) written in **Vue 3**, living in the `prawobiorca-frontend/` directory of this repository, next to the Python services described in [General information](architecture.md).

It talks to `core-service` exclusively over the HTTP REST API — it has no direct access to the database, the object storage, or any of the compute services.

---

## 2. Technology Stack

* **Vue 3** with the Composition API and `<script setup>` single-file components.
* **TypeScript**, type-checked with `vue-tsc` (the `tsc` CLI cannot resolve `.vue` imports).
* **Vite** as the dev server and production bundler.
* **Vue Router** for client-side routing, in HTML5 history mode.
* **Pinia** for shared application state.
* **Element Plus** as the component library, including its dark theme variables.
* **axios** as the HTTP client.
* **Vitest** for unit tests, **oxlint** + **ESLint** for linting and **oxfmt** for formatting.

Required toolchain versions are declared in `prawobiorca-frontend/package.json`: Node `^24.15.0` (`engines`) and pnpm `11.24.0` (`packageManager`, enabled through Corepack).

---

## 3. Project Structure

All application code lives in `prawobiorca-frontend/src`:

* **`api/`** — one module per API area (`auth`, `accounts`, `cases`, `documents`, `regulations`), plus the shared axios instance.
* **`types/api/`** — TypeScript types mirroring the request/response contracts of `core-service`.
* **`pages/`** — route-level views (`MainPage`, `SearchPage`, `CasePage`, `LoginPage`, `RegisterPage`).
* **`components/`** — reusable components organised by **Atomic Design**: `atoms/` (badges, buttons), `molecules/` (cards, dialogs, selectors) and `organisms/` (navbar, footer, forms, lists).
* **`composables/`** — reusable stateful logic (dark mode, regulation upload, preparation status polling).
* **`stores/`** — Pinia stores; currently `auth`, holding the session state.
* **`router/`** — route definitions.
* **`utils/`**, **`assets/`** — error helpers and global styles.
* **`__tests__/`** — unit tests, placed in a `__tests__` directory next to the code they cover.

`src/main.ts` is the entry point: it wires Pinia, the router and Element Plus, registers the session-expiry handler and resolves the current session before mounting the app.

---

## 4. API Integration

* The shared axios instance (`src/api/axios.ts`) is created with `baseURL` taken from the `VITE_PRAWOBIORCA_API_URL` environment variable, defaulting to `/api`. Copy `.env.example` to `.env` to override it for local development.
* `withCredentials` is enabled — access and refresh tokens are carried in cookies, never stored by the application itself.
* A response interceptor retries a request once after refreshing the tokens when `core-service` answers `401`. Concurrent refreshes share a single in-flight request, and the auth endpoints themselves are excluded from this path.
* When the refresh fails, the session-expiry handler resets the auth store and redirects to the login page.

`prawobiorca-frontend/api.json` is a dump of the `core-service` OpenAPI schema, kept for reference when writing the API modules and their types.

---

## 5. Build and Deployment

`prawobiorca-frontend/Containerfile` defines a two-stage build: the first stage installs dependencies with pnpm and runs `pnpm run build`, the second copies the resulting `dist/` into an **nginx:alpine** image listening on port `8000`. The bundled `nginx.conf` falls back to `index.html` for unknown paths, which is what the history-mode router requires.

The image is built as `prawobiorca-frontend` by `poe build_frontend` (and as part of `poe build_images`).

In both deployment environments the frontend is served at the root path, behind the same entry point as the API:

* **On-Premise**: `deploy/local/prawobiorca-frontend.yaml`, routed by the nginx ingress defined in `deploy/local/nginx-config.yaml` — `/` goes to the frontend, `/api` to `core-service`.
* **Cloud (GCP)**: `deploy/gcp/prawobiorca-frontend.yaml`, routed by `deploy/gcp/ingress.yaml`.

---

## 6. Development Commands

All commands are run from the `prawobiorca-frontend/` directory:

| Command | Purpose |
| --- | --- |
| `pnpm install` | Install dependencies. |
| `pnpm dev` | Vite dev server with hot reload. |
| `pnpm build` | Type-check and build the production bundle. |
| `pnpm test:unit` | Run unit tests with Vitest. |
| `pnpm lint` | Run oxlint and ESLint with autofix. |
| `pnpm format` | Format `src/` with oxfmt. |

A JetBrains IDE (PyCharm Professional, free for students under a non-commercial licence) with the Vue plugin is recommended, so that the whole repository — Python services and frontend — is handled by a single IDE. In VS Code, the [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) extension is required to make the TypeScript language service aware of `.vue` types.
