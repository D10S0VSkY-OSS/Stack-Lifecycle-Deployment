#!/bin/bash
# Script to clean up old redundant workflows

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🧹 Cleaning up redundant GitHub Actions workflows...${NC}\n"

WORKFLOWS_DIR=".github/workflows"

# Old workflows to remove (redundant with build-and-push-images.yml)
OLD_WORKFLOWS=(
    "sld-api-docker-image.yml"
    "sld-dashboard-docker-image.yml"
    "sld-remote-state-docker-image.yml"
    "sld-schedule-docker-image.yml"
)

# PR workflows (optional to keep for CI validation)
PR_WORKFLOWS=(
    "sld-api-docker-image-pr.yml"
    "sld-dashboard-docker-image-pr.yml"
    "sld-remote-state-docker-image-pr.yml"
    "sld-schedule-docker-image-pr.yml"
)

echo -e "${RED}📋 Workflows to REMOVE (redundant):${NC}"
for workflow in "${OLD_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        echo "  ❌ $workflow"
    fi
done

echo -e "\n${YELLOW}📋 PR Workflows (optional to keep for CI):${NC}"
for workflow in "${PR_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        echo "  ⚠️  $workflow"
    fi
done

echo -e "\n${GREEN}📋 New unified workflows (KEEP):${NC}"
echo "  ✅ build-and-push-images.yml"
echo "  ✅ update-manifests-on-release.yml"

echo -e "\n${YELLOW}Do you want to remove redundant workflows? (y/n)${NC}"
read -r response

if [ "$response" = "y" ]; then
    echo -e "\n${RED}Removing redundant workflows...${NC}"
    for workflow in "${OLD_WORKFLOWS[@]}"; do
        if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
            rm "$WORKFLOWS_DIR/$workflow"
            echo "  ✅ Removed $workflow"
        fi
    done
    
    echo -e "\n${YELLOW}Do you also want to remove PR workflows? (y/n)${NC}"
    echo "  (They only build, don't push. Can be useful for PR validation)"
    read -r pr_response
    
    if [ "$pr_response" = "y" ]; then
        for workflow in "${PR_WORKFLOWS[@]}"; do
            if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
                rm "$WORKFLOWS_DIR/$workflow"
                echo "  ✅ Removed $workflow"
            fi
        done
    else
        echo -e "\n${GREEN}Keeping PR workflows for CI validation${NC}"
    fi
    
    echo -e "\n${GREEN}✅ Cleanup complete!${NC}"
    echo -e "\n${YELLOW}Next steps:${NC}"
    echo "  1. Review changes: git status"
    echo "  2. Commit: git add .github/workflows/"
    echo "  3. Push: git commit -m 'chore: remove redundant workflows' && git push"
else
    echo -e "\n${YELLOW}⏭️  Skipped cleanup${NC}"
fi
