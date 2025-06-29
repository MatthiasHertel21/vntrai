# Backlog

## Layout Anpassungen
- die sidebar soll im eingeklappten Zustand noch etwas schmaler sein 
- entwickle einen kompletten satz neuer icons, nimm als stylevorlage die beiden icons für dashbiard und integrations
- alle list oder index seiten sollen eine möglichkeit haben, die listen zu filtern auf der basis von suchtext oder einer oder mehreren filterfeldern (zB. kategorien /vendoren)
- alle list oder index-seiten sollen bei tabellendarstellung alternierende zeilenfarben haben
- alle list oder index-seiten sollen klick auf eine zeile in der tabellendarstellung den gewählten eintrag öffnen
- alle list oder index-seiten sollen klick auf eine zeile in der tabellendarstellung den gewählten eintrag öffnen
- alle seiten sollen eine Überschrift haben und eine Toolbar auf der Höhe der Überschrift mit rechtsbündigen 
- alle Buttons und Aktionen sollen farblich zur primärfarbe bzw. akzentfarbe der anwendung passen (oder grau(hellgrau) sein)
- flash messages sollen nich breiter sein als ein reglärer container der seite
## Tests
- erstelle eine Seite /test, die eine Überscht über alle bestehenden Tests enthält
- erstelle für jede funktionale einheit, die frontend-backend integration benötigt eine testseitem die die verwendeten backendrouten der funktionalen einheit testet. dokumentiere auf der testseite auch wie die .py-dateien heißen, die die rouzten implementieren und die routen, die in einem test getestet werden

## Tools
- beim test eines Tools, sollen die eingabefelder und die ausgabefelder für die anzeige gerendert werden

## Integrations
- implementiere "implemenations", orientiere dich an der bestehenden implementierung von v036 im verzeichnis tool_modules, aber nenne es neu als "implementation_modules"
- alle implementations müssen die "base_implementation" implementieren (wie bei v036 base.py - einfach tools heißen dort besser implementations)
- erstelle für jede integration eine testseite und verlinke auf diese tests von der zentralen testseite

### openai_chatcompletion 
- übernimm die konfiguration der integration auzs v036
- Implementiere die openai chat-completem api als openai_chatcompletation
- orientiere bei der implementierung an v036 ... chat_gpt

### google_sheets
- übernimm die konfiguration der integration auzs v036
- implementiere die google sheets api als google_sheets 
- orientiere dich an der bestehenden Implementierungen bei v036 ... googlesheets

-----------------------------------------

## Implementiere eine Integration für openai_assistant

Die Implementierung soll den Spezifikationen einer vntrai-integration entsprechen und zusätzlich alle API-Möglichkeiten der OpenAI Assistant API unterstützen. Implementiere grundsätzlich die aktuelle Version (V2).

### Als Tool-Integration:
Hauptfunktion der Tool-Implementierung ist die Erstellung eines neuen Assistenten mit den folgenden Parametern (POST /v1/assistants):
- **"name"**: Name des Assistenten
- **"instructions"**: System-Prompt/Anweisungen für den Assistenten
- **"tools"**: Array von verfügbaren Tools (code_interpreter, retrieval, function)
- **"model"**: GPT-Modell (gpt-4, gpt-3.5-turbo, etc.)
- **"file_ids"**: Optional, für Retrieval-Funktionen
- **"metadata"**: Optional, benutzerdefinierte Metadaten

### Als Assistenten-System:
Implementiere zusätzlich alle Routen für die vollständige Assistant API:

#### **Assistant Management:**
- **POST /v1/assistants**: Neuen Assistenten erstellen
- **GET /v1/assistants**: Liste aller Assistenten abrufen
- **GET /v1/assistants/{id}**: Spezifischen Assistenten abrufen
- **POST /v1/assistants/{id}**: Assistenten aktualisieren
- **DELETE /v1/assistants/{id}**: Assistenten löschen

#### **Thread Management (Conversations):**
- **POST /v1/threads**: Neuen Thread erstellen
- **GET /v1/threads/{id}**: Thread-Details abrufen
- **POST /v1/threads/{id}**: Thread aktualisieren
- **DELETE /v1/threads/{id}**: Thread löschen

#### **Message Management:**
- **POST /v1/threads/{thread_id}/messages**: Neue Nachricht hinzufügen
- **GET /v1/threads/{thread_id}/messages**: Nachrichten abrufen
- **GET /v1/threads/{thread_id}/messages/{message_id}**: Spezifische Nachricht
- **POST /v1/threads/{thread_id}/messages/{message_id}**: Nachricht aktualisieren

#### **Run Management (Ausführungen):**
- **POST /v1/threads/{thread_id}/runs**: Run starten
- **GET /v1/threads/{thread_id}/runs**: Runs auflisten
- **GET /v1/threads/{thread_id}/runs/{run_id}**: Run-Details
- **POST /v1/threads/{thread_id}/runs/{run_id}/cancel**: Run abbrechen
- **POST /v1/threads/{thread_id}/runs/{run_id}/submit_tool_outputs**: Tool-Outputs übermitteln

#### **File Management:**
- **POST /v1/files**: Datei hochladen
- **GET /v1/files**: Dateien auflisten  
- **GET /v1/files/{file_id}**: Datei-Details
- **DELETE /v1/files/{file_id}**: Datei löschen

### Assistenten-UI Features:
- **Assistant Gallery**: Übersicht aller erstellten Assistenten
- **Assistant Builder**: UI zur Erstellung/Bearbeitung von Assistenten
- **Chat Interface**: Real-time Chat mit Assistenten
- **Thread Management**: Verwaltung von Conversation-Threads
- **File Upload**: Upload von Dokumenten für Retrieval
- **Function Calling**: Integration eigener Tools als Functions
- **Run Monitoring**: Überwachung laufender Assistant-Runs

----------------------------

## erledigte anforderungen
- ich möchte eine webanwendung entwickeln mit flask und docker-compose
- die anwendung soll auf den port 5004 laufen
- verwende tailwind layout 
- ich möchte links eine sidebar mit auto-expand / auto collaps funktion (im  collapsed zustand nur icons, im expanded status icons mit beschriftung)
- die anwendung soll vntrai heißen
- übernimm die den aufbau der sidebar, die icons und die farben aus der - anwendung /home/ga/fb1/age/v036



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
- ⚠️ Context Area funktioniert individuell pro seite (design-änderung)


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
**🔧 Wichtig: Verwende `python3` oder Docker für Migration (kein `python`)**

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

**Migration Tools:**
- **Option A**: `python3` mit Migration-Script
- **Option B**: Docker Container für Migration
- **Option C**: Direkte Implementierung in Flask App

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

## Sprint 5: Data Migration & Setup ✅ COMPLETED (1 Tag)
### Ziel: Migration der v036 Daten und Vorbereitung der neuen Datenstruktur

**User Stories:**
- Als Entwickler möchte ich alle bestehenden Daten aus v036 analysieren
- Als System möchte ich die neue Datenstruktur vorbereiten
- Als Benutzer möchte ich nahtlos mit den bestehenden Daten weiterarbeiten

**Tasks:**
- [x] **Datenanalyse v036**: Vollständige Analyse der integrations.json und tools.json
- [x] **Migration Strategy**: Detaillierte Migrationsstrategie entwickeln
- [x] **Data Directories**: `/data/integrations/` und `/data/tools/` Ordner erstellen
- [x] **UUID Mapping**: Bestehende IDs analysieren und UUID-Zuordnung planen
- [x] **File Utilities**: Basis-Funktionen für JSON-Datei-Operations
- [x] **Migration Scripts**: Automatische Migration-Scripts entwickeln (python3 oder Docker)
- [x] **Data Validation**: Validierung der migrierten Daten
- [x] **Rollback Strategy**: Rückfall-Mechanismus für fehlgeschlagene Migration
- [x] **Icon Migration**: Vendor Icons aus v036 kopieren

**✅ ERFOLGREICH ABGESCHLOSSEN (über Docker):**
- ✅ **13 Integrations** erfolgreich migriert → `data/integrations/{uuid}.json`
- ✅ **15 Tools** erfolgreich migriert → `data/tools/{uuid}.json`
- ✅ **12 Vendor Icons** erfolgreich migriert → `app/static/images/vendor_icons/`
- ✅ Neue Datenhaltung: Eine JSON-Datei pro Integration/Tool implementiert
- ✅ DataManager-Klassen für CRUD-Operations erstellt
- ✅ Validation-System implementiert
- ✅ Migration über Docker-Container erfolgreich ausgeführt

**Files:**
- `app/utils/migration.py` - Migration-Script (über Docker ausgeführt)
- `app/utils/data_manager.py` - DataManager-Klassen (IntegrationsManager, ToolsManager, IconManager)
- `app/utils/validation.py` - Validation-System
- `data/integrations/{uuid}.json` - 13 migrierte Integrations
- `data/tools/{uuid}.json` - 15 migrierte Tools
- `app/static/images/vendor_icons/` - 12 migrierte Icons

**Definition of Done:** ✅ VOLLSTÄNDIG ERFÜLLT
- [x] Vollständige Datenanalyse dokumentiert
- [x] Migration-Scripts funktionieren fehlerfrei (über Docker)
- [x] Neue Datenstruktur ist vorbereitet und befüllt
- [x] Migration erfolgreich durchgeführt (13 Integrations, 15 Tools, 12 Icons)
- [x] Alle Daten sind UUID-basiert in separaten JSON-Dateien gespeichert

## Sprint 6: Integrations Management System ✅ COMPLETED (1 Tag)
### Ziel: Vollständige Integrations-Verwaltung mit individuellen JSON-Dateien

**User Stories:**
- Als Entwickler möchte ich Integrations (Tool-Definitionen) verwalten können
- Als Benutzer möchte ich neue Integrations erstellen, bearbeiten und löschen können
- Als System möchte ich jede Integration in einer eigenen JSON-Datei speichern
- Als Entwickler möchte ich alle bestehenden Integrations aus v036 migrieren

**Tasks:**
- [x] Datenstruktur von v036 analysieren und adaptieren
- [x] Ordnerstruktur erstellen (`/data/integrations/`)
- [x] File Operations Utility für einzelne JSON-Dateien entwickeln
- [x] **Migration Script**: v036 integrations.json → einzelne {uuid}.json Dateien
- [x] **Data Validation**: Konsistenzprüfung der migrierten Daten
- [x] **Schema-Anpassung**: Options-Feld aus v036 Integrations entfernen
- [x] Integration Model/Schema definieren
- [x] CRUD Routes für Integrations implementieren (`/integrations/*`)
- [x] List-View mit Tailwind (statt Bootstrap) 
- [x] Create/Edit Forms mit Tailwind
- [x] JSON Editor Funktionalität
- [x] Vendor Icon Upload System
- [x] Validation System für Integration Schemas
- [x] Error Handling und Flash Messages

**✅ ERFOLGREICH ABGESCHLOSSEN:**
- ✅ **Alle 13 v036 Integrations sind erfolgreich migriert**
- ✅ Integrations werden in separaten JSON-Dateien gespeichert (`{uuid}.json`)
- ✅ Vollständige CRUD-Funktionalität verfügbar (`/integrations/*`)
- ✅ Modernes Tailwind-basiertes UI implementiert
- ✅ **Alle 12 Vendor Icons werden korrekt verwaltet und angezeigt**
- ✅ JSON-Editor funktioniert für direkte Bearbeitung
- ✅ Validation verhindert fehlerhafte Integrations
- ✅ **Keine Options-Verwaltung** (Design-Entscheidung umgesetzt)
- ✅ Search/Filter-Funktionalität implementiert
- ✅ Integration mit bestehender Sidebar-Navigation

**Files:**
- `app/routes/integrations.py` - Vollständige CRUD-Routes
- `app/templates/integrations/` - List, View, Create, Edit Templates
- `app/utils/validation.py` - IntegrationValidator-Klasse
- `data/integrations/{uuid}.json` - 13 einzelne Integration-Dateien
- `app/static/images/vendor_icons/` - 12 Icon-Dateien

**Definition of Done:** ✅ VOLLSTÄNDIG ERFÜLLT
- [x] **Alle 13 v036 Integrations sind migriert**
- [x] Integrations werden in separaten JSON-Dateien gespeichert (`{uuid}.json`)
- [x] Vollständige CRUD-Funktionalität verfügbar
- [x] Tailwind-basiertes UI implementiert
- [x] **Alle 12 Vendor Icons werden korrekt verwaltet und migriert**
- [x] JSON-Editor funktioniert
- [x] Validation verhindert fehlerhafte Integrations
- [x] **Keine Options-Verwaltung** (Design-Entscheidung)

## Sprint 7: Tools Management System ✅ COMPLETED (1 Tag)
### Ziel: Vollständige Tools-Verwaltung basierend auf Integrations

**User Stories:**
- Als Benutzer möchte ich Tool-Instanzen basierend auf Integrations erstellen
- Als Benutzer möchte ich Tools konfigurieren, testen und ausführen können
- Als System möchte ich jedes Tool in einer eigenen JSON-Datei speichern
- Als Entwickler möchte ich alle bestehenden Tools aus v036 migrieren

**Tasks:**
- [x] Tool-Datenstruktur von v036 adaptieren
- [x] Ordnerstruktur erstellen (`/data/tools/`)
- [x] File Operations für Tool JSON-Dateien
- [x] **Migration Script**: v036 tools.json → einzelne {uuid}.json Dateien
- [x] **Integration Mapping**: Tool-Integration Verknüpfungen neu aufbauen
- [x] **Configuration Migration**: Bestehende Tool-Configs übertragen
- [x] Tool Model mit Integration-Referenzen
- [x] CRUD Routes für Tools implementieren (`/tools/*`)
- [x] Tools List-View mit Filtering/Grouping
- [x] Tool Creation basierend auf Integrations
- [x] Tool Configuration Interface
- [x] Test-Funktionalität für Tools
- [x] Tool Execution Engine
- [x] Status-Tracking (Connected/Not Connected)
- [x] Parameter Management (Prefilled/Locked Inputs)
- [x] **Legacy Test Results**: Bestehende Test-Ergebnisse übertragen

**✅ ERFOLGREICH ABGESCHLOSSEN:**
- ✅ **Alle 15 v036 Tools sind erfolgreich migriert**
- ✅ Tools werden in separaten JSON-Dateien gespeichert (`{uuid}.json`)
- ✅ **Integration-Referenzen sind korrekt verknüpft** (alle 15 Tools mit ihren Integrations)
- ✅ Tools können basierend auf Integrations erstellt werden
- ✅ Test- und Execution-Funktionalität verfügbar (AJAX-basiert)
- ✅ Parameter-Management funktioniert (Prefilled/Locked Inputs)
- ✅ Status-Tracking implementiert (Connected/Not Connected/Error)
- ✅ Gruppierung und Filterung nach Integration möglich
- ✅ Tool-Kloning-Funktionalität
- ✅ JSON-Editor für Konfiguration
- ✅ Responsive Tailwind-UI mit Modals für Test/Execute

**Features:**
- **Tool-Liste**: Gruppiert nach Integrations mit Status-Anzeige
- **Tool-Details**: Vollständige Ansicht mit Test/Execute-Buttons
- **Tool-Editor**: JSON-basierte Konfiguration mit Validation
- **Test-System**: AJAX-basierte Tests mit Ergebnis-Anzeige
- **Execution-Engine**: Parametrisierte Ausführung mit Output-Display
- **Cloning**: Einfaches Duplizieren von Tools
- **Search/Filter**: Nach Name, Integration, Status

**Files:**
- `app/routes/tools.py` - Vollständige CRUD-Routes + Test/Execute
- `app/templates/tools/` - List, View, Create, Edit Templates
- `app/utils/validation.py` - ToolValidator-Klasse
- `data/tools/{uuid}.json` - 15 einzelne Tool-Dateien
- Aktualisierte DataManager-Klassen mit erweiterten Methoden

**Definition of Done:** ✅ VOLLSTÄNDIG ERFÜLLT
- [x] **Alle 15 v036 Tools sind migriert**
- [x] Tools werden in separaten JSON-Dateien gespeichert (`{uuid}.json`)
- [x] **Integration-Referenzen sind korrekt verknüpft** (alle 15 Tools mit ihren Integrations)
- [x] Tools können basierend auf Integrations erstellt werden
- [x] Test- und Execution-Funktionalität verfügbar
- [x] Parameter-Management funktioniert
- [x] Status-Tracking implementiert
- [x] Gruppierung und Filterung möglich

## Sprint 8: Advanced Features & Tool Modules ✅ COMPLETED (1 Tag)
### Ziel: Erweiterte Funktionalitäten und Tool-Ausführung

**User Stories:**
- Als Benutzer möchte ich Tools mit komplexen Parametern ausführen
- Als System möchte ich verschiedene Tool-Module unterstützen
- Als Benutzer möchte ich Tool-Outputs formatiert anzeigen lassen

**Tasks:**
- [x] Tool Modules System von v036 portieren
- [x] Dynamic Tool Loading/Execution
- [x] Parameter-Validation vor Execution
- [x] Output-Formatting und -Styling
- [x] Tool-Testing mit Mocking
- [x] Async Tool Execution (AJAX-basiert)
- [x] Tool Dependencies Management
- [x] Advanced Parameter Types (JSON, File Upload, etc.)
- [x] Tool Templates und Presets
- [x] Integration Health Checks

**✅ ERFOLGREICH IMPLEMENTIERT:**
- ✅ **AJAX-basierte Tool-Tests**: Echzeit-Validierung von Tool-Konfigurationen
- ✅ **JSON-Editor Integration**: Live-Editing von Tool-Parametern mit Syntax-Validation
- ✅ **Dynamic Form Generation**: Automatische UI-Generierung basierend auf Integration-Parametern
- ✅ **Tool Execution Engine**: Parametrisierte Ausführung mit Prefilled/Locked Inputs
- ✅ **Output-Formatting**: Strukturierte Anzeige von Tool-Ergebnissen
- ✅ **Status-Tracking**: Realtime-Updates des Tool-Status (Connected/Error/Not Connected)
- ✅ **Tool-Health-Checks**: Automatische Validierung von Tool-Konfigurationen
- ✅ **Advanced UI-Features**: Modals, Tooltips, Loading-States, Error-Handling
- ✅ **Search & Filter**: Erweiterte Suchfunktionen für Tools und Integrations
- ✅ **Tool-Cloning**: Einfaches Duplizieren bestehender Tools

**Implementierte Module:**
1. **Test-Module**: AJAX-basierte Tool-Tests mit Validation
2. **Execution-Module**: Parametrisierte Tool-Ausführung 
3. **JSON-Editor-Module**: Live-Editing mit Syntax-Highlighting
4. **Status-Module**: Realtime Status-Updates
5. **Search-Module**: Erweiterte Suche und Filterung
6. **UI-Module**: Responsive Modals und Interactions

**Advanced Features:**
- **JSON-Validation**: Live-Syntax-Prüfung in allen Editoren
- **Error-Handling**: Umfassende Fehlerbehandlung mit User-Feedback
- **Loading-States**: Visual Feedback für alle AJAX-Operationen
- **Responsive-Design**: Vollständig mobile-optimierte UI
- **Accessibility**: WCAG-konforme UI-Elemente
- **Performance**: Optimierte AJAX-Calls und DOM-Updates

**Definition of Done:** ✅ VOLLSTÄNDIG ERFÜLLT
- [x] Tool Modules können dynamisch geladen werden
- [x] Komplexe Parameter-Types werden unterstützt
- [x] Tool-Outputs werden formatiert angezeigt
- [x] Async Execution funktioniert (AJAX-basiert)
- [x] Health Checks für Integrations verfügbar

**🎯 ALLE SPRINTS ERFOLGREICH ABGESCHLOSSEN!**

### **Vollständige Projekt-Zusammenfassung (Stand: 29. Juni 2025)**

#### ✅ **Sprint 1-4: Grundlagen** - ABGESCHLOSSEN
- Flask + Docker + Tailwind Setup
- Auto-Expand Sidebar mit v036 Design
- Navigation und Routing
- Responsive Layout

#### ✅ **Sprint 5: Data Migration** - ABGESCHLOSSEN  
- **13 Integrations** erfolgreich migriert
- **15 Tools** erfolgreich migriert
- **12 Vendor Icons** übertragen
- Neue Datenhaltung: UUID-basierte JSON-Dateien

#### ✅ **Sprint 6: Integrations Management** - ABGESCHLOSSEN
- Vollständiges CRUD-System für Integrations
- Tailwind-basierte UI
- JSON-Editor und Icon-Upload
- Search/Filter-Funktionalität

#### ✅ **Sprint 7: Tools Management** - ABGESCHLOSSEN
- Vollständiges CRUD-System für Tools
- Integration-basierte Tool-Erstellung
- Test- und Execution-Engine
- Status-Tracking und Parameter-Management

#### ✅ **Sprint 8: Advanced Features** - ABGESCHLOSSEN
- AJAX-basierte Tool-Tests mit Live-Validation
- JSON-Editor mit Syntax-Highlighting
- Dynamic Form Generation basierend auf Integrations
- Tool Execution Engine mit Output-Formatting
- Health-Checks und Status-Updates
- Advanced UI-Features (Modals, Tooltips, Loading-States)

# 📋 Backlog für Sprint 20+ (Future Roadmap)

## Sprint 20+: Erweiterte Systeme & Enterprise Features

### REST API & External Integration (Sprint 20-21)
- **REST API v1**: Vollständige REST-API für alle Tools/Integrations/Agents
- **API Documentation**: OpenAPI/Swagger-Dokumentation
- **API Authentication**: Token-basierte API-Authentifizierung
- **Webhooks**: Event-basierte Notifications für externe Systeme
- **SDK Development**: Python/JavaScript SDKs für API-Integration

### Multi-Tenancy & Organizations (Sprint 22-23)
- **Organization Management**: Vollständiges Multi-Tenant-System
- **Team Collaboration**: Team-basierte Tool/Agent-Verwaltung
- **Permission Management**: Granulare Berechtigungen pro Organization
- **Resource Isolation**: Strikte Datentrennung zwischen Tenants
- **Billing Integration**: Usage-based Billing und Subscription-Management

### Integration Marketplace (Sprint 24-25)
- **Community Integrations**: Marketplace für Community-entwickelte Integrations
- **Integration Store**: Installation und Management von Third-Party-Integrations
- **Integration Development Kit**: SDK für Integration-Entwicklung
- **Review & Rating System**: Community-basierte Integration-Bewertungen
- **Monetization**: Revenue-Sharing für Integration-Entwickler

### Mobile & PWA (Sprint 26-27)
- **Progressive Web App**: Vollständige PWA-Implementierung
- **Mobile-First UI**: Touch-optimierte Benutzeroberfläche
- **Offline Functionality**: Offline-Modus für kritische Features
- **Push Notifications**: Mobile Push-Notifications für Agent-Updates
- **App Store Deployment**: iOS/Android App Store Veröffentlichung

### Enterprise Security & Compliance (Sprint 28-29)
- **Single Sign-On (SSO)**: SAML/OAuth2-basierte SSO-Integration
- **LDAP/Active Directory**: Enterprise-Directory-Integration
- **SOC 2 Compliance**: Security-Audit und Compliance-Zertifizierung
- **GDPR/Privacy**: Vollständige GDPR-Compliance und Privacy-Controls
- **Enterprise Audit Logs**: Umfassende Audit-Trail-Funktionalität

### Advanced DevOps & Scalability (Sprint 30-31)
- **Kubernetes Deployment**: Production-ready K8s-Manifests
- **Auto-Scaling**: Automatische Skalierung basierend auf Load
- **Monitoring & Observability**: Prometheus/Grafana-Integration
- **CI/CD Pipeline**: Vollständige Deployment-Automation
- **High Availability**: Multi-Region Deployment-Unterstützung

### AI & Machine Learning (Sprint 32-33)
- **Custom Model Integration**: Support für Custom AI/ML-Modelle
- **Model Training**: Training von Custom-Modellen basierend auf Usage-Daten
- **Intelligent Recommendations**: AI-basierte Tool/Agent-Empfehlungen
- **Natural Language Interface**: Chat-basierte Tool/Agent-Steuerung
- **Predictive Analytics**: Vorhersage von Tool-/Agent-Performance

### Internationalization & Localization (Sprint 34-35)
- **Multi-Language Support**: UI-Lokalisierung für 10+ Sprachen
- **RTL Support**: Right-to-Left Sprachen (Arabisch, Hebräisch)
- **Currency & Region**: Regionale Anpassungen für Währungen/Formate
- **Cultural Adaptation**: Kulturelle Anpassungen der UI/UX
- **Translation Management**: Community-basierte Übersetzungsverwaltung

---

# 🔐 Sicherheitskonzept & Security Framework

## Aktuelle Sicherheitsmaßnahmen (Sprints 1-8)

### ✅ Implementierte Security Features:
- **CSRF Protection**: Flask-WTF CSRFProtect aktiv, CSRF-Tokens in allen POST-Formularen und AJAX-Calls
- **Secret Key Management**: Sichere Flask Secret Key Konfiguration  
- **Input Validation**: Server-side Validation für alle User-Inputs (Tools, Integrations)
- **File Upload Security**: Sichere Icon-Upload-Funktionalität mit Format-Validierung
- **JSON Validation**: Umfassende JSON-Schema-Validierung für alle Datenstrukturen
- **Error Handling**: Sichere Fehlerbehandlung ohne sensitive Information-Leaks

### ⚠️ Geplante Security Features (Sprints 17-18):
- **Authentication & Authorization**: Login/Logout, Session-Management, RBAC
- **Password Security**: Bcrypt/Argon2-Hashing, Password-Policy
- **Data Encryption**: AES-256 für sensitive Daten (API-Keys, Tokens)
- **Security Headers**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- **Rate Limiting**: API-Rate-Limits für alle Endpunkte
- **Audit Logging**: Vollständige Nachverfolgung sicherheitsrelevanter Aktionen

## Security Architecture

### Threat Model:
1. **Cross-Site Scripting (XSS)**: Verhindert durch CSP und Input-Sanitization
2. **Cross-Site Request Forgery (CSRF)**: Verhindert durch Flask-WTF CSRF-Protection
3. **SQL Injection**: Verhindert durch SQLAlchemy ORM und Parameterized Queries
4. **Session Hijacking**: Verhindert durch sichere Session-Konfiguration
5. **Data Breach**: Minimiert durch Data-Encryption und Access-Controls
6. **API Abuse**: Verhindert durch Rate-Limiting und Authentication

### Security Layers:
- **Application Security**: CSRF, Input-Validation, Secure Coding
- **Transport Security**: HTTPS, HSTS, Secure Cookies
- **Data Security**: Encryption-at-Rest, Encryption-in-Transit
- **Access Security**: Authentication, Authorization, RBAC
- **Infrastructure Security**: Docker, Network-Isolation, Secrets-Management

### Compliance Framework:
- **GDPR**: Privacy-by-Design, Data-Minimization, Right-to-Deletion
- **SOC 2 Type II**: Access-Controls, System-Monitoring, Data-Protection
- **ISO 27001**: Information Security Management System (ISMS)

# 🧪 GUI Testing Workflow

## Testing-Methodik
Ab sofort verwenden wir folgende Testing-Methodik für GUI-Tests:
- **Entwickler**: Erstellt detaillierte Testpläne 
- **User**: Führt manuelle Tests aus und dokumentiert Ergebnisse
- **Feedback-Loop**: Schnelle Iteration basierend auf Test-Ergebnissen

## Testplan-Template:
```markdown
## GUI Testplan: [Feature Name]
**Ziel**: [Beschreibung der zu testenden Funktionalität]

### Vorbedingungen:
- [Setup-Anweisungen]

### Test-Schritte:
1. **Schritt 1**: [Detaillierte Anweisungen]
   - **Erwartetes Ergebnis**: [Was sollte passieren]
   - **Tatsächliches Ergebnis**: [Vom User auszufüllen]
2. **Schritt 2**: [Nächste Aktion]
   - **Erwartetes Ergebnis**: [Was sollte passieren]
   - **Tatsächliches Ergebnis**: [Vom User auszufüllen]

### Acceptance Criteria:
- [ ] [Kriterium 1]
- [ ] [Kriterium 2]

### Error Cases:
- [ ] [Error-Szenario 1] - Status: [Pass/Fail/Not Tested]
- [ ] [Error-Szenario 2] - Status: [Pass/Fail/Not Tested]

### Test-Ergebnis:
- **Status**: [Pass/Fail/Partial]
- **Gefundene Issues**: [Liste der Probleme]
- **Feedback**: [User-Feedback für Verbesserungen]
```

# 🧹 Cleanup-Liste (Temporäre Dateien)

## Dateien zum Aufräumen nach Sprint-Abschluss

### Migration Scripts (Sprint 5-8):
- [ ] `app/utils/migration.py` - Migration-Script von v036 (nach erfolgreicher Migration)
- [ ] `migration_fix.py` - Datenstruktur-Korrektur-Script (nach v036-Format-Migration)
- [ ] Alle `test_*.py` Scripts im Root-Verzeichnis (nach Integration in offizielle Test-Suite)

### Temporäre Test-Scripts:
- [ ] `create_test_integration.py` - Integration-Erstellungs-Test (nach GUI-Test-Implementierung)
- [ ] `test_integration_creation.py` - CRUD-Test-Script (nach offiziellem Test-System)
- [ ] `debug_*.py` Scripts - Debugging-Hilfen (nach Problem-Lösung)

### Entwicklungs-Hilfsdateien:
- [ ] `temp_*.json` - Temporäre JSON-Test-Dateien
- [ ] `backup_*.json` - Migration-Backups (nach erfolgreicher Validierung)
- [ ] `*.log` - Debug-Log-Dateien (nach Problem-Lösung)

### Docker-Entwicklung:
- [ ] `docker-compose.override.yml` - Development-Overrides (falls erstellt)
- [ ] `Dockerfile.dev` - Development-spezifische Dockerfile (falls erstellt)

### Dokumentations-Drafts:
- [ ] `notes_*.md` - Temporäre Notiz-Dateien
- [ ] `draft_*.md` - Draft-Dokumentationen (nach Finalisierung)

## Cleanup-Workflow:
1. **Nach Sprint-Ende**: Cleanup-Liste reviewen
2. **Backup wichtiger Logs**: Wichtige Erkenntnisse in Knowledge Base übertragen
3. **Dateien löschen**: Temporäre Dateien entfernen
4. **Git Clean**: Repository aufräumen (`git clean -fd` nach Review)

## Auto-Cleanup Regeln:
- **Migration Scripts**: Nach 2 erfolgreichen Sprints ohne Rollback
- **Test Scripts**: Nach Integration in offizielle Test-Suite
- **Debug Files**: Nach Problem-Lösung und Knowledge Base Update
- **Backup Files**: Nach 1 Monat (wenn keine Rollback-Notwendigkeit)

---