#!/usr/bin/env bash
# Stop existing containers
docker-compose down
# Rebuild and start containers
docker-compose up -d --build
