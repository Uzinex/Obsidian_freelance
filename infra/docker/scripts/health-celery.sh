#!/bin/sh
set -eu
celery -A obsidian_backend inspect ping >/tmp/celery_ping
