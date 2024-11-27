ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS builder
WORKDIR /tmp

# Download using
# curl -L "https://drive.usercontent.google.com/download?id=1TRJtctjETgVVD5p7frSVPmgw8z8FFtjD&confirm=xxx" -o models.zip
COPY ./models.zip .
RUN apt-get update; \
    apt-get install -y --no-install-recommends curl unzip; \
    unzip models.zip; \
    rm models.zip

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

FROM gcr.io/distroless/python3-debian12:nonroot
ARG PYTHON_VERSION=3.11

WORKDIR /app
COPY --from=builder /tmp/models /app/models
COPY --from=builder /usr/local/lib/python${PYTHON_VERSION}/site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages
ENV PYTHONPATH=/usr/local/lib/python${PYTHON_VERSION}/site-packages
COPY *.py ./
COPY ./utils ./utils

CMD ["engine.py"]
EXPOSE 8124
