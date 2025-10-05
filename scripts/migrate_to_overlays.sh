#!/bin/bash
# Migration script from old k8s/ structure to new overlays structure
# This script helps transition existing deployments to the new Kustomize overlay system

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  SLD Kubernetes Migration Helper                      ║${NC}"
echo -e "${BLUE}║  From: play-with-sld/kubernetes/k8s/                  ║${NC}"
echo -e "${BLUE}║  To:   play-with-sld/kubernetes/overlays/             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "play-with-sld/kubernetes" ]; then
    echo -e "${RED}❌ Error: Must be run from project root${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Migration Steps:${NC}"
echo ""
echo "1. ✅ New structure already created:"
echo "   - base/ (base manifests without versions)"
echo "   - overlays/dev/ (development with :latest)"
echo "   - overlays/prod/ (production with versioned tags)"
echo ""

# Check if old directory exists
if [ -d "play-with-sld/kubernetes/k8s" ]; then
    echo -e "${YELLOW}2. 🔍 Old directory detected: play-with-sld/kubernetes/k8s/${NC}"
    echo ""
    echo "   Options:"
    echo "   a) Keep old directory as backup (rename to k8s.old)"
    echo "   b) Remove old directory"
    echo "   c) Do nothing (manual cleanup later)"
    echo ""
    read -p "   Choose option (a/b/c): " choice
    
    case $choice in
        a)
            echo -e "${GREEN}   📦 Renaming k8s/ to k8s.old/${NC}"
            mv play-with-sld/kubernetes/k8s play-with-sld/kubernetes/k8s.old
            echo -e "${GREEN}   ✅ Backup created${NC}"
            ;;
        b)
            read -p "   ⚠️  Are you sure? This cannot be undone (y/n): " confirm
            if [ "$confirm" = "y" ]; then
                echo -e "${RED}   🗑️  Removing old k8s/ directory${NC}"
                rm -rf play-with-sld/kubernetes/k8s
                echo -e "${GREEN}   ✅ Old directory removed${NC}"
            fi
            ;;
        c)
            echo -e "${BLUE}   ⏭️  Skipping cleanup${NC}"
            ;;
    esac
else
    echo -e "${GREEN}2. ✅ No old directory found - clean installation${NC}"
fi

echo ""
echo -e "${YELLOW}3. 🔧 Testing new Kustomize configuration:${NC}"
echo ""

# Test dev overlay
echo -e "   ${BLUE}Testing dev overlay...${NC}"
if kustomize build play-with-sld/kubernetes/overlays/dev > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Dev overlay: Valid${NC}"
else
    echo -e "   ${RED}❌ Dev overlay: Invalid${NC}"
    echo -e "   ${YELLOW}   Run: kustomize build play-with-sld/kubernetes/overlays/dev${NC}"
fi

# Test prod overlay
echo -e "   ${BLUE}Testing prod overlay...${NC}"
if kustomize build play-with-sld/kubernetes/overlays/prod > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Prod overlay: Valid${NC}"
else
    echo -e "   ${RED}❌ Prod overlay: Invalid${NC}"
    echo -e "   ${YELLOW}   Run: kustomize build play-with-sld/kubernetes/overlays/prod${NC}"
fi

echo ""
echo -e "${YELLOW}4. 📝 Next Steps:${NC}"
echo ""
echo "   ${BLUE}For Development:${NC}"
echo "   kubectl apply -k play-with-sld/kubernetes/overlays/dev"
echo ""
echo "   ${BLUE}For Production:${NC}"
echo "   kubectl apply -k play-with-sld/kubernetes/overlays/prod"
echo ""
echo "   ${BLUE}Check deployment:${NC}"
echo "   kubectl get pods -n sld-dev    # for dev"
echo "   kubectl get pods -n sld-prod   # for prod"
echo ""

echo -e "${YELLOW}5. 🔄 Update kplay.sh script:${NC}"
echo ""
echo "   The kplay.sh script should be updated to use the new overlay structure."
echo "   Current: kubectl apply -f k8s/"
echo "   New:     kubectl apply -k overlays/dev"
echo ""

read -p "   Update kplay.sh automatically? (y/n): " update_kplay

if [ "$update_kplay" = "y" ]; then
    KPLAY_SCRIPT="play-with-sld/kubernetes/kplay.sh"
    if [ -f "$KPLAY_SCRIPT" ]; then
        # Backup original
        cp "$KPLAY_SCRIPT" "$KPLAY_SCRIPT.backup"
        
        # Update kubectl apply commands
        sed -i 's|kubectl apply -f k8s/|kubectl apply -k overlays/dev/|g' "$KPLAY_SCRIPT"
        sed -i 's|kubectl delete -f k8s/|kubectl delete -k overlays/dev/|g' "$KPLAY_SCRIPT"
        
        echo -e "   ${GREEN}✅ kplay.sh updated (backup saved as kplay.sh.backup)${NC}"
    else
        echo -e "   ${YELLOW}⚠️  kplay.sh not found${NC}"
    fi
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Migration Complete!                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "   - Versioning Guide: docs/VERSIONING.md"
echo "   - Play with SLD: play-with-sld/README.md"
echo ""
echo -e "${BLUE}🚀 Deploy now:${NC}"
echo "   cd play-with-sld/kubernetes"
echo "   kubectl apply -k overlays/dev"
echo ""
