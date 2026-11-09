#!/usr/bin/env bash
# Run the whole pipeline from data to deliverables with one command (T6)
#
#   ./reproduce.sh --dry-run                 # only print the commands that would run, do not run them
#   DATA_ROOT=/kaggle/input/... ./reproduce.sh
#   ./reproduce.sh --skip-train --with-analysis
#
# Assumes a Kaggle Notebook by default (cache under /kaggle/temp). Pass --cache explicitly when running locally.
set -euo pipefail

DATA_ROOT="${DATA_ROOT:-}"
CACHE="${CACHE:-/kaggle/temp/cache}"
OUT="${OUT:-results}"
PY="${PYTHON:-python}"
DRY=0
SKIP_TRAIN=0
WITH_ANALYSIS=0
MODELS=""
DATASETS=""
LIMIT=""

usage() {
  cat <<'EOF'
Usage: ./reproduce.sh [options]

  --data-root PATH   Data root (contains data/D1/...); found by src.locate_data if omitted
  --cache PATH       224 cache directory (default /kaggle/temp/cache; use a writable dir locally)
  --out PATH         Output directory (default results)
  --models LIST      Run only the listed models, comma separated (default all)
  --datasets LIST    Run only the listed datasets (default all)
  --limit-runs N     Run only the first N entries of the matrix (for debugging)
  --skip-train       Skip caching / splitting / training; only rebuild aggregates, figures and tables
  --with-analysis    Also run efficiency + lime (CPU, slow)
  --dry-run          Only print the commands
  -h, --help         Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --data-root) DATA_ROOT="$2"; shift 2 ;;
    --cache) CACHE="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --models) MODELS="$2"; shift 2 ;;
    --datasets) DATASETS="$2"; shift 2 ;;
    --limit-runs) LIMIT="$2"; shift 2 ;;
    --skip-train) SKIP_TRAIN=1; shift ;;
    --with-analysis) WITH_ANALYSIS=1; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

step() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
do_run() {
  if [[ $DRY -eq 1 ]]; then
    printf '  [dry-run] %s\n' "$*"
  else
    printf '  $ %s\n' "$*"
    "$@"
  fi
}

if [[ -z "$DATA_ROOT" ]]; then
  if [[ $DRY -eq 1 ]]; then
    DATA_ROOT="<auto: python -m src.locate_data>"
    printf '  [dry-run] %s -m src.locate_data --search-root /kaggle/input --wait 300\n' "$PY"
  else
    step "0/7 Locate data"
    DATA_ROOT="$("$PY" -m src.locate_data --search-root /kaggle/input --wait 300)"
    echo "  DATA_ROOT=$DATA_ROOT"
  fi
fi

if [[ $SKIP_TRAIN -eq 0 ]]; then
  step "1/7 Build the 224 cache"
  do_run "$PY" -m src.data_prepare --data-root "$DATA_ROOT" --out "$CACHE" --size 224

  step "2/7 Generate splits (skipped if present; never regenerate once splits/ is frozen)"
  if [[ -f splits/D1.csv && -f splits/D2.csv ]]; then
    echo "  splits/D1.csv and D2.csv already exist, skipping (back them up and get the group's agreement before rebuilding)"
  else
    do_run "$PY" -m src.splits --data-root "$DATA_ROOT" --out splits --seed 42
  fi

  step "3/7 Training matrix (66 runs, GPU)"
  BATCH_ARGS=(--data-root "$DATA_ROOT" --cache-root "$CACHE" --out "$OUT" --save-weights)
  [[ -n "$MODELS" ]] && BATCH_ARGS+=(--models "$MODELS")
  [[ -n "$DATASETS" ]] && BATCH_ARGS+=(--datasets "$DATASETS")
  [[ -n "$LIMIT" ]] && BATCH_ARGS+=(--limit-runs "$LIMIT")
  do_run "$PY" -m src.batch "${BATCH_ARGS[@]}"
else
  step "1-3/7 Training skipped (--skip-train)"
fi

step "4/7 Aggregate leaderboard.csv"
do_run "$PY" -m src.aggregate

step "5/7 Report figures (T1)"
do_run "$PY" -m analysis.make_figures

step "6/7 Report tables (T2, with cell-by-cell checks)"
do_run "$PY" -m analysis.export_tables --check

if [[ $WITH_ANALYSIS -eq 1 ]]; then
  step "7/7 Efficiency (T3) and LIME (T4)"
  do_run "$PY" -m analysis.efficiency
  do_run "$PY" -m analysis.lime_explain
else
  step "7/7 Skipping efficiency / lime (only runs with --with-analysis)"
fi

printf '\nDone. Deliverables:\n'
printf '  %s/leaderboard.csv\n  %s/figures/ (fig_*.png + INDEX.md)\n  reports/tables/ (*.md + *.tex)\n' "$OUT" "$OUT"
[[ $DRY -eq 1 ]] && printf '\n(dry run: no command was executed)\n'
