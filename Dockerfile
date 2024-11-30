# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM as python-base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=true \
    POETRY_VIRTUALENVS_OPTIONS_SYSTEM_SITE_PACKAGES=true \
    POETRY_VIRTUALENVS_PATH="/venv" \
    POETRY_WARNINGS_EXPORT=false \
    APP_PATH="/app"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$POETRY_VIRTUALENVS_PATH/bin:$PATH"

WORKDIR $APP_PATH

FROM python-base as builder

# py3-meson-python is a build dependency
RUN apk add --no-cache \
  python3 \
  py3-grpcio \
  py3-inflect \
  py3-nltk \
  py3-numpy \
  py3-scipy \
  py3-werkzeug \
  py3-unidecode \
  build-base \
  py3-meson-python \
  python3-dev

# Install last Poetry version, respects $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN which poetry

# Copy dependencies
COPY ./poetry.lock ./pyproject.toml ./

# Install runtime dependencies
RUN poetry run pip3 install --no-warn-script-location --user poetry-plugin-export
RUN poetry export --no-cache --only main > requirements.txt
RUN poetry run -- python3 -c 'import sys, platform; print("sys:", sys.platform, "\nmachine:", platform.machine())'
# RUN poetry run pip3 install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
#
# FROM builder as distribution
#
# # Copy poetry and venv
# COPY --from=builder $POETRY_HOME $POETRY_HOME
# COPY --from=builder $POETRY_VIRTUALENVS_PATH $POETRY_VIRTUALENVS_PATH
#
# # Copy full project and build it (generate distribution files in /app/dist)
# COPY . .
# RUN . $POETRY_VIRTUALENVS_PATH/bin/activate && poetry build
#
# FROM python-base as addon
#
# COPY --from=builder $POETRY_VIRTUALENVS_PATH $POETRY_VIRTUALENVS_PATH
# COPY --from=distribution $APP_PATH/dist .
#
# COPY *.py utils models ./
#
# # Install just the wheels
# RUN . $POETRY_VIRTUALENVS_PATH/bin/activate && pip install *.whl
