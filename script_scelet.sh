#!/bin/bash
# shellcheck shell=bash
# Minimal Shell Script Template with Variables, Functions, and Signal Handling

set -euo pipefail
IFS=$'\n\t'

SCRIPT_NAME="$(basename "$0")"

# --- Load Variables from External Source (if available) ---
VARS_FILE="./env.vars"
if [[ -f "$VARS_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$VARS_FILE"
fi

# --- Signal Handling ---
cleanup() {
  echo "[$SCRIPT_NAME] Caught signal or exiting, cleaning up..."
  # Add any cleanup code here
}
trap cleanup SIGINT SIGTERM EXIT

# --- Functions ---
info() {
  echo "[$SCRIPT_NAME] INFO: $*"
}

error_exit() {
  echo "[$SCRIPT_NAME] ERROR: $*" >&2
  exit 1
}

main() {
  info "Script started."

  if [[ $# -eq 0 ]]; then
    error_exit "No arguments provided. Usage: $SCRIPT_NAME <arg1> [arg2 ...]"
  fi

  info "Arguments: $*"

  # Simulate workload (replace with actual logic)
  sleep 10

  info "Script completed successfully."
}

# --- Execute ---
main "$@"

