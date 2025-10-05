#!/usr/bin/env python3
"""
SLD Version Manager
===================
Utility script to manage versions across all services and Kubernetes manifests.

Usage:
    ./scripts/version_manager.py show                    # Show current versions
    ./scripts/version_manager.py bump 2.8.0              # Bump all versions
    ./scripts/version_manager.py sync                    # Sync K8s manifests with pyproject.toml
    ./scripts/version_manager.py validate                # Validate version consistency
"""

import sys
import re
from pathlib import Path
from typing import Dict, Optional
import subprocess

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

# Project root
ROOT = Path(__file__).parent.parent

# Services configuration
SERVICES = {
    'sld-api-backend': ROOT / 'sld-api-backend' / 'pyproject.toml',
    'sld-dashboard': ROOT / 'sld-dashboard' / 'pyproject.toml',
    'sld-remote-state': ROOT / 'sld-remote-state' / 'pyproject.toml',
    'sld-schedule': ROOT / 'sld-schedule' / 'pyproject.toml',
}

# Kubernetes manifests
KUSTOMIZE_PROD = ROOT / 'play-with-sld' / 'kubernetes' / 'overlays' / 'prod' / 'kustomization.yaml'


def read_version_from_pyproject(path: Path) -> Optional[str]:
    """Extract version from pyproject.toml"""
    if not path.exists():
        return None
    
    with open(path) as f:
        for line in f:
            if match := re.match(r'^version\s*=\s*"([^"]+)"', line):
                return match.group(1)
    return None


def update_version_in_pyproject(path: Path, new_version: str) -> bool:
    """Update version in pyproject.toml"""
    if not path.exists():
        return False
    
    with open(path) as f:
        content = f.read()
    
    updated = re.sub(
        r'^version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    
    with open(path, 'w') as f:
        f.write(updated)
    
    return True


def read_kustomize_versions() -> Dict[str, str]:
    """Read image versions from Kustomize prod overlay"""
    versions = {}
    
    if not KUSTOMIZE_PROD.exists():
        return versions
    
    with open(KUSTOMIZE_PROD) as f:
        content = f.read()
    
    # Extract image tags
    for match in re.finditer(r'name:\s+(d10s0vsky/sld-\w+)\s+newTag:\s+v?([^\s]+)', content):
        image_name = match.group(1).split('/')[-1]  # Get just 'sld-api' part
        version = match.group(2)
        versions[image_name] = version
    
    return versions


def update_kustomize_versions(new_version: str) -> bool:
    """Update all image versions in Kustomize prod overlay"""
    if not KUSTOMIZE_PROD.exists():
        print(f"{Colors.RED}❌ Kustomize prod overlay not found{Colors.NC}")
        return False
    
    try:
        # Use yq to update versions
        tag_with_v = f"v{new_version}"
        
        for image in ['sld-api', 'sld-dashboard', 'sld-remote-state', 'sld-schedule']:
            cmd = [
                'yq', 'eval', '-i',
                f'(.images[] | select(.name == "d10s0vsky/{image}")).newTag = "{tag_with_v}"',
                str(KUSTOMIZE_PROD)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
        
        # Update version label
        cmd = [
            'yq', 'eval', '-i',
            f'.commonLabels.version = "{new_version}"',
            str(KUSTOMIZE_PROD)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Failed to update Kustomize: {e}{Colors.NC}")
        return False
    except FileNotFoundError:
        print(f"{Colors.YELLOW}⚠️  yq not found. Install it with: sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 && sudo chmod +x /usr/local/bin/yq{Colors.NC}")
        return False


def cmd_show():
    """Show current versions across all services"""
    print(f"{Colors.BOLD}{'='*60}{Colors.NC}")
    print(f"{Colors.BOLD}📦 SLD Version Status{Colors.NC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.NC}\n")
    
    # Services versions
    print(f"{Colors.BLUE}🔧 Services (pyproject.toml):{Colors.NC}")
    versions = {}
    for service_name, path in SERVICES.items():
        version = read_version_from_pyproject(path)
        versions[service_name] = version
        status = f"{Colors.GREEN}✓{Colors.NC}" if version else f"{Colors.RED}✗{Colors.NC}"
        print(f"  {status} {service_name:20} → {version or 'NOT FOUND'}")
    
    # Kustomize versions
    print(f"\n{Colors.BLUE}☸️  Kubernetes Production (overlays/prod):{Colors.NC}")
    k8s_versions = read_kustomize_versions()
    if k8s_versions:
        for image, version in k8s_versions.items():
            print(f"  {Colors.GREEN}✓{Colors.NC} {image:20} → v{version}")
    else:
        print(f"  {Colors.YELLOW}⚠️  No versions found{Colors.NC}")
    
    # Consistency check
    print(f"\n{Colors.BLUE}🔍 Consistency Check:{Colors.NC}")
    all_versions = list(versions.values())
    if all_versions and all(v == all_versions[0] for v in all_versions if v):
        print(f"  {Colors.GREEN}✅ All services have the same version: {all_versions[0]}{Colors.NC}")
    else:
        print(f"  {Colors.RED}❌ Version mismatch detected!{Colors.NC}")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.NC}")


def cmd_bump(new_version: str):
    """Bump version across all services and manifests"""
    print(f"{Colors.BOLD}🚀 Bumping version to {new_version}{Colors.NC}\n")
    
    # Update all pyproject.toml files
    print(f"{Colors.BLUE}📝 Updating pyproject.toml files...{Colors.NC}")
    for service_name, path in SERVICES.items():
        if update_version_in_pyproject(path, new_version):
            print(f"  {Colors.GREEN}✓{Colors.NC} Updated {service_name}")
        else:
            print(f"  {Colors.RED}✗{Colors.NC} Failed to update {service_name}")
    
    # Update Kustomize manifests
    print(f"\n{Colors.BLUE}☸️  Updating Kubernetes manifests...{Colors.NC}")
    if update_kustomize_versions(new_version):
        print(f"  {Colors.GREEN}✓{Colors.NC} Updated production overlay")
    else:
        print(f"  {Colors.RED}✗{Colors.NC} Failed to update Kustomize")
    
    print(f"\n{Colors.GREEN}✅ Version bump complete!{Colors.NC}")
    print(f"\n{Colors.YELLOW}Next steps:{Colors.NC}")
    print(f"  1. Review changes: git diff")
    print(f"  2. Commit changes: git add . && git commit -m 'chore: bump version to {new_version}'")
    print(f"  3. Create release: gh release create v{new_version}")


def cmd_sync():
    """Sync Kubernetes manifests with pyproject.toml versions"""
    print(f"{Colors.BOLD}🔄 Syncing K8s manifests with pyproject.toml...{Colors.NC}\n")
    
    # Get version from first service
    version = read_version_from_pyproject(SERVICES['sld-api-backend'])
    if not version:
        print(f"{Colors.RED}❌ Could not read version from sld-api-backend{Colors.NC}")
        return
    
    print(f"📦 Using version: {version}")
    
    if update_kustomize_versions(version):
        print(f"{Colors.GREEN}✅ Kubernetes manifests synchronized{Colors.NC}")
    else:
        print(f"{Colors.RED}❌ Failed to sync{Colors.NC}")


def cmd_validate():
    """Validate version consistency"""
    print(f"{Colors.BOLD}🔍 Validating version consistency...{Colors.NC}\n")
    
    # Check all services have the same version
    versions = {name: read_version_from_pyproject(path) for name, path in SERVICES.items()}
    
    all_same = all(v == list(versions.values())[0] for v in versions.values() if v)
    
    if all_same:
        print(f"{Colors.GREEN}✅ All services have consistent version: {list(versions.values())[0]}{Colors.NC}")
    else:
        print(f"{Colors.RED}❌ Version mismatch detected:{Colors.NC}")
        for name, version in versions.items():
            print(f"  - {name}: {version}")
        sys.exit(1)
    
    # Check Kustomize versions
    k8s_versions = read_kustomize_versions()
    if k8s_versions:
        print(f"{Colors.GREEN}✅ Kubernetes manifests configured{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}⚠️  Kubernetes versions not found or not configured{Colors.NC}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'show':
        cmd_show()
    elif command == 'bump':
        if len(sys.argv) < 3:
            print(f"{Colors.RED}❌ Missing version argument{Colors.NC}")
            print(f"Usage: {sys.argv[0]} bump <version>")
            sys.exit(1)
        cmd_bump(sys.argv[2])
    elif command == 'sync':
        cmd_sync()
    elif command == 'validate':
        cmd_validate()
    else:
        print(f"{Colors.RED}❌ Unknown command: {command}{Colors.NC}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
