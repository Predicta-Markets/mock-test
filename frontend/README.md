# Frontend (Next.js + shadcn/ui)

## Stack

- Next.js 14 App Router (TypeScript, React 18)
- Tailwind CSS + shadcn/ui component primitives
- TanStack Query for data fetching
- pnpm for package management

## Local setup

```bash
cd capital-gains/frontend
pnpm install
cp .env.example .env            # adjust NEXT_PUBLIC_API_URL if needed
pnpm dev
```

## Scripts

| Command      | Description                 |
| ------------ | --------------------------- |
| `pnpm dev`   | Start dev server w/ HMR     |
| `pnpm build` | Next.js production build    |
| `pnpm start` | Run production server       |
| `pnpm lint`  | Run ESLint                  |

## API Contract

The frontend expects the FastAPI backend from `../backend` to expose:

- `GET /markets` – list markets
- `POST /markets` – create market
- `GET /markets/{id}` – market detail
- `POST /markets/{id}/orders` – buy/sell
- `GET /markets/{id}/positions` – holdings summary
- `POST /markets/{id}/resolve` – resolution

Set `NEXT_PUBLIC_API_URL` so these calls resolve correctly (Docker Compose does this automatically).

