# Food Store — Frontend

React + TypeScript + Vite + Tailwind CSS

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy `.env.example` to `.env` and fill in values:
   ```bash
   cp .env.example .env
   ```

3. Start dev server:
   ```bash
   npm run dev
   ```

4. App at http://localhost:5173

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |
| `VITE_MP_PUBLIC_KEY` | MercadoPago public key | `TEST-xxxx` |

## Architecture — Feature-Sliced Design

```
app/          # Root: providers, router
pages/        # Page components
features/     # Encapsulated feature logic
entities/     # Domain models
shared/       # UI base, utils, reusable hooks
```

Imports flow: `Pages → Features → Entities → Shared`

## State Management

- **Server state**: TanStack Query 5
- **Client state**: Zustand 4 (cart, session, UI, payments)
- **HTTP**: Axios + JWT interceptor (attach + auto-refresh)
- **Forms**: TanStack Form
- **Charts**: Recharts
- **Payments**: `@mercadopago/sdk-react`

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npx tsc --noEmit` | Type-check without emitting |
