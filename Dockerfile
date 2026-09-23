# syntax=docker/dockerfile:1

# -----------------------------------------------------------------------------
# base: system packages + uv, shared by every other stage
# -----------------------------------------------------------------------------
FROM debian:trixie-slim AS base

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_LINK_MODE=copy \
    UV_ADD_BOUNDS=major

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        python3 \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

WORKDIR /app

# -----------------------------------------------------------------------------
# deps: third-party dependencies only - cached across ordinary source edits
# -----------------------------------------------------------------------------
FROM base AS deps

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# -----------------------------------------------------------------------------
# production: the published, distributable image - lean, no dev tools, no root
# -----------------------------------------------------------------------------
FROM deps AS production

COPY md2epub/ ./md2epub/
COPY README.md LICENSE CHANGELOG.md ./
RUN uv sync --frozen --no-dev

RUN groupadd --gid 1000 md2epub \
    && useradd --uid 1000 --gid 1000 --shell /usr/sbin/nologin -M md2epub \
    && chown -R md2epub:md2epub /app
USER md2epub

ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["md2epub"]
CMD ["--help"]

# -----------------------------------------------------------------------------
# devel: interactive development inside the devcontainer (VS Code bind-mounts
# the workspace over /app at container start, see postCreateCommand for the
# actual dependency install - nothing baked in this stage survives that mount)
# -----------------------------------------------------------------------------
FROM base AS devel

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        openssh-client \
        sudo \
        nano \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID --shell /bin/bash -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && chown $USERNAME:$USERNAME /app

USER $USERNAME

ENV PATH="/app/.venv/bin:$PATH"


# OLD

FROM debian:trixie-slim

# Avoid interactive prompts (e.g. tzdata) during apt installs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_LINK_MODE=copy

# --------------------------------------------------------------------------
# System packages: Python 3
# --------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        openssh-client \
        sudo \
        nano \
        curl \
        ca-certificates \
        python3 \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

WORKDIR /app

# Create and set user to vscode
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID --shell /bin/bash -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && chown $USERNAME:$USERNAME /app

USER $USERNAME

# Dependencies first - this layer stays cached unless pyproject.toml/uv.lock change.
COPY --chown=$USERNAME:$USERNAME pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Now the project itself (fast: its dependencies are already in place).
COPY --chown=$USERNAME:$USERNAME md2epub/ ./md2epub/
COPY --chown=$USERNAME:$USERNAME README.md LICENSE CHANGELOG.md ./
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["md2epub"]
CMD ["--help"]
