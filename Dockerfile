# refer to: https://stackoverflow.com/a/54763270

FROM python:3.10.1

ARG YOUR_ENV

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.12

# System deps:
RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /code

EXPOSE 80
CMD ["gunicorn", "instagram.asgi:application", "--bind", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker"]


# Usage
## Build Dockerfile for production
# docker build -t django_poetry --build-arg YOUR_ENV=production .

## Test run
# docker run --publish 9000:80 -e SECRET_KEY={{SECRET_KEY}} -e ..
