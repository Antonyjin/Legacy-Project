# ADR-006: Deployment Platform

**Status**: Accepted  
**Date**: 2025-10-31  
**Deciders**: Antonyjin  
**Consequences**: Infrastructure costs, DevOps complexity, scalability constraints

## Context

We need to choose a deployment platform for production that:

1. Supports both OCaml and Python runtimes
2. Scales with user demand
3. Minimizes operational overhead
4. Supports monitoring and logging
5. Is cost-effective for open-source project

## Problem

Multiple deployment options exist with different trade-offs:
- **Heroku**: Simple but expensive
- **AWS**: Powerful but complex
- **Docker on VPS**: Good balance but requires management
- **GitHub Pages**: Limited (static only)

We must choose based on project needs and constraints.

## Decision

We use a **Docker-on-VPS approach** with docker-compose as the primary deployment method:

### Primary Platform: Docker on VPS

**Chosen VPS Provider**: DigitalOcean (or similar - AWS EC2, Linode)

**Rationale**:
- ✅ Supports both OCaml binaries and Python runtime
- ✅ Docker isolates dependencies cleanly
- ✅ Cost-effective ($5-10/month for basic tier)
- ✅ Simple git-based deployment (git push → deploy)
- ✅ Easy to add monitoring and logging
- ✅ Open-source friendly

### Architecture

```
┌─────────────────────────────────────┐
│         VPS (DigitalOcean)          │
├─────────────────────────────────────┤
│  ┌──────────────────────────────┐   │
│  │     Docker Container         │   │
│  ├──────────────────────────────┤   │
│  │  GeneWeb Application         │   │
│  │  ├─ Python Flask Proxy       │   │
│  │  ├─ OCaml Binaries (gwd)     │   │
│  │  └─ GEDCOM Database          │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │     Nginx Reverse Proxy      │   │
│  │     (SSL termination)        │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
         ↑
    Public Internet (HTTPS)
```

### Implementation Details

#### 1. VPS Setup
```bash
# Provider: DigitalOcean (or AWS, Linode, etc.)
# OS: Ubuntu 22.04 LTS
# Size: Basic tier (1 CPU, 1GB RAM, 25GB SSD)
# Cost: ~$5/month
```

#### 2. Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "2317:2317"
    volumes:
      - ./bases:/app/bases
      - ./logs:/app/logs
    environment:
      - BACKEND=ocaml
      - LOG_LEVEL=info
    restart: always
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - app
```

#### 3. Deployment Process
```bash
# 1. Push to main branch (or tag for release)
git push origin main

# 2. GitHub Actions CI runs tests
# If tests pass:

# 3. Deploy to VPS
ssh deploy@geneweb.example.com
cd /opt/geneweb
git pull origin main
docker-compose up -d --build

# 4. Monitor deployment
curl https://geneweb.example.com/health
```

#### 4. SSL/HTTPS
- Use Let's Encrypt (free certificates)
- Certbot for automation
- Auto-renewal via systemd timer

#### 5. Monitoring & Logging
- Application logs → `/var/log/geneweb/`
- System monitoring via standard tools
- Optional: DataDog, New Relic, or Sentry for advanced monitoring

## Deployment Alternatives

### Alternative 1: Heroku

**Pros**:
- Extremely simple (git push → deploy)
- Built-in monitoring and scaling
- No DevOps knowledge needed

**Cons**:
- ❌ Expensive ($50+/month for production dyno)
- ❌ Requires Heroku-specific buildpack for OCaml
- ❌ Limited customization
- ❌ Not ideal for open-source projects

**Verdict**: Rejected due to cost

### Alternative 2: AWS (ECS/Fargate)

**Pros**:
- Highly scalable
- Managed container service
- Enterprise-grade reliability

**Cons**:
- ❌ Complex setup (CloudFormation, IAM, VPC, etc.)
- ❌ Expensive for low-traffic projects ($50-100+/month)
- ❌ Steep learning curve
- ❌ Overkill for current scale

**Verdict**: Rejected (too complex for project needs)

### Alternative 3: Kubernetes

**Pros**:
- Industry standard for containers
- Highly scalable
- Multi-node support

**Cons**:
- ❌ Extreme complexity for single-container application
- ❌ Kubernetes learning curve
- ❌ Expensive managed K8s ($100+/month)
- ❌ Operational overhead

**Verdict**: Rejected (premature complexity)

### Alternative 4: GitHub Pages + Static Export

**Pros**:
- Free hosting
- No infrastructure management

**Cons**:
- ❌ Cannot run OCaml daemon
- ❌ Cannot execute Python code
- ❌ Only suitable for static content

**Verdict**: Rejected (doesn't meet requirements)

## Consequences

### Positive
- ✅ Simple to understand and manage
- ✅ Cost-effective ($5-20/month)
- ✅ Supports full stack (OCaml + Python)
- ✅ Easy to add monitoring/logging
- ✅ Quick to deploy changes
- ✅ Easy to scale vertically
- ✅ Good for open-source projects

### Negative
- ❌ Requires basic DevOps knowledge
- ❌ Manual server management
- ❌ Not suitable for extremely high traffic
- ❌ Single point of failure (need backup strategy)
- ❌ Manual security updates

## Scaling Strategy

### Phase 1: Single VPS
- Basic $5-10/month tier
- Suitable for 1-10 concurrent users
- No horizontal scaling needed

### Phase 2: Larger VPS
- Upgrade to $20-40/month tier
- Suitable for 10-100 concurrent users
- Add Redis for caching (if needed)

### Phase 3: Multi-Server (if needed)
- Load balancer (nginx, HAProxy)
- Multiple application servers
- Shared database/cache layer
- Consider managed Kubernetes at this scale

## Related Decisions

- **ADR-004**: Migration strategy
- **ADR-007**: CI/CD pipeline design
- **ADR-008**: Monitoring and observability (future)

## References

- Docker Documentation: https://docs.docker.com/
- DigitalOcean Pricing: https://www.digitalocean.com/pricing
- Let's Encrypt: https://letsencrypt.org/
- Nginx Documentation: https://nginx.org/
