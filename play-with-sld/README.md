# 📖 Play with SLD - Quick Start Guide

This guide will help you quickly deploy and test Stack Lifecycle Deployment (SLD) locally.

## 🚀 Quick Start Options

### Option 1: Kubernetes with Kind (Recommended)

```bash
# Navigate to kubernetes playground
cd play-with-sld/kubernetes

# Start Kind cluster and deploy SLD
./kplay.sh

# Access the dashboard
# Dashboard: http://localhost:30000
# API: http://localhost:30800
```

**What this deploys:**
- ✅ Development environment (uses `latest` images)
- ✅ All SLD services (API, Dashboard, Remote State, Scheduler)
- ✅ Infrastructure (MySQL, MongoDB, Redis)
- ✅ Workers (3 Celery workers for parallel deployments)

### Option 2: Docker Compose

```bash
# Navigate to docker playground
cd play-with-sld/docker

# Start all services
./play.sh

# Or manually
docker compose -f docker-compose.yml up -d
```

**What this deploys:**
- ✅ Development environment
- ✅ All services with latest images
- ✅ Faster startup (no Kubernetes overhead)

---

## 🎯 Environment Options

### Development Environment

Uses **latest** images, always pulls newest code:

```bash
# Kubernetes
kubectl apply -k play-with-sld/kubernetes/overlays/dev

# Verify
kubectl get pods -n sld-dev
```

**Characteristics:**
- Namespace: `sld-dev`
- Images: `:latest` tag
- Debug: Enabled
- Auto-pull: Always

### Production Environment

Uses **versioned** images (e.g., `v3.6.2`):

```bash
# Kubernetes
kubectl apply -k play-with-sld/kubernetes/overlays/prod

# Verify
kubectl get pods -n sld-prod
```

**Characteristics:**
- Namespace: `sld-prod`
- Images: `:v3.6.2` tag
- Debug: Disabled
- Replicas: 2 (for API and Dashboard)
- Resource limits: Configured

---

## 🔧 Accessing Services

### Kubernetes (Kind)

After running `./kplay.sh`:

| Service | URL | Port |
|---------|-----|------|
| Dashboard | http://localhost:30000 | 30000 |
| API | http://localhost:30800 | 30800 |
| Remote State | http://localhost:30808 | 30808 |
| Scheduler | http://localhost:31000 | 31000 |

### Docker Compose

| Service | URL | Port |
|---------|-----|------|
| Dashboard | http://localhost:5000 | 5000 |
| API | http://localhost:8000 | 8000 |
| Remote State | http://localhost:8080 | 8080 |
| Scheduler | http://localhost:10000 | 10000 |

---

## 📝 Default Credentials

```
Username: admin@admin.com
Password: admin (change on first login!)
```

---

## 🎮 First Steps

1. **Login to Dashboard**: http://localhost:30000 (Kind) or http://localhost:5000 (Docker)
2. **Add Cloud Credentials**: Settings → Cloud Accounts
3. **Create a Stack**: Stacks → New Stack
4. **Add Variables**: Configure your Terraform variables
5. **Deploy**: Click "Deploy" button

---

## 🔄 Updating Services

### Pull Latest Images

**Development (Kubernetes):**
```bash
# Restart deployments to pull latest
kubectl rollout restart deployment -n sld-dev api-backend
kubectl rollout restart deployment -n sld-dev sld-dashboard
```

**Docker Compose:**
```bash
cd play-with-sld/docker
docker compose pull
docker compose up -d
```

---

## 🛠️ Troubleshooting

### Check Pod Status (Kubernetes)

```bash
# View all pods
kubectl get pods -n sld-dev

# View specific pod logs
kubectl logs -f -n sld-dev deployment/api-backend

# Describe pod for issues
kubectl describe pod -n sld-dev <pod-name>
```

### Check Container Status (Docker)

```bash
# View all containers
docker compose ps

# View logs
docker compose logs -f api-backend

# Restart specific service
docker compose restart api-backend
```

### Reset Everything

**Kubernetes:**
```bash
cd play-with-sld/kubernetes
kind delete cluster --name sld-cluster
./kplay.sh
```

**Docker:**
```bash
cd play-with-sld/docker
docker compose down -v
./play.sh
```

---

## 📚 Next Steps

- Read the [Versioning Guide](../../docs/VERSIONING.md) for production deployments
- Check the [ROADMAP](../../ROADMAP.md) for upcoming features
- Explore the [API Documentation](http://localhost:30800/docs) (Swagger UI)

---

## 🎯 Architecture

```
┌─────────────┐
│  Dashboard  │ ← User Interface (Flask)
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│     API     │────→│   RabbitMQ   │
│  (FastAPI)  │     │  (optional)  │
└──────┬──────┘     └──────┬───────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌──────────────┐
│   Workers   │     │    Redis     │
│  (Celery)   │     │   (cache)    │
└──────┬──────┘     └──────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│ Remote State│     │    MySQL     │
│  (FastAPI)  │     │  (metadata)  │
└─────────────┘     └──────────────┘
       │
       ▼
┌─────────────┐
│   MongoDB   │
│   (states)  │
└─────────────┘
```

---

## 🆘 Need Help?

- **Issues**: [GitHub Issues](https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment/issues)
- **Discussions**: [GitHub Discussions](https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment/discussions)

---

**Happy deploying! 🚀**
