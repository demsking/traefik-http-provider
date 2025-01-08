Traefik HTTP-Provider is a REST service that allows external services to
register and expose their Traefik HTTP provider JSON content. It saves this
data to the filesystem and allows for retrieval of merged provider data that
has been updated within the last 30 minutes.

## Deployment

Use the official Docker image [`demsking/traefik-http-provider`](https://hub.docker.com/r/demsking/traefik-http-provider)
to run Traefik HTTP-Provider:

```sh
docker run -d --env-file <path_to_env_file> -p 6116:6116 demsking/traefik-http-provider
```

Replace `<path_to_env_file>` with the path to your environment variable file
containing the necessary configurations.

**Traefik HTTP-Provider Documentation**

Open the documentation URL to access the API documentation. In your web browser,
navigate to [http://localhost:6116/docs](http://localhost:6116/docs).

## Environment Variables

The following environment variables can be used to configure the Traefik
HTTP-Provider Docker containers:

**General Configuration**

- **EXPIRATION_MINUTES** (required): Specifies the time window (in minutes)
  for filtering provider configurations. Default is `30`.

- **TZ**: The timezone for the application. Set this to ensure logs and
  schedules match your local timezone. (e.g., `"UTC"`, `"Europe/Paris"`).

**Path Configuration**

- **DATA_PATH**: Directory path where to store providers data files. Default
  is `"/data"`.

- **ROOT_PATH**: The root path under which the application operates, useful
  when the app is hosted behind a reverse proxy. Default is `"/"`.

**Logging and Performance**

- **LOG_FILE**: The file where logs will be stored. If left empty, logs will
  be printed to the console.

- **LOG_LEVEL**: Defines the verbosity of logs. Default is `"INFO"`, but you
  can set it to other levels like `"DEBUG"` for more detailed output.

- **WORKERS**: The number of worker processes to run for the application. This
  is set based on the number of CPU cores but can be overridden for
  performance tuning.
