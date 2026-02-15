# Nginx Configuration for WebTics

## For Nginx Proxy Manager (NPM)

If you're using Nginx Proxy Manager:

1. Add a new Proxy Host in NPM
2. Set **Domain Names**: `webtics.yourdomain.com`
3. Set **Scheme**: `http`
4. Set **Forward Hostname/IP**: `webtics_backend` (or `localhost` if on same machine)
5. Set **Forward Port**: `8013`
6. Enable **Websockets Support**: No
7. Enable **Block Common Exploits**: Yes
8. Enable **SSL** with Let's Encrypt (for production)

### Custom Nginx Configuration in NPM

In the "Advanced" tab, add:

```nginx
# Client upload size for batch events
client_max_body_size 10M;

# CORS headers for web games
add_header Access-Control-Allow-Origin *;
add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
add_header Access-Control-Allow-Headers 'Content-Type, Authorization';

# Compression
gzip on;
gzip_types application/json;
gzip_min_length 1000;
```

## For Standard Nginx

1. Copy `webtics.conf` to `/etc/nginx/sites-available/`
2. Create symlink: `sudo ln -s /etc/nginx/sites-available/webtics.conf /etc/nginx/sites-enabled/`
3. Update `server_name` to your domain
4. Test config: `sudo nginx -t`
5. Reload: `sudo systemctl reload nginx`

## For Docker Compose Nginx

Add nginx service to your `docker-compose.yml`:

```yaml
  nginx:
    image: nginx:alpine
    container_name: webtics_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/webtics.conf:/etc/nginx/conf.d/default.conf
      - ./nginx/ssl:/etc/nginx/ssl  # For SSL certificates
    depends_on:
      - backend
```

## Testing

1. Start backend: `docker-compose up -d`
2. Test health check: `curl http://localhost/health`
3. Test API: `curl http://localhost/api/v1/`

## Production Checklist

- [ ] Use HTTPS with valid SSL certificate
- [ ] Restrict CORS to your game domains only
- [ ] Set up rate limiting
- [ ] Enable fail2ban or similar
- [ ] Set up monitoring/alerts
- [ ] Configure log rotation
- [ ] Use strong SSL ciphers
- [ ] Enable security headers
