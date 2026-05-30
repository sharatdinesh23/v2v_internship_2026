#!/usr/bin/env bash
# Stop existing containers using docker compose (v2)
docker compose down
# Rebuild and start containers using docker compose (v2)
docker compose up -d --build
