#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

AIWC="${AIWC:-./.venv/bin/aiwc}"
COMMIT_MESSAGE="${COMMIT_MESSAGE:-Update World Cup results and leaderboard}"

if [[ ! -x "$AIWC" ]]; then
  echo "Could not find executable aiwc at: $AIWC"
  echo "Create the virtual environment and install the project first, or run with AIWC=/path/to/aiwc."
  exit 1
fi

echo "Syncing latest match data..."
"$AIWC" data sync --sources openfootball,worldcup26

echo "Recalculating scores..."
"$AIWC" evaluate tournament --completed-only

echo "Exporting website JSON..."
"$AIWC" site export

echo "Current tournament leaderboard:"
"$AIWC" leaderboard tournament

echo "Staging website/data updates..."
git add data/snapshots website/public/data

if git diff --cached --quiet; then
  echo "No website/data changes to commit."
  exit 0
fi

echo "Committing updates..."
git commit -m "$COMMIT_MESSAGE"

echo "Pushing to GitHub..."
git push

echo "Daily update complete."
