# Deployment Guide

This document provides detailed instructions for deploying the SCC Criminal Cases RAG system in various environments.

## Docker Deployment

### Prerequisites

- Docker and Docker Compose
- OpenAI API key for embeddings and generation (or Anthropic API key as an alternative)

### Basic Deployment

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/scc-criminal-rag.git
   cd scc-criminal-rag
   ```

2. Create a `.env` file in the project root with your API keys:

   ```bash
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

3. Build and start the containers:

   ```bash
   docker-compose up -d
   ```

4. Access the web interface at `http://localhost:8080`

## Multi-Architecture Deployment

The system now supports deployment on both x86/AMD64 and ARM64 architectures. This allows deployment on a variety of hardware, including ARM-based servers and Apple Silicon Macs.

### Building Multi-Architecture Images

1. Use the provided `build_multiarch.sh` script to build images for multiple architectures:

   ```bash
   ./build_multiarch.sh
   ```

   This script:

   - Logs into Docker Hub (will prompt for credentials)
   - Sets up Docker Buildx for multi-architecture builds
   - Builds and pushes images for both AMD64 and ARM64 architectures

2. The multi-architecture images are published to Docker Hub and can be pulled automatically based on your server's architecture.

### ARM Deployment Considerations

When deploying on ARM architecture:

1. Ensure your server meets the minimum requirements:

   - ARM64 CPU
   - At least 4GB RAM
   - At least 10GB free disk space

2. For optimal performance on ARM:
   - Adjust container memory limits as needed
   - Consider using swap if RAM is limited

## Reverse Proxy Configuration

The application is designed to work behind a reverse proxy, which can provide additional benefits like SSL termination, load balancing, and caching.

### Nginx Reverse Proxy Configuration

Below is a sample Nginx configuration for setting up a reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Frontend proxy
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}
```

### Apache Reverse Proxy Configuration

For Apache, use the following configuration:

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /path/to/fullchain.pem
    SSLCertificateKeyFile /path/to/privkey.pem
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1

    # Frontend proxy
    ProxyPass / http://localhost:8080/
    ProxyPassReverse / http://localhost:8080/

    # Backend API proxy
    ProxyPass /api/ http://localhost:8000/
    ProxyPassReverse /api/ http://localhost:8000/

    # Let's Encrypt ACME challenge
    Alias /.well-known/acme-challenge/ /var/www/html/.well-known/acme-challenge/
</VirtualHost>
```

## SSL/TLS Certificate Setup

For production deployments, it's recommended to secure your site with SSL/TLS certificates.

### Let's Encrypt Certificates

1. Install Certbot:

   ```bash
   # On Ubuntu/Debian
   apt-get update
   apt-get install certbot

   # On CentOS/RHEL
   yum install certbot
   ```

2. Obtain a certificate:

   ```bash
   # For Nginx
   certbot --nginx -d your-domain.com

   # For Apache
   certbot --apache -d your-domain.com

   # Standalone (if not using Nginx/Apache)
   certbot certonly --standalone -d your-domain.com
   ```

3. Certificate automatic renewal:

   ```bash
   # Test renewal
   certbot renew --dry-run

   # Set up automatic renewal
   echo "0 0,12 * * * root python -c 'import random; import time; time.sleep(random.random() * 3600)' && certbot renew" | sudo tee -a /etc/crontab > /dev/null
   ```

### Cloudflare SSL Configuration

If using Cloudflare as your DNS provider and CDN:

1. Set up Cloudflare for your domain
2. In the SSL/TLS section, choose the appropriate SSL mode:
   - Full: Encrypts traffic between Cloudflare and your server (requires valid SSL certificate on your server)
   - Full (Strict): Similar to Full but verifies your server's certificate (recommended)
   - Flexible: Encrypts traffic between users and Cloudflare, but not between Cloudflare and your server (less secure)

## Troubleshooting

### Common Issues

1. **Container fails to start**

   - Check container logs: `docker logs scc-criminal-rag-backend-1`
   - Verify environment variables are correctly set
   - Ensure volumes are properly mounted

2. **API connection errors**

   - Verify reverse proxy configuration
   - Check network connectivity between containers
   - Ensure API paths are correctly mapped

3. **ARM architecture issues**

   - Verify container images are compatible with ARM64
   - Check for any platform-specific dependencies
   - Monitor resource usage, as ARM may have different performance characteristics

4. **SSL certificate problems**
   - Verify certificate paths in nginx/apache configuration
   - Check certificate expiration dates
   - Ensure certificates form a complete chain

For additional help, consult the project's issue tracker or contact the maintainers.
