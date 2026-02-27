#!/bin/bash
# DevinClaw — One-Command Setup
# Bootstrap script for the DevinClaw AI modernization framework.
# Usage: ./setup.sh

set -euo pipefail

DEVINCLAW_VERSION="1.0.0"
REQUIRED_NODE_VERSION="18"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "============================================="
echo "  DevinClaw v${DEVINCLAW_VERSION}"
echo "  AI Modernization Framework for Federal Systems"
echo "============================================="
echo -e "${NC}"

# -----------------------------------------------
# 1. Check prerequisites
# -----------------------------------------------
echo -e "${YELLOW}[1/8] Checking prerequisites...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed.${NC}"
    echo "Install Node.js ${REQUIRED_NODE_VERSION}+ from https://nodejs.org/"
    exit 1
fi

NODE_MAJOR=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_MAJOR" -lt "$REQUIRED_NODE_VERSION" ]; then
    echo -e "${RED}ERROR: Node.js ${REQUIRED_NODE_VERSION}+ required (found $(node -v)).${NC}"
    exit 1
fi
echo -e "  ${GREEN}Node.js $(node -v)${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}ERROR: npm is not installed.${NC}"
    exit 1
fi
echo -e "  ${GREEN}npm $(npm -v)${NC}"

# Check git
if ! command -v git &> /dev/null; then
    echo -e "${RED}ERROR: git is not installed.${NC}"
    exit 1
fi
echo -e "  ${GREEN}git $(git --version | awk '{print $3}')${NC}"

echo -e "  ${GREEN}All prerequisites met.${NC}"

# -----------------------------------------------
# 2. Install OpenClaw
# -----------------------------------------------
echo ""
echo -e "${YELLOW}[2/8] Installing OpenClaw...${NC}"

if command -v openclaw &> /dev/null; then
    echo -e "  ${GREEN}OpenClaw already installed ($(openclaw --version 2>/dev/null || echo 'version unknown')).${NC}"
else
    echo "  Installing openclaw globally..."
    npm install -g openclaw
    echo -e "  ${GREEN}OpenClaw installed.${NC}"
fi

# -----------------------------------------------
# 3. Initialize workspace
# -----------------------------------------------
echo ""
echo -e "${YELLOW}[3/8] Initializing OpenClaw workspace...${NC}"

openclaw init --workspace "$SCRIPT_DIR"
echo -e "  ${GREEN}Workspace initialized at ${SCRIPT_DIR}${NC}"

# -----------------------------------------------
# 4. Install skills
# -----------------------------------------------
echo ""
echo -e "${YELLOW}[4/8] Installing DevinClaw skills...${NC}"

SKILL_COUNT=0
for skill_dir in "$SCRIPT_DIR"/skills/*/; do
    if [ -f "${skill_dir}SKILL.md" ]; then
        skill_name=$(basename "$skill_dir")
        echo "  Installing skill: ${skill_name}"
        openclaw skills install "$skill_dir"
        SKILL_COUNT=$((SKILL_COUNT + 1))
    fi
done

echo -e "  ${GREEN}${SKILL_COUNT} skills installed.${NC}"

# -----------------------------------------------
# 5. Configure Devin API
# -----------------------------------------------
echo ""
echo -e "${YELLOW}[5/8] Configuring Devin API...${NC}"

if [ -n "${DEVIN_API_KEY:-}" ]; then
    echo "  Using DEVIN_API_KEY from environment."
else
    echo "  Enter your Devin API key (from https://app.devin.ai/settings):"
    echo -n "  API Key: "
    read -rs DEVIN_API_KEY
    echo ""
fi

if [ -z "${DEVIN_API_KEY:-}" ]; then
    echo -e "  ${YELLOW}WARNING: No Devin API key provided. Devin Cloud/API features will be unavailable.${NC}"
    echo "  You can set it later: openclaw config set tools.devin.apiKey <YOUR_KEY>"
else
    openclaw config set tools.devin.apiKey "$DEVIN_API_KEY"
    echo -e "  ${GREEN}Devin API key configured.${NC}"
fi

# -----------------------------------------------
# 6. Configure DeepWiki MCP
# -----------------------------------------------
echo ""
echo -e "${YELLOW}[6/8] Configuring DeepWiki MCP...${NC}"

DEEPWIKI_CONFIG="$SCRIPT_DIR/deepwiki/mcp-config.json"
if [ -f "$DEEPWIKI_CONFIG" ]; then
    openclaw config set tools.mcp.deepwiki "$(cat "$DEEPWIKI_CONFIG")"
    echo -e "  ${GREEN}DeepWiki MCP configured from ${DEEPWIKI_CONFIG}${NC}"
else
    echo -e "  ${YELLOW}WARNING: DeepWiki config not found at ${DEEPWIKI_CONFIG}. Skipping.${NC}"
    echo "  You can configure it later: openclaw config set tools.mcp.deepwiki <config>"
fi

# -----------------------------------------------
# 7. Configure workspace files
# -----------------------------------------------
echo ""
echo -e "${YELLOW}[7/8] Registering workspace files...${NC}"

WORKSPACE_FILES=("SOUL.md" "GUARDRAILS.md" "TOOLS.md" "SECURITY.md" "SKILLS-MAP.md")
for wf in "${WORKSPACE_FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/$wf" ]; then
        openclaw workspace add "$SCRIPT_DIR/$wf"
        echo "  Registered: ${wf}"
    else
        echo -e "  ${YELLOW}Skipped (not found): ${wf}${NC}"
    fi
done

echo -e "  ${GREEN}Workspace files registered.${NC}"

# -----------------------------------------------
# 8. Verify installation
# -----------------------------------------------
echo ""
echo -e "${YELLOW}[8/8] Verifying installation...${NC}"

echo ""
echo "  OpenClaw status:"
openclaw status
echo ""
echo "  Installed skills:"
openclaw skills list

# -----------------------------------------------
# Done
# -----------------------------------------------
echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}  DevinClaw is ready!${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo "  Quick start:"
echo "    openclaw                                   # Start interactive chat"
echo "    openclaw run 'Analyze the PALM codebase'   # Run a task directly"
echo ""
echo "  Optional integrations:"
echo "    openclaw config set tools.mcp.jira <config>       # Connect Jira"
echo "    openclaw config set tools.mcp.slack <config>      # Connect Slack"
echo "    openclaw config set tools.mcp.sonarqube <config>  # Connect SonarQube"
echo ""
echo "  Documentation:"
echo "    README.md        — Setup guide and architecture"
echo "    SKILLS-MAP.md    — All available skills"
echo "    SECURITY.md      — Federal compliance posture"
echo "    GUARDRAILS.md    — Hard gates and session limits"
echo ""
