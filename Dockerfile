# Use official Bun image (Bun is fast & great for elizaOS-style TS projects)
FROM oven/bun:1 AS base

WORKDIR /app

# Copy monorepo essentials
COPY package.json bun.lockb* ./
COPY runtime ./runtime
COPY agents ./agents
COPY nodes ./nodes
COPY spaces ./spaces
COPY skills ./skills

# Install deps (runtime + core)
RUN bun install --frozen-lockfile

# Build TS → JS if needed (optional — Bun can run TS directly)
RUN bun run --cwd runtime build   # if you added "build" script

# Production image (slim)
FROM base AS production
CMD ["bun", "run", "--cwd", "runtime", "index.ts"]
