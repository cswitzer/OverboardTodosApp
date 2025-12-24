# -------------------------
# Stage 1: Builder
# -------------------------

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install temporary build tools to compile dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install python deps into /install instead of /usr/local to keep them isolated
COPY requirements.txt /requirements.txt
RUN pip install --prefix=/install --no-cache-dir -r /requirements.txt

# -------------------------
# Stage 2: Final / runtime
# -------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copy everything from the builder stage from /install to /usr/local, which is where Python
# looks for installed packages
COPY --from=builder /install /usr/local

# Copy entrypoint and start scripts
COPY ./compose/fastapi/entrypoint /entrypoint
COPY ./compose/fastapi/start /start
COPY ./compose/fastapi/celery/worker/start /start-celeryworker
COPY ./compose/fastapi/celery/beat/start /start-celerybeat
COPY ./compose/fastapi/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /entrypoint /start /start-celeryworker /start-celerybeat /start-flower
RUN chmod +x /entrypoint /start /start-celeryworker /start-celerybeat /start-flower

# Copy your application code into the image (key for k8s deployments)
COPY . /app

ENTRYPOINT ["/entrypoint"]

# -------------------------
# Stage 3: Development
# -------------------------

FROM runtime AS dev

# Dev-only OS tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        telnet \
        netcat-openbsd && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    debugpy \
    ipython \
    watchfiles
