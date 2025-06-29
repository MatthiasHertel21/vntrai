# Backlog

ich möchte in der anwendung die funktionalität für tools und für integrations haben wie in der anwendung im verzeichnis v036, aber mit einigenen änderungen:

tailwind layout
die datenhaltung für alle integrations soll nicht in einer datei "integrations,json" erfolgen sondern jede integration soll ihre eigene json datei haben. diese soll so heißen wie die uuid der integration und in einem verezeichnis "integrations" liegen
die datenhaltung für alle tools soll nicht in einer datei "tools,json" erfolgen sondern jedes tools soll seine eigene json datei haben. diese soll so heißen wie die uuid des tools und in einem verezeichnis "tools" liegen

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