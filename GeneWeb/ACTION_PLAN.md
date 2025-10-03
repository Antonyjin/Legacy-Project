# Plan d'Action - Projet Legacy GeneWeb (1-2 mois)

## 🎯 Objectif Réajusté

**Mission** : Démontrer vos compétences avec un prototype fonctionnel + documentation professionnelle  
**Deadline** : 6-8 semaines  
**Priorité** : 60% implémentation, 40% documentation  

## 📅 Planning Sprint par Sprint

### 🚀 **Sprint 1 (Semaine 1-2) : Foundation + MVP**

#### Jour 1-3 : Setup Infrastructure
```bash
# Checklist Jour 1-3
□ Créer repository GitHub
□ Setup Docker Compose (MySQL + volumes)
□ Configuration CI/CD GitHub Actions basique
□ Setup environnement développement local
□ Test déploiement "Hello World"

# Commandes essentielles
mkdir geneweb-modern && cd geneweb-modern
git init && git remote add origin <your-repo>

# Structure projet
mkdir frontend backend database docs
touch docker-compose.yml README.md
```

#### Jour 4-7 : Backend MVP
```python
# Objectifs Backend Sprint 1
□ FastAPI app basique avec Swagger
□ Modèles SQLAlchemy (Person, Family, Tree)
□ Endpoints CRUD basiques
□ Authentification JWT simple
□ Tests unitaires modèles

# Structure backend/
backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── crud.py           # CRUD operations
│   ├── auth.py           # JWT auth
│   └── database.py       # DB connection
├── tests/
│   └── test_models.py    # Tests unitaires
├── requirements.txt
└── Dockerfile
```

#### Jour 8-14 : Frontend MVP
```typescript
// Objectifs Frontend Sprint 1
□ App React avec TypeScript
□ Routing basique (React Router)
□ Composants de base (PersonList, PersonForm)
□ Intégration API backend
□ UI moderne avec Material-UI

// Structure frontend/src/
src/
├── components/
│   ├── PersonList.tsx
│   ├── PersonForm.tsx
│   └── Layout.tsx
├── services/
│   └── api.ts            // Axios calls
├── types/
│   └── index.ts          // TypeScript types
├── App.tsx
└── index.tsx
```

**Livrable Sprint 1** : Prototype avec CRUD personnes fonctionnel

### 🌟 **Sprint 2 (Semaine 3-4) : Features Démonstrables**

#### Semaine 3 : Import GEDCOM + Visualisation
```python
# Backend - Import GEDCOM
□ Parser GEDCOM basique (ou lib existante)
□ Endpoint upload fichier
□ Conversion GEDCOM → MySQL
□ Validation données importées

# Frontend - Upload Interface
□ Composant upload fichier
□ Progress bar import
□ Affichage résultats import
□ Gestion erreurs
```

```typescript
// Frontend - Visualisation Arbre
□ Intégration D3.js basique
□ Affichage arbre généalogique simple
□ Navigation dans l'arbre
□ Responsive design mobile
```

#### Semaine 4 : Recherche + Polish
```yaml
Fonctionnalités:
□ Recherche temps réel (nom, prénom)
□ Filtres basiques (dates, lieux)
□ Export GEDCOM
□ Interface utilisateur polie

Tests:
□ Tests E2E critiques (Cypress/Playwright)
□ Tests intégration API
□ Couverture >70%
```

**Livrable Sprint 2** : Démo complète Import → Visualisation → Export

### 🔒 **Sprint 3 (Semaine 5-6) : Qualité + Sécurité**

#### Semaine 5 : Sécurité + Performance
```yaml
Sécurité:
□ Authentification JWT complète
□ Validation entrées (Pydantic)
□ Protection CORS
□ HTTPS en production
□ Audit sécurité basique

Performance:
□ Optimisation requêtes DB
□ Cache basique (Redis optionnel)
□ Optimisation bundle frontend
□ Métriques performance
```

#### Semaine 6 : Tests + CI/CD
```yaml
Tests Automatisés:
□ Tests unitaires backend >80%
□ Tests intégration API
□ Tests E2E workflows critiques
□ Tests performance basiques

CI/CD:
□ Pipeline GitHub Actions
□ Tests automatiques sur PR
□ Déploiement automatique staging
□ Quality gates (coverage, linting)
```

**Livrable Sprint 3** : Application sécurisée avec tests automatisés

### 🎬 **Sprint 4 (Semaine 7-8) : Démonstration + Finalisation**

#### Semaine 7 : Documentation + Démo
```yaml
Documentation:
□ README complet avec setup
□ Documentation API (Swagger)
□ Guide utilisateur basique
□ Architecture technique documentée

Démonstration:
□ Vidéo démo 3-5 minutes
□ Présentation PowerPoint
□ Comparaison avant/après
□ Métriques et bénéfices
```

#### Semaine 8 : Finalisation + Soutenance
```yaml
Finition:
□ Corrections bugs critiques
□ Polish interface utilisateur
□ Optimisations finales
□ Préparation soutenance

Livrables Finaux:
□ Code source complet
□ Documentation technique
□ Vidéo démonstration
□ Présentation soutenance
□ Dossier évaluation
```

## 🛠️ Stack Technique Définitive

### Backend (Python)
```txt
# requirements.txt - VERSION FINALE
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pytest==7.4.3
pytest-cov==4.1.0
```

### Frontend (React)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^4.9.5",
    "@mui/material": "^5.14.18",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "d3": "^7.8.5",
    "axios": "^1.6.0",
    "react-router-dom": "^6.18.0",
    "react-hook-form": "^7.47.0"
  }
}
```

### Infrastructure
```yaml
# docker-compose.yml - VERSION PRODUCTION
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [mysql]
    environment:
      - DATABASE_URL=mysql+pymysql://geneweb:password@mysql:3306/geneweb
      - SECRET_KEY=your-secret-key-here
    
  mysql:
    image: mysql:8.0
    ports: ["3306:3306"]
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=geneweb
      - MYSQL_USER=geneweb
      - MYSQL_PASSWORD=password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  mysql_data:
```

## 🎯 Features Prioritaires par Importance

### P0 - CRITIQUE (Obligatoires)
```yaml
□ CRUD Personnes/Familles
□ Import GEDCOM basique
□ Visualisation arbre simple
□ Interface moderne responsive
□ Authentification basique
□ Base de données MySQL
□ Tests automatisés basiques
□ Déploiement Docker
```

### P1 - IMPORTANT (Démonstrables)
```yaml
□ Recherche temps réel
□ Export GEDCOM
□ Calculs parenté basiques
□ Interface mobile optimisée
□ CI/CD pipeline
□ Monitoring basique
□ Documentation technique
□ Vidéo démonstration
```

### P2 - OPTIONNEL (Si temps)
```yaml
□ Multi-utilisateurs
□ Statistiques avancées
□ Thèmes/Personnalisation
□ API documentation avancée
□ Tests performance
□ Monitoring avancé
```

## 📊 Métriques de Succès

### Technique
- ✅ **Application fonctionnelle** : Import → Affichage → Export
- ✅ **Performance** : <2s chargement, <500ms API
- ✅ **Tests** : >70% couverture backend, tests E2E critiques
- ✅ **Sécurité** : JWT, validation, HTTPS
- ✅ **CI/CD** : Pipeline automatisé fonctionnel

### Fonctionnel
- ✅ **Import GEDCOM** : Compatible avec fichiers standards
- ✅ **Visualisation** : Arbre interactif moderne
- ✅ **Recherche** : Temps réel, intuitive
- ✅ **Mobile** : Interface responsive utilisable
- ✅ **Export** : GEDCOM compatible

### Documentation
- ✅ **README** : Setup en 5 minutes
- ✅ **Architecture** : Diagrammes clairs
- ✅ **API** : Documentation Swagger
- ✅ **Démo** : Vidéo 3-5 minutes
- ✅ **Présentation** : Support soutenance

## 🚨 Points d'Attention Critiques

### ⚠️ **Gestion du Temps**
- **60% développement** / 40% documentation
- Prototype fonctionnel AVANT perfectionnement
- Tests automatisés dès le début
- Documentation au fur et à mesure

### ⚠️ **Scope Creep**
- Se limiter aux features P0 et P1
- Pas de sur-ingénierie
- Interface fonctionnelle > parfaite
- Démo qui marche > features complètes

### ⚠️ **Risques Techniques**
- Tester Docker setup dès le début
- Valider import GEDCOM sur vrais fichiers
- Tests E2E sur workflows critiques
- Backup code régulier (Git)

## 📋 Checklist Hebdomadaire

### Fin Semaine 2 ✅
- [ ] CRUD personnes fonctionnel
- [ ] Interface React basique
- [ ] Docker Compose setup
- [ ] Tests unitaires modèles

### Fin Semaine 4 ✅
- [ ] Import GEDCOM fonctionne
- [ ] Visualisation arbre D3.js
- [ ] Recherche temps réel
- [ ] Interface responsive

### Fin Semaine 6 ✅
- [ ] Authentification JWT
- [ ] Tests automatisés >70%
- [ ] CI/CD pipeline
- [ ] Sécurité basique

### Fin Semaine 8 ✅
- [ ] Application complète déployée
- [ ] Documentation technique
- [ ] Vidéo démonstration
- [ ] Présentation prête

## 🎯 Conseil Final

**Pour réussir ce projet de rattrapage** :

1. **Commencez par coder** - Prototype fonctionnel d'abord
2. **Documentez au fur et à mesure** - Pas tout à la fin
3. **Testez continuellement** - Évitez les régressions
4. **Préparez la démo tôt** - Dernière semaine = polish seulement
5. **Restez pragmatique** - Fonctionnel > parfait

**Vous avez déjà 70% du travail d'analyse fait** - maintenant il faut **IMPLÉMENTER** pour prouver vos compétences ! 🚀

**Good luck!** 💪
