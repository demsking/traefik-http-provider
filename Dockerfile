#
## Stage 1: Builder
FROM python:3.11-alpine AS builder

ENV UV_LINK_MODE=copy

# Set the shell to /bin/ash and enable pipefail
SHELL ["/bin/ash", "-eo", "pipefail", "-c"]

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory
WORKDIR /opt/demsking

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-dev --locked --no-install-project --compile-bytecode

# Sync the project
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --no-dev --locked \
    && uv build

#
## Stage 2: Final
FROM python:3.11-alpine

ENV PATH="/opt/demsking/.venv/bin:$PATH"
ENV PYTHONPATH="/opt/demsking/.venv/lib/python3.11/site-packages"
ENV PYTHONUNBUFFERED="1"
ENV PYTHONDONTWRITEBYTECODE="1"

# Logging configuration
ENV LOG_LEVEL="INFO"
ENV LOG_FILE=

# Set the shell to /bin/ash and enable pipefail
SHELL ["/bin/ash", "-eo", "pipefail", "-c"]

# Copy the environment, but not the source code
COPY --from=builder /opt/demsking/.venv /opt/demsking/.venv
COPY --from=builder /opt/demsking/src /opt/demsking/src
COPY pyproject.toml /opt/demsking/src/pyproject.toml
COPY DOCUMENTATION.md /opt/demsking/src/DOCUMENTATION.md

# Expose the port
EXPOSE 6116

ENTRYPOINT ["traefik-http-provider"]
