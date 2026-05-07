# Multi-stage build for frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Copy root package files
COPY package*.json turbo.json ./

# Copy app-specific files
COPY apps/frontend ./apps/frontend
COPY apps/backend/package.json ./apps/backend/
COPY packages ./packages

# Install dependencies
RUN npm ci

# Build frontend
RUN npm run build -w apps/frontend

# Production stage
FROM node:18-alpine AS runtime

WORKDIR /app

# Copy only production files
COPY --from=builder /app/apps/frontend/dist ./dist
COPY --from=builder /app/apps/frontend/package*.json ./

# Install nginx
RUN apk add --no-cache nginx

# Copy nginx config
COPY apps/frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
