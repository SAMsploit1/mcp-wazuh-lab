#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
cleanup() { docker compose down; }
trap cleanup EXIT INT TERM
docker compose config --quiet
docker compose up -d manager
attempt=0
until docker compose exec -T manager test -S /var/ossec/queue/sockets/logtest; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    docker compose logs manager
    exit 1
  fi
  sleep 1
done
rm -f evidence/events.jsonl
docker compose run --rm fixture
python3 tests/verify_rules.py
docker compose stats --no-stream > evidence/resources.txt
