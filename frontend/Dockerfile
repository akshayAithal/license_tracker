# Frontend Dockerfile - Multi-stage build
# Stage 1: Build the React frontend
FROM node:18-alpine as builder

WORKDIR /app/ui

# Enable proxy for inbound traffic (if needed)
ARG HTTP_PROXY
ARG HTTPS_PROXY
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}

# Copy UI source files
COPY license_tracker/ui/package*.json ./
COPY license_tracker/ui/.babelrc ./
COPY license_tracker/ui/webpack.config.js ./

# Set Node memory limit and OpenSSL legacy provider for compatibility
ENV NODE_OPTIONS="--max-old-space-size=4096 --openssl-legacy-provider"

# Install dependencies
RUN npm config set registry https://registry.npmjs.org/ && \
    npm config set strict-ssl false && \
    npm install --legacy-peer-deps

# Copy source files
COPY license_tracker/ui/js ./js
COPY license_tracker/ui/assets ./assets
COPY license_tracker/ui/home.html ./home.html

# Build the frontend
RUN npm run build

# Stage 2: Production server
FROM node:18-alpine as production

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S frontend -u 1001

WORKDIR /app

# Copy package files and install production dependencies only
COPY frontend/package*.json ./

ARG HTTP_PROXY
ARG HTTPS_PROXY
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}

RUN npm install --only=production && npm cache clean --force

# Clear proxy after npm install
ENV http_proxy=
ENV https_proxy=

# Copy server files
COPY frontend/server.js ./

# Create public directory structure
RUN mkdir -p public/assets

# Copy built assets from builder stage
COPY --from=builder /app/ui/assets ./public/assets
COPY --from=builder /app/ui/home.html ./public/index.html

# Set ownership to non-root user
RUN chown -R frontend:nodejs /app

# Switch to non-root user
USER frontend

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Start the server
CMD ["node", "server.js"]
