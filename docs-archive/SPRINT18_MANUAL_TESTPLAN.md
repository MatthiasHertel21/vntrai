# 🧪 Sprint 18 Task Management Revolution - Manueller Testplan

**Datum:** 1. Juli 2025  
**Sprint:** 18 - Task Management Revolution  
**URL:** http://localhost:5004  
**Testumgebung:** Docker Container

## 📋 **Übersicht**

Dieser Testplan validiert die vollständige Implementierung der Sprint 18 Features:
- Task-Definitionen in agent.json integriert
- Task-Ausführung in agentrun.json verwaltet  
- Tools "options" Field mit "assistant" Option
- Agent Task Editor in Agent Edit Page
- Sprint 18 API-Endpunkte

---

## 🎯 **TEIL 1: AGENT TASK EDITOR TESTS**

### Test 1.1: Agent Creation & Basic UI
**Ziel:** Validierung der Agent-Erstellung und Task Editor Integration

**Schritte:**
1. 🌐 Navigiere zu `http://localhost:5004/agents`
2. ✅ Überprüfe: Agents Overview lädt korrekt
3. ➕ Klicke "Create Agent" oder "New Agent"
4. 📝 Fülle aus:
   - Name: "Test Agent Sprint 18"
   - Category: "Testing"
   - Description: "Sprint 18 Task Management Test Agent"
5. 💾 Speichere Agent
6. ✅ Überprüfe: Agent wurde erfolgreich erstellt

**Erwartetes Ergebnis:**
- Agent wird in der Liste angezeigt
- Neue agent.json Datei wird unter `data/agents/` erstellt
- `tasks: []` Array ist vorhanden

---

### Test 1.2: Task Editor Integration
**Ziel:** Validierung des Task Editors in Agent Edit Page

**Schritte:**
1. 🖱️ Klicke "Edit" bei erstelltem Test Agent
2. ✅ Überprüfe Layout:
   - Linke Spalte: Basic Information, **Task Editor**
   - Rechte Spalte: AI Assistant, Tasks, Files, etc.
3. 📋 Lokalisiere "Task Editor" Container
4. ✅ Überprüfe Elemente:
   - Header "Task Editor" 
   - "Add Task" Button mit "+" Icon
   - Leere Task-Liste (bei neuem Agent)

**Erwartetes Ergebnis:**
- Task Editor ist sichtbar und funktional
- UI-Layout entspricht Sprint 18 Spezifikation

---

### Test 1.3: AI Task Creation
**Ziel:** Erstellung einer AI Task über Task Editor

**Schritte:**
1. ➕ Klicke "Add Task" im Task Editor
2. 📝 Fülle Task Details aus:
   - **Name:** "Content Generation Task"
   - **Type:** "AI" (auswählen)
   - **Description:** "Generate marketing content"
   - **Instructions:** "Create compelling marketing copy"
   - **Output Format:** "markdown"
3. ➕ Füge Input Fields hinzu:
   - Field Name: "topic"
   - Field Type: "text" 
   - Field Label: "Content Topic"
   - Default Value: "AI Technology"
4. 💾 Speichere Task
5. ✅ Überprüfe: Task erscheint in Task Preview

**Erwartetes Ergebnis:**
- Task wird erfolgreich erstellt
- Task erscheint in "Tasks" Container (rechte Spalte)
- agent.json enthält Task-Definition im `tasks[]` Array

---

### Test 1.4: Tool Task Creation
**Ziel:** Erstellung einer Tool Task über Task Editor

**Schritte:**
1. ➕ Klicke "Add Task" im Task Editor
2. 📝 Fülle Task Details aus:
   - **Name:** "API Integration Task"
   - **Type:** "Tool" (auswählen)
   - **Description:** "Execute API call via tool"
   - **Tool Selection:** [Verfügbares Tool auswählen]
3. ⚙️ Konfiguriere Tool-spezifische Eingaben
4. 💾 Speichere Task
5. ✅ Überprüfe: Tool Task erscheint in Task Preview

**Erwartetes Ergebnis:**
- Tool Task wird erfolgreich erstellt
- Tool-Konfiguration wird korrekt gespeichert
- Task-Definition enthält tool_config Sektion

---

### Test 1.5: Task Management Operations
**Ziel:** Edit, Delete, Reorder Funktionen testen

**Schritte:**
1. 📝 **Task Edit:**
   - Klicke "Edit" bei vorhandener Task
   - Ändere Name und Description
   - Speichere Änderungen
   - ✅ Überprüfe: Änderungen sind sichtbar

2. 🔄 **Task Reorder:**
   - Nutze Drag & Drop oder Up/Down Buttons
   - Ändere Reihenfolge der Tasks
   - ✅ Überprüfe: Neue Reihenfolge wird beibehalten

3. 🗑️ **Task Delete:**
   - Klicke "Delete" bei einer Task
   - Bestätige Löschung
   - ✅ Überprüfe: Task wird entfernt

**Erwartetes Ergebnis:**
- Alle CRUD-Operationen funktionieren korrekt
- Änderungen werden in agent.json persistiert
- UI aktualisiert sich in Echtzeit

---

## 🛠️ **TEIL 2: TOOLS "OPTIONS" FIELD TESTS**

### Test 2.1: Tools Overview & Options
**Ziel:** Validierung des "options" Fields bei Tools

**Schritte:**
1. 🌐 Navigiere zu `http://localhost:5004/tools`
2. 🔍 Wähle ein Tool aus (z.B. OpenAI-basiertes Tool)
3. ✏️ Klicke "Edit" 
4. 📋 Suche nach "Options" Sektion
5. ✅ Überprüfe:
   - "Assistant" Option vorhanden
   - Checkbox für "Enable Assistant"
   - Assistant-Konfigurationsfelder

**Erwartetes Ergebnis:**
- Options Sektion ist sichtbar
- Assistant-Konfiguration verfügbar
- Einstellungen sind speicherbar

---

### Test 2.2: Assistant Option Activation
**Ziel:** Aktivierung der Assistant Option für ein Tool

**Schritte:**
1. ✅ Aktiviere "Enable Assistant" Checkbox
2. 📝 Konfiguriere Assistant Settings:
   - Model: "gpt-4-turbo-preview"
   - Instructions: "You are a helpful assistant for this tool"
   - Auto-Create: ✅ enabled
3. 💾 Speichere Tool-Konfiguration
4. 🔄 Lade Seite neu
5. ✅ Überprüfe: Einstellungen bleiben erhalten

**Erwartetes Ergebnis:**
- Assistant Option wird aktiviert
- Konfiguration wird in tool.json gespeichert
- `options.assistant.enabled: true`

---

### Test 2.3: Agent Tool Selection Filter
**Ziel:** Nur Assistant-enabled Tools in Agent verfügbar

**Schritte:**
1. 🔙 Zurück zu Agent Edit Page
2. 🤖 Gehe zur "AI Assistant" Sektion
3. 📋 Überprüfe Tool-Auswahl Dropdown
4. ✅ Validiere:
   - Nur Tools mit Assistant Option erscheinen
   - Nicht-Assistant Tools sind ausgeblendet
   - Tool-Liste ist gefiltert

**Erwartetes Ergebnis:**
- Tool-Filter funktioniert korrekt
- Nur Assistant-fähige Tools verfügbar
- UI zeigt korrekte Tools an

---

## 🚀 **TEIL 3: AGENTRUN TASK EXECUTION TESTS**

### Test 3.1: Agent Run Creation
**Ziel:** Erstellung eines Agent Runs mit Task States

**Schritte:**
1. 👤 Gehe zu Agent Detail Page
2. ▶️ Klicke "New Run" oder "Start Session"
3. 📝 Benenne Agent Run: "Sprint 18 Test Run"
4. 🚀 Starte Agent Run
5. ✅ Überprüfe:
   - Agent Run wird erstellt
   - Task States werden aus Agent übernommen
   - Alle Tasks haben Status "pending"

**Erwartetes Ergebnis:**
- agentrun.json wird erstellt unter `data/agentrun/`
- `task_states[]` Array enthält alle Agent Tasks
- Initial Status: alle Tasks "pending"

---

### Test 3.2: Task Execution Interface
**Ziel:** Task-Ausführung über Agent Run UI

**Schritte:**
1. 🌐 Navigiere zu Agent Run Page
2. ✅ Überprüfe Layout:
   - Linke Spalte: "Task Output"
   - Rechte Spalte: "Tasks", "Files", "Feedback"
3. 📋 Lokalisiere Task-Liste in rechter Spalte
4. ✅ Überprüfe Task-Anzeige:
   - Task Namen und Descriptions
   - Status Indicators (pending/running/completed)
   - "Execute" Buttons

**Erwartetes Ergebnis:**
- Agent Run UI lädt korrekt
- Task-Definitionen werden aus Agent geladen
- Task-Status wird aus agentrun.json geladen

---

### Test 3.3: Task Execution Flow
**Ziel:** Ausführung einer Task mit Status-Updates

**Schritte:**
1. ▶️ Klicke "Execute" bei einer AI Task
2. 📝 Fülle Input-Felder aus (falls vorhanden)
3. 🚀 Starte Task-Ausführung
4. ⏱️ Beobachte Status-Änderungen:
   - pending → running → completed/error
5. 📄 Überprüfe Task Output im "Task Output" Bereich

**Erwartetes Ergebnis:**
- Task Status wird korrekt aktualisiert
- Inputs werden in agentrun.json gespeichert
- Results erscheinen im Output-Bereich
- execution_time wird berechnet

---

## 🌐 **TEIL 4: API ENDPUNKTE TESTS**

### Test 4.1: Sprint 18 Task Management API
**Ziel:** Validierung der neuen API Endpunkte

**API Tests über Browser Developer Tools oder Postman:**

```bash
# Agent Task Definitions
GET /api/task_management/agent/{agent_uuid}/tasks
POST /api/task_management/agent/{agent_uuid}/tasks
PUT /api/task_management/agent/{agent_uuid}/tasks/{task_uuid}
DELETE /api/task_management/agent/{agent_uuid}/tasks/{task_uuid}

# Agent Run Task Execution
GET /api/task_management/run/{run_uuid}/tasks
POST /api/task_management/run/{run_uuid}/tasks/{task_uuid}/execute
GET /api/task_management/run/{run_uuid}/tasks/{task_uuid}/status

# Tools Options API
GET /api/task_management/tools/{tool_id}/options
PUT /api/task_management/tools/{tool_id}/options
```

**Erwartetes Ergebnis:**
- Alle Endpunkte antworten mit korrekten HTTP Status Codes
- JSON Responses enthalten erwartete Datenstrukturen
- CSRF Protection funktioniert

---

## 🧩 **TEIL 5: INTEGRATION & MIGRATION TESTS**

### Test 5.1: Legacy Migration Support
**Ziel:** Prüfung der Abwärtskompatibilität

**Schritte:**
1. 📁 Überprüfe bestehende Agent-Dateien (falls vorhanden)
2. 🔄 Lade Agent in neuer Sprint 18 UI
3. ✅ Validiere:
   - Legacy Agents werden korrekt geladen
   - Migration-Warnungen erscheinen (falls nötig)
   - Upgrade auf Sprint 18 Format möglich

**Erwartetes Ergebnis:**
- Keine Breaking Changes für bestehende Daten
- Klare Migration-Pfade verfügbar

---

### Test 5.2: Data Persistence Validation
**Ziel:** Validierung der Datenpersistierung

**Schritte:**
1. 📝 Erstelle komplexe Task-Struktur
2. 🔄 Stoppe Docker Container: `sudo docker-compose down`
3. 🚀 Starte Container neu: `sudo docker-compose up -d`
4. ✅ Überprüfe:
   - Alle Tasks sind erhalten
   - Agent Run States sind korrekt
   - Keine Datenverluste

**Erwartetes Ergebnis:**
- Vollständige Datenpersistierung
- Keine Corruption nach Restart

---

## 📊 **TEIL 6: PERFORMANCE & FEHLERBEHANDLUNG**

### Test 6.1: Error Handling
**Ziel:** Robustheit bei Fehlereingaben

**Schritte:**
1. 🚫 Versuche ungültige Task-Definitionen
2. ❌ Teste fehlerhafte API Calls
3. 🔧 Überprüfe Error Messages
4. 📝 Validiere Rollback-Mechanismen

**Erwartetes Ergebnis:**
- Graceful Error Handling
- Benutzerfreundliche Fehlermeldungen
- Keine System-Crashes

---

### Test 6.2: UI Responsiveness
**Ziel:** Performance der neuen UI-Komponenten

**Schritte:**
1. 📱 Teste auf verschiedenen Bildschirmgrößen
2. ⚡ Überprüfe Ladezeiten
3. 🖱️ Teste Interaktivität (Drag & Drop, etc.)
4. 📊 Validiere mit vielen Tasks (10+ Tasks)

**Erwartetes Ergebnis:**
- Responsive Design funktioniert
- Keine Performance-Probleme
- Smooth User Experience

---

## ✅ **ABNAHMEKRITERIEN - SPRINT 18 DEFINITION OF DONE**

Nach Abschluss aller Tests müssen folgende Kriterien erfüllt sein:

- [ ] **Task-Editor vollständig in Agent Edit Page integriert**
- [ ] **Task-Definitionen werden in agent.json gespeichert**  
- [ ] **AgentRun UI verwaltet Task-Ausführung und -Results**
- [ ] **Keine eigenständigen Task-CRUD-Operationen mehr**
- [ ] **Task-Status wird in agentrun.json verwaltet**
- [ ] **Tools "options" Feld mit "assistant" Option implementiert**
- [ ] **Sprint 18 API-Endpunkte funktionieren**
- [ ] **Data Manager erweitert mit Sprint 18 Methoden**
- [ ] **Legacy API als deprecated markiert**

---

## 📝 **TESTPROTOKOLL**

**Tester:** _________________  
**Datum:** _________________  
**Version:** Sprint 18  

### Testergebnisse:
- [ ] Teil 1: Agent Task Editor - ✅ Bestanden / ❌ Fehlgeschlagen
- [ ] Teil 2: Tools Options Field - ✅ Bestanden / ❌ Fehlgeschlagen  
- [ ] Teil 3: AgentRun Task Execution - ✅ Bestanden / ❌ Fehlgeschlagen
- [ ] Teil 4: API Endpunkte - ✅ Bestanden / ❌ Fehlgeschlagen
- [ ] Teil 5: Integration & Migration - ✅ Bestanden / ❌ Fehlgeschlagen
- [ ] Teil 6: Performance & Error Handling - ✅ Bestanden / ❌ Fehlgeschlagen

### Gefundene Issues:
1. ________________________________
2. ________________________________
3. ________________________________

### Empfehlungen:
_________________________________________________
_________________________________________________

**Gesamtbewertung:** ✅ Sprint 18 Ready für Production / ❌ Weitere Entwicklung erforderlich

---

## 🎯 **NÄCHSTE SCHRITTE**

Nach erfolgreichem Abschluss der Tests:

1. **Sprint 18 als abgeschlossen markieren**
2. **Documentation Update in development.md**
3. **Sprint 18 nach closed_sprints.md verschieben**
4. **Sprint 19 "Agent Run Revolution" vorbereiten**

---

**Hinweis:** Dieser Testplan deckt alle kritischen Sprint 18 Features ab. Bei Problemen siehe Debug-Logs im Docker Container: `sudo docker logs age_web_1`
