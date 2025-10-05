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
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes']),
              default='docker', help='Deployment mode')
@click.option('--build-first', '-b', is_flag=True, help='Build images before starting')
def start(mode, build_first):
    """Start SLD locally"""
    project_root = get_project_root()
    
    if build_first:
        click.echo(f"{Colors.YELLOW}📦 Building images first...{Colors.NC}\n")
        ctx = click.get_current_context()
        ctx.invoke(build, service='all', tag='latest', no_cache=False)
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
        click.echo(f"{Colors.BOLD}☸️  Starting SLD with Kubernetes (kind)...{Colors.NC}\n")
        
        # Check prerequisites
        missing = [r for r in ['kind', 'kubectl'] if subprocess.run(
            f'which {r}', shell=True, capture_output=True
        ).returncode != 0]
        
        if missing:
            click.echo(f"{Colors.RED}❌ Missing prerequisites: {', '.join(missing)}{Colors.NC}")
            sys.exit(1)
        
        k8s_dir = project_root / 'play-with-sld' / 'kubernetes'
        
        click.echo("Creating kind cluster...")
        run_command("kind create cluster --config kind.yml", cwd=k8s_dir, check=False)
        
        click.echo("\nLoading images into kind...")
        images = [
            'd10s0vsky/sld-api:latest',
            'd10s0vsky/sld-dashboard:latest',
            'd10s0vsky/sld-remote-state:latest',
            'd10s0vsky/sld-schedule:latest'
        ]
        
        for img in images:
            click.echo(f"  Loading {img}...")
            run_command(f"kind load docker-image {img}", check=False)
        
        click.echo("\nDeploying application...")
        run_command("kubectl apply -k k8s/", cwd=k8s_dir)
        
        click.echo(f"\n{Colors.GREEN}✅ Cluster created and application deployed!{Colors.NC}\n")
    
    click.echo(f"{Colors.BOLD}Available endpoints:{Colors.NC}")
    click.echo(f"  • Dashboard: {Colors.BLUE}http://localhost:5000/{Colors.NC}")
    click.echo(f"  • API Docs:  {Colors.BLUE}http://localhost:8000/docs{Colors.NC}")
    click.echo(f"\n{Colors.YELLOW}Run 'sld-cli init' to create initial user{Colors.NC}")


@cli.command()
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes']),
              default='docker', help='Deployment mode')
def stop(mode):
    """Stop SLD services"""
    project_root = get_project_root()
    
    if mode == 'docker':
        click.echo(f"{Colors.BOLD}🛑 Stopping Docker Compose services...{Colors.NC}\n")
        docker_dir = project_root / 'play-with-sld' / 'docker'
        run_command("docker compose down", cwd=docker_dir)
        
    else:  # kubernetes
        click.echo(f"{Colors.BOLD}🛑 Deleting kind cluster...{Colors.NC}\n")
        run_command("kind delete cluster")
    
    click.echo(f"{Colors.GREEN}✅ Services stopped!{Colors.NC}")


@cli.command()
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes']),
              default='docker', help='Deployment mode')
def init(mode):
    """Initialize admin user and credentials"""
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
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes']),
              default='docker', help='Deployment mode')
@click.option('--service', '-s', help='Specific service (for kubernetes)')
@click.option('--follow', '-f', is_flag=True, help='Follow logs')
def logs(mode, service, follow):
    """View service logs"""
    project_root = get_project_root()
    
    if mode == 'docker':
        docker_dir = project_root / 'play-with-sld' / 'docker'
        follow_flag = '-f' if follow else ''
        
        if service:
            run_command(f"docker compose logs {follow_flag} {service}", cwd=docker_dir)
        else:
            run_command(f"docker compose logs {follow_flag}", cwd=docker_dir)
    else:  # kubernetes
        follow_flag = '-f' if follow else ''
        
        if service:
            run_command(f"kubectl logs {follow_flag} deployment/{service}")
        else:
            click.echo("Available services:")
            run_command("kubectl get deployments")


@cli.command()
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes']),
              default='docker', help='Deployment mode')
def status(mode):
    """View services status"""
    project_root = get_project_root()
    
    click.echo(f"{Colors.BOLD}📊 Services status:{Colors.NC}\n")
    
    if mode == 'docker':
        docker_dir = project_root / 'play-with-sld' / 'docker'
        run_command("docker compose ps", cwd=docker_dir)
    else:  # kubernetes
        click.echo(f"{Colors.BOLD}Pods:{Colors.NC}")
        run_command("kubectl get pods")
        click.echo(f"\n{Colors.BOLD}Deployments:{Colors.NC}")
        run_command("kubectl get deployments")
        click.echo(f"\n{Colors.BOLD}Services:{Colors.NC}")
        run_command("kubectl get services")


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
@click.option('--mode', '-m', type=click.Choice(['docker', 'kubernetes']),
              default='docker', help='Deployment mode')
@click.option('--skip-check', is_flag=True, help='Skip prerequisites check')
def quickstart(mode, skip_check):
    """
    🚀 Quick start: build, start and initialize everything at once
    
    This command executes the complete flow:
    1. Checks prerequisites
    2. Builds all Docker images with UV
    3. Starts services (Docker Compose or Kubernetes)
    4. Waits for services to be ready
    5. Initializes admin user
    """
    click.echo(f"{Colors.BOLD}{'=' * 60}{Colors.NC}")
    click.echo(f"{Colors.BOLD}🚀 SLD QuickStart - All in one!{Colors.NC}")
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
        ctx.invoke(build, service='all', tag='latest', no_cache=False)
    except SystemExit:
        click.echo(f"\n{Colors.RED}❌ Error building images{Colors.NC}")
        sys.exit(1)
    
    click.echo(f"\n{Colors.GREEN}✓ Images built successfully{Colors.NC}\n")
    
    # Step 3: Start services
    click.echo(f"{Colors.BLUE}[Step 3/5]{Colors.NC} Starting services ({mode})...\n")
    
    try:
        ctx.invoke(start, mode=mode, build_first=False)
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
        run_command("kubectl get pods", check=False)
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
    click.echo(f"  • View status:    {Colors.YELLOW}./sld_cli.py status{Colors.NC}")
    click.echo(f"  • View logs:      {Colors.YELLOW}./sld_cli.py logs -f{Colors.NC}")
    click.echo(f"  • Verify UV:      {Colors.YELLOW}./sld_cli.py verify{Colors.NC}")
    click.echo(f"  • Stop:           {Colors.YELLOW}./sld_cli.py stop{Colors.NC}\n")
    
    if mode == 'docker':
        click.echo(f"{Colors.BOLD}💡 Tip:{Colors.NC} Open the links in your browser and start using SLD!")
    else:
        click.echo(f"{Colors.BOLD}💡 Tip:{Colors.NC} Run 'kubectl get pods' to see all running pods")


if __name__ == '__main__':
    cli()
