#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source /usr/lib/bashio/bashio.sh

# ---- Read options ----
API_KEY=$(bashio::config 'api_key')
SECRET_PREFIX=$(bashio::config 'secret_prefix')

# CORS
CORS_ORIGINS=$(bashio::config 'cors_allowed_origins|join(,)')

# Extra env (prefixed secrets + anything else you want)
# This merges into process env; only vars starting with SECRET_PREFIX are exposable
if bashio::config.has_value 'extra_env'; then
  for key in $(bashio::config 'extra_env|keys'); do
    val=$(bashio::config "extra_env[${key}]")
    export "${key}=${val}"
  done
fi

# Git sync (optional)
GIT_ENABLED=$(bashio::config 'git_sync.enabled')
GIT_REPO=$(bashio::config 'git_sync.repo')
GIT_BRANCH=$(bashio::config 'git_sync.branch')
GIT_SUBDIR=$(bashio::config 'git_sync.subdir')

APP_DIR="/app/app"
if [ "${GIT_ENABLED}" = "true" ]; then
  bashio::log.info "Git sync enabled; cloning ${GIT_REPO} (${GIT_BRANCH})"
  mkdir -p /data/app
  if [ -d /data/app/.git ]; then
    git -C /data/app fetch origin
    git -C /data/app checkout "${GIT_BRANCH}"
    git -C /data/app pull --ff-only origin "${GIT_BRANCH}"
  else
    git clone --branch "${GIT_BRANCH}" --depth 1 "${GIT_REPO}" /data/app
  fi
  if [ -n "${GIT_SUBDIR}" ]; then
    APP_DIR="/data/app/${GIT_SUBDIR}"
  else 
    APP_DIR="/data/app"
  fi
  export PYTHONPATH="${APP_DIR}:${PYTHONPATH:-}"
fi

# Google OAuth config
GOOGLE_ENABLED=$(bashio::config 'google.enabled')
export GOOGLE_ENABLED

export GOOGLE_CLIENT_ID=$(bashio::config 'google.client_id')
export GOOGLE_CLIENT_SECRET=$(bashio::config 'google.client_secret')
export GOOGLE_SCOPES=$(bashio::config 'google.scopes|join( )')
export GOOGLE_REDIRECT_BASE=$(bashio::config 'google.redirect_base')
export GOOGLE_TOKEN_LABEL=$(bashio::config 'google.token_label')

# Server config exposed as env
export HS_API_KEY="${API_KEY}"
export HS_SECRET_PREFIX="${SECRET_PREFIX}"
export HS_CORS_ALLOWED_ORIGINS="${CORS_ORIGINS}"

# Ensure persistent storage for tokens etc.
mkdir -p /data/hs
chmod 700 /data/hs

bashio::log.info "Starting Home Secrets Server on :8126"
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8126