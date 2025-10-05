#!/usr/bin/env python3
"""
SLD CLI - Tool to test Stack Lifecycle Deployment locally with UV
"""
import sys
import time
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import click


# Colors for output
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'


def run_command(cmd, cwd=None, check=True, capture_output=False):
    """Execute a shell command"""
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                check=check,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=True, cwd=cwd, check=check)
            return result.returncode == 0
    except subprocess.CalledProcessError as e:
        click.echo(f"{Colors.RED}❌ Error executing: {cmd}{Colors.NC}", err=True)
        click.echo(f"{Colors.RED}   {str(e)}{Colors.NC}", err=True)
        if check:
            sys.exit(1)
        return False


def check_requirements():
    """Check if prerequisites are installed"""
    requirements = []
    
    # Check Docker
    result = subprocess.run('docker --version', shell=True, capture_output=True)
    if result.returncode != 0:
        requirements.append('Docker')
    
    # Check Docker Compose (modern version: docker compose)
    result = subprocess.run('docker compose version', shell=True, capture_output=True)
    if result.returncode != 0:
        # Try legacy docker-compose
        result = subprocess.run('docker-compose --version', shell=True, capture_output=True)
        if result.returncode != 0:
            requirements.append('Docker Compose')
    
    # Check Kind (optional for Kubernetes)
    result = subprocess.run('which kind', shell=True, capture_output=True)
    if result.returncode != 0:
        requirements.append('Kind (for Kubernetes)')
    
    # Check kubectl (optional for Kubernetes)
    result = subprocess.run('which kubectl', shell=True, capture_output=True)
    if result.returncode != 0:
        requirements.append('kubectl (for Kubernetes)')
    
    return requirements


def get_project_root():
    """Get project root directory"""
    script_dir = Path(__file__).parent.absolute()
    return script_dir


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    🚀 SLD CLI - Tool to test Stack Lifecycle Deployment with UV
    
    Migration from pip to uv for faster dependency installation.
    """
    pass


@cli.command()
@click.option('--service', '-s', type=click.Choice(['api', 'dashboard', 'remote-state', 'schedule', 'all']),
              default='all', help='Service to build')
@click.option('--tag', '-t', default='latest', help='Tag for images')
@click.option('--no-cache', is_flag=True, help='Build without cache')
@click.option('--parallel', '-p', is_flag=True, help='Build images in parallel (faster)')
@click.option('--max-workers', default=4, help='Maximum parallel builds (default: 4)')
def build(service, tag, no_cache, parallel, max_workers):
    """Build Docker images with UV and optional parallel building"""
    project_root = get_project_root()
    
    click.echo(f"{Colors.BOLD}🚀 Building Docker images with UV...{Colors.NC}\n")
    
    services = {
        'api': ('sld-api-backend', 'd10s0vsky/sld-api'),
        'dashboard': ('sld-dashboard', 'd10s0vsky/sld-dashboard'),
        'remote-state': ('sld-remote-state', 'd10s0vsky/sld-remote-state'),
        'schedule': ('sld-schedule', 'd10s0vsky/sld-schedule'),
    }
    
    if service == 'all':
        to_build = list(services.items())
    else:
        to_build = [(service, services[service])]
    
    total = len(to_build)
    cache_flag = '--no-cache' if no_cache else ''
    failed_services = []
    
    # Helper function for building a single service
    def build_service(svc_info):
        svc, (directory, image_name) = svc_info
        cmd = f"docker build {cache_flag} -t {image_name}:{tag} ./{directory}"
        success = run_command(cmd, cwd=project_root, check=False)
        return svc, success
    
    if parallel and service == 'all':
        # Build in parallel
        click.echo(f"{Colors.YELLOW}⚡ Building {total} services in parallel (max {max_workers} workers)...{Colors.NC}\n")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all build tasks
            future_to_service = {
                executor.submit(build_service, svc_info): svc_info[0] 
                for svc_info in to_build
            }
            
            # Process results as they complete
            completed = 0
            for future in as_completed(future_to_service):
                svc_name = future_to_service[future]
                completed += 1
                
                try:
                    svc, success = future.result()
                    if success:
                        click.echo(f"{Colors.GREEN}✓ [{completed}/{total}]{Colors.NC} {Colors.BOLD}{svc}{Colors.NC} completed")
                    else:
                        click.echo(f"{Colors.RED}✗ [{completed}/{total}]{Colors.NC} {Colors.BOLD}{svc}{Colors.NC} failed")
                        failed_services.append(svc)
                except Exception as e:
                    click.echo(f"{Colors.RED}✗ [{completed}/{total}]{Colors.NC} {Colors.BOLD}{svc_name}{Colors.NC} exception: {str(e)}")
                    failed_services.append(svc_name)
    else:
        # Build sequentially
        for idx, svc_info in enumerate(to_build, 1):
            svc, (directory, image_name) = svc_info
            click.echo(f"{Colors.BLUE}[{idx}/{total}]{Colors.NC} Building {Colors.BOLD}{svc}{Colors.NC}...")
            
            svc, success = build_service(svc_info)
            
            if success:
                click.echo(f"{Colors.GREEN}✓{Colors.NC} {svc} completed\n")
            else:
                click.echo(f"{Colors.RED}✗{Colors.NC} {svc} failed\n")
                failed_services.append(svc)
                if service != 'all':
                    sys.exit(1)
    
    if failed_services:
        click.echo(f"\n{Colors.RED}❌ Build failed for: {', '.join(failed_services)}{Colors.NC}\n")
        sys.exit(1)
    
    click.echo(f"\n{Colors.GREEN}✅ Build completed!{Colors.NC}\n")
    
    # Show created images
    click.echo("Created images:")
    run_command(f"docker images | grep 'd10s0vsky/sld-' | grep '{tag}'", check=False)


@cli.command()
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes', 'k8s']),
              default='docker', help='Deployment mode (k8s = kubernetes)')
@click.option('--env', '-e', type=click.Choice(['dev', 'prod']),
              default='dev', help='Environment for Kubernetes (dev=latest, prod=versioned)')
@click.option('--build-first', '-b', is_flag=True, help='Build images before starting')
def start(mode, env, build_first):
    """Start SLD locally"""
    project_root = get_project_root()
    
    # Normalize mode
    if mode == 'k8s':
        mode = 'kubernetes'
    
    if build_first:
        click.echo(f"{Colors.YELLOW}📦 Building images first...{Colors.NC}\n")
        ctx = click.get_current_context()
        ctx.invoke(build, service='all', tag='latest', no_cache=False, parallel=False, max_workers=4)
        click.echo()
    
    if mode == 'docker':
        click.echo(f"{Colors.BOLD}🐳 Starting SLD with Docker Compose...{Colors.NC}\n")
        
        docker_dir = project_root / 'play-with-sld' / 'docker'
        
        click.echo("Starting database services...")
        run_command("docker compose up -d db redis mongodb", cwd=docker_dir)
        
        click.echo("Waiting for DB to be ready...")
        time.sleep(15)
        
        click.echo("Starting backend and workers...")
        run_command("docker compose up -d api-backend worker remote-state", cwd=docker_dir)
        
        time.sleep(10)
        
        click.echo("Starting frontend...")
        run_command("docker compose up -d sld-dashboard schedule", cwd=docker_dir)
        
        click.echo(f"\n{Colors.GREEN}✅ Services started!{Colors.NC}\n")
        
    else:  # kubernetes
        click.echo(f"{Colors.BOLD}☸️  Starting SLD with Kubernetes (kind) - {env.upper()} environment{Colors.NC}\n")
        
        # Check prerequisites
        missing = [r for r in ['kind', 'kubectl'] if subprocess.run(
            f'which {r}', shell=True, capture_output=True
        ).returncode != 0]
        
        if missing:
            click.echo(f"{Colors.RED}❌ Missing prerequisites: {', '.join(missing)}{Colors.NC}")
            click.echo(f"\n{Colors.YELLOW}Install missing tools:{Colors.NC}")
            if 'kind' in missing:
                click.echo("  Kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation")
            if 'kubectl' in missing:
                click.echo("  kubectl: https://kubernetes.io/docs/tasks/tools/")
            sys.exit(1)
        
        k8s_dir = project_root / 'play-with-sld' / 'kubernetes'
        
        # Check if cluster exists
        cluster_exists = subprocess.run(
            "kind get clusters | grep -q '^kind$'",
            shell=True,
            capture_output=True
        ).returncode == 0
        
        if not cluster_exists:
            click.echo(f"{Colors.YELLOW}⚠️  No Kind cluster found. Creating one...{Colors.NC}\n")
            
            # Create cluster
            click.echo("Creating Kind cluster with configuration...")
            result = run_command("kind create cluster --config kind.yml", cwd=k8s_dir, check=False)
            
            if not result:
                click.echo(f"\n{Colors.RED}❌ Failed to create Kind cluster{Colors.NC}")
                sys.exit(1)
            
            click.echo(f"\n{Colors.GREEN}✓{Colors.NC} Kind cluster created successfully\n")
        else:
            click.echo(f"{Colors.GREEN}✓{Colors.NC} Kind cluster is running\n")
        
        # Load images into kind if using dev
        if env == 'dev':
            click.echo("Loading latest images into kind...")
            images = [
                'd10s0vsky/sld-api:latest',
                'd10s0vsky/sld-dashboard:latest',
                'd10s0vsky/sld-remote-state:latest',
                'd10s0vsky/sld-schedule:latest'
            ]
            
            for img in images:
                # Check if image exists locally
                result = subprocess.run(
                    f"docker images -q {img}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    click.echo(f"  Loading {img}...")
                    run_command(f"kind load docker-image {img}", check=False)
                else:
                    click.echo(f"  {Colors.YELLOW}⚠️  {img} not found locally{Colors.NC}")
            
            click.echo()
        
        # Deploy using kustomize overlays
        overlay_path = f"overlays/{env}"
        click.echo(f"Deploying {env.upper()} environment with Kustomize...")
        run_command(f"kubectl apply -k {overlay_path}/", cwd=k8s_dir)
        
        click.echo(f"\n{Colors.GREEN}✅ {env.upper()} environment deployed!{Colors.NC}\n")
        click.echo(f"{Colors.YELLOW}💡 Namespace: default{Colors.NC}\n")
    
    click.echo(f"{Colors.BOLD}Available endpoints:{Colors.NC}")
    click.echo(f"  • Dashboard: {Colors.BLUE}http://localhost:5000/{Colors.NC}")
    click.echo(f"  • API Docs:  {Colors.BLUE}http://localhost:8000/docs{Colors.NC}")
    click.echo(f"\n{Colors.YELLOW}Run './sld_cli.py init' to create initial user{Colors.NC}")


@cli.command()
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes', 'k8s']),
              default='docker', help='Deployment mode (k8s = kubernetes)')
@click.option('--env', '-e', type=click.Choice(['dev', 'prod']),
              default='dev', help='Environment for Kubernetes')
def stop(mode, env):
    """Stop SLD services"""
    project_root = get_project_root()
    
    # Normalize mode
    if mode == 'k8s':
        mode = 'kubernetes'
    
    if mode == 'docker':
        click.echo(f"{Colors.BOLD}🛑 Stopping Docker Compose services...{Colors.NC}\n")
        docker_dir = project_root / 'play-with-sld' / 'docker'
        run_command("docker compose down", cwd=docker_dir)
        
    else:  # kubernetes
        click.echo(f"{Colors.BOLD}🛑 Stopping Kubernetes {env.upper()} environment...{Colors.NC}\n")
        
        if click.confirm('Delete the entire kind cluster?'):
            run_command("kind delete cluster")
        else:
            # Delete resources from default namespace
            k8s_dir = project_root / 'play-with-sld' / 'kubernetes'
            overlay_path = f"overlays/{env}"
            click.echo(f"Deleting {env.upper()} resources from default namespace...")
            run_command(f"kubectl delete -k {overlay_path}/", cwd=k8s_dir, check=False)
    
    click.echo(f"{Colors.GREEN}✅ Services stopped!{Colors.NC}")


@cli.command()
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes', 'k8s']),
              default='docker', help='Deployment mode (k8s = kubernetes)')
def init(mode):
    """Initialize admin user and credentials"""
    # Normalize mode
    if mode == 'k8s':
        mode = 'kubernetes'
    
    click.echo(f"{Colors.BOLD}🔑 Initializing credentials...{Colors.NC}\n")
    
    # Wait for API to be ready
    click.echo("Checking if API is ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            result = subprocess.run(
                "curl -s http://localhost:8000/api/v1/ > /dev/null",
                shell=True,
                capture_output=True
            )
            if result.returncode == 0:
                break
        except:
            pass
        
        if i < max_retries - 1:
            time.sleep(2)
            click.echo(".", nl=False)
        else:
            click.echo(f"\n{Colors.RED}❌ API is not available{Colors.NC}")
            sys.exit(1)
    
    click.echo(f"\n{Colors.GREEN}✓{Colors.NC} API ready\n")
    
    # Create initial user
    click.echo("Creating admin user...")
    run_command(
        'curl -X POST "http://localhost:8000/api/v1/users/start" '
        '-H "accept: application/json" '
        '-H "Content-Type: application/json" '
        '-d \'{"password":"Password08@"}\' '
        '-s -o /dev/null',
        check=False
    )
    
    time.sleep(2)
    
    # Get token
    click.echo("Getting authentication token...")
    token = run_command(
        'curl -X POST -s "http://localhost:8000/api/v1/authenticate/access-token-json" '
        '-H "accept: application/json" '
        '-H "Content-Type: application/json" '
        '-d \'{"username":"admin","password":"Password08@"}\' '
        '| grep -o \'"access_token":"[^"]*"\' | cut -d\'"\' -f4',
        capture_output=True
    )
    
    if not token:
        click.echo(f"{Colors.YELLOW}⚠️  Could not get token. User may already exist.{Colors.NC}")
    else:
        # Create schedule user
        click.echo("Creating schedule user...")
        run_command(
            f'curl -X POST "http://localhost:8000/api/v1/users/" '
            f'-H "accept: application/json" '
            f'-H "Authorization: Bearer {token}" '
            f'-H "Content-Type: application/json" '
            f'-d \'{{"username":"schedule","fullname":"schedule bot","password":"Schedule1@local",'
            f'"email":"schedule@example.com","privilege":true,"is_active":true,"master":true,"squad":"bot"}}\' '
            f'-s -o /dev/null',
            check=False
        )
    
    click.echo(f"\n{Colors.GREEN}{'#' * 50}{Colors.NC}")
    click.echo(f"{Colors.GREEN}#  Now you can play with SLD! 🕹️{Colors.NC}")
    click.echo(f"{Colors.GREEN}{'#' * 50}{Colors.NC}\n")
    click.echo(f"{Colors.BOLD}Dashboard:{Colors.NC} {Colors.BLUE}http://localhost:5000/{Colors.NC}")
    click.echo(f"{Colors.BOLD}API Docs:{Colors.NC}  {Colors.BLUE}http://localhost:8000/docs{Colors.NC}")
    click.echo(f"\n{Colors.BOLD}Credentials:{Colors.NC}")
    click.echo(f"  • Username:  {Colors.GREEN}admin{Colors.NC}")
    click.echo(f"  • Password: {Colors.GREEN}Password08@{Colors.NC}\n")


@cli.command()
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes', 'k8s']),
              default='docker', help='Deployment mode (k8s = kubernetes)')
@click.option('--env', '-e', type=click.Choice(['dev', 'prod']),
              default='dev', help='Environment for Kubernetes')
@click.option('--service', '-s', help='Specific service (for kubernetes)')
@click.option('--follow', '-f', is_flag=True, help='Follow logs')
def logs(mode, env, service, follow):
    """View service logs"""
    project_root = get_project_root()
    
    # Normalize mode
    if mode == 'k8s':
        mode = 'kubernetes'
    
    if mode == 'docker':
        docker_dir = project_root / 'play-with-sld' / 'docker'
        follow_flag = '-f' if follow else ''
        
        if service:
            run_command(f"docker compose logs {follow_flag} {service}", cwd=docker_dir)
        else:
            run_command(f"docker compose logs {follow_flag}", cwd=docker_dir)
    else:  # kubernetes
        follow_flag = '-f' if follow else ''
        namespace = "default"
        
        if service:
            run_command(f"kubectl logs {follow_flag} -n {namespace} deployment/{service}")
        else:
            click.echo(f"Available services in {namespace}:")
            run_command(f"kubectl get deployments -n {namespace}")


@cli.command()
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes', 'k8s']),
              default='docker', help='Deployment mode (k8s = kubernetes)')
@click.option('--env', '-e', type=click.Choice(['dev', 'prod']),
              default='dev', help='Environment for Kubernetes')
def status(mode, env):
    """View services status"""
    project_root = get_project_root()
    
    # Normalize mode
    if mode == 'k8s':
        mode = 'kubernetes'
    
    click.echo(f"{Colors.BOLD}📊 Services status:{Colors.NC}\n")
    
    if mode == 'docker':
        docker_dir = project_root / 'play-with-sld' / 'docker'
        run_command("docker compose ps", cwd=docker_dir)
    else:  # kubernetes
        namespace = "default"
        click.echo(f"{Colors.BOLD}Environment: {env.upper()} (namespace: {namespace}){Colors.NC}\n")
        click.echo(f"{Colors.BOLD}Pods:{Colors.NC}")
        run_command(f"kubectl get pods -n {namespace}")
        click.echo(f"\n{Colors.BOLD}Deployments:{Colors.NC}")
        run_command(f"kubectl get deployments -n {namespace}")
        click.echo(f"\n{Colors.BOLD}Services:{Colors.NC}")
        run_command(f"kubectl get services -n {namespace}")


@cli.command()
def verify():
    """Verify UV is installed in images"""
    click.echo(f"{Colors.BOLD}🔍 Verifying UV installation...{Colors.NC}\n")
    
    images = [
        ('API Backend', 'd10s0vsky/sld-api:latest'),
        ('Dashboard', 'd10s0vsky/sld-dashboard:latest'),
        ('Remote State', 'd10s0vsky/sld-remote-state:latest'),
        ('Schedule', 'd10s0vsky/sld-schedule:latest'),
    ]
    
    for name, image in images:
        click.echo(f"{Colors.BLUE}Checking {name}...{Colors.NC}")
        
        # Check if image exists
        result = subprocess.run(
            f"docker images -q {image}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            click.echo(f"  {Colors.RED}✗ Image not found{Colors.NC}")
            continue
        
        # Check UV
        result = subprocess.run(
            f"docker run --rm {image} which uv",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Get version
            version_result = subprocess.run(
                f"docker run --rm {image} uv --version",
                shell=True,
                capture_output=True,
                text=True
            )
            version = version_result.stdout.strip() if version_result.returncode == 0 else "unknown"
            click.echo(f"  {Colors.GREEN}✓ UV installed: {version}{Colors.NC}")
        else:
            click.echo(f"  {Colors.RED}✗ UV not found{Colors.NC}")
    
    click.echo()


@cli.command()
def check():
    """Check system prerequisites"""
    click.echo(f"{Colors.BOLD}🔍 Checking prerequisites...{Colors.NC}\n")
    
    missing = check_requirements()
    
    if not missing:
        click.echo(f"{Colors.GREEN}✅ All prerequisites are installed!{Colors.NC}\n")
        
        # Show versions
        click.echo(f"{Colors.BOLD}Versions:{Colors.NC}")
        for cmd in ['docker', 'kind', 'kubectl']:
            result = subprocess.run(
                f"{cmd} --version 2>&1 | head -1",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                click.echo(f"  • {cmd}: {result.stdout.strip()}")
        
        # Check docker compose version
        result = subprocess.run(
            "docker compose version 2>&1 | head -1",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            click.echo(f"  • docker compose: {result.stdout.strip()}")
    else:
        click.echo(f"{Colors.RED}❌ Missing prerequisites:{Colors.NC}")
        for item in missing:
            click.echo(f"  • {item}")
        click.echo(f"\n{Colors.YELLOW}Please install missing prerequisites.{Colors.NC}")
        sys.exit(1)


@cli.command()
def clean():
    """Clean local Docker images"""
    click.echo(f"{Colors.BOLD}🧹 Cleaning local images...{Colors.NC}\n")
    
    if click.confirm('Do you want to remove all local SLD images?'):
        images = [
            'd10s0vsky/sld-api:latest',
            'd10s0vsky/sld-dashboard:latest',
            'd10s0vsky/sld-remote-state:latest',
            'd10s0vsky/sld-schedule:latest'
        ]
        
        for img in images:
            click.echo(f"Removing {img}...")
            run_command(f"docker rmi {img}", check=False)
        
        click.echo(f"\n{Colors.GREEN}✅ Cleanup completed!{Colors.NC}")
    else:
        click.echo("Operation cancelled.")


@cli.command()
@click.option('--service', '-s', type=click.Choice(['api', 'dashboard', 'remote-state', 'schedule', 'all']),
              default='all', help='Service to format')
@click.option('--check', is_flag=True, help='Check only, do not modify files')
def format(service, check):
    """
    Format code with Black
    
    This command runs Black code formatter on the selected service(s).
    """
    project_root = get_project_root()
    
    click.echo(f"{Colors.BOLD}🎨 Formatting code with Black...{Colors.NC}\n")
    
    services = {
        'api': 'sld-api-backend',
        'dashboard': 'sld-dashboard',
        'remote-state': 'sld-remote-state',
        'schedule': 'sld-schedule',
    }
    
    if service == 'all':
        to_format = list(services.values())
    else:
        to_format = [services[service]]
    
    total = len(to_format)
    failed = []
    
    for idx, svc_dir in enumerate(to_format, 1):
        svc_path = project_root / svc_dir
        
        if not svc_path.exists():
            click.echo(f"{Colors.RED}✗ [{idx}/{total}] {svc_dir} not found{Colors.NC}\n")
            failed.append(svc_dir)
            continue
        
        click.echo(f"{Colors.BLUE}[{idx}/{total}]{Colors.NC} Formatting {Colors.BOLD}{svc_dir}{Colors.NC}...")
        
        # Run Black
        check_flag = '--check --diff' if check else ''
        black_result = run_command(
            f"uv run black {check_flag} .",
            cwd=svc_path,
            check=False
        )
        
        if black_result:
            click.echo(f"  {Colors.GREEN}✓ Black completed{Colors.NC}")
        else:
            click.echo(f"  {Colors.YELLOW}⚠ Black had issues{Colors.NC}")
            failed.append(svc_dir)
        
        click.echo()
    
    if failed:
        click.echo(f"{Colors.YELLOW}⚠️  Some services had issues: {', '.join(failed)}{Colors.NC}\n")
    else:
        if check:
            click.echo(f"{Colors.GREEN}✅ All code is properly formatted!{Colors.NC}\n")
        else:
            click.echo(f"{Colors.GREEN}✅ Code formatting completed!{Colors.NC}\n")


@cli.command()
@click.option('--service', '-s', type=click.Choice(['api', 'dashboard', 'remote-state', 'schedule', 'all']),
              default='all', help='Service to lint')
def lint(service):
    """
    Run linting checks with Ruff
    
    Fast Python linter that checks for code quality issues.
    """
    project_root = get_project_root()
    
    click.echo(f"{Colors.BOLD}🔍 Running linter...{Colors.NC}\n")
    
    services = {
        'api': 'sld-api-backend',
        'dashboard': 'sld-dashboard',
        'remote-state': 'sld-remote-state',
        'schedule': 'sld-schedule',
    }
    
    if service == 'all':
        to_lint = list(services.values())
    else:
        to_lint = [services[service]]
    
    total = len(to_lint)
    failed = []
    
    for idx, svc_dir in enumerate(to_lint, 1):
        svc_path = project_root / svc_dir
        
        if not svc_path.exists():
            click.echo(f"{Colors.RED}✗ [{idx}/{total}] {svc_dir} not found{Colors.NC}\n")
            failed.append(svc_dir)
            continue
        
        click.echo(f"{Colors.BLUE}[{idx}/{total}]{Colors.NC} Linting {Colors.BOLD}{svc_dir}{Colors.NC}...")
        
        result = run_command(
            "uv run ruff check .",
            cwd=svc_path,
            check=False
        )
        
        if result:
            click.echo(f"{Colors.GREEN}✓ No issues found{Colors.NC}\n")
        else:
            click.echo(f"{Colors.YELLOW}⚠ Issues found (run './sld_cli.py format -s {list(services.keys())[list(services.values()).index(svc_dir)]}' to fix){Colors.NC}\n")
            failed.append(svc_dir)
    
    if failed:
        click.echo(f"{Colors.RED}❌ Linting failed for: {', '.join(failed)}{Colors.NC}\n")
        sys.exit(1)
    else:
        click.echo(f"{Colors.GREEN}✅ All code passes linting checks!{Colors.NC}\n")


@cli.group()
def kind():
    """Manage Kind (Kubernetes in Docker) cluster"""
    pass


@kind.command('create')
def kind_create():
    """Create a Kind cluster for SLD"""
    project_root = get_project_root()
    k8s_dir = project_root / 'play-with-sld' / 'kubernetes'
    
    click.echo(f"{Colors.BOLD}☸️  Creating Kind cluster...{Colors.NC}\n")
    
    # Check if kind is installed
    result = subprocess.run('which kind', shell=True, capture_output=True)
    if result.returncode != 0:
        click.echo(f"{Colors.RED}❌ Kind is not installed{Colors.NC}")
        click.echo(f"\n{Colors.YELLOW}Install Kind:{Colors.NC}")
        click.echo("  curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64")
        click.echo("  chmod +x ./kind")
        click.echo("  sudo mv ./kind /usr/local/bin/kind")
        sys.exit(1)
    
    # Check if cluster already exists
    cluster_exists = subprocess.run(
        "kind get clusters | grep -q '^kind$'",
        shell=True,
        capture_output=True
    ).returncode == 0
    
    if cluster_exists:
        click.echo(f"{Colors.YELLOW}⚠️  Kind cluster already exists{Colors.NC}")
        if not click.confirm('Do you want to delete and recreate it?'):
            click.echo("Operation cancelled.")
            return
        
        click.echo("\nDeleting existing cluster...")
        run_command("kind delete cluster")
        click.echo()
    
    # Create cluster
    click.echo("Creating cluster with configuration...")
    run_command("kind create cluster --config kind.yml", cwd=k8s_dir)
    
    # Verify cluster
    click.echo("\nVerifying cluster...")
    run_command("kubectl cluster-info --context kind-kind")
    
    click.echo(f"\n{Colors.GREEN}✅ Kind cluster created successfully!{Colors.NC}\n")
    click.echo(f"{Colors.BOLD}Next steps:{Colors.NC}")
    click.echo(f"  • Deploy DEV:  {Colors.YELLOW}./sld_cli.py start -m kubernetes -e dev{Colors.NC}")
    click.echo(f"  • Deploy PROD: {Colors.YELLOW}./sld_cli.py start -m kubernetes -e prod{Colors.NC}")


@kind.command('delete')
def kind_delete():
    """Delete the Kind cluster"""
    click.echo(f"{Colors.BOLD}🛑 Deleting Kind cluster...{Colors.NC}\n")
    
    # Check if cluster exists
    cluster_exists = subprocess.run(
        "kind get clusters | grep -q '^kind$'",
        shell=True,
        capture_output=True
    ).returncode == 0
    
    if not cluster_exists:
        click.echo(f"{Colors.YELLOW}⚠️  No Kind cluster found{Colors.NC}")
        return
    
    if click.confirm('Are you sure you want to delete the cluster?'):
        run_command("kind delete cluster")
        click.echo(f"\n{Colors.GREEN}✅ Cluster deleted!{Colors.NC}")
    else:
        click.echo("Operation cancelled.")


@kind.command('status')
def kind_status():
    """Show Kind cluster status"""
    click.echo(f"{Colors.BOLD}☸️  Kind Cluster Status{Colors.NC}\n")
    
    # Check if kind is installed
    result = subprocess.run('which kind', shell=True, capture_output=True)
    if result.returncode != 0:
        click.echo(f"{Colors.RED}❌ Kind is not installed{Colors.NC}")
        return
    
    # List clusters
    click.echo(f"{Colors.BOLD}Clusters:{Colors.NC}")
    result = subprocess.run("kind get clusters", shell=True, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        click.echo(result.stdout)
        
        # Check if 'kind' cluster exists
        if 'kind' in result.stdout:
            click.echo(f"\n{Colors.BOLD}Nodes:{Colors.NC}")
            run_command("kubectl get nodes", check=False)
            
            click.echo(f"\n{Colors.BOLD}Namespaces:{Colors.NC}")
            run_command("kubectl get namespaces | grep -E '(NAME|sld-)'", check=False)
    else:
        click.echo(f"{Colors.YELLOW}No clusters found{Colors.NC}")


@kind.command('load-images')
@click.option('--tag', '-t', default='latest', help='Image tag to load')
def kind_load_images(tag):
    """Load Docker images into Kind cluster"""
    click.echo(f"{Colors.BOLD}📦 Loading images into Kind cluster...{Colors.NC}\n")
    
    # Check if cluster exists
    cluster_exists = subprocess.run(
        "kind get clusters | grep -q '^kind$'",
        shell=True,
        capture_output=True
    ).returncode == 0
    
    if not cluster_exists:
        click.echo(f"{Colors.RED}❌ No Kind cluster found. Create one first with: ./sld_cli.py kind create{Colors.NC}")
        sys.exit(1)
    
    images = [
        f'd10s0vsky/sld-api:{tag}',
        f'd10s0vsky/sld-dashboard:{tag}',
        f'd10s0vsky/sld-remote-state:{tag}',
        f'd10s0vsky/sld-schedule:{tag}'
    ]
    
    failed = []
    for img in images:
        # Check if image exists locally
        result = subprocess.run(
            f"docker images -q {img}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            click.echo(f"{Colors.YELLOW}⚠️  {img} not found locally, skipping...{Colors.NC}")
            failed.append(img)
            continue
        
        click.echo(f"Loading {img}...")
        if not run_command(f"kind load docker-image {img}", check=False):
            failed.append(img)
    
    if failed:
        click.echo(f"\n{Colors.YELLOW}⚠️  Some images failed to load: {', '.join(failed)}{Colors.NC}")
        click.echo(f"\n{Colors.BOLD}Build them first:{Colors.NC} ./sld_cli.py build --tag {tag}")
    else:
        click.echo(f"\n{Colors.GREEN}✅ All images loaded successfully!{Colors.NC}")


@cli.command()
@click.option('--env', '-e', type=click.Choice(['dev', 'prod']),
              required=True, help='Environment to build manifest for')
@click.option('--output', '-o', help='Output file (default: print to stdout)')
def kustomize(env, output):
    """
    Build Kustomize manifests for dev or prod environment
    
    Examples:
      ./sld_cli.py kustomize -e dev              # Show dev manifest
      ./sld_cli.py kustomize -e prod -o prod.yml # Save prod manifest
    """
    project_root = get_project_root()
    k8s_dir = project_root / 'play-with-sld' / 'kubernetes'
    overlay_path = f"overlays/{env}"
    
    click.echo(f"{Colors.BOLD}🔧 Building Kustomize manifest for {env.upper()}...{Colors.NC}\n")
    
    if output:
        # Save to file
        cmd = f"kubectl kustomize {overlay_path}/ > {output}"
        run_command(cmd, cwd=k8s_dir)
        click.echo(f"{Colors.GREEN}✓{Colors.NC} Manifest saved to: {output}\n")
    else:
        # Print to stdout
        run_command(f"kubectl kustomize {overlay_path}/", cwd=k8s_dir)


@cli.command()
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes', 'k8s']),
              default='docker', help='Deployment mode (k8s = kubernetes)')
@click.option('--skip-check', is_flag=True, help='Skip prerequisites check')
@click.option('--env', '-e', type=click.Choice(['dev', 'prod']),
              default='dev', help='Environment for Kubernetes (dev=latest, prod=versioned)')
def quickstart(mode, skip_check, env):
    """
    🚀 Quick start: build, start and initialize everything at once
    
    This command executes the complete flow:
    1. Checks prerequisites
    2. Builds all Docker images with UV
    3. Starts services (Docker Compose or Kubernetes)
    4. Waits for services to be ready
    5. Initializes admin user
    """
    # Normalize mode
    if mode == 'k8s':
        mode = 'kubernetes'
    
    click.echo(f"{Colors.BOLD}{'=' * 60}{Colors.NC}")
    click.echo(f"{Colors.BOLD}🚀 SLD QuickStart - All in one!{Colors.NC}")
    if mode == 'kubernetes':
        click.echo(f"{Colors.BOLD}   Environment: {env.upper()}{Colors.NC}")
    click.echo(f"{Colors.BOLD}{'=' * 60}{Colors.NC}\n")
    
    # Step 1: Check prerequisites
    if not skip_check:
        click.echo(f"{Colors.BLUE}[Step 1/5]{Colors.NC} Checking prerequisites...\n")
        missing = check_requirements()
        
        if missing:
            click.echo(f"{Colors.RED}❌ Missing prerequisites: {', '.join(missing)}{Colors.NC}")
            click.echo(f"\n{Colors.YELLOW}Install prerequisites and try again.{Colors.NC}")
            click.echo(f"Or run: {Colors.BOLD}./sld_cli.py check{Colors.NC} for more details")
            sys.exit(1)
        
        click.echo(f"{Colors.GREEN}✓ All prerequisites are installed{Colors.NC}\n")
    else:
        click.echo(f"{Colors.YELLOW}⚠️  Skipping prerequisites check{Colors.NC}\n")
    
    # Step 2: Build images
    click.echo(f"{Colors.BLUE}[Step 2/5]{Colors.NC} Building Docker images with UV...\n")
    click.echo(f"{Colors.YELLOW}⏱️  This may take 10-15 minutes the first time...{Colors.NC}\n")
    
    ctx = click.get_current_context()
    try:
        ctx.invoke(build, service='all', tag='latest', no_cache=False, parallel=False, max_workers=4)
    except SystemExit:
        click.echo(f"\n{Colors.RED}❌ Error building images{Colors.NC}")
        sys.exit(1)
    
    click.echo(f"\n{Colors.GREEN}✓ Images built successfully{Colors.NC}\n")
    
    # Step 3: Start services
    click.echo(f"{Colors.BLUE}[Step 3/5]{Colors.NC} Starting services ({mode})...\n")
    
    try:
        ctx.invoke(start, mode=mode, env=env, build_first=False)
    except SystemExit:
        click.echo(f"\n{Colors.RED}❌ Error starting services{Colors.NC}")
        sys.exit(1)
    
    click.echo(f"\n{Colors.GREEN}✓ Services started{Colors.NC}\n")
    
    # Step 4: Wait for services to be ready
    click.echo(f"{Colors.BLUE}[Step 4/5]{Colors.NC} Waiting for services to be ready...\n")
    
    if mode == 'docker':
        click.echo("Waiting 45 seconds for services to initialize completely...")
        for i in range(45):
            time.sleep(1)
            if i % 5 == 0:
                click.echo(f"  {45-i} seconds remaining...", nl=False)
                click.echo()
    else:  # kubernetes
        click.echo("Waiting for pods to be ready...")
        time.sleep(30)
        click.echo("\nChecking pod status...")
        run_command("kubectl get pods -n default", check=False)
        time.sleep(20)
    
    click.echo(f"\n{Colors.GREEN}✓ Services ready{Colors.NC}\n")
    
    # Step 5: Initialize credentials
    click.echo(f"{Colors.BLUE}[Step 5/5]{Colors.NC} Initializing admin user...\n")
    
    try:
        ctx.invoke(init, mode=mode)
    except SystemExit:
        click.echo(f"\n{Colors.YELLOW}⚠️  User may already exist{Colors.NC}")
    
    # Final summary
    click.echo(f"\n{Colors.BOLD}{'=' * 60}{Colors.NC}")
    click.echo(f"{Colors.GREEN}{Colors.BOLD}✅ QuickStart completed successfully!{Colors.NC}")
    click.echo(f"{Colors.BOLD}{'=' * 60}{Colors.NC}\n")
    
    click.echo(f"{Colors.BOLD}🎉 Your SLD environment is ready to use!{Colors.NC}\n")
    
    click.echo(f"{Colors.BOLD}Access:{Colors.NC}")
    click.echo(f"  • Dashboard: {Colors.BLUE}{Colors.BOLD}http://localhost:5000/{Colors.NC}")
    click.echo(f"  • API Docs:  {Colors.BLUE}{Colors.BOLD}http://localhost:8000/docs{Colors.NC}\n")
    
    click.echo(f"{Colors.BOLD}Credentials:{Colors.NC}")
    click.echo(f"  • Username:  {Colors.GREEN}{Colors.BOLD}admin{Colors.NC}")
    click.echo(f"  • Password: {Colors.GREEN}{Colors.BOLD}Password08@{Colors.NC}\n")
    
    click.echo(f"{Colors.BOLD}Useful commands:{Colors.NC}")
    if mode == 'kubernetes':
        click.echo(f"  • View status:    {Colors.YELLOW}./sld_cli.py status -m kubernetes -e {env}{Colors.NC}")
        click.echo(f"  • View logs:      {Colors.YELLOW}./sld_cli.py logs -m kubernetes -e {env} -f{Colors.NC}")
    else:
        click.echo(f"  • View status:    {Colors.YELLOW}./sld_cli.py status{Colors.NC}")
        click.echo(f"  • View logs:      {Colors.YELLOW}./sld_cli.py logs -f{Colors.NC}")
    click.echo(f"  • Verify UV:      {Colors.YELLOW}./sld_cli.py verify{Colors.NC}")
    click.echo(f"  • Stop:           {Colors.YELLOW}./sld_cli.py stop -m {mode}{Colors.NC}\n")
    
    if mode == 'docker':
        click.echo(f"{Colors.BOLD}💡 Tip:{Colors.NC} Open the links in your browser and start using SLD!")
    else:
        click.echo(f"{Colors.BOLD}💡 Tip:{Colors.NC} Run './sld_cli.py status -m kubernetes -e {env}' to see all running pods")


if __name__ == '__main__':
    cli()
