# /etc/nginx/sites-available/lockiner.com
# Full Nginx Configuration for lockiner.com
#
# After creating this file:
#   1. sudo ln -s /etc/nginx/sites-available/lockiner.com /etc/nginx/sites-enabled/
#   2. sudo nginx -t
#   3. sudo systemctl reload nginx
#   4. sudo certbot --nginx -d lockiner.com -d www.lockiner.com

# ============================================
# HTTP Server - Redirect to HTTPS
# ============================================
server {
    listen 80;
    listen [::]:80;
    server_name lockiner.com www.lockiner.com;

    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        allow all;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# ============================================
# HTTPS Server - Main Configuration
# ============================================
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name lockiner.com www.lockiner.com;

    # ----------------------------------------
    # SSL Configuration
    # ----------------------------------------
    # These paths will be configured by Certbot
    ssl_certificate /etc/letsencrypt/live/lockiner.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lockiner.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/lockiner.com/chain.pem;

    # SSL settings (inherited from main nginx.conf, can override here)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # ----------------------------------------
    # Security Headers
    # ----------------------------------------
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    # Content Security Policy - adjust as needed for your application
    # add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'self';" always;

    # ----------------------------------------
    # Logging
    # ----------------------------------------
    access_log /var/log/nginx/lockiner.com.access.log detailed;
    error_log /var/log/nginx/lockiner.com.error.log warn;

    # ----------------------------------------
    # Root and Index
    # ----------------------------------------
    root /var/www/lockiner.com/html;
    index index.html index.htm;

    # ----------------------------------------
    # Rate Limiting
    # ----------------------------------------
    limit_req zone=general burst=20 nodelay;
    limit_conn addr 10;

    # ----------------------------------------
    # Static Files Location
    # ----------------------------------------
    location / {
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
    }

    # ----------------------------------------
    # API Proxy (Backend)
    # ----------------------------------------
    # Uncomment and configure if you have a backend API
    location /api/ {
        # Rate limit for API
        limit_req zone=general burst=50 nodelay;

        # Proxy settings
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        # WebSocket support (if needed)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # ----------------------------------------
    # Login/Auth Rate Limiting
    # ----------------------------------------
    location /api/auth/login {
        limit_req zone=login burst=5 nodelay;

        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ----------------------------------------
    # WebSocket Location (if needed)
    # ----------------------------------------
    # location /ws/ {
    #     proxy_pass http://127.0.0.1:8000;
    #     proxy_http_version 1.1;
    #     proxy_set_header Upgrade $http_upgrade;
    #     proxy_set_header Connection "upgrade";
    #     proxy_set_header Host $host;
    #     proxy_set_header X-Real-IP $remote_addr;
    #     proxy_read_timeout 86400;
    # }

    # ----------------------------------------
    # Health Check Endpoint
    # ----------------------------------------
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # ----------------------------------------
    # Deny Access to Hidden Files
    # ----------------------------------------
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Deny access to sensitive files
    location ~* ^/(README|LICENSE|CHANGELOG|composer\.(json|lock)|package\.(json|lock)|yarn\.lock|\.git|\.env) {
        deny all;
        access_log off;
        log_not_found off;
    }

    # ----------------------------------------
    # Favicon and Robots
    # ----------------------------------------
    location = /favicon.ico {
        log_not_found off;
        access_log off;
    }

    location = /robots.txt {
        log_not_found off;
        access_log off;
        allow all;
    }

    # ----------------------------------------
    # Error Pages
    # ----------------------------------------
    error_page 404 /404.html;
    location = /404.html {
        root /var/www/lockiner.com/html;
        internal;
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /var/www/lockiner.com/html;
        internal;
    }
}

# ============================================
# WWW to Non-WWW Redirect (Optional)
# ============================================
# Uncomment if you want to redirect www to non-www
# server {
#     listen 443 ssl http2;
#     listen [::]:443 ssl http2;
#     server_name www.lockiner.com;
#
#     ssl_certificate /etc/letsencrypt/live/lockiner.com/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/lockiner.com/privkey.pem;
#
#     return 301 https://lockiner.com$request_uri;
# }
