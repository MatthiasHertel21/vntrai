# Backlog
ich möchte eine webanwendung entwickeln mit flask und docker-compose
die anwendung soll auf den port 5004 laufen
verwende tailwind layout 
ich möchte links eine sidebar mit auto-expand / auto collaps funktion (im collapsed zustand nur icons, im expanded status icons mit beschriftung)
die anwendung soll vntrai heißen
übernimm die den aufbau der sidebar, die icons und die farben aus der anwendung /home/ga/fb1/age/v036

## 🆕 Neue Anforderungen: Tools & Integrations (v036 Funktionalität)
ich möchte in der anwendung die funktionalität für tools und für integrations haben wie in der anwendung im verzeichnis v036, aber mit eigenen änderungen:
- **Tailwind Layout** (statt Bootstrap aus v036)
- **Separate JSON-Dateien für Integrations**: Die Datenhaltung für alle integrations soll nicht in einer datei "integrations.json" erfolgen sondern jede integration soll ihre eigene json datei haben. Diese soll so heißen wie die uuid der integration und in einem verzeichnis "integrations" liegen
- **Separate JSON-Dateien für Tools**: Die Datenhaltung für alle tools soll nicht in einer datei "tools.json" erfolgen sondern jedes tool soll seine eigene json datei haben. Diese soll so heißen wie die uuid des tools und in einem verzeichnis "tools" liegen

### 📋 v036 Analyse - Zu übernehmende Features:
**Integrations:**
- ✅ CRUD Operations (Create, Read, Update, Delete)
- ✅ JSON Editor für direkte Bearbeitung
- ✅ Upload von Vendor Icons
- ✅ Tool Definition Management
- ✅ Config/Input/Output Parameter Verwaltung
- ✅ Validation von Tool Definitionen
- ⚠️ **Keine Options-Verwaltung** (nicht erforderlich)

**Tools:**
- ✅ Tool-Instanzen basierend auf Integrations
- ✅ Konfiguration und Parameter-Management
- ✅ Test-Funktionalität für Tools
- ✅ Execution von Tools
- ✅ Prefilled/Locked Inputs
- ✅ Status-Tracking (Connected/Not Connected)
- ✅ Gruppierung nach Integrations

# Sprints

## Sprint 1: Grundstruktur und Setup (3-5 Tage)
### Ziel: Basis-Setup der Flask-Anwendung mit Docker basierend auf v036 Architektur

**User Stories:**
- Als Entwickler möchte ich eine Flask-Anwendung mit Docker-Compose aufsetzen, damit die Entwicklungsumgebung konsistent ist
- Als Benutzer möchte ich auf die Anwendung über Port 5004 zugreifen können
- Als Entwickler möchte ich die bewährte Ordnerstruktur von v036 übernehmen

**Tasks:**
- [x] Docker-Compose Setup erstellen (basierend auf v036/docker-compose.yml) ✅
- [x] Flask-Grundstruktur implementieren (app/__init__.py, config.py, run.py) ✅
- [x] Ordnerstruktur von v036 übernehmen (app/templates/, app/static/, app/routes/) ✅
- [x] Tailwind CSS integrieren + Bootstrap Icons ✅
- [x] Basis-HTML-Template erstellen (base.html mit vntr-layout-wrapper) ✅
- [x] Port 5004 konfigurieren ✅
- [x] VNTRAI Logo und Branding Assets übertragen ✅
- [x] README.md mit Setup-Anweisungen ✅

**Definition of Done:** ✅ ABGESCHLOSSEN
- ✅ Anwendung startet erfolgreich mit `docker-compose up` auf Port 5004
- ✅ Tailwind CSS und Bootstrap Icons funktionieren
- ✅ Grundlegendes HTML-Layout mit vntr-layout-wrapper vorhanden
- ✅ Logo wird korrekt angezeigt

## Sprint 2: Sidebar-Implementierung mit v036 Design (5-7 Tage)
### Ziel: Vollständig funktionsfähige Sidebar mit Auto-Expand/Collapse basierend auf v036

**User Stories:**
- Als Benutzer möchte ich eine Sidebar mit dem exakten Design von v036 sehen
- Als Benutzer möchte ich Hover-Effekte (weiße Icons werden schwarz bei Hover)
- Als Benutzer möchte ich im kollabierten Zustand nur Icons sehen
- Als Benutzer möchte ich im expandierten Zustand Icons mit Beschriftung sehen

**Tasks:**
- [x] Sidebar HTML-Struktur von v036 übernehmen (vntr-sidebar, vntr-nav-items) ✅
- [x] CSS von v036 adaptieren (style.css Sidebar-Regeln übernehmen) ✅
- [x] Icons von v036 übertragen (Dashboard, Insights, Tools, User, Company etc.) ✅
- [x] Farbschema implementieren (#0CC0DF als Hauptfarbe) ✅
- [x] Auto-Expand/Collapse JavaScript implementieren ✅
- [ ] Context Area Toggle Button (wie in v036) ⚠️ ENTFERNT (nicht benötigt)
- [x] Hover-Animationen (weiß → schwarz bei Icons) ✅
- [x] Responsive Design für verschiedene Bildschirmgrößen ✅
- [x] Navigation-Links und Routing vorbereiten ✅

**Definition of Done:** ✅ ABGESCHLOSSEN
- ✅ Sidebar sieht identisch zu v036 aus
- ✅ Hover-Effekte funktionieren (Icons weiß→schwarz)
- ✅ Alle Icons werden korrekt angezeigt
- ✅ Auto-expand/collapse funktioniert smooth
- ⚠️ Context Area Toggle implementiert (ENTFERNT - Context Area individuell pro Seite)

## Sprint 3: Navigation und Routing (3-4 Tage)
### Ziel: Funktionsfähige Navigation mit Flask-Routes

**User Stories:**
- Als Benutzer möchte ich durch die Navigation zu verschiedenen Seiten gelangen
- Als Benutzer möchte ich sehen, auf welcher Seite ich mich befinde (aktive Navigation)

**Tasks:**
- [x] Flask-Routes für alle Sidebar-Menüpunkte erstellen ✅
- [x] Template-Struktur erweitern (Dashboard, Insights, Tools etc.) ✅
- [x] Active-State für Navigation implementieren ✅
- [x] Error-Handling für 404/500 Seiten ✅
- [x] URL-Struktur definieren ✅
- [x] Template-Vererbung optimieren ✅
- [ ] Breadcrumb-System implementieren ⚠️ ENTFERNT (nicht benötigt)

**Definition of Done:** ✅ ABGESCHLOSSEN
- ✅ Alle Sidebar-Links führen zu funktionsfähigen Seiten
- ✅ Active-State wird korrekt angezeigt (Orange #FA7100)
- ⚠️ Breadcrumbs funktionieren (ENTFERNT - nicht benötigt)
- ✅ Error-Pages sind implementiert

## Sprint 4: Content Areas und Layout-Finalisierung (4-5 Tage)
### Ziel: Vollständiges Layout mit Context Area und Content Bereich

**User Stories:**
- Als Benutzer möchte ich eine Context Area sehen, die sich ein-/ausblenden lässt
- Als Benutzer möchte ich einen responsiven Content-Bereich haben
- Als Benutzer möchte ich Flash-Messages sehen können

**Tasks:**
- [x] Content Area Layout (vntr-content-area) ✅
- [x] Flash-Messages System ✅
- [x] Mobile Responsiveness optimieren ✅
- [x] Layout-Container (vntr-main-container, vntr-content-context-container) ✅
- [x] Smooth Animationen für alle Übergänge ✅
- [x] Context Area individuell pro Seite implementiert ✅
- [x] Konsistente Abstände zur Sidebar für alle Seiten ✅
- [ ] Context Area Expand/Collapse Button ⚠️ NICHT BENÖTIGT (individuell pro Seite)
- [ ] LocalStorage für Context Area State ⚠️ NICHT BENÖTIGT (individuell pro Seite)

**Definition of Done:** ✅ TEILWEISE ABGESCHLOSSEN
- ✅ Layout ist vollständig responsive
- ✅ Alle Animationen sind smooth
- ✅ Flash-Messages funktionieren
- ⚠️ Context Area funktioniert individuell pro Seite (Design-Änderung)


## Technische Spezifikationen basierend auf v036

### **🆕 Tools & Integrations Datenstrukturen:**

#### **Integration JSON Schema:**
```json
{
  "id": "uuid4-string",
  "name": "Integration Name",
  "description": "Description",
  "vendor": "Vendor Name",
  "api_documentation_link": "https://...",
  "vendor_icon": "filename.png",
  "config_params": [
    {
      "name": "api_key",
      "type": "text|select|json|file",
      "required": true,
      "label": "API Key",
      "description": "Your API key"
    }
  ],
  "input_params": [...],
  "output_params": [...]
}
```

#### **Tool JSON Schema:**
```json
{
  "uuid": "uuid4-string",
  "name": "Tool Instance Name",
  "description": "Tool description",
  "integration_id": "uuid4-string",
  "tool_definition": "Integration Name",
  "config": { "api_key": "..." },
  "prefilled_inputs": { "model": "gpt-4" },
  "locked_inputs": ["temperature"],
  "output_params": {...},
  "last_test": {
    "timestamp": "ISO-8601",
    "result": { "success": true, "message": "..." }
  },
  "last_execution": {...},
  "node_type": "Tool|Agent|Input|Output",
  "associated_datasets": [],
  "options": []
}
```

#### **Migration aus v036:**
```
v036 Struktur:
├── data/integrations.json      # 13 Integrations
├── data/tools.json            # 15 Tool-Instanzen
└── static/icons/vendors/      # 12 Icon-Dateien

Neue Struktur:
├── data/
│   ├── integrations/
│   │   ├── {uuid1}.json       # ChatGPT Integration
│   │   ├── {uuid2}.json       # ContextOutput Integration
│   │   └── ...                # 13 Integrations total
│   ├── tools/
│   │   ├── {uuid1}.json       # GPT (cool) Tool
│   │   ├── {uuid2}.json       # Test Tool
│   │   └── ...                # 15 Tools total
│   └── vendor_icons/
│       ├── openai.png
│       └── ...                # 12 Icons total
```

#### **Migration-Statistiken:**
- **13 Integrations** zu migrieren
- **15 Tool-Instanzen** zu migrieren  
- **12 Vendor Icons** zu kopieren
- **UUID-basierte Dateibenennung** (bereits in v036 vorhanden)

#### **Migration-Strategie:**
1. **Integrations Migration** (13 Dateien):
   - Parse v036 `integrations.json` (Array von 13 Objekten)
   - Für jede Integration: `{integration.id}.json` erstellen
   - Vendor Icons von `/vendors/` nach `/vendor_icons/` kopieren
   - Schema-Kompatibilität sicherstellen
   - **Options-Feld entfernen** (nicht mehr benötigt)

2. **Tools Migration** (15 Dateien):
   - Parse v036 `tools.json` (Array von 15 Tool-Instanzen)
   - Für jedes Tool: `{tool.uuid}.json` erstellen
   - Integration-Referenzen via `integration_id` neu verknüpfen
   - Bestehende Configurations und Test-Results übertragen

3. **Icon Migration** (12 Dateien):
   - Icons von `/app/static/icons/vendors/` nach `/data/vendor_icons/`
   - UUID-basierte Dateinamen beibehalten
   - Integration-Referenzen in JSON-Dateien aktualisieren

#### **Datei-Organisation:**
```
/data/
├── integrations/
│   ├── {uuid1}.json
│   ├── {uuid2}.json
│   └── ...
├── tools/
│   ├── {uuid1}.json
│   ├── {uuid2}.json
│   └── ...
└── vendor_icons/
    ├── icon1.png
    └── icon2.svg
```

### Farbschema:
- **Hauptfarbe:** #0CC0DF (Türkis)
- **Active State:** #FA7100 (Orange)
- **Sidebar:** Türkiser Hintergrund mit weißen Icons/Text
- **Hover:** Icons weiß → schwarz Transition
- **Background:** #ffffff für Content-Bereiche

### Icon-Set (von v036 zu übernehmen):
- Dashboard (Dashboard - blue.svg)
- Insights (Insights - black.png)
- Tools (Tools - black.png)
- Integrations (Integrations - white.svg)
- User (User - black.png)
- Company (Company - black.png)
- Workflow/Flows (Workflow - black.png)

### CSS-Klassen (von v036):
- `.vntr-layout-wrapper`
- `.vntr-sidebar`
- `.vntr-nav-items`, `.vntr-nav-item`, `.vntr-nav-link`
- `.vntr-nav-icon`
- `.vntr-main-container`
- `.vntr-context-area`
- `.vntr-content-area`

### JavaScript-Features:
- Context Area Toggle mit localStorage
- Smooth expand/collapse Animationen
- Hover-Effekte für Icons
- Responsive Sidebar-Verhalten
- **🆕 Dynamic Form Generation** für Tool/Integration Parameters
- **🆕 AJAX-basierte Tool Testing**
- **🆕 JSON Editor Integration**

## Sprint 5: Data Migration & Setup (2-3 Tage)
### Ziel: Migration der v036 Daten und Vorbereitung der neuen Datenstruktur

**User Stories:**
- Als Entwickler möchte ich alle bestehenden Daten aus v036 analysieren
- Als System möchte ich die neue Datenstruktur vorbereiten
- Als Benutzer möchte ich nahtlos mit den bestehenden Daten weiterarbeiten

**Tasks:**
- [ ] **Datenanalyse v036**: Vollständige Analyse der integrations.json und tools.json
- [ ] **Migration Strategy**: Detaillierte Migrationsstrategie entwickeln
- [ ] **Data Directories**: `/data/integrations/` und `/data/tools/` Ordner erstellen
- [ ] **UUID Mapping**: Bestehende IDs analysieren und UUID-Zuordnung planen
- [ ] **File Utilities**: Basis-Funktionen für JSON-Datei-Operations
- [ ] **Migration Scripts**: Automatische Migration-Scripts entwickeln
- [ ] **Data Validation**: Validierung der migrierten Daten
- [ ] **Rollback Strategy**: Rückfall-Mechanismus für fehlgeschlagene Migration
- [ ] **Icon Migration**: Vendor Icons aus v036 kopieren

**Definition of Done:**
- Vollständige Datenanalyse dokumentiert
- Migration-Scripts funktionieren fehlerfrei
- Neue Datenstruktur ist vorbereitet
- Testmigration erfolgreich durchgeführt
- Rollback-Mechanismus funktioniert

## Sprint 6: Integrations Management System (5-7 Tage)
### Ziel: Vollständige Integrations-Verwaltung mit individuellen JSON-Dateien

**User Stories:**
- Als Entwickler möchte ich Integrations (Tool-Definitionen) verwalten können
- Als Benutzer möchte ich neue Integrations erstellen, bearbeiten und löschen können
- Als System möchte ich jede Integration in einer eigenen JSON-Datei speichern
- Als Entwickler möchte ich alle bestehenden Integrations aus v036 migrieren

**Tasks:**
- [ ] Datenstruktur von v036 analysieren und adaptieren
- [ ] Ordnerstruktur erstellen (`/data/integrations/`)
- [ ] File Operations Utility für einzelne JSON-Dateien entwickeln
- [ ] **Migration Script**: v036 integrations.json → einzelne {uuid}.json Dateien
- [ ] **Data Validation**: Konsistenzprüfung der migrierten Daten
- [ ] **Schema-Anpassung**: Options-Feld aus v036 Integrations entfernen
- [ ] Integration Model/Schema definieren
- [ ] CRUD Routes für Integrations implementieren (`/integrations/*`)
- [ ] List-View mit Tailwind (statt Bootstrap) 
- [ ] Create/Edit Forms mit Tailwind
- [ ] JSON Editor Funktionalität
- [ ] Vendor Icon Upload System
- [ ] **Icon Migration**: Vendor Icons aus v036 übertragen
- [ ] Validation System für Integration Schemas
- [ ] Error Handling und Flash Messages

**Definition of Done:**
- **Alle 13 v036 Integrations sind migriert**
- Integrations werden in separaten JSON-Dateien gespeichert (`{uuid}.json`)
- Vollständige CRUD-Funktionalität verfügbar
- Tailwind-basiertes UI implementiert
- **Alle 12 Vendor Icons werden korrekt verwaltet und migriert**
- JSON-Editor funktioniert
- Validation verhindert fehlerhafte Integrations
- **Keine Options-Verwaltung** (Design-Entscheidung)

## Sprint 7: Tools Management System (5-7 Tage)
### Ziel: Vollständige Tools-Verwaltung basierend auf Integrations

**User Stories:**
- Als Benutzer möchte ich Tool-Instanzen basierend auf Integrations erstellen
- Als Benutzer möchte ich Tools konfigurieren, testen und ausführen können
- Als System möchte ich jedes Tool in einer eigenen JSON-Datei speichern
- Als Entwickler möchte ich alle bestehenden Tools aus v036 migrieren

**Tasks:**
- [ ] Tool-Datenstruktur von v036 adaptieren
- [ ] Ordnerstruktur erstellen (`/data/tools/`)
- [ ] File Operations für Tool JSON-Dateien
- [ ] **Migration Script**: v036 tools.json → einzelne {uuid}.json Dateien
- [ ] **Integration Mapping**: Tool-Integration Verknüpfungen neu aufbauen
- [ ] **Configuration Migration**: Bestehende Tool-Configs übertragen
- [ ] Tool Model mit Integration-Referenzen
- [ ] CRUD Routes für Tools implementieren (`/tools/*`)
- [ ] Tools List-View mit Filtering/Grouping
- [ ] Tool Creation basierend auf Integrations
- [ ] Tool Configuration Interface
- [ ] Test-Funktionalität für Tools
- [ ] Tool Execution Engine
- [ ] Status-Tracking (Connected/Not Connected)
- [ ] Parameter Management (Prefilled/Locked Inputs)
- [ ] **Legacy Test Results**: Bestehende Test-Ergebnisse übertragen

**Definition of Done:**
- **Alle 15 v036 Tools sind migriert**
- Tools werden in separaten JSON-Dateien gespeichert (`{uuid}.json`)
- **Integration-Referenzen sind korrekt verknüpft** (alle 15 Tools mit ihren Integrations)
- Tools können basierend auf Integrations erstellt werden
- Test- und Execution-Funktionalität verfügbar
- Parameter-Management funktioniert
- Status-Tracking implementiert
- Gruppierung und Filterung möglich

## Sprint 8: Advanced Features & Tool Modules (4-5 Tage)
### Ziel: Erweiterte Funktionalitäten und Tool-Ausführung

**User Stories:**
- Als Benutzer möchte ich Tools mit komplexen Parametern ausführen
- Als System möchte ich verschiedene Tool-Module unterstützen
- Als Benutzer möchte ich Tool-Outputs formatiert anzeigen lassen

**Tasks:**
- [ ] Tool Modules System von v036 portieren
- [ ] Dynamic Tool Loading/Execution
- [ ] Parameter-Validation vor Execution
- [ ] Output-Formatting und -Styling
- [ ] Tool-Testing mit Mocking
- [ ] Async Tool Execution
- [ ] Tool Dependencies Management
- [ ] Advanced Parameter Types (JSON, File Upload, etc.)
- [ ] Tool Templates und Presets
- [ ] Integration Health Checks

**Definition of Done:**
- Tool Modules können dynamisch geladen werden
- Komplexe Parameter-Types werden unterstützt
- Tool-Outputs werden formatiert angezeigt
- Async Execution funktioniert
- Health Checks für Integrations verfügbar

## Backlog für zukünftige Sprints
- **API-Endpunkte** für Tools/Integrations
- **Tool Workflows** (Verkettung von Tools)
- **Tool Monitoring** und Logging
- **Integration Marketplace**
- **Tool-Performance Analytics**
- **Backup/Export** von Tools und Integrations
- Content für Dashboard, Insights, Tools Pages
- Authentifizierung/Login-System
- Datenbankintegration
- Search Funktionalität
- User Settings/Preferences
- Dark/Light Theme Toggle
- Notifications System
- File Upload/Management

## Technische Debt / Verbesserungen
- Code-Reviews nach jedem Sprint
- Security-Audit
- Performance-Monitoring
- Accessibility-Verbesserungen (WCAG)
- Browser-Kompatibilität Testing
- Automated Testing Pipeline
- Docker Multi-stage Builds

# Documentation

## 🎯 **Projekt Status: Sprint 1-3 ABGESCHLOSSEN** ✅

### **Erfolgreiche Implementierung (Stand: 29. Juni 2025)**

#### ✅ **Sprint 1: Grundstruktur und Setup** - ABGESCHLOSSEN
- Docker-Compose läuft stabil auf Port 5004
- Flask-Anwendung mit bewährter v036 Struktur
- Tailwind CSS + Bootstrap Icons vollständig integriert
- VNTRAI Logo und Branding korrekt implementiert

#### ✅ **Sprint 2: Sidebar-Implementierung** - ABGESCHLOSSEN  
- **Auto-Expand/Collapse**: Sidebar expandiert von 80px → 250px bei Hover
- **Türkises Design**: #0CC0DF Hauptfarbe wie v036
- **Hover-Effekte**: Icons weiß → schwarz Transition
- **Active State**: Orange (#FA7100) Hervorhebung für aktuelle Seite
- **Responsive**: Funktioniert auf verschiedenen Bildschirmgrößen

#### ✅ **Sprint 3: Navigation und Routing** - ABGESCHLOSSEN
- Alle 10 Sidebar-Menüpunkte funktional
- Active-State korrekt implementiert
- Template-Vererbung sauber strukturiert
- Error-Handling für 404/500 implementiert

#### ✅ **Sprint 4: Layout-Finalisierung** - TEILWEISE ABGESCHLOSSEN
- Context Area individuell pro Seite (Design-Änderung)
- Konsistente Abstände zur Sidebar
- Flash-Messages System funktional
- Responsive Design optimiert

### **Technische Implementierung**

#### **Ordnerstruktur:**
```
/home/ga/fb1/age/
├── docker-compose.yml          # Container-Setup Port 5004
├── Dockerfile                  # Flask-App Image
├── requirements.txt            # Python Dependencies
├── run.py                      # Flask Entry Point
├── app/
│   ├── __init__.py            # App Factory
│   ├── config.py              # Konfiguration
│   ├── routes/
│   │   └── main.py            # Alle Routes
│   ├── templates/
│   │   ├── base.html          # Basis-Template
│   │   ├── index.html         # Dashboard (mit Context Area)
│   │   ├── insights.html      # Ohne Context Area
│   │   ├── tools.html         # Ohne Context Area
│   │   └── [...]              # Weitere Seiten
│   └── static/
│       ├── css/
│       │   └── style.css      # Haupt-Stylesheet
│       ├── icons/             # Icons von v036
│       └── image/             # VNTRAI Logo
└── README.md                  # Setup-Anweisungen
```

#### **CSS-Klassen System:**
- `.vntr-layout-wrapper`: Haupt-Container
- `.vntr-sidebar`: Auto-Expand Sidebar
- `.vntr-content-area.no-context`: Seiten ohne Context Area (Abstand zur Sidebar)
- `.vntr-content-area.with-context`: Seiten mit Context Area (kein Abstand)

#### **Sidebar Features:**
```css
/* Auto-Expand/Collapse */
.vntr-sidebar { width: 80px; transition: width 0.3s ease; }
.vntr-sidebar:hover { width: 250px; }

/* Text Animation */
.vntr-nav-link span { opacity: 0; transition: opacity 0.3s ease; }
.vntr-sidebar:hover .vntr-nav-link span { opacity: 1; }

/* Active State */
.vntr-nav-link.active { background-color: #FA7100; }
```

#### **Implementierte Seiten:**
1. **Dashboard** (`/`) - Mit Context Area
2. **Insights** (`/insights`) - Ohne Context Area  
3. **Flows** (`/flows`) - Ohne Context Area
4. **Tools** (`/tools`) - Ohne Context Area
5. **Integrations** (`/integrations`) - Ohne Context Area
6. **Datasets** (`/datasets`) - Ohne Context Area
7. **Flowboards** (`/flowboards`) - Ohne Context Area
8. **Agents** (`/agents`) - Ohne Context Area
9. **Prompts** (`/prompts`) - Ohne Context Area
10. **Profile** (`/profile`) - Ohne Context Area
11. **Company** (`/company`) - Ohne Context Area

#### **Design-Spezifikationen:**
- **Hauptfarbe**: #0CC0DF (Türkis)
- **Active State**: #FA7100 (Orange)
- **Sidebar**: Türkiser Hintergrund, weiße Icons/Text
- **Hover**: Icons/Text → schwarz
- **Context Area**: #E7E7E7 (Grau), fullscreen height
- **Logo**: Fixed size, kein Scaling

#### **Responsive Breakpoints:**
- **Desktop**: Sidebar 80px → 250px
- **Mobile** (<768px): Sidebar 60px → 200px

### **Setup & Deployment:**

#### **Lokale Entwicklung:**
```bash
cd /home/ga/fb1/age
sudo docker-compose up -d
# Anwendung läuft auf http://localhost:5004
```

#### **Projekt-Dependencies:**
- **Frontend**: Tailwind CSS, Bootstrap Icons
- **Backend**: Flask, Python 3.9
- **Container**: Docker, Docker-Compose

### **Erfolge:**
✅ Vollständig funktionsfähige vntrai Webanwendung  
✅ Auto-Expand/Collapse Sidebar wie gewünscht  
✅ Pixel-perfekte Übernahme des v036 Designs  
✅ Responsive und performant  
✅ Saubere Code-Struktur