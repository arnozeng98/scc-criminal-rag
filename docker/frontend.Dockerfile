FROM node:16-alpine

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy frontend code
COPY frontend/ ./

# Build for production
RUN npm run build

# Use Nginx to serve the static files
FROM nginx:alpine

# Copy built assets from the builder stage
COPY --from=0 /app/build /usr/share/nginx/html

# Copy custom Nginx config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"] 