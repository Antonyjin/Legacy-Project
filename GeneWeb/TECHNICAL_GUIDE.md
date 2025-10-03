# Guide Technique - GeneWeb Modern

## 🎯 Vue d'Ensemble

**Objectif** : Moderniser GeneWeb (OCaml) vers stack Python/React
**Contrainte** : 1-2 mois, projet
**Approche** : MVP fonctionnel avec Golden Master Testing

## 🏗️ Architecture

### Stack Retenue
| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| **Frontend** | React + TypeScript + Material-UI | Interface moderne, composants |
| **Backend** | Python + FastAPI + SQLAlchemy | Rapidité développement, APIs |
| **Database** | MySQL 8.0 | Robustesse, compatibilité |
| **Visualisation** | D3.js | Arbres généalogiques interactifs |
| **Tests UI** | Playwright | Plus moderne que Selenium |
| **Containers** | Docker Compose | Setup simplifié |

### Architecture 3-Tiers Localhost

#### Vue d'Ensemble
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│     React App       │    │   FastAPI Server    │    │   MySQL Database    │
│   localhost:3000    │◄──►│   localhost:8000    │◄──►│   localhost:3306    │
│                     │    │                     │    │                     │
│ • Interface moderne │    │ • API REST          │    │ • Données structurées│
│ • D3.js arbres      │    │ • Auth JWT          │    │ • Relations familiales│
│ • Material-UI       │    │ • GEDCOM parser     │    │ • Index optimisés   │
│ • State management  │    │ • Business logic    │    │ • Backup auto       │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

#### Flux de Données Détaillé
```
GEDCOM Upload → FastAPI Parser → MySQL Storage → API Query → React Display → D3.js Tree

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 📁 GEDCOM   │───►│ 🔧 Parser   │───►│ 💾 MySQL    │───►│ 🌳 React    │
│ File Upload │    │ Validation  │    │ Normalized  │    │ Tree View   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

#### Architecture de Déploiement (Docker Compose)
```yaml
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Network                           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  frontend   │  │   backend   │  │    mysql    │             │
│  │   :3000     │  │    :8000    │  │    :3306    │             │
│  │             │  │             │  │             │             │
│  │ React Build │◄─┤ FastAPI     │◄─┤ MySQL 8.0   │             │
│  │ Nginx       │  │ + Uvicorn   │  │ + Volume    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  Host: localhost                                                │
└─────────────────────────────────────────────────────────────────┘
```

#### Comparaison Architecture : Legacy vs Modern

```
LEGACY (GeneWeb OCaml)              MODERN (Python/React)
┌─────────────────────┐            ┌─────────────────────┐
│   Browser Client    │            │   React SPA         │
│   (HTML statique)   │            │   (Interface moderne)│
└─────────┬───────────┘            └─────────┬───────────┘
          │ HTTP                             │ HTTP + WebSocket
          ▼                                  ▼
┌─────────────────────┐            ┌─────────────────────┐
│  gwd (OCaml daemon) │            │  FastAPI Server     │
│  Port 2317          │            │  Port 8000          │
│                     │            │                     │
│ • Serveur intégré   │            │ • API REST moderne  │
│ • Templates HTML    │            │ • Auth JWT          │
│ • Logique métier    │            │ • Validation Pydantic│
│ • Pas de séparation │            │ • Swagger docs      │
└─────────┬───────────┘            └─────────┬───────────┘
          │ File I/O                         │ SQL
          ▼                                  ▼
┌─────────────────────┐            ┌─────────────────────┐
│   Fichiers .gwb     │            │   MySQL Database    │
│   (Format binaire)  │            │   (SQL Standard)    │
│                     │            │                     │
│ • Format propriétaire│           │ • Relations normalisées│
│ • Pas de requêtes   │            │ • Index optimisés   │
│ • Backup complexe   │            │ • Transactions ACID │
│ • Concurrence limitée│           │ • Backup standard   │
└─────────────────────┘            └─────────────────────┘

PROBLÈMES LEGACY:                   SOLUTIONS MODERNES:
❌ Interface vieillotte             ✅ UI moderne responsive
❌ Pas d'API                        ✅ API REST documentée
❌ Format propriétaire              ✅ Base SQL standard
❌ Monolithe difficile à maintenir  ✅ Architecture modulaire
❌ Sécurité basique                 ✅ JWT + HTTPS + validation
❌ Tests difficiles                 ✅ Tests automatisés
```

## 🗄️ Schéma Base de Données Minimal

```sql
-- Utilisateurs
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Arbres généalogiques
CREATE TABLE family_trees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- Personnes
CREATE TABLE persons (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tree_id INT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    gender ENUM('M', 'F', 'U') DEFAULT 'U',
    birth_date DATE,
    birth_place VARCHAR(255),
    death_date DATE,
    death_place VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tree_id) REFERENCES family_trees(id),
    INDEX idx_names (first_name, last_name)
);

-- Familles
CREATE TABLE families (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tree_id INT NOT NULL,
    husband_id INT,
    wife_id INT,
    marriage_date DATE,
    marriage_place VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tree_id) REFERENCES family_trees(id),
    FOREIGN KEY (husband_id) REFERENCES persons(id),
    FOREIGN KEY (wife_id) REFERENCES persons(id)
);

-- Relations parent-enfant
CREATE TABLE relationships (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parent_id INT NOT NULL,
    child_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES persons(id),
    FOREIGN KEY (child_id) REFERENCES persons(id),
    UNIQUE KEY unique_relationship (parent_id, child_id)
);
```

## 🚀 Setup Rapide

### 1. Structure Projet
```
geneweb-modern/
├── frontend/          # React app
├── backend/           # FastAPI app  
├── database/          # SQL scripts
├── docker-compose.yml
└── README.md
```

### 2. Docker Compose
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [mysql]
    environment:
      - DATABASE_URL=mysql+pymysql://geneweb:password@mysql:3306/geneweb
    
  mysql:
    image: mysql:8.0
    ports: ["3306:3306"]
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=geneweb
      - MYSQL_USER=geneweb
      - MYSQL_PASSWORD=password
    volumes:
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
```

### 3. Commandes de Base
```bash
# Lancement
docker-compose up -d

# Tests
docker-compose exec backend pytest
docker-compose exec frontend npm test

# Logs
docker-compose logs -f
```

## 🔧 Implémentation Backend

### FastAPI App Minimale
```python
# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GeneWeb Modern API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/persons")
def get_persons(db: Session = Depends(get_db)):
    return crud.get_persons(db)

@app.post("/api/persons")
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    return crud.create_person(db, person)
```

### Modèles SQLAlchemy
```python
# backend/app/models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Person(Base):
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    tree_id = Column(Integer, ForeignKey("family_trees.id"))
    first_name = Column(String(100))
    last_name = Column(String(100))
    birth_date = Column(Date)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
```

## ⚛️ Implémentation Frontend

### App React Principale
```tsx
// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Header from './components/Header';
import PersonList from './components/PersonList';
import FamilyTree from './components/FamilyTree';

const theme = createTheme({
  palette: {
    primary: { main: '#2f6400' },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Header />
        <Routes>
          <Route path="/" element={<PersonList />} />
          <Route path="/tree" element={<FamilyTree />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
```

### Composant Liste Personnes
```tsx
// frontend/src/components/PersonList.tsx
import React, { useState, useEffect } from 'react';
import { List, ListItem, ListItemText, Button } from '@mui/material';
import { Person } from '../types';
import { getPersons } from '../services/api';

const PersonList: React.FC = () => {
  const [persons, setPersons] = useState<Person[]>([]);

  useEffect(() => {
    const fetchPersons = async () => {
      const data = await getPersons();
      setPersons(data);
    };
    fetchPersons();
  }, []);

  return (
    <div>
      <h2>Personnes</h2>
      <List>
        {persons.map((person) => (
          <ListItem key={person.id}>
            <ListItemText
              primary={`${person.first_name} ${person.last_name}`}
              secondary={person.birth_date}
            />
          </ListItem>
        ))}
      </List>
    </div>
  );
};

export default PersonList;
```

## 🧪 Tests Essentiels

### Golden Master Testing (Recommandé pour Legacy)

Le Golden Master Testing capture le comportement du système legacy comme référence pour valider que le nouveau système produit les mêmes résultats.

#### Setup Golden Master
```python
# backend/tests/test_golden_master.py
import pytest
import json
import os
from pathlib import Path
from app.services.gedcom_service import GedcomService
from app.services.tree_service import TreeService

class TestGoldenMaster:
    """Tests Golden Master pour validation comportement legacy"""
    
    @pytest.fixture
    def golden_master_dir(self):
        """Répertoire contenant les fichiers de référence"""
        return Path(__file__).parent / "golden_masters"
    
    def test_gedcom_import_golden_master(self, db, golden_master_dir):
        """Test import GEDCOM vs référence legacy"""
        
        # Given - Fichier GEDCOM de test
        gedcom_file = golden_master_dir / "sample_family.ged"
        expected_output_file = golden_master_dir / "expected_import_result.json"
        
        # When - Import avec nouveau système
        service = GedcomService()
        result = service.import_gedcom(db, str(gedcom_file))
        
        # Normalisation pour comparaison
        normalized_result = self.normalize_import_result(result)
        
        # Then - Comparaison avec golden master
        if expected_output_file.exists():
            # Mode validation - compare avec référence
            with open(expected_output_file, 'r', encoding='utf-8') as f:
                expected = json.load(f)
            
            assert normalized_result == expected, f"Différence détectée avec golden master"
        else:
            # Mode création - génère la référence
            with open(expected_output_file, 'w', encoding='utf-8') as f:
                json.dump(normalized_result, f, indent=2, ensure_ascii=False)
            
            pytest.skip(f"Golden master créé: {expected_output_file}")
    
    def test_tree_calculation_golden_master(self, db, golden_master_dir):
        """Test calculs généalogiques vs référence legacy"""
        
        # Setup données test
        self.setup_test_family_tree(db)
        
        # Test calculs ancêtres
        service = TreeService()
        ancestors = service.get_ancestors(db, person_id=1, max_generations=5)
        
        # Normalisation
        normalized_ancestors = self.normalize_tree_data(ancestors)
        
        # Golden master comparison
        self.assert_golden_master(
            normalized_ancestors,
            golden_master_dir / "expected_ancestors.json"
        )
    
    def test_sosa_numbering_golden_master(self, db, golden_master_dir):
        """Test numérotation Sosa vs legacy"""
        
        # Setup
        self.setup_test_family_tree(db)
        
        # Calcul Sosa
        service = TreeService()
        sosa_numbers = service.calculate_sosa_numbers(db, tree_id=1, root_person_id=1)
        
        # Normalisation (tri par ID pour reproductibilité)
        normalized_sosa = dict(sorted(sosa_numbers.items()))
        
        # Validation
        self.assert_golden_master(
            normalized_sosa,
            golden_master_dir / "expected_sosa_numbers.json"
        )
    
    def normalize_import_result(self, result):
        """Normalise résultat import pour comparaison stable"""
        return {
            'persons_count': len(result.get('persons', [])),
            'families_count': len(result.get('families', [])),
            'persons': sorted([
                {
                    'first_name': p.get('first_name', ''),
                    'last_name': p.get('last_name', ''),
                    'birth_date': str(p.get('birth_date', '')),
                    'gender': p.get('gender', 'U')
                }
                for p in result.get('persons', [])
            ], key=lambda x: (x['last_name'], x['first_name']))
        }
    
    def normalize_tree_data(self, tree_data):
        """Normalise données arbre pour comparaison"""
        return {
            'total_persons': len(tree_data),
            'generations': sorted(list(set(p.get('generation', 0) for p in tree_data))),
            'persons_by_generation': {
                gen: len([p for p in tree_data if p.get('generation') == gen])
                for gen in range(1, 6)
            }
        }
    
    def assert_golden_master(self, actual, golden_file_path):
        """Helper pour assertion golden master"""
        if golden_file_path.exists():
            with open(golden_file_path, 'r', encoding='utf-8') as f:
                expected = json.load(f)
            assert actual == expected
        else:
            with open(golden_file_path, 'w', encoding='utf-8') as f:
                json.dump(actual, f, indent=2, ensure_ascii=False)
            pytest.skip(f"Golden master créé: {golden_file_path}")
```

#### Génération des Golden Masters depuis Legacy
```python
# tools/generate_golden_masters.py
"""
Script pour générer les golden masters depuis le système legacy
À exécuter une fois pour capturer le comportement de référence
"""

import subprocess
import json
import os
from pathlib import Path

class LegacyGoldenMasterGenerator:
    def __init__(self, legacy_geneweb_path: str):
        self.legacy_path = Path(legacy_geneweb_path)
        self.output_dir = Path("tests/golden_masters")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_all_golden_masters(self):
        """Génère tous les golden masters depuis le legacy"""
        
        # 1. Import GEDCOM
        self.generate_import_golden_master()
        
        # 2. Calculs généalogiques  
        self.generate_tree_calculations_golden_master()
        
        # 3. Export GEDCOM
        self.generate_export_golden_master()
        
        print("✅ Tous les golden masters générés!")
    
    def generate_import_golden_master(self):
        """Génère golden master pour import GEDCOM"""
        
        # Commande legacy pour import
        cmd = [
            str(self.legacy_path / "ged2gwb"),
            "-o", "/tmp/test_base",
            "tests/fixtures/sample_family.ged"
        ]
        
        subprocess.run(cmd, check=True)
        
        # Extraction données importées (via gwu ou analyse directe .gwb)
        extracted_data = self.extract_legacy_data("/tmp/test_base.gwb")
        
        # Sauvegarde golden master
        with open(self.output_dir / "expected_import_result.json", 'w') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    def generate_tree_calculations_golden_master(self):
        """Génère golden master pour calculs arbres"""
        
        # Utilisation API legacy ou extraction directe
        # (dépend de l'interface disponible dans GeneWeb legacy)
        
        legacy_calculations = {
            "ancestors": self.get_legacy_ancestors(person_id="I1", generations=5),
            "sosa_numbers": self.get_legacy_sosa_numbers(root_id="I1"),
            "relationships": self.get_legacy_relationships("I1", "I2")
        }
        
        with open(self.output_dir / "expected_tree_calculations.json", 'w') as f:
            json.dump(legacy_calculations, f, indent=2, ensure_ascii=False)
    
    def extract_legacy_data(self, gwb_file_path: str):
        """Extrait données du fichier .gwb legacy"""
        # Implémentation selon format .gwb
        # Peut utiliser gwu pour export puis parsing
        
        cmd = [str(self.legacy_path / "gwu"), gwb_file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return self.parse_gwu_output(result.stdout)

# Usage
if __name__ == "__main__":
    generator = LegacyGoldenMasterGenerator("/path/to/legacy/geneweb")
    generator.generate_all_golden_masters()
```

#### Configuration pytest pour Golden Master
```python
# backend/tests/conftest.py
import pytest
import os

@pytest.fixture(autouse=True)
def golden_master_mode():
    """Configure le mode golden master via variable d'environnement"""
    return os.getenv("GOLDEN_MASTER_MODE", "validate")  # "create" ou "validate"

# pytest.ini
[tool:pytest]
addopts = 
    --cov=app
    --cov-report=html:reports/coverage
    -v
markers =
    golden_master: marks tests as golden master tests
    slow: marks tests as slow

# Commandes utiles
# Création golden masters: GOLDEN_MASTER_MODE=create pytest -m golden_master
# Validation: pytest -m golden_master
```

### Tests Unitaires Classiques
```python
# backend/tests/test_models.py
import pytest
from app.models import Person

def test_person_full_name():
    person = Person(first_name="Jean", last_name="Dupont")
    assert person.get_full_name() == "Jean Dupont"

def test_create_person(db):
    person_data = {"first_name": "Marie", "last_name": "Martin"}
    person = Person(**person_data)
    db.add(person)
    db.commit()
    
    assert person.id is not None
    assert person.first_name == "Marie"
```

### Tests Frontend avec Golden Master
```typescript
// frontend/src/components/FamilyTree.test.tsx
import { render } from '@testing-library/react';
import FamilyTree from './FamilyTree';
import { toMatchSnapshot } from 'jest-snapshot';

// Golden Master pour rendu React
test('family tree renders correctly', () => {
  const mockData = {
    id: 1,
    name: "Jean Dupont",
    children: [
      { id: 2, name: "Marie Dupont" },
      { id: 3, name: "Paul Dupont" }
    ]
  };
  
  const { container } = render(<FamilyTree data={mockData} />);
  
  // Golden Master via snapshot
  expect(container.firstChild).toMatchSnapshot();
});

// Golden Master pour données D3.js
test('d3 tree calculation matches expected output', () => {
  const treeCalculator = new TreeCalculator();
  const result = treeCalculator.calculateLayout(mockFamilyData);
  
  // Normalisation pour comparaison stable
  const normalized = {
    nodes: result.nodes.map(n => ({
      id: n.id,
      x: Math.round(n.x),
      y: Math.round(n.y)
    })).sort((a, b) => a.id - b.id),
    links: result.links.sort((a, b) => a.source.id - b.source.id)
  };
  
  expect(normalized).toMatchSnapshot();
});
```

### Tests E2E avec Playwright (Recommandé 2024 - Plus moderne que Selenium)
```python
# tests/test_e2e_playwright.py
import pytest
from playwright.sync_api import sync_playwright, expect
import json
import time

class TestGeneWebE2E:
    """Tests End-to-End avec Playwright - Plus moderne et rapide que Selenium"""
    
    @pytest.fixture
    def browser_context(self):
        """Setup Playwright avec multi-navigateurs"""
        with sync_playwright() as p:
            # Test sur Chrome ET Firefox
            for browser_name in ['chromium', 'firefox']:
                browser = getattr(p, browser_name).launch(
                    headless=True,  # Mode sans interface pour CI
                    slow_mo=50 if browser_name == 'chromium' else 0  # Debug si besoin
                )
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    record_video_dir='test-results/videos/',  # Enregistrement auto
                    record_har_path='test-results/network.har'  # Capture réseau
                )
                
                yield context, browser_name
                
                context.close()
                browser.close()
    
    def test_complete_genealogy_workflow(self, browser_context):
        """Test workflow complet : Import → Visualisation → Navigation"""
        context, browser_name = browser_context
        page = context.new_page()
        
        # 1. Accès application avec retry automatique
        page.goto("http://localhost:3000", wait_until="networkidle")
        
        # Vérification chargement (plus robuste que Selenium)
        expect(page).to_have_title(re.compile("GeneWeb Modern"))
        
        # 2. Upload fichier GEDCOM (plus stable)
        page.set_input_files("#gedcom-upload", "fixtures/test_family.ged")
        
        # Attendre import avec retry automatique (plus fiable que Selenium)
        page.wait_for_selector(".import-success", timeout=30000)
        
        # Screenshot automatique pour debugging
        page.screenshot(path=f"test-results/import-success-{browser_name}.png")
        
        # 3. Navigation vers arbre
        page.click("text=Arbre généalogique")
        page.wait_for_load_state("networkidle")
        
        # 4. Vérification visualisation D3.js (plus robuste)
        tree_svg = page.locator("svg")
        expect(tree_svg).to_be_visible()
        
        # Attendre que D3.js termine le rendu
        page.wait_for_function("() => document.querySelectorAll('.person-node').length > 0")
        
        # Vérifier noeuds personnes
        person_nodes = page.locator(".person-node")
        expect(person_nodes).to_have_count_greater_than(0)
        
        # 5. Test interactivité : clic sur personne
        person_nodes.first.click()
        
        # Vérifier popup détails (plus stable)
        details_popup = page.locator(".person-details")
        expect(details_popup).to_be_visible()
        expect(details_popup).to_contain_text("Nom:")
        
        # Screenshot final
        page.screenshot(path=f"test-results/tree-view-{browser_name}.png")
    
    def test_responsive_design(self, driver):
        """Test interface responsive mobile/desktop"""
        
        # Test desktop
        driver.set_window_size(1920, 1080)
        driver.get("http://localhost:3000")
        
        header = driver.find_element(By.TAG_NAME, "header")
        assert header.is_displayed()
        
        # Test mobile
        driver.set_window_size(375, 667)  # iPhone dimensions
        time.sleep(1)  # Attendre resize
        
        # Vérifier menu burger apparaît
        mobile_menu = driver.find_element(By.CLASS_NAME, "mobile-menu-button")
        assert mobile_menu.is_displayed()
        
        # Test navigation mobile
        mobile_menu.click()
        nav_menu = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "mobile-nav"))
        )
        assert nav_menu.is_displayed()
    
    def test_search_functionality(self, driver):
        """Test recherche temps réel"""
        
        driver.get("http://localhost:3000")
        
        # Saisie dans champ recherche
        search_input = driver.find_element(By.ID, "person-search")
        search_input.send_keys("Martin")
        
        # Attendre résultats
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
        )
        
        results = driver.find_elements(By.CLASS_NAME, "search-result-item")
        assert len(results) > 0
        
        # Vérifier contenu résultats
        first_result = results[0]
        assert "Martin" in first_result.text
        
        # Test clic résultat
        first_result.click()
        
        # Vérifier navigation vers profil
        WebDriverWait(driver, 5).until(
            EC.url_contains("/person/")
        )
        
        assert "/person/" in driver.current_url
    
    def test_performance_loading(self, driver):
        """Test performance chargement pages"""
        
        start_time = time.time()
        driver.get("http://localhost:3000")
        
        # Attendre chargement complet
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "app-loaded"))
        )
        
        load_time = time.time() - start_time
        
        # Assertion performance : < 3 secondes
        assert load_time < 3.0, f"Page trop lente: {load_time:.2f}s"
    
    def test_legacy_comparison_visual(self, driver):
        """Test comparaison visuelle avec legacy (Golden Master UI)"""
        
        # Screenshot nouveau système
        driver.get("http://localhost:3000/tree")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "svg"))
        )
        
        driver.save_screenshot("screenshots/modern_tree.png")
        
        # Note: Comparaison avec screenshot legacy sauvegardé
        # Utilisation possible de tools comme pixelmatch pour diff images
        
        # Pour ce test, on vérifie juste que les éléments principaux existent
        assert driver.find_element(By.CLASS_NAME, "tree-container")
        assert len(driver.find_elements(By.CLASS_NAME, "person-node")) > 0

# Configuration pytest pour Selenium
# pytest.ini
[tool:pytest]
markers =
    e2e: marks tests as end-to-end tests (Selenium)
    slow: marks tests as slow running

# Commandes utiles
# Tests E2E: pytest -m e2e
# Tests E2E avec interface: pytest -m e2e --headed
```

### Setup Selenium dans Docker
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [mysql]
    
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=geneweb_test
    
  selenium-tests:
    build: 
      context: .
      dockerfile: Dockerfile.selenium
    depends_on: [frontend, backend]
    volumes:
      - ./tests:/tests
      - ./screenshots:/screenshots
    command: pytest -m e2e --html=reports/selenium_report.html

# Dockerfile.selenium
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=`curl -sS chromedriver.chromium.org/LATEST_RELEASE` \
    && wget -O /tmp/chromedriver.zip http://chromedriver.chromium.org/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

COPY requirements-test.txt .
RUN pip install -r requirements-test.txt

WORKDIR /tests
```

## 🔒 Sécurité Basique

### Authentification JWT
```python
# backend/app/auth.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
```

## 📊 Import GEDCOM Basique

### Parser GEDCOM Simple
```python
# backend/app/gedcom_parser.py
import re
from typing import Dict, List

class GedcomParser:
    def __init__(self, file_content: str):
        self.lines = file_content.split('\n')
        self.persons = {}
        self.families = {}
    
    def parse(self) -> Dict:
        current_record = None
        
        for line in self.lines:
            if not line.strip():
                continue
                
            level, tag, value = self.parse_line(line)
            
            if level == 0 and tag in ['INDI', 'FAM']:
                current_record = {'id': value, 'type': tag, 'data': {}}
                
            elif level == 1 and current_record:
                if tag == 'NAME':
                    names = value.split('/')
                    current_record['data']['first_name'] = names[0].strip()
                    if len(names) > 1:
                        current_record['data']['last_name'] = names[1].strip()
                elif tag == 'BIRT':
                    current_record['data']['birth'] = {}
                elif tag == 'SEX':
                    current_record['data']['gender'] = value
                    
        return {'persons': self.persons, 'families': self.families}
    
    def parse_line(self, line: str):
        match = re.match(r'^(\d+)\s+(@\w+@\s+)?(\w+)(\s+(.*))?', line)
        if match:
            level = int(match.group(1))
            tag = match.group(3)
            value = match.group(5) or ''
            return level, tag, value
        return 0, '', ''
```

## 🎨 Visualisation Arbre D3.js

### Composant Arbre Basique
```tsx
// frontend/src/components/FamilyTree.tsx
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface TreeNode {
  id: number;
  name: string;
  children?: TreeNode[];
}

interface Props {
  data: TreeNode;
}

const FamilyTree: React.FC<Props> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = 800;
    const height = 600;

    const root = d3.hierarchy(data);
    const treeLayout = d3.tree<TreeNode>().size([width - 100, height - 100]);
    
    treeLayout(root);

    const g = svg.append("g").attr("transform", "translate(50,50)");

    // Liens
    g.selectAll(".link")
      .data(root.links())
      .enter()
      .append("path")
      .attr("class", "link")
      .attr("d", d3.linkHorizontal()
        .x((d: any) => d.y)
        .y((d: any) => d.x)
      )
      .attr("fill", "none")
      .attr("stroke", "#ccc");

    // Noeuds
    const nodes = g.selectAll(".node")
      .data(root.descendants())
      .enter()
      .append("g")
      .attr("class", "node")
      .attr("transform", d => `translate(${d.y},${d.x})`);

    nodes.append("circle")
      .attr("r", 20)
      .attr("fill", "#69b3a2");

    nodes.append("text")
      .attr("dy", 3)
      .attr("text-anchor", "middle")
      .text(d => d.data.name);

  }, [data]);

  return <svg ref={svgRef} width={800} height={600} />;
};

export default FamilyTree;
```

## 📋 Checklist Implémentation

### Phase 1 (Semaine 1-2)
- [ ] Setup Docker Compose
- [ ] Backend FastAPI avec CRUD basique
- [ ] Frontend React avec Material-UI
- [ ] Base de données MySQL connectée
- [ ] Tests unitaires basiques

### Phase 2 (Semaine 3-4)  
- [ ] Import GEDCOM fonctionnel
- [ ] Visualisation arbre D3.js
- [ ] Interface responsive
- [ ] Recherche basique
- [ ] Export GEDCOM

### Phase 3 (Semaine 5-6)
- [ ] Authentification JWT
- [ ] Tests automatisés >70%
- [ ] CI/CD GitHub Actions
- [ ] Sécurité basique (validation, CORS)
- [ ] Documentation API

### Phase 4 (Semaine 7-8)
- [ ] Polish interface utilisateur
- [ ] Optimisation performance
- [ ] Vidéo démonstration
- [ ] Documentation finale
- [ ] Préparation soutenance

Ce guide technique vous donne les éléments essentiels pour implémenter le prototype dans les temps ! 🚀
