# photo-service

Backend service to create photos, align with google albums.


## Usage example

```Zsh
% curl -H "Content-Type: application/json" \
  -X POST \
  --data '{"username":"admin","password":"passw123"}' \
  http://localhost:8080/login
% export ACCESS="" #token from response
% curl -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS" \
  -X POST \
  --data @tests/files/user.json \
  http://localhost:8080/users
% curl -H "Authorization: Bearer $ACCESS"  http://localhost:8080/users
```

## Architecture

Layers:

- views: routing functions, maps representations to/from model
- services: enforce validation, calls adapter-layer for storing/retrieving objects
- models: model-classes
- adapters: adapters to external services

## Environment variables

To run the service locally, you need to supply a set of environment variables. A simple way to solve this is to supply a .env file in the root directory.

A minimal .env:

```Zsh
JWT_SECRET=secret
JWT_EXP_DELTA_SECONDS=3600
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password
USERS_HOST_SERVER=localhost
USERS_HOST_PORT=8086
DB_USER=photo-service
DB_PASSWORD=password
LOGGING_LEVEL=DEBUG
```

## Requirement for development

Install [uv](https://docs.astral.sh/uv/), e.g.:

```Zsh
% curl -LsSf https://astral.sh/uv/install.sh | sh
```

## If required - virtual environment

Install: curl <https://pyenv.run> | bash
Create: python -m venv .venv (replace .venv with your preferred name)
Install python 3.12: pyenv install 3.12
Activate:
source .venv/bin/activate

## Then install the dependencies:

```Zsh
% uv sync
```

To upgrade:

```Zsh
% uv sync --upgrade
```

## Running the API locally

Start the server locally:

```Zsh
% uv run adev runserver -p 8080 photo_service
```

## Running the API in a wsgi-server (gunicorn)

```Zsh
% uv run gunicorn photo_service:create_app --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker
```

## Running the wsgi-server in Docker

To build and run the api in a Docker container:

```Zsh
% docker build -t langrenn-sprint/photo-service:latest .
% docker run --env-file .env -p 8080:8080 -d langrenn-sprint/photo-service:latest
```

The easier way would be with docker-compose:

```Zsh
docker compose up --build
```

## Running tests

We use [pytest](https://docs.pytest.org/en/latest/) for contract testing.

To run linters, checkers and tests:

```Zsh
% uv run poe release
```

To run tests with logging, do:

```Zsh
% uv run pytest -m integration -- --log-cli-level=DEBUG
```
To upgrade:

```Zsh
% uv sync --upgrade
```
