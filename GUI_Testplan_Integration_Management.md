# GUI Testplan: Integration Management
**Ziel**: Vollständige Funktionalität der Integration-Verwaltung testen (CRUD-Operationen, UI-Komponenten, v036-Format-Kompatibilität)

## Vorbedingungen:
- Docker-Container läuft auf Port 5004
- Browser geöffnet auf http://localhost:5004
- Mindestens 1 bestehende Integration vorhanden

## Test-Schritte:

### 1. Navigation zur Integrations-Seite
**Schritt 1**: Klick auf "Integrations" in der Sidebar
- **Erwartetes Ergebnis**: Integrations-Liste wird geladen, Überschrift "Integrations" und Toolbar mit "Export" + "New Integration" Buttons sind sichtbar
- **Tatsächliches Ergebnis**: [Vom User auszufüllen]

### 2. Integrations-Liste anzeigen
**Schritt 2**: Überprüfe die Darstellung der Integrations-Liste
- **Erwartetes Ergebnis**: 
  - Tabelle mit alternierenden Zeilenfarben
  - Spalten: Name, Vendor, Type, Status, Actions
  - Icons werden korrekt angezeigt
  - Suchfeld und Filter sind vorhanden
- **Tatsächliches Ergebnis**: [Vom User auszufüllen]

### 3. Neue Integration erstellen
**Schritt 3**: Klick auf "New Integration" Button
- **Erwartetes Ergebnis**: Create-Formular öffnet sich mit Feldern: Name, Vendor, Type, Description, Icon-Upload
- **Tatsächliches Ergebnis**: [Vom User auszufüllen]

**Schritt 4**: Ausfüllen des Create-Formulars
- Name: "Test Integration"
- Vendor: "Test Vendor" 
- Type: "api"
- Description: "Test integration for GUI testing"
- **Erwartetes Ergebnis**: Alle Felder sind ausfüllbar, Validierung funktioniert
- **Tatsächliches Ergebnis**: [Vom User auszufüllen]

**Schritt 5**: Formular absenden
- **Erwartetes Ergebnis**: 
  - Success-Message wird angezeigt
  - Weiterleitung zur Integration-Detail-Seite
  - Integration erscheint in der Liste
- **Tatsächliches Ergebnis**: [Vom User auszufüllen]

### 4. Integration anzeigen (View)
**Schritt 6**: Klick auf eine Integration in der Liste
- **Erwartetes Ergebnis**: 
  - Detail-Seite öffnet sich
  - v036-Format-Felder werden angezeigt: config_params, input_params, output_params
  - Edit/Delete Buttons sind vorhanden
- **Tatsächliches Ergebnis**: [Vom User auszufüllen]

### 5. Integration bearbeiten (Edit)
**Schritt 7**: Klick auf "Edit" Button in der Detail-Ansicht
- **Erwartetes Ergebnis**: Edit-Formular öffnet sich mit vorausgefüllten Daten
- **Tatsächliches Ergebnis**: [Vom User auszufüllen]

**Schritt 8**: Änderung vornehmen (z.B. Description ändern)
- **Erwartetes Ergebnis**: Änderungen werden gespeichert, Success-Message angezeigt
- **Tatsächliches Ergebnis**: [Vom User auszufüllen]

### 6. Integration löschen (Delete)
**Schritt 9**: Klick auf "Delete" Button (bei Test-Integration)
- **Erwartetes Ergebnis**: 
  - Bestätigungs-Dialog oder direktes Löschen
  - Integration verschwindet aus der Liste
  - Success-Message wird angezeigt
- **Tatsächliches Ergebnis**: [Vom User auszufüllen]

## Acceptance Criteria:
- [ ] Überschrift und Toolbar sind auf Integrations-Seite sichtbar
- [ ] "New Integration" Button funktioniert und öffnet Create-Formular
- [ ] Integration kann erfolgreich erstellt werden
- [ ] Integration-Details werden mit v036-Format angezeigt (config_params, input_params, output_params)
- [ ] Integration kann bearbeitet werden
- [ ] Integration kann gelöscht werden
- [ ] Alle CRUD-Operationen zeigen entsprechende Success/Error-Messages
- [ ] Navigation zwischen Listen-, Detail- und Edit-Ansicht funktioniert

## Error Cases:
- [ ] Leere Pflichtfelder beim Erstellen - Status: [Pass/Fail/Not Tested]
- [ ] Ungültige JSON-Daten - Status: [Pass/Fail/Not Tested]
- [ ] Nicht existierende Integration aufrufen - Status: [Pass/Fail/Not Tested]
- [ ] CSRF-Token-Fehler bei POST-Requests - Status: [Pass/Fail/Not Tested]

## UI/UX Checks:
- [ ] Buttons haben korrekte Farben (türkis für primary, grau für secondary)
- [ ] Flash-Messages sind nicht breiter als Container
- [ ] Alternierende Zeilenfarben in Tabelle
- [ ] Klick auf Tabellenzeile öffnet Integration-Details
- [ ] Responsive Design funktioniert auf verschiedenen Bildschirmgrößen

## Test-Ergebnis:
- **Status**: [Pass/Fail/Partial]
- **Gefundene Issues**: [Liste der Probleme]
- **Feedback**: [User-Feedback für Verbesserungen]

---
**Testplan erstellt am**: 29. Juni 2025  
**Getestet von**: [User Name]  
**Getestet am**: [Datum]
