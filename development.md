# Backlog
ich möchte eine webanwendung entwickeln mit flask und docker-compose
die anwendung soll auf den port 5004 laufen
verwende tailwind layout 
ich möchte links eine sidebar mit auto-expand / auto collaps funktion (im collapsed zustand nur icons, im expanded status icons mit beschriftung)
die anwendung soll vntrai heißen
übernimm die den aufbau der sidebar, die icons und die farben aus der anwendung /home/ga/fb1/age/v036

# Sprints

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
- [ ] Flask-Routes für alle Sidebar-Menüpunkte erstellen
- [ ] Template-Struktur erweitern (Dashboard, Insights, Tools etc.)
- [ ] Active-State für Navigation implementieren
- [ ] Breadcrumb-System implementieren (wie v036)
- [ ] Error-Handling für 404/500 Seiten
- [ ] URL-Struktur definieren
- [ ] Template-Vererbung optimieren

**Definition of Done:**
- Alle Sidebar-Links führen zu funktionsfähigen Seiten
- Active-State wird korrekt angezeigt
- Breadcrumbs funktionieren
- Error-Pages sind implementiert

## Sprint 4: Content Areas und Layout-Finalisierung (4-5 Tage)
### Ziel: Vollständiges Layout mit Context Area und Content Bereich

**User Stories:**
- Als Benutzer möchte ich eine Context Area sehen, die sich ein-/ausblenden lässt
- Als Benutzer möchte ich einen responsiven Content-Bereich haben
- Als Benutzer möchte ich Flash-Messages sehen können

**Tasks:**
- [ ] Context Area implementieren (vntr-context-area aus v036)
- [ ] Content Area Layout (vntr-content-area)
- [ ] Context Area Expand/Collapse Button
- [ ] LocalStorage für Context Area State
- [ ] Flash-Messages System
- [ ] Mobile Responsiveness optimieren
- [ ] Layout-Container (vntr-main-container, vntr-content-context-container)
- [ ] Smooth Animationen für alle Übergänge

**Definition of Done:**
- Context Area funktioniert wie in v036
- Layout ist vollständig responsive
- Alle Animationen sind smooth
- Flash-Messages funktionieren

## Sprint 5: Erweiterte Features und Polish (3-4 Tage)
### Ziel: Zusätzliche Features und Code-Qualität

**User Stories:**
- Als Benutzer möchte ich eine konsistente und performante Anwendung
- Als Entwickler möchte ich sauberen, dokumentierten Code haben

**Tasks:**
- [ ] Performance-Optimierungen
- [ ] Code-Dokumentation vervollständigen
- [ ] Unit Tests implementieren
- [ ] Logging konfigurieren
- [ ] Security-Headers implementieren
- [ ] CSS/JS Minification
- [ ] Docker-Image optimieren
- [ ] Deployment-Dokumentation

**Definition of Done:**
- Code ist gut dokumentiert und getestet
- Performance ist optimiert
- Sicherheitsstandards erfüllt
- Deployment-ready

## Technische Spezifikationen basierend auf v036

### Farbschema:
- **Hauptfarbe:** #0CC0DF (Türkis)
- **Sidebar:** Dunkler Hintergrund mit weißen Icons/Text
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

## Backlog für zukünftige Sprints
- Content für Dashboard, Insights, Tools Pages
- Authentifizierung/Login-System
- Datenbankintegration
- API-Endpunkte
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