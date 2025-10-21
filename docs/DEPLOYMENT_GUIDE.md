# 🚀 Deployment Guide

**Status**: 📝 DRAFT - Will be completed during Week 2 sprint  
**Last Updated**: October 21, 2024

---

## Overview

This guide covers deployment of the GeneWeb application in various environments.

**Current State**: OCaml binaries + manual deployment  
**Planned**: Docker containerization + automated deployment (Week 2-3)

---

## 📦 Current Deployment (OCaml Binaries)

### Local Development

**macOS**:
```bash
cd GeneWeb
./geneweb.sh
# Access: http://localhost:2317/test
```

**Linux**:
```bash
# Download Linux binaries
wget https://github.com/geneweb/geneweb/releases/download/v7.1-beta/geneweb-7.1-beta-linux-x86_64.tar.gz
tar -xzf geneweb-7.1-beta-linux-x86_64.tar.gz -C gw-linux

# Run
cd GeneWeb
gw-linux/gw/gwd -hd ./gw -bd ./bases -p 2317 -lang en
```

### Prerequisites
- macOS or Linux
- Web browser
- Terminal access

### Environment Variables
```bash
# Optional
export GW_PORT=2317        # Web server port
export GW_SETUP_PORT=2316  # Admin interface port
export GW_LANG=en          # Default language (en, fr, etc.)
```

---

## 🐳 Docker Deployment (Planned - Week 2)

**Issues**: #120 (Dockerfile), #121 (docker-compose)  
**Status**: To be implemented

### Planned Architecture

```
geneweb:latest
├─ Base: debian:slim or alpine
├─ OCaml binaries (gwd, gwsetup, ged2gwb, gwb2ged)
├─ Python environment (for migrated functions)
├─ Templates & assets
└─ Exposed ports: 2317 (gwd), 2316 (gwsetup)
```

### Planned docker-compose.yml

```yaml
version: '3.8'

services:
  geneweb:
    build: .
    ports:
      - "2317:2317"  # Web interface
      - "2316:2316"  # Admin interface
    volumes:
      - ./bases:/app/bases  # Database files
      - ./logs:/app/logs    # Log files
    environment:
      - GW_LANG=en
      - LOG_LEVEL=info
    restart: unless-stopped

  # Future: PostgreSQL for migrated Python backend
  # postgres:
  #   image: postgres:15
  #   ...
```

### Planned Commands

```bash
# Build image
docker build -t geneweb:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f geneweb

# Stop
docker-compose down

# Access application
open http://localhost:2317/test
```

---

## ☁️ Production Deployment (Planned - Week 3)

**Issues**: #142 (Deploy to prod), #143 (Test deployment)  
**Status**: To be implemented

### Deployment Options

#### Option 1: VPS (Digital Ocean / Linode / Hetzner)
**Pros**: Full control, cost-effective  
**Cons**: Manual management

**Steps** (to be detailed):
1. Provision VPS (Ubuntu 22.04 LTS)
2. Install Docker & docker-compose
3. Clone repository
4. Run `docker-compose up -d`
5. Configure nginx reverse proxy
6. Setup SSL (Let's Encrypt)

#### Option 2: AWS ECS/Fargate
**Pros**: Managed, scalable  
**Cons**: More complex, higher cost

#### Option 3: Heroku
**Pros**: Simplest, git-based deploy  
**Cons**: Limited customization

#### Option 4: Static Export (Future)
For Python version: pre-render static HTML + JavaScript SPA

---

## 🔐 Security Considerations

### Current
- ⚠️ No authentication on gwd (public genealogy data)
- ⚠️ Wizard mode requires caution (data modification)
- ✅ GEDCOM exports respect privacy settings

### Planned
- [ ] HTTPS/TLS termination
- [ ] Basic authentication for admin interface
- [ ] Rate limiting
- [ ] Input validation
- [ ] Security headers
- [ ] Regular updates

---

## 📊 Monitoring & Logging

### Current Logging
```bash
# gwd logs
tail -f GeneWeb/gwd.out

# gwsetup logs
tail -f GeneWeb/gwsetup.out
```

### Planned Monitoring (Week 3)
- [ ] Application logs (structured JSON)
- [ ] Access logs (nginx)
- [ ] Error tracking (Sentry or similar)
- [ ] Uptime monitoring
- [ ] Performance metrics

---

## 🔄 CI/CD Pipeline (Week 2)

**Issue**: #117 (GitHub Actions workflow)

### Planned Workflow

```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/python/ --cov=tests
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t geneweb:${{ github.sha }} .
      - name: Push to registry
        # if: github.ref == 'refs/heads/main'
        run: echo "Push to Docker Hub or GH Container Registry"

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: echo "SSH to server and docker-compose pull && up"
```

---

## 🧪 Smoke Tests After Deployment

### Manual Checklist
```bash
# 1. Home page loads
curl http://localhost:2317/test | grep "GeneWeb"

# 2. Person page works
curl http://localhost:2317/test?p=Charles&n=Windsor | grep "Charles"

# 3. French localization
curl http://localhost:2317/test?lang=fr | grep "Accueil"

# 4. GEDCOM export works
curl "http://localhost:2317/test?m=GEDCOM" > test.ged
wc -l test.ged  # Should have >100 lines

# 5. Admin interface (if enabled)
curl http://localhost:2316 | grep "gwsetup"
```

### Automated (Issue #143)
```bash
# Run smoke tests
pytest tests/python/integration/test_deployment_smoke.py -v
```

---

## 📁 File Structure

```
Legacy-Project/
├── Dockerfile                    # (Week 2) Container definition
├── docker-compose.yml            # (Week 2) Orchestration
├── .dockerignore                 # Files to exclude from image
├── scripts/
│   └── deploy.sh                 # (Week 3) Deployment automation
├── GeneWeb/
│   ├── gw/                       # Binaries
│   ├── bases/                    # Databases (volume mount)
│   ├── logs/                     # Logs (volume mount)
│   └── geneweb.sh                # Local dev launcher
└── .github/
    └── workflows/
        └── ci.yml                # (Week 2) CI/CD pipeline
```

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -ti:2317 | xargs kill -9

# Or change port
docker-compose down
# Edit docker-compose.yml ports
docker-compose up -d
```

### Database Not Found
```bash
# Check volume mounts
docker-compose ps
docker-compose logs geneweb

# Ensure bases/ directory exists and has .gwb files
ls -la GeneWeb/bases/
```

### Container Won't Start
```bash
# View logs
docker-compose logs geneweb

# Check Dockerfile syntax
docker build -t geneweb:test .

# Enter container for debugging
docker-compose run --entrypoint /bin/bash geneweb
```

---

## 📞 Support

- **Issues**: https://github.com/Antonyjin/Legacy-Project/issues
- **Wiki**: https://github.com/Antonyjin/Legacy-Project/wiki
- **Deployment Issues**: Label with `deployment`

---

## 🗓️ Implementation Timeline

| Week | Tasks | Issues |
|------|-------|--------|
| **Week 1** (Oct 8-15) | Tests foundation | #97-111 |
| **Week 2** (Oct 16-22) | Docker + CI/CD | #117-121 |
| **Week 3** (Oct 23-29) | Production deploy | #142-143 |

**Status**: Week 2-3 tasks are planned but not yet implemented. This guide will be updated as implementation progresses.

---

**Last Updated**: October 21, 2024  
**Next Update**: October 22, 2024 (after Docker implementation)  
**Defense Date**: October 29, 2024

