# 📋 Sprint-Backlog: Insights-Modul für `vntrai`

## 🎯 Ziel
Ein Nutzer kann ein Insight starten, mit der AI chatten, Dateien hochladen, Kontext über Wrapups wiederverwenden und die Systemkonfiguration im Admin-Bereich pflegen. Alles wird persistent als JSON gespeichert.

---

## 🧪 Sprint 1 – Basisfunktionen: Insights starten & speichern

### ✅ Ziel: Insights als JSON speichern, GUI-Grundstruktur

### EPIC 1: Insight-Initialisierung & Speicherung

- [ ] **I1**: UUID-Generierung bei Insight-Start
- [ ] **I2**: Leeres Insight-Objekt (`uuid`, `messages[]`, `created_at`) schreiben in `data/insights/{uuid}.json`
- [ ] **I3**: Globale `insights/config.json` mit `assistant_id`, `model`, `system_prompt`, `tools[]`
- [ ] **I4**: Fallback: Falls `assistant_id` nicht gesetzt → Assistant erzeugen & speichern
- [ ] **I5**: Backend-API: Insight anlegen & laden
- [ ] **I6**: GUI-Layout: Zweispaltige Ansicht (Chat | Files/Datasets/Knowledge/Prompts)

→ **Testbar:** Insight-UUID wird generiert, gespeichert, geladen, angezeigt.

---

## 💬 Sprint 2 – Chat-Thread mit OpenAI & Streaming

### ✅ Ziel: AI-Nachrichten senden und empfangen, Verlauf speichern

### EPIC 2: Chat & Thread-Integration

- [ ] **C1**: Gemeinsamer Thread für alle Insights in `config.json`
- [ ] **C2**: GUI: Message-Eingabe + Send-Button
- [ ] **C3**: Backend: Message an Thread senden (inkl. `additional_instructions`)
- [ ] **C4**: Streaming-API: Ausgabe in GUI zeilenweise anzeigen
- [ ] **C5**: Nachricht (user & assistant) in `insight.json > messages[]` speichern
- [ ] **C6**: Jede Message speichert: `role`, `content`, `timestamp`, `chunks[]`
- [ ] **C7**: GUI: Verlauf anzeigen mit Zeilenlimit (konfigurierbar)
- [ ] **C8**: Chatmarkierung bei Wrapups (nicht sichtbar, aber „Wrapup nach X“)

→ **Testbar:** Chat mit Streaming, Messages gespeichert, Verlauf ladbar.

---

## 📁 Sprint 3 – File Upload & Verwaltung im Insight

### ✅ Ziel: Dateien hochladen, registrieren, löschen

### EPIC 3: Filehandling

- [ ] **F1**: Upload-Control im „Files“-Container
- [ ] **F2**: Speicherung in `data/insights/{uuid}/{filename}`
- [ ] **F3**: Eintrag in `insight.json > files[]`: `{filename, size, mimetype, uploaded_at}`
- [ ] **F4**: FileID der Session hinzufügen (für Assistant)
- [ ] **F5**: GUI: Dateiliste anzeigen, Löschen einzelner Dateien
- [ ] **F6**: Backend: Datei aus Insight entfernen + Datei löschen

→ **Testbar:** Datei hochladen, Datei sehen, Datei löschen, JSON korrekt.

---

## 🧠 Sprint 4 – Wrapup & Knowledgebase

### ✅ Ziel: Manuelles Wrapup starten, Knowledge speichern

### EPIC 4: Wrapup & Knowledge

- [ ] **K1**: Button „Wrapup“ bei zu großer Session (Schwellenwert)
- [ ] **K2**: Wrapup durch Assistant: Zusammenfassung aller relevanten Erkenntnisse
- [ ] **K3**: Backend: Neues `wrapup`-Element erzeugen (Message + Kontext)
- [ ] **K4**: Speicherung in `insight.json > knowledge_base[]`
- [ ] **K5**: Neues Wrapup kombiniert altes + neue Inhalte
- [ ] **K6**: Wrapups sind unsichtbar für User, aber zählbar
- [ ] **K7**: GUI: Wrapup-Zähler mit Timestamp

→ **Testbar:** Wrapup erzeugbar, gespeichert, sichtbar als Statistik.

---

## 🛠️ Sprint 5 – Insight Admin Panel

### ✅ Ziel: Assistant verwalten, Konfiguration ändern

### EPIC 5: Admin-Panel

- [ ] **A1**: GUI: Admin-Ansicht unter `/insight-admin`
- [ ] **A2**: Formular zur Konfiguration von:
  - Model
  - System Prompt
  - Tools[]
  - Temperatur
  - Zeilenlimit
- [ ] **A3**: Anzeige der aktuellen Assistant-Konfiguration
- [ ] **A4**: Button „Assistant zurücksetzen“ → neue Assistant ID erzeugen
- [ ] **A5**: Backend: `config.json` speichern + validieren

→ **Testbar:** Konfiguration sichtbar, editierbar, Assistant zurücksetzbar.

---

## ✅ Sprint 6 – Stabilisierung & End2End-Test

### EPIC 6: Validierung & Tests

- [ ] **T1**: Insight anlegen, chatten, Datei hochladen, wrapup → End2End durchspielen
- [ ] **T2**: JSON-Validierung für `insight.json` (Schema: messages, files, knowledge_base)
- [ ] **T3**: Logging & Fehleranzeige bei fehlender Datei / defekter Assistant-Konfiguration
- [ ] **T4**: Cleanup-Script: Alte Dateien & leere Insights löschen
- [ ] **T5**: Tests für Assistant-Initialisierung

→ **Testbar:** Komplette Session mit Chat + File + Wrapup wiederverwendbar.

---

