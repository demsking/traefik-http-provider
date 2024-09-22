Traefik HTTP-Provider is a REST service that allows external services to
register and expose their Traefik HTTP provider JSON content. It saves this data
to an SQLite database and allows for retrieval of merged provider data that has
been updated within the last 30 minutes.

## Deployment

Use the official Docker image [`demsking/traefik-http-provider`](https://hub.docker.com/r/demsking/traefik-http-provider)
to run Traefik HTTP-Provider:

```sh
docker run -d --env-file <path_to_env_file> -p 6116:6116 demsking/traefik-http-provider
```

Replace `<path_to_env_file>` with the path to your environment variable file
containing the necessary configurations.

**Traefik HTTP-Provider API**

Open the documentation URL to access the API documentation. In your web browser,
navigate to [http://localhost:6116/docs](http://localhost:6116/docs).

## Environment Variables

The following environment variables can be used to configure the Traefik
HTTP-Provider Docker containers:

| Variable Name         | Description                                                                   | Default Value                 |
|-----------------------|-------------------------------------------------------------------------------|-------------------------------|
| `EXPIRATION_MINUTES`  | Specifies the time window (in minutes) for filtering provider configurations. | `30`                          |
| `PROVIDERS_DATABASE`  | The path to the SQLite database file for storing provider configurations      | `"/data/providers.db"`        |
| `LOG_LEVEL`           | Logging level                                                                 | `"info"`                      |
| `LOG_FILE`            | Log file path                                                                 |                               |
| `WORKER`              | Number of worker instances                                                    | `multiprocessing.cpu_count()` |

## Running Behind a TLS Termination Proxy

If you need to run Traefik HTTP-Provider behind a TLS termination proxy (such as
Nginx or Traefik), you must inform Traefik HTTP-Provider to trust the headers
sent by the proxy that indicate the application is running behind HTTPS. This is
done by using the `--proxy-headers` option:

```sh
docker run -d -p 6116:6116 demsking/traefik-http-provider --proxy-headers
```

By adding the `--proxy-headers` option, Traefik HTTP-Provider will correctly
interpret the proxy headers indicating that it is operating behind an HTTPS
proxy. This ensures that the application behaves as expected in a secure
environment.
