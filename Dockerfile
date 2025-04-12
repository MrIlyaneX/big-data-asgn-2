FROM firasj/spark-docker-cluster
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1


RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

COPY ./app/requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --no-cache-dir -r /tmp/requirements.txt
