#!/usr/bin/env bash
set -euo pipefail

# -------------------------
# Helper functions
# -------------------------
wait_for_webui() {
  echo "Waiting for Open WebUI to start..."
  until curl -s -o /dev/null "http://localhost:8080/health"; do
    sleep 2
  done
  echo "Open WebUI started successfully"
}

signup_admin() {
  echo "Creating default admin user..."
  local signup_response
  signup_response=$(curl -s -X POST "http://localhost:8080/api/v1/auths/signup" \
    -H "Content-Type: application/json" \
    --data-raw "{\"name\":\"${WEBUI_ADMIN_USER}\", \"email\":\"${WEBUI_ADMIN_EMAIL}\", \"password\":\"${WEBUI_ADMIN_PASS}\"}")
  API_KEY=$(echo "${signup_response}" | jq -r '.token')
  echo "Received API_KEY for function import"
}

import_functions() {
  local export_file="/app/backend/functions-export.json"
  if [[ -f "${export_file}" ]]; then
    echo "Importing functions from JSON file..."
    jq -c '.[]' "${export_file}" | while read -r function_data; do
      local function_name
      function_name=$(echo "${function_data}" | jq -r '.name')
      echo "Importing function: ${function_name}"

      curl -s -X POST "http://localhost:8080/api/v1/functions/create" \
        -H "Authorization: Bearer ${API_KEY}" \
        -H "Content-Type: application/json" \
        --data-raw "${function_data}" || echo "Failed to import function: ${function_name}"
    done
    echo "Function import process completed"
  else
    echo "No functions export file found at ${export_file}"
  fi
}

# -------------------------
# Main execution
# -------------------------

echo "Starting Open WebUI server..."
/app/backend/start.sh &

wait_for_webui
signup_admin
import_functions

# Keep the container running for background processes.
wait 