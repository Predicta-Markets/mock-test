FROM node:20-alpine

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@8.15.9 --activate

COPY package.json ./
COPY tsconfig.json ./
COPY next.config.js ./
COPY postcss.config.js ./
COPY tailwind.config.ts ./

RUN pnpm install

COPY . .

EXPOSE 3000

CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3000"]

