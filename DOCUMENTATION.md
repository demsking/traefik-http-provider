Traefik HTTP Provider is a REST service that allows external services to
register and expose their Traefik HTTP provider JSON content. It now stores
data in Redis for concurrent-safe access and automatically expires data after
a defined period (default 30 minutes).

## Deployment

Use the official Docker image [`demsking/traefik-http-provider`](https://hub.docker.com/r/demsking/traefik-http-provider)
and Redis 8 in a Docker Compose setup.

### Example `docker-compose.yml`

```yaml
version: '3.8'

services:
  server:
    image: demsking/traefik-http-provider:latest
    restart: unless-stopped
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - EXPIRATION_MINUTES=10
    ports:
      - "6116:6116"

  redis:
    image: redis:8-alpine
    restart: unless-stopped
    command:
      - redis-server
      - "--appendonly"
      - "yes"
      - "--appendfsync"
      - "everysec"
      - "--save"
      - "60 1"
      - "--maxmemory-policy"
      - "allkeys-lru"
      - "--bind"
      - "0.0.0.0"
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
````

Once deployed, access the API documentation at
[http://localhost:6116/docs](http://localhost:6116/docs).

---

## Environment Variables

### General Configuration

* **EXPIRATION_MINUTES** *(required)*
  Time window (in minutes) for filtering provider configurations. Default: `10`.

### Redis Configuration

* **REDIS_HOST** *(required)*
  Redis hostname or service name. Example: `redis`.

* **REDIS_PORT**
  Redis port. Default: `6379`.

* **REDIS_DB**
  Redis database index to use. Default: `0`.

### Path Configuration

* **ROOT_PATH**
  Root path under which the app operates (useful behind a reverse proxy). Default: `"/"`.

### Logging

* **LOG_FILE**
  Path to a log file. If unset, logs are printed to stdout.

* **LOG_LEVEL**
  Log verbosity level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). Default: `INFO`.

---

### Start the Stack

```sh
docker compose up -d
```

### Check Logs

```sh
docker compose logs -f server
```

### Test API

```sh
curl http://localhost:6116/api/provider
```
