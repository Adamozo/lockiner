# Frontend Dockerfile (Nuxt 4 + Node 20)

FROM node:20-alpine

# Metadata
LABEL maintainer="LockIner"
LABEL description="Nuxt 4 frontend for personal finance management"

# Set working directory
WORKDIR /app

# Install system dependencies (for node-gyp, better-sqlite3, etc)
RUN apk add --no-cache \
    curl \
    python3 \
    make \
    g++

# Copy package files first (Docker layer caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose Nuxt port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

# Run Nuxt dev server
# For production: npm run build && npm run preview
CMD ["npm", "run", "dev"]
