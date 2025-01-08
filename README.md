# Traefik HTTP-Provider

[![Buy me a beer](https://img.shields.io/badge/Buy%20me-a%20beer-1f425f.svg)](https://www.buymeacoffee.com/demsking)

Traefik HTTP-Provider is a REST service that allows external services to register
and expose their Traefik HTTP provider JSON content. It saves this data to the
filesystem and allows for retrieval of merged provider data that has been
updated within the last 30 minutes.

## Features

- **POST `/api/config/{service_id}`**: Register or update a service's Traefik
  HTTP provider configuration.

- **GET `/api/config`**: Retrieve a merged configuration of all providers
  updated in the last 30 minutes.

## HTTP-Provider Documentation

Open the documentation URL to access the API documentation. In your web browser,
navigate to [https://demsking.gitlab.io/traefik-http-provider](https://demsking.gitlab.io/traefik-http-provider).

## Contribute

Please follow [CONTRIBUTING.md](https://gitlab.com/demsking/traefik-http-provider/blob/main/CONTRIBUTING.md).

## Versioning

Given a version number `MAJOR.MINOR.PATCH`, increment the:

- `MAJOR` version when you make incompatible API changes,
- `MINOR` version when you add functionality in a backwards-compatible manner,
  and
- `PATCH` version when you make backwards-compatible bug fixes.

Additional labels for pre-release and build metadata are available as extensions
to the `MAJOR.MINOR.PATCH` format.

See [SemVer.org](https://semver.org/) for more details.

## License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.
You may obtain a copy of the License at [LICENSE](https://gitlab.com/demsking/traefik-http-provider/blob/main/LICENSE).
