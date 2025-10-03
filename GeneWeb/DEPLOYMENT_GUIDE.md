# Guide de Déploiement et Hébergement - GeneWeb Modern

## 🎯 Vue d'Ensemble

**Objectif** : Présenter les solutions d'hébergement et de déploiement adaptées aux besoins du client  
**Approche** : Analyse des besoins → Solutions recommandées → Justification des choix  
**Focus** : Localhost/On-premise avec possibilité d'évolution cloud  

## 📊 Analyse des Besoins Client

### Profil Client Type - Association Généalogique

#### Besoins Identifiés
- **Données sensibles** : Informations personnelles/familiales
- **Contrôle total** : Maîtrise complète des données
- **Budget limité** : Associations souvent à budget serré
- **Simplicité** : Équipes techniques limitées
- **Évolutivité** : Croissance progressive des bases

#### Contraintes Techniques
- **Sécurité** : Conformité RGPD obligatoire
- **Performance** : Support 10-100 utilisateurs simultanés
- **Disponibilité** : 99.5% minimum (8h/mois d'indisponibilité acceptable)
- **Sauvegarde** : Backup quotidien automatique
- **Maintenance** : Interventions minimales

#### Contraintes Budgétaires
- **CAPEX** : Budget initial limité (<10k€)
- **OPEX** : Coûts récurrents maîtrisés (<200€/mois)
- **Personnel** : Pas d'administrateur système dédié
- **Formation** : Budget formation limité

## 🏗️ Solutions d'Hébergement Recommandées

### Solution 1 : **Localhost/On-Premise** (RECOMMANDÉE)

#### Architecture Technique
```
┌─────────────────────────────────────────────┐
│         SERVEUR LOCAL / MINI-PC             │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │           DOCKER STACK                  │ │
│  ├─────────────────────────────────────────┤ │
│  │                                         │ │
│  │  ┌──────────┐  ┌──────────┐  ┌────────┐ │ │
│  │  │  React   │  │  FastAPI │  │  MySQL │ │ │
│  │  │   :3000  │  │   :8000  │  │  :3306 │ │ │
│  │  └──────────┘  └──────────┘  └────────┘ │ │
│  │                                         │ │
│  │  ┌──────────┐  ┌──────────┐             │ │
│  │  │  Nginx   │  │  Backup  │             │ │
│  │  │   :80    │  │  Service │             │ │
│  │  └──────────┘  └──────────┘             │ │
│  │                                         │ │
│  └─────────────────────────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │        STOCKAGE LOCAL                   │ │
│  │  • Bases de données MySQL              │ │
│  │  • Fichiers média (photos)             │ │
│  │  • Sauvegardes automatiques            │ │
│  │  • Logs système                        │ │
│  └─────────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
         │
         │ Réseau Local (LAN/WiFi)
         │
┌─────────────────────────────────────────────┐
│          POSTES CLIENTS                     │
│                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ PC/Mac  │  │ Tablet  │  │ Mobile  │     │
│  │ Bureau  │  │         │  │         │     │
│  └─────────┘  └─────────┘  └─────────┘     │
│                                             │
└─────────────────────────────────────────────┘
```

#### Spécifications Matérielles Recommandées

##### Configuration Minimale (10-20 utilisateurs)
```yaml
Processeur: Intel i5 / AMD Ryzen 5 (4 cœurs)
Mémoire: 8 GB RAM
Stockage: 256 GB SSD + 1 TB HDD (backup)
Réseau: Gigabit Ethernet
OS: Ubuntu Server 22.04 LTS
Coût: ~800-1200€
```

##### Configuration Optimale (50-100 utilisateurs)
```yaml
Processeur: Intel i7 / AMD Ryzen 7 (8 cœurs)
Mémoire: 16 GB RAM
Stockage: 512 GB SSD + 2 TB HDD (backup)
Réseau: Gigabit Ethernet + WiFi 6
OS: Ubuntu Server 22.04 LTS
Redondance: UPS 1500VA
Coût: ~1500-2500€
```

#### Déploiement avec Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - static_files:/var/www/static
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile.prod
    volumes:
      - static_files:/app/build
    restart: unless-stopped

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=mysql+pymysql://geneweb:${DB_PASSWORD}@mysql:3306/geneweb
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    volumes:
      - media_files:/app/media
      - backup_files:/app/backups
    depends_on:
      - mysql
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=geneweb
      - MYSQL_USER=geneweb
      - MYSQL_PASSWORD=${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/conf.d:/etc/mysql/conf.d
      - ./backup/mysql:/backup
    restart: unless-stopped
    command: --default-authentication-plugin=mysql_native_password

  backup:
    image: mysql:8.0
    volumes:
      - mysql_data:/var/lib/mysql
      - ./backup:/backup
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
    command: >
      sh -c "
        while true; do
          sleep 86400  # 24h
          mysqldump -h mysql -u root -p${MYSQL_ROOT_PASSWORD} --all-databases > /backup/backup_$(date +%Y%m%d_%H%M%S).sql
          find /backup -name '*.sql' -mtime +7 -delete  # Garde 7 jours
        done
      "
    restart: unless-stopped

volumes:
  mysql_data:
  static_files:
  media_files:
  backup_files:
```

#### Script d'Installation Automatique
```bash
#!/bin/bash
# install-geneweb.sh

set -e

echo "🚀 Installation GeneWeb Modern - Version Locale"

# Vérifications prérequis
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé"
    exit 1
fi

# Configuration
read -p "📧 Email administrateur: " ADMIN_EMAIL
read -s -p "🔐 Mot de passe MySQL root: " MYSQL_ROOT_PASSWORD
echo
read -s -p "🔐 Mot de passe base GeneWeb: " DB_PASSWORD
echo

# Génération clés sécurisées
SECRET_KEY=$(openssl rand -hex 32)

# Création fichier .env
cat > .env << EOF
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
DB_PASSWORD=$DB_PASSWORD
SECRET_KEY=$SECRET_KEY
ADMIN_EMAIL=$ADMIN_EMAIL
EOF

# Création répertoires
mkdir -p backup/mysql ssl logs

# Génération certificat SSL auto-signé (dev/test)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/geneweb.key \
    -out ssl/geneweb.crt \
    -subj "/CN=geneweb.local"

# Configuration Nginx
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name localhost geneweb.local;

        ssl_certificate /etc/nginx/ssl/geneweb.crt;
        ssl_certificate_key /etc/nginx/ssl/geneweb.key;

        location / {
            root /var/www/static;
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /media/ {
            alias /var/www/media/;
        }
    }
}
EOF

# Lancement des services
echo "🏗️ Construction et lancement des services..."
docker-compose -f docker-compose.prod.yml up -d --build

# Attente démarrage MySQL
echo "⏳ Attente démarrage base de données..."
sleep 30

# Import schéma initial
echo "🗄️ Import schéma base de données..."
docker-compose -f docker-compose.prod.yml exec -T mysql mysql -u root -p$MYSQL_ROOT_PASSWORD geneweb < database/init.sql

echo "✅ Installation terminée!"
echo "🌐 Accès: https://localhost"
echo "📧 Admin: $ADMIN_EMAIL"
echo "🔧 Logs: docker-compose logs -f"
```

#### Avantages Solution Localhost
✅ **Contrôle total** : Données restent sur site  
✅ **Coût maîtrisé** : Pas d'abonnement mensuel  
✅ **Performance** : Accès réseau local rapide  
✅ **Sécurité** : Pas d'exposition internet  
✅ **Conformité** : RGPD facilité (données locales)  
✅ **Personnalisation** : Configuration sur mesure  

#### Inconvénients
❌ **Maintenance** : Administration système nécessaire  
❌ **Sauvegarde** : Responsabilité client  
❌ **Évolutivité** : Limitée par matériel  
❌ **Accès distant** : VPN nécessaire  
❌ **Haute disponibilité** : Pas de redondance  

### Solution 2 : **Cloud Hybride** (ÉVOLUTION)

#### Architecture Hybride
```
┌─────────────────────────────────────────────┐
│              CLOUD (AWS/OVH)                │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │         APPLICATION TIER                │ │
│  │  ┌──────────┐  ┌──────────┐             │ │
│  │  │  React   │  │  FastAPI │             │ │
│  │  │  (CDN)   │  │ (Container)            │ │
│  │  └──────────┘  └──────────┘             │ │
│  └─────────────────────────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │          DATABASE TIER                  │ │
│  │  ┌──────────┐  ┌──────────┐             │ │
│  │  │  MySQL   │  │  Redis   │             │ │
│  │  │ (Managed)│  │ (Cache)  │             │ │
│  │  └──────────┘  └──────────┘             │ │
│  └─────────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
                    │
                 VPN/API
                    │
┌─────────────────────────────────────────────┐
│            ON-PREMISE                       │
│  ┌─────────────────────────────────────────┐ │
│  │        DONNÉES SENSIBLES                │ │
│  │  • Backup local                        │ │
│  │  • Données personnelles                │ │
│  │  • Synchronisation                     │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

#### Coûts Cloud (Estimation)
| Service | Spécification | Coût/mois |
|---------|---------------|-----------|
| **Compute** | 2 vCPU, 4GB RAM | 50-80€ |
| **Database** | MySQL managed 20GB | 30-50€ |
| **Storage** | 100GB SSD + backup | 20-30€ |
| **Network** | 1TB transfert | 10-20€ |
| **CDN** | Global delivery | 10-15€ |
| **Total** | | **120-195€/mois** |

### Solution 3 : **SaaS Managé** (OPTION PREMIUM)

#### Architecture SaaS Multi-tenant
```
┌─────────────────────────────────────────────┐
│           PLATEFORME SAAS                   │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │        TENANT ISOLATION                 │ │
│  │                                         │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │ │
│  │  │ Client  │  │ Client  │  │ Client  │  │ │
│  │  │   A     │  │   B     │  │   C     │  │ │
│  │  └─────────┘  └─────────┘  └─────────┘  │ │
│  └─────────────────────────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │        SHARED SERVICES                  │ │
│  │  • Authentication                      │ │
│  │  • Backup & Recovery                   │ │
│  │  • Monitoring                          │ │
│  │  • Updates                             │ │
│  └─────────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

#### Modèle Tarifaire SaaS
| Plan | Utilisateurs | Stockage | Fonctionnalités | Prix/mois |
|------|--------------|----------|-----------------|-----------|
| **Basic** | 5 | 1GB | Core features | 29€ |
| **Standard** | 20 | 10GB | + Advanced search | 79€ |
| **Premium** | 100 | 50GB | + API access | 199€ |
| **Enterprise** | Illimité | 500GB | + Support dédié | 499€ |

## 🎯 Recommandation par Profil Client

### Matrice de Décision

| Critère | Localhost | Cloud Hybride | SaaS |
|---------|-----------|---------------|------|
| **Contrôle données** | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Coût initial** | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| **Coût récurrent** | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| **Simplicité** | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Évolutivité** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Sécurité** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Maintenance** | ⭐ | ⭐⭐ | ⭐⭐⭐ |

### Recommandations Spécifiques

#### Association Généalogique Locale (10-50 membres)
**Recommandation** : 🏆 **Localhost**
- Budget initial : 1500€ (matériel)
- Coût récurrent : 0€ (hors électricité)
- Contrôle total des données
- Formation équipe nécessaire

#### Centre de Documentation (50-200 utilisateurs)
**Recommandation** : 🏆 **Cloud Hybride**
- Évolutivité nécessaire
- Accès multi-sites
- Sécurité renforcée
- Budget : 150€/mois

#### Généalogiste Professionnel
**Recommandation** : 🏆 **SaaS Premium**
- Pas de gestion technique
- Accès client facilité
- Support professionnel
- Budget : 199€/mois

## 🛠️ Procédures de Déploiement Détaillées

### Déploiement Localhost - Guide Pas à Pas

#### Phase 1 : Préparation (Jour J-7)
```bash
# 1. Commande matériel
# Mini-PC ou serveur selon spécifications

# 2. Installation OS
# Ubuntu Server 22.04 LTS
# Configuration réseau statique
# Mise à jour sécurité

# 3. Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 4. Configuration firewall
sudo ufw enable
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH admin
```

#### Phase 2 : Configuration (Jour J-3)
```bash
# 1. Téléchargement code source
git clone https://github.com/geneweb/geneweb-modern.git
cd geneweb-modern

# 2. Configuration environnement
cp .env.example .env
# Éditer .env avec paramètres spécifiques

# 3. Génération certificats SSL
./scripts/generate-ssl.sh

# 4. Test déploiement
docker-compose -f docker-compose.prod.yml up -d
```

#### Phase 3 : Migration Données (Jour J-1)
```bash
# 1. Export données legacy
./scripts/export-legacy-data.sh /path/to/legacy/geneweb

# 2. Import dans nouveau système
./scripts/import-data.sh backup.gedcom

# 3. Validation données
./scripts/validate-migration.sh

# 4. Tests fonctionnels
./scripts/run-tests.sh
```

#### Phase 4 : Mise en Production (Jour J)
```bash
# 1. Arrêt ancien système
sudo systemctl stop geneweb-legacy

# 2. Redirection trafic
# Configuration routeur/DNS vers nouveau serveur

# 3. Monitoring activation
./scripts/start-monitoring.sh

# 4. Formation utilisateurs
# Sessions formation planifiées
```

### Procédure de Rollback

#### En cas de Problème Critique
```bash
# 1. Arrêt nouveau système
docker-compose -f docker-compose.prod.yml down

# 2. Restauration ancien système
sudo systemctl start geneweb-legacy

# 3. Redirection trafic
# Reconfiguration routeur vers ancien serveur

# 4. Analyse problème
./scripts/analyze-failure.sh

# 5. Communication utilisateurs
# Notification incident + planning correction
```

## 📊 Monitoring et Maintenance

### Dashboard de Monitoring

#### Métriques Système
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"
    
volumes:
  grafana_data:
```

#### Alertes Automatiques
```python
# monitoring/alerts.py
import smtplib
from email.mime.text import MIMEText
import psutil
import mysql.connector

class SystemMonitor:
    def check_disk_space(self):
        """Vérifie espace disque"""
        usage = psutil.disk_usage('/')
        percent_used = usage.used / usage.total * 100
        
        if percent_used > 90:
            self.send_alert("Espace disque critique", f"Utilisation: {percent_used:.1f}%")
    
    def check_database_connection(self):
        """Vérifie connexion base"""
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='geneweb',
                password='password',
                database='geneweb'
            )
            conn.close()
        except Exception as e:
            self.send_alert("Base de données inaccessible", str(e))
    
    def send_alert(self, subject, message):
        """Envoi alerte email"""
        msg = MIMEText(message)
        msg['Subject'] = f"[GeneWeb Alert] {subject}"
        msg['From'] = "monitoring@geneweb.local"
        msg['To'] = "admin@geneweb.local"
        
        # Configuration SMTP
        server = smtplib.SMTP('localhost', 587)
        server.send_message(msg)
        server.quit()
```

### Plan de Maintenance

#### Maintenance Préventive (Mensuelle)
- [ ] Mise à jour sécurité OS
- [ ] Vérification sauvegardes
- [ ] Nettoyage logs anciens
- [ ] Test procédure restauration
- [ ] Vérification certificats SSL
- [ ] Optimisation base de données

#### Maintenance Corrective (Si besoin)
- [ ] Analyse logs erreurs
- [ ] Correction bugs critiques
- [ ] Mise à jour dépendances
- [ ] Optimisation performances

## 💰 Analyse Coût Total de Possession (TCO)

### TCO 5 ans - Solution Localhost

#### Coûts Initiaux (Année 1)
| Poste | Coût |
|-------|------|
| **Matériel serveur** | 2000€ |
| **Installation/Config** | 1500€ |
| **Formation équipe** | 1000€ |
| **Migration données** | 2000€ |
| **Total Initial** | **6500€** |

#### Coûts Récurrents (Années 2-5)
| Poste | Coût/an |
|-------|---------|
| **Maintenance** | 800€ |
| **Électricité** | 200€ |
| **Mises à jour** | 500€ |
| **Support** | 1000€ |
| **Total Récurrent** | **2500€/an** |

**TCO 5 ans Localhost** : 6500€ + (4 × 2500€) = **16 500€**

### Comparaison Solutions

| Solution | Coût Initial | Coût/an | TCO 5 ans |
|----------|--------------|---------|-----------|
| **Localhost** | 6500€ | 2500€ | **16 500€** |
| **Cloud Hybride** | 2000€ | 1800€ | **9 200€** |
| **SaaS Premium** | 0€ | 2400€ | **12 000€** |

## 📋 Conclusion et Recommandation Finale

### Pour Association Généalogique Type

**Recommandation** : 🏆 **Solution Localhost avec évolution Cloud**

#### Phase 1 (Années 1-2) : Localhost
- Démarrage avec solution locale
- Maîtrise des coûts
- Apprentissage équipe
- Validation fonctionnalités

#### Phase 2 (Années 3-5) : Migration Cloud
- Évolution vers cloud hybride
- Amélioration disponibilité
- Facilitation maintenance
- Accès multi-sites

### Justification des Choix

#### Technique
✅ **Évolutivité** : Architecture containerisée portable  
✅ **Sécurité** : Contrôle total puis migration sécurisée  
✅ **Performance** : Optimisée pour usage local puis cloud  

#### Économique
✅ **Investissement progressif** : Coûts étalés  
✅ **ROI mesurable** : Bénéfices immédiats  
✅ **Flexibilité** : Adaptation selon croissance  

#### Organisationnel
✅ **Formation progressive** : Montée en compétence équipe  
✅ **Risque maîtrisé** : Migration par étapes  
✅ **Support adapté** : Accompagnement sur mesure  

Cette stratégie de déploiement assure une migration réussie avec maîtrise des coûts et des risques, tout en préparant l'évolution future vers le cloud. 🚀
