FROM python:3.10

RUN mkdir -p /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install "poetry==1.1.6"
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

ADD photo_service /app/photo_service

EXPOSE 8080

CMD gunicorn "photo_service:create_app"  --config=photo_service/gunicorn_config.py --worker-class aiohttp.GunicornWebWorker
