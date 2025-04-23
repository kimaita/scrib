FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD src /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev

FROM jrottenberg/ffmpeg AS ffmpeg

# Final image
FROM python:3.12-slim-bookworm

COPY --from=builder --chown=app:app /app /app

# Copy ffmpeg
ENV LD_LIBRARY_PATH=/usr/local/lib
COPY --from=ffmpeg /usr/local /usr/local/
COPY --from=ffmpeg /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu
COPY --from=ffmpeg /lib/x86_64-linux-gnu/* /usr/lib/


# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

CMD ["fastapi", "dev", "--host", "0.0.0.0", "/app/main.py"]
