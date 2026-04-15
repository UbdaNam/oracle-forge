#!/bin/bash
# Oracle Forge — MCP Toolbox Startup Script
# Starts Google MCP Toolbox for Databases with all 4 DB types configured
#
# Prerequisites:
#   - toolbox binary in ~/toolbox (downloaded during setup)
#   - .env file with PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, MONGO_URI
#   - All DAB databases loaded
#
# Usage:
#   bash agent/start_toolbox.sh
#   Toolbox runs on http://localhost:5000

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
TOOLBOX_BIN="${HOME}/toolbox"
TOOLS_YAML="${SCRIPT_DIR}/tools.yaml"
DAB_PATH="${HOME}/DataAgentBench"

# Load environment variables
if [ -f "${DAB_PATH}/.env" ]; then
    export $(grep -v '^#' "${DAB_PATH}/.env" | xargs)
fi

# Export DAB_PATH for tools.yaml variable substitution
export DAB_PATH

# Verify toolbox binary exists
if [ ! -f "$TOOLBOX_BIN" ]; then
    echo "ERROR: toolbox binary not found at $TOOLBOX_BIN"
    echo "Run: curl -O https://storage.googleapis.com/genai-toolbox/v0.30.0/linux/amd64/toolbox && chmod +x toolbox"
    exit 1
fi

# Verify tools.yaml exists
if [ ! -f "$TOOLS_YAML" ]; then
    echo "ERROR: tools.yaml not found at $TOOLS_YAML"
    exit 1
fi

echo "Starting Oracle Forge MCP Toolbox..."
echo "  Config: $TOOLS_YAML"
echo "  DAB path: $DAB_PATH"
echo "  PostgreSQL: ${PG_HOST}:${PG_PORT}"
echo "  MongoDB: ${MONGO_URI}"
echo ""

# Start toolbox
"$TOOLBOX_BIN" --config "$TOOLS_YAML" --port 5000

echo "MCP Toolbox running on http://localhost:5000"
echo "Verify: curl http://localhost:5000/v1/tools | python3 -m json.tool | grep name"
