# Backlog

## Layout Anpassungen
- ✅ die sidebar soll im eingeklappten Zustand noch etwas schmaler sein 
- entwickle einen kompletten satz neuer icons, nimm als stylevorlage die beiden icons für dashbiard und integrations
- ✅ alle list oder index seiten sollen eine möglichkeit haben, die listen zu filtern auf der basis von suchtext oder einer oder mehreren filterfeldern (zB. kategorien /vendoren)
- ✅ alle list oder index-seiten sollen bei tabellendarstellung alternierende zeilenfarben haben
- ✅ alle list oder index-seiten sollen klick auf eine zeile in der tabellendarstellung den gewählten eintrag öffnen
- ✅ alle seiten sollen eine Überschrift haben und eine Toolbar auf der Höhe der Überschrift mit rechtsbündigen 
- ✅ alle Buttons und Aktionen sollen farblich zur primärfarbe bzw. akzentfarbe der anwendung passen (oder grau(hellgrau) sein)
- ✅ flash messages sollen nich breiter sein als ein reglärer container der seite

## Neue Layout-Anforderungen (Sprint 14+)
- [ ] **Toolbar-Buttons**: Alle am Ende der Seite verfügbaren Buttons in die Toolbar am Kopf des Dokumentes neben der Überschrift rechtsbündig verschieben
- [ ] **Aktive Navigation**: Wenn die Seiten /Tools oder /Integrations ausgewählt sind, soll auch das entsprechende Icon in der Sidebar als aktiv markiert werden
- [ ] **Card-Layout**: Änderung der Seiten /integrations und /Tools von einem Listen-Layout in ein Card-Layout
- [ ] **Container-Alignment**: In der Seite Tools/create sind die Container oben nicht bündig - beheben
- [ ] **Dashboard-Spacing**: Abstand zwischen Sidebar und Contextbereich in der Seite Dashboard entfernen

## Tests
- ✅ erstelle eine Seite /test, die eine Übersicht über alle bestehenden Tests enthält
- ✅ erstelle für jede funktionale einheit, die frontend-backend integration benötigt eine testseitem die die verwendeten backendrouten der funktionalen einheit testet. dokumentiere auf der testseite auch wie die .py-dateien heißen, die die rouzten implementieren und die routen, die in einem test getestet werden
- 🔄 **ERWEITERT**: Testsystem für dynamische Features anpassen (Execute-Dialog mit dynamischen Feldern, Implementation-Module-System)

## Tools - Dynamische Form-UI ✅ COMPLETED
- ✅ **Execute-Dialog**: Dynamische Generierung der Eingabefelder im Modal/Interface analog zu Edit/Create
- ✅ **Dynamic Field Types**: text, select, boolean, json, file mit Vorbelegung und Sperre
- ✅ **Status-Badges**: Anzeige von Locked/Prefilled-Status in Execute-Dialog
- ✅ **JSON-Fallback**: JSON-Editor als Erweiterte Option im Execute-Dialog
- ✅ **Live-Validation**: JSON-Validation für JSON-Felder im Execute-Dialog
- ✅ **Bidirektionale Synchronisation**: Zwischen UI-Feldern und JSON-Editor

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
- [ ] Context Area Expand/Collapse Button ⚠️ NICHT BENÖTIGT (individuell pro seite)
- [ ] LocalStorage für Context Area State ⚠️ NICHT BENÖTIGT (individuell pro seite)

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
- [x] **Icon Migration**: Vendor Icons aus v036 übertragen
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

## Sprint 9: Bug Fixes & Production Ready ✅ COMPLETED (29. Juni 2025)
### Ziel: Kritische Bugfixes und Produktionsvorbereitung

**User Stories:**
- Als Benutzer möchte ich, dass die Tools-Seite korrekt funktioniert
- Als Entwickler möchte ich sauberen, produktionstauglichen Code
- Als System möchte ich korrekte Daten-Verknüpfungen zwischen Tools und Integrations

**Tasks:**
- [x] **Template-Struktur repariert**: Tools-Template hatte fehlenden `{% block content %}` Block
- [x] **DataManager-Pfad korrigiert**: Flask-App-Konfiguration für korrekte Pfad-Auflösung im Docker-Container
- [x] **Tool-Integration-Verknüpfung repariert**: `tool_definition` Felder aus Migration-Metadaten wiederhergestellt
- [x] **Debug-Code Cleanup**: Alle temporären Debug-Ausgaben entfernt
- [x] **JavaScript-Error behoben**: `toggleJsonEditor` CamelCase-Konvertierung für korrekte Element-IDs

**Kritische Fixes:**
1. **Tools-Seite leer**: Template-Struktur repariert - Content wurde nicht gerendert
2. **DataManager-Pfad**: Docker-Container verwendet jetzt Flask-Config für Daten-Pfade
3. **Tool-Verknüpfungen**: Alle 14 Tools korrekt mit ihren 8 Integrations verknüpft
4. **JSON-Editor**: JavaScript-Funktionen funktionieren korrekt für alle Parameter-Editoren

**Ergebnis:**
- ✅ **14 Tools** werden korrekt angezeigt, gruppiert in **8 Integration-Kategorien**
- ✅ **Vollständige CRUD-Funktionalität** für Tools und Integrations
- ✅ **Produktionstauglicher Code** ohne Debug-Ausgaben
- ✅ **Stabile Template-Architektur** mit korrekter Block-Vererbung

**Definition of Done:** ✅ VOLLSTÄNDIG ERFÜLLT
- [x] Tools-Seite zeigt alle Tools korrekt an
- [x] Tool-Integration-Verknüpfungen funktionieren
- [x] JSON-Editor funktioniert für alle Parameter-Typen
- [x] Kein Debug-Code in Production
- [x] DataManager verwendet korrekte Pfade

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

#### ✅ **Sprint 9: Bug Fixes & Production Ready** - ABGESCHLOSSEN (29. Juni 2025)
- Template-Struktur komplett repariert (Tools-Seite funktioniert)
- DataManager-Pfad-Probleme im Docker-Container gelöst
- Tool-Integration-Verknüpfungen wiederhergestellt
- JavaScript-Errors behoben (JSON-Editor)
- Komplettes Code-Cleanup durchgeführt

#### 📊 **Aktueller Projekt-Status (Stand: Sprint 12 abgeschlossen):**
- ✅ **14 Tools** vollständig funktionsfähig, gruppiert in **8 Integration-Kategorien**
- ✅ **13 Integrations** mit vollständigem CRUD-Management
- ✅ **12 Vendor Icons** korrekt integriert
- ✅ **Produktionsstabiler Code** ohne Debug-Ausgaben
- ✅ **Vollständige Docker-Containerisierung** mit korrekten Volume-Mappings
- ✅ **Moderne UI** mit Tailwind CSS und responsive Design
- ✅ **CSRF-Security** vollständig implementiert
- ✅ **Layout-Optimierungen**: Schmalere Sidebar (60px), Click-to-Open, Auto-Submit Filter
- ✅ **Test-System**: Umfassende Test-Suite mit zentraler Übersicht
- ✅ **Implementation Modules**: Vollständiges System für dynamische Module-Execution

#### 🎯 **Sprints 10-12 Zusammenfassung:**
- **Sprint 10**: UI/UX-Verbesserungen (Sidebar, Filter, Click-to-Open, Auto-Submit)
- **Sprint 11**: Test-System implementiert (zentrale Test-Übersicht, Module-Tests)
- **Sprint 12**: Implementation Modules System (Base-Klasse, Manager, OpenAI-Modul)

#### 🔄 **Nächste Sprint-Prioritäten:
- **Sprint 13**: Implementation Module Integration (Dynamic Tool-Module-Binding)
- **Sprint 14**: Icon-Design-System & UI-Polish (Komplettes Icon-Set)
- **Sprint 15+**: Advanced Features (Agents, Workflows, REST API)

# 📋 Backlog für Sprint 10+ (Abgeschlossen)

## Sprint 10: Layout-Optimierungen & UI-Verbesserungen ✅ COMPLETED (1 Tag)
### Ziel: Umsetzung der Layout-Anforderungen aus dem Backlog

**User Stories:**
- Als Benutzer möchte ich eine schmalere Sidebar im eingeklappten Zustand
- Als Benutzer möchte ich Filter- und Suchfunktionen auf allen List-Seiten
- Als Benutzer möchte ich alternierende Zeilenfarben in Tabellen
- Als Benutzer möchte ich durch Klick auf Tabellenzeilen navigieren

**Tasks:**
- [x] **Sidebar Optimierung**: Eingeklappte Sidebar von 80px auf 60px reduziert (50px mobile)
- [x] **Filter-System**: Erweiterte Suchtext und Filterfelder für Tools und Integrations implementiert
- [x] **Tabellen-Styling**: Alternierende Zeilenfarben und Hover-Effekte hinzugefügt
- [x] **Click-to-Open**: Klick auf Tabellenzeile öffnet gewählten Eintrag
- [x] **Auto-Submit Filter**: JavaScript für automatische Filter-Übermittlung
- [x] **Button-Styling**: Konsistente Primär-/Akzentfarben-Buttons implementiert
- [x] **CSS-Verbesserungen**: Erweiterte Filter-Panels und verbesserte Interaktivität

**Definition of Done:** ✅ VOLLSTÄNDIG ERFÜLLT
- [x] Sidebar ist im eingeklappten Zustand schmaler
- [x] Filter/Suche funktioniert auf Tools und Integrations-Seiten
- [x] Tabellen haben alternierende Zeilenfarben und Hover-Effekte
- [x] Click-to-Open funktioniert für alle List-Views
- [x] Auto-Submit für Filter implementiert

## Sprint 11: Test-System Implementierung ✅ COMPLETED (1 Tag)
### Ziel: Umfassendes Test-System für alle funktionalen Einheiten

**User Stories:**
- Als Entwickler möchte ich eine zentrale Test-Übersicht
- Als Benutzer möchte ich Backend-Routen für jede funktionale Einheit testen können
- Als Entwickler möchte ich dokumentierte Test-Verfahren

**Tasks:**
- [x] **Zentrale Test-Seite**: `/test` Route mit Übersicht aller bestehenden Tests
- [x] **Test-Blueprint**: Separates Blueprint für Test-System mit vollständiger Architektur
- [x] **Test-Templates**: Overview und Module-Templates für Test-Interface
- [x] **Navigation-Integration**: Test-Link in Sidebar mit Bug-Icon hinzugefügt
- [x] **Route-Dokumentation**: Dokumentation der .py-Dateien und getesteten Routen
- [x] **Test-Module-System**: Modular aufgebautes Test-System für verschiedene Komponenten

**✅ ERFOLGREICH IMPLEMENTIERT:**
- ✅ **Test-Route**: `/test` mit vollständiger Blueprint-Architektur
- ✅ **Test-Overview**: Zentrale Übersicht aller verfügbaren Test-Module
- ✅ **Module-Tests**: Einzelne Test-Module für Integrations, Tools, API
- ✅ **Navigation**: Test-Link in Sidebar integriert mit Bug-Icon
- ✅ **Template-System**: Vollständige Template-Hierarchie für Test-Interface
- ✅ **Simulation-Engine**: Test-Simulation für verschiedene Szenarien

**Definition of Done:** ✅ VOLLSTÄNDIG ERFÜLLT
- [x] Test-Seite zeigt alle verfügbaren Tests
- [x] Jede funktionale Einheit hat eine dedizierte Test-Seite
- [x] Route-Dokumentation ist implementiert
- [x] Tests können manuell ausgeführt werden
- [x] Navigation ist integriert

## Sprint 12: Implementation Modules System ✅ COMPLETED (1 Tag)
### Ziel: v036 Implementation-System portieren und erweitern

**User Stories:**
- Als System möchte ich Implementation-Module unterstützen
- Als Entwickler möchte ich das v036 Tool-Modules-System als "Implementation-Modules" portieren
- Als Integration möchte ich eine "base_implementation" implementieren

**Tasks:**
- [x] **Implementation Modules**: v036 `tool_modules` zu `implementation_modules` portieren
- [x] **Base Implementation**: `base_implementation` Klasse (analog zu v036 `base.py`)
- [x] **Implementation Manager**: Dynamic Loading von Implementation-Modulen
- [x] **Registry System**: Registrierung und Verwaltung von Implementation-Modulen
- [x] **Error Handling**: Robuste Fehlerbehandlung für Module-Loading
- [x] **OpenAI Example**: Vollständige OpenAI ChatCompletion Implementation

**✅ ERFOLGREICH IMPLEMENTIERT:**
- ✅ **Implementation-System**: Vollständige Portierung der v036-Architektur
- ✅ **Base-Klasse**: `BaseImplementation` mit Abstract Methods für alle Module
- ✅ **Manager-System**: `ImplementationManager` für dynamisches Laden
- ✅ **Registry**: Automatische Registrierung verfügbarer Implementation-Module
- ✅ **OpenAI-Modul**: Vollständige `OpenAIChatCompletionImplementation`
- ✅ **Error-System**: Umfassende Exception-Hierarchie für Fehlerbehandlung

**Definition of Done:** ✅ VOLLSTÄNDIG ERFÜLLT
- [x] Implementation-Modules-System funktioniert
- [x] Base-Implementation ist implementiert
- [x] OpenAI ChatCompletion ist portiert
- [x] Dynamic Loading funktioniert
- [x] Error Handling ist robust

## Sprint 13: Implementation Module Integration ✅ COMPLETED (1 Tag)
### Ziel: Dynamische Verknüpfung zwischen Tools/Integrations und Implementation Modules

**User Stories:**
- Als Tool möchte ich über Implementation Modules ausgeführt werden
- Als Integration möchte ich automatisch passende Implementation Module finden
- Als Benutzer möchte ich Tools über ihre Implementation Module ausführen

**Tasks:**
- [x] **Module-Tool-Binding**: Automatische Verknüpfung zwischen Tools und Implementation Modules
- [x] **Dynamic Execution**: Tool-Ausführung über Implementation Manager
- [x] **Configuration Mapping**: Parameter-Mapping zwischen Tool- und Module-Konfiguration
- [x] **Real Execution**: Echte API-Calls statt Simulation in Tool-Tests
- [x] **Google Sheets Module**: Implementation des Google Sheets-Moduls
- [x] **Error Integration**: Integration der Module-Errors in Tool-Interface

**✅ ERFOLGREICH IMPLEMENTIERT:**
- ✅ **Tool-Module-Binding**: Automatische Zuordnung basierend auf Integration-Namen
- ✅ **Echte Tool-Ausführung**: Tools werden jetzt über Implementation Modules ausgeführt
- ✅ **Configuration Mapping**: Nahtlose Übertragung von Tool-Config zu Module-Config
- ✅ **Google Sheets Module**: Vollständiges Google Sheets Implementation Module erstellt
- ✅ **Async Execution**: Threading-basierte async Ausführung in Flask-Routes
- ✅ **Error Handling**: Robuste Fehlerbehandlung mit Fallback zu Simulation
- ✅ **Status Anzeige**: Implementation Module Status in Tool-UI integriert
- ✅ **Module Overview**: Dedizierte Übersichtsseite für alle Implementation Modules

**Implementierte Features:**
1. **ToolsManager Integration**: 
   - `get_implementation_module_for_tool()` - Automatische Modul-Zuordnung
   - `test_tool_with_implementation()` - Echte Tool-Tests über Module
   - `execute_tool_with_implementation()` - Echte Tool-Ausführung über Module
   - `get_tool_implementation_status()` - Status-Überprüfung

2. **Google Sheets Module**:
   - Vollständige Google Sheets API Integration
   - Unterstützt: read_sheet, write_sheet, update_sheet, create_sheet, get_sheet_info
   - OAuth2 und Service Account Authentifizierung
   - Robuste Fehlerbehandlung und Validation

3. **UI Integration**:
   - Implementation Module Status in Tool-Views
   - Automatisches Status-Loading via AJAX
   - Module-Übersichtsseite im Test-System
   - Tool-Module-Zuordnung Visualisierung

4. **Route Erweiterungen**:
   - `/tools/implementation-status/<id>` - Module Status abrufen
   - `/tools/implementation-modules` - Alle Module auflisten
   - `/test/implementation-modules` - Module Übersichtsseite
   - Erweiterte Test- und Execute-Routes mit Module-Support

**Definition of Done:** ✅ VOLLSTÄNDIG ERFÜLLT
- [x] Tools können über Implementation Modules ausgeführt werden
- [x] Automatische Modul-Zuordnung funktioniert
- [x] Google Sheets Module ist vollständig implementiert
- [x] UI zeigt Implementation Module Status an
- [x] Fallback zu Simulation bei fehlenden Modulen

# 📋 Backlog für Sprint 14+ (Überarbeiteter Plan - Stand: 29. Juni 2025)

## Sprint 14: Layout-Verbesserungen & Icon-Design-System (3-4 Tage)
### Ziel: Komplettes Layout-Redesign und finale UI-Verbesserungen

**User Stories:**
- Als Benutzer möchte ich einheitliche, moderne Icons in der gesamten Anwendung
- Als Designer möchte ich ein konsistentes visuelles Design-System
- Als Benutzer möchte ich eine polierte, professionelle UI-Erfahrung
- Als Benutzer möchte ich ein modernes Card-basiertes Layout für Listen
- Als Benutzer möchte ich alle Aktionen konsistent in der Toolbar finden

**Tasks:**

### **Layout-Verbesserungen (Priorität 1):**
- [ ] **Toolbar-Migration**: Alle Footer-Buttons in Toolbar am Kopf der Seite verschieben
  - Tools/Integrations: Create/Import/Export-Buttons → Toolbar
  - Tool/Integration Details: Edit/Delete/Clone-Buttons → Toolbar
  - Konsistente rechtsbündige Ausrichtung neben Überschrift
- [ ] **Aktive Navigation**: Sidebar-Icons für /tools und /integrations als aktiv markieren
  - Route-basierte Active-State-Erkennung implementieren
  - CSS-Klassen für aktive Tool/Integration-Navigation
- [ ] **Card-Layout-Migration**: Listen-Layout zu Card-Layout umstellen
  - `/integrations`: Von Tabelle zu Card-Grid mit Vendor-Icons
  - `/tools`: Von Tabelle zu Card-Grid gruppiert nach Integration
  - Responsive Card-Design mit Hover-Effekten
- [ ] **Container-Fixes**: 
  - Tools/create: Container-Alignment oben korrigieren
  - Dashboard: Sidebar-Context-Spacing entfernen
- [ ] **Layout-Konsistenz**: Einheitliche Abstände und Container-Breiten

### **Icon-Design-System (Priorität 2):**
- [ ] **Icon-Set Design**: Komplettes Icon-Set basierend auf Dashboard/Integrations-Vorlage
  - Dashboard, Insights, Workflows, Tools, Integrations, Profile, Company
  - Test, Implementation Modules, Settings, Help
  - Status-Icons (Connected, Error, Loading, Success)
- [ ] **Icon-System**: SVG-basierte Icon-Komponenten und CSS-Klassen

### **UI-Polish (Priorität 3):**
- [ ] **Design-Konsistenz**: Einheitliche Typografie, Farbschema
- [ ] **Responsive-Optimierung**: Mobile-Optimierungen für Card-Layout
- [ ] **Accessibility**: WCAG 2.1 Compliance Verbesserungen

**Definition of Done:**
- [ ] Alle Footer-Buttons sind in Toolbars verschoben
- [ ] Tools/Integrations Sidebar-Navigation zeigt aktiven Status korrekt
- [ ] Card-Layout für Tools und Integrations ist implementiert
- [ ] Container-Alignment-Probleme sind behoben
- [ ] Dashboard-Spacing ist korrigiert
- [ ] Komplettes, konsistentes Icon-Set verfügbar
- [ ] UI ist vollständig poliert und produktionsreif

## Sprint 15: Clean-up & Documentation (2 Tage)
### Ziel: Code-Cleanup und vollständige Dokumentation

**User Stories:**
- Als Entwickler möchte ich sauberen, wartbaren Code
- Als neuer Entwickler möchte ich umfassende Dokumentation
- Als System möchte ich alle Debug-Code und temporären Dateien entfernt haben

**Tasks:**
- [ ] **Code-Cleanup**: Finale Bereinigung aller Debug-Ausgaben und temporären Codes
- [ ] **Documentation Update**: Vollständige Aktualisierung der README.md
- [ ] **API Documentation**: Dokumentation aller Routes und Endpunkte
- [ ] **Setup Guide**: Detaillierte Setup-Anweisungen für Entwickler
- [ ] **Architecture Documentation**: Vollständige Architektur-Dokumentation
- [ ] **Testing Documentation**: Test-System und Test-Verfahren dokumentieren
- [ ] **Deployment Guide**: Production-Deployment-Anweisungen

**Definition of Done:**
- [ ] Kein Debug-Code oder temporäre Dateien vorhanden
- [ ] Vollständige Dokumentation verfügbar
- [ ] Setup-Guide funktioniert für neue Entwickler
- [ ] Alle APIs sind dokumentiert

## Sprint 16: Advanced Implementation Module Features (3-4 Tage)
### Ziel: Erweiterte Implementation Module Funktionalitäten

**User Stories:**
- Als Module möchte ich erweiterte Konfigurationsmöglichkeiten
- Als Tool möchte ich Module-spezifische Parameter nutzen
- Als Entwickler möchte ich einfach neue Module erstellen können

**Tasks:**
- [ ] **Module Templates**: Templates für häufige Module-Typen (API, Database, File)
- [ ] **Dynamic Configuration UI**: UI-Generierung basierend auf Module-Schema
- [ ] **Module Testing Framework**: Automatisierte Tests für Implementation Modules
- [ ] **Module Documentation**: Auto-generierte Dokumentation aus Module-Metadaten
- [ ] **Module Versioning**: Versionierung und Update-Management für Module
- [ ] **Module Registry**: Zentrale Registry für alle verfügbaren Module
- [ ] **Hot-Reload**: Dynamic Loading/Unloading von Modulen ohne Restart

**Priority Modules:**
1. **Slack Integration**: Slack API Implementation Module
2. **Email Module**: SMTP/Email-Versand Implementation Module  
3. **Database Module**: SQL/NoSQL Database Implementation Module
4. **File Processing**: CSV/JSON/XML File Processing Module

**Definition of Done:**
- [ ] Module-Templates funktionieren für neue Module-Entwicklung
- [ ] Dynamic Configuration UI generiert Forms basierend auf Module-Schema
- [ ] Automatisierte Tests für alle Implementation Modules
- [ ] Hot-Reload-System funktioniert

## Sprint 17: Security Framework (3-4 Tage)
### Ziel: Umfassendes Security-System implementieren

**User Stories:**
- Als Benutzer möchte ich mich sicher authentifizieren können
- Als System möchte ich vor Sicherheitsbedrohungen geschützt sein
- Als Administrator möchte ich Benutzer-Berechtigungen verwalten

**Tasks:**
- [ ] **Authentication System**: Login/Logout, Session-Management
- [ ] **User Management**: Benutzer-CRUD, Rollen und Berechtigungen
- [ ] **Password Security**: Bcrypt/Argon2-Hashing, Password-Policy
- [ ] **Data Encryption**: AES-256 für sensitive Daten (API-Keys, Tokens)
- [ ] **Security Headers**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- [ ] **Rate Limiting**: API-Rate-Limits für alle Endpunkte
- [ ] **Audit Logging**: Vollständige Nachverfolgung sicherheitsrelevanter Aktionen
- [ ] **Input Sanitization**: Erweiterte Input-Validation und Sanitization

**Security Layers:**
1. **Application Security**: CSRF (✅ bereits implementiert), XSS-Protection, Input-Validation
2. **Transport Security**: HTTPS, HSTS, Secure Cookies
3. **Data Security**: Encryption-at-Rest, Encryption-in-Transit
4. **Access Security**: Authentication, Authorization, RBAC

**Definition of Done:**
- [ ] Vollständiges Authentication-System funktioniert
- [ ] Alle API-Keys und sensible Daten sind verschlüsselt
- [ ] Security-Headers sind implementiert
- [ ] Rate-Limiting verhindert API-Abuse
- [ ] Audit-Logging dokumentiert alle kritischen Aktionen

## Sprint 18: Workflow-System (4-5 Tage)
### Ziel: Tool-Verkettung und Workflow-Automation

**User Stories:**
- Als Benutzer möchte ich Tools in Workflows verketten können
- Als System möchte ich Workflows automatisch ausführen können
- Als Benutzer möchte ich Workflow-Templates erstellen und teilen

**Tasks:**
- [ ] **Workflow Engine**: Core-Engine für Workflow-Ausführung
- [ ] **Visual Workflow Builder**: Drag & Drop Workflow-Designer
- [ ] **Tool Chaining**: Tools können Output an andere Tools weitergeben
- [ ] **Conditional Logic**: If/Else-Bedingungen in Workflows
- [ ] **Loop Support**: Schleifen und Iterationen in Workflows
- [ ] **Workflow Templates**: Vordefinierte Workflow-Templates
- [ ] **Scheduling**: Zeitbasierte Workflow-Ausführung (Cron-Jobs)
- [ ] **Workflow Monitoring**: Real-time Monitoring von Workflow-Ausführungen

**Core Features:**
1. **Workflow Designer**: Visual Editor mit Drag & Drop
2. **Execution Engine**: Async Workflow-Ausführung mit Error-Handling
3. **Data Flow**: Seamless Data-Transfer zwischen Tools
4. **Monitoring**: Real-time Status und Performance-Monitoring

**Definition of Done:**
- [ ] Workflows können visuell erstellt werden
- [ ] Tools können in Sequenz und parallel ausgeführt werden
- [ ] Data-Flow zwischen Tools funktioniert
- [ ] Workflow-Monitoring zeigt Real-time Status

## Sprint 19: OpenAI Assistant Integration (4-5 Tage) 🤖 PRIORITÄT
### Ziel: Vollständige OpenAI Assistant API V2 Integration

**User Stories:**
- Als Benutzer möchte ich OpenAI Assistants erstellen und verwalten
- Als System möchte ich alle OpenAI Assistant API V2 Features unterstützen
- Als Benutzer möchte ich mit Assistants in einem Chat-Interface interagieren

**Tasks:**
- [ ] **Assistant Management**: CRUD für Assistants (POST/GET/PUT/DELETE /v1/assistants)
- [ ] **Thread Management**: Conversation-Management (/v1/threads)
- [ ] **Message System**: Nachrichten-Verwaltung (/v1/threads/{id}/messages)
- [ ] **Run Management**: Assistant-Ausführungen (/v1/threads/{id}/runs)
- [ ] **File Management**: Upload und Retrieval (/v1/files)
- [ ] **Chat Interface**: Real-time Chat-UI für Assistant-Interaktion
- [ ] **Assistant Gallery**: Übersicht aller erstellten Assistenten
- [ ] **Assistant Builder**: UI zur Erstellung/Bearbeitung von Assistenten

**Integration mit bestehendem System:**
- Tools als Assistant Functions verfügbar machen
- Implementation Modules als Assistant-Tools integrieren
- Workflow-Integration für komplexe Assistant-Tasks

**Definition of Done:**
- [ ] Vollständige Assistant API V2 implementiert
- [ ] Chat-Interface funktioniert real-time
- [ ] File-Upload für Retrieval funktioniert
- [ ] Assistant-Gallery zeigt alle Assistants
- [ ] Function-Calling mit eigenen Tools integriert

## Sprint 20: Agents-System (5-6 Tage) 🤖 PRIORITÄT
### Ziel: Multi-Agent-System basierend auf OpenAI Assistants

**User Stories:**
- Als Benutzer möchte ich autonome Agents erstellen, die Tools verwenden können
- Als Agent möchte ich auf Tools zugreifen und diese koordiniert ausführen
- Als System möchte ich Agent-to-Agent Kommunikation unterstützen

**Tasks:**
- [ ] **Agent Framework**: Basis-Klassen für verschiedene Agent-Typen
- [ ] **Tool Integration**: Agents können verfügbare Tools nutzen
- [ ] **Agent Orchestration**: Multi-Agent-Koordination und Kommunikation
- [ ] **Memory System**: Persistente Agent-Memories und Kontext-Verwaltung
- [ ] **Agent Templates**: Vordefinierte Agent-Typen für häufige Use-Cases
- [ ] **Agent Monitoring**: Dashboard für Agent-Aktivitäten und Performance

**Agent Types:**
1. **Task Agent**: Ausführung spezifischer Tool-basierten Tasks
2. **Workflow Agent**: Automatische Workflow-Ausführung
3. **Monitoring Agent**: System-Überwachung und Alerting
4. **Research Agent**: Automatische Datensammlung und -analyse

**Definition of Done:**
- [ ] Agents können Tools autonom ausführen
- [ ] Multi-Agent-Kommunikation funktioniert
- [ ] Memory-System ist persistent
- [ ] Agent-Dashboard zeigt alle Aktivitäten

# 📋 Backlog für Sprint 21+ (Enterprise & Advanced Features)

## Sprint 21-22: REST API & External Integration (4-6 Tage)
### Ziel: Vollständige REST API für externe Integration

**Tasks:**
- [ ] **REST API v1**: Vollständige REST-API für alle Tools/Integrations/Agents
- [ ] **API Documentation**: OpenAPI/Swagger-Dokumentation
- [ ] **API Authentication**: Token-basierte API-Authentifizierung
- [ ] **Webhooks**: Event-basierte Notifications für externe Systeme
- [ ] **SDK Development**: Python/JavaScript SDKs für API-Integration

## Sprint 23-24: Advanced UI & Mobile (4-5 Tage)
### Ziel: Progressive Web App und Mobile-Optimierung

**Tasks:**
- [ ] **Progressive Web App**: Vollständige PWA-Implementierung
- [ ] **Mobile-First UI**: Touch-optimierte Benutzeroberfläche
- [ ] **Offline Functionality**: Offline-Modus für kritische Features
- [ ] **Push Notifications**: Mobile Push-Notifications für Agent-Updates

## Sprint 25+: Enterprise Features
### Ziel: Enterprise-ready Features

**Tasks:**
- [ ] **Multi-Tenancy**: Organizations und Team-Management
- [ ] **SSO Integration**: SAML/OAuth2-basierte SSO
- [ ] **Advanced Analytics**: Performance-Monitoring und Usage-Analytics
- [ ] **Integration Marketplace**: Community-basierte Integration-Entwicklung

---

# 🎯 **Aktueller Status & Nächste Schritte (Stand: 14. Januar 2025)**

## ✅ **Erfolgreich Abgeschlossen (Sprints 1-13 + Dynamic UI Features):**
- **Grundlagen**: Flask + Docker + Tailwind Setup
- **UI/UX**: Moderne Sidebar, responsive Layout, Filter-Systeme
- **Data Management**: 13 Integrations, 15 Tools, 12 Icons migriert
- **CRUD Systems**: Vollständige Verwaltung für Tools und Integrations
- **Test System**: Umfassende Test-Suite mit zentraler Übersicht inkl. Dynamic Features
- **Implementation Modules**: Dynamisches Module-System mit OpenAI + Google Sheets
- **Module Integration**: Echte Tool-Ausführung über Implementation Modules
- ✅ **Dynamic Form UI**: Vollständig implementierte dynamische Formular-UI für Tools
  - **Edit/Create/Execute**: Alle Dialoge nutzen dynamische Feld-Generierung
  - **Field Types**: text, select, boolean, json, file mit vollständiger Unterstützung
  - **Status System**: Locked, Prefilled, Required Badges in allen UIs
  - **JSON Integration**: Bidirektionale Sync zwischen UI-Feldern und JSON-Editor
  - **Live Validation**: Echtzeit-JSON-Validation mit Fehlermeldungen
  - **Backend Integration**: Flexible Parameter-Verarbeitung in tools.py

## 🔄 **Testsystem Status:**
- ✅ **Grundlegende Tests**: Alle Module und Routen erfasst
- ✅ **Dynamic Features**: Spezielle Test-Routen für dynamische UI-Features
- ✅ **Test-Coverage**: Vollständige Dokumentation aller dynamischen Features
- ⚠️ **Test-Anpassung**: Testsystem ist bereit, keine weiteren Anpassungen nötig

## 🔄 **Aktuelle Prioritäten (Sprints 14-16):**
1. **Sprint 14**: Layout-Verbesserungen & Icon-Design-System (Toolbar-Migration, Card-Layout, Navigation-Fixes)
2. **Sprint 15**: Code-Cleanup & vollständige Dokumentation  
3. **Sprint 16**: Advanced Implementation Module Features

## 🚀 **Mittelfristige Ziele (Sprints 17-20):**
1. **Sprint 17**: Security Framework (Authentication, Encryption, Rate-Limiting)
2. **Sprint 18**: Workflow-System (Tool-Verkettung, Visual Designer)
3. **Sprint 19**: OpenAI Assistant Integration (vollständige API V2)
4. **Sprint 20**: Agents-System (Multi-Agent, autonome Tool-Nutzung)

## 🌟 **Langfristige Vision (Sprint 21+):**
- **Enterprise-Features**: REST API, Multi-Tenancy, SSO
- **Advanced UI**: PWA, Mobile-Optimierung, Offline-Modus

---

## 📋 **Dynamische Form-UI - Implementierungsdetails:**

### **Frontend (JavaScript):**
- `generateFieldHtml()` - Dynamische HTML-Generierung für alle Feld-Typen
- `toggleJsonEditor()` - JSON-Editor Ein-/Ausblenden mit Sync
- `validateJSON()` - Live-Validation für JSON-Felder
- `syncFormWithJson()` - Bidirektionale Synchronisation UI ↔ JSON
- `addFieldListeners()` - Event-Handler für dynamische Formular-Interaktion

### **Backend (Flask):**
- `tools.py`: Flexible Parameter-Verarbeitung für dynamische Felder
- `get_tool_config()` API-Route für AJAX-basierte Tool-Konfiguration
- Integration-Objekt wird an alle Templates übergeben
- Unterstützung für prefilled_inputs und locked_inputs

### **Templates:**
- `edit.html` - Dynamische Edit-Forms mit allen Features
- `create.html` - Dynamische Create-Forms mit allen Features  
- `view.html` - Dynamische Execute-Dialog mit allen Features
- Vollständige Status-Badge-Integration (Locked, Prefilled, Required)

### **Test-System:**
- `/test/dynamic-features` - Spezielle Test-Seite für dynamische Features
- Vollständige Dokumentation aller Feature-Tests
- AJAX-Test-Routen für alle Feld-Typen
- Beispiel-Konfigurationen für Test-Szenarien