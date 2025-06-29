# VNTRAI - Web Application

VNTRAI ist eine moderne Webanwendung basierend auf Flask und Docker, die eine intelligente Sidebar mit Auto-Expand/Collapse-Funktionalität bietet.

## Features

- ✅ **Flask-basierte Webanwendung** mit modularer Struktur
- ✅ **Docker & Docker-Compose** für einfache Entwicklung und Deployment
- ✅ **Auto-Expand/Collapse Sidebar** - Icons im kollabierten Zustand, Icons + Text im expandierten Zustand
- ✅ **Responsive Design** mit Tailwind CSS und Bootstrap Icons
- ✅ **Context Area** mit Toggle-Funktionalität
- ✅ **Moderne UI** basierend auf bewährtem v036 Design
- ✅ **Port 5004** Konfiguration

## Quick Start

### Voraussetzungen

- Docker
- Docker Compose

### Installation

1. **Repository klonen:**
   ```bash
   cd /home/ga/fb1/age
   ```

2. **Anwendung starten:**
   ```bash
   docker-compose up --build
   ```

3. **Anwendung öffnen:**
   ```
   http://localhost:5004
   ```

## Projektstruktur

```
vntrai/
├── app/
│   ├── __init__.py              # Flask App Factory
│   ├── config.py                # Konfiguration
│   ├── routes/
│   │   └── main.py              # Hauptrouten
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Haupt-Stylesheet
│   │   ├── js/
│   │   │   └── main.js          # JavaScript-Funktionen
│   │   ├── icons/               # Icon-Sammlung von v036
│   │   └── image/               # VNTRAI Logo und Bilder
│   └── templates/
│       ├── base.html            # Basis-Template
│       ├── index.html           # Dashboard
│       └── *.html               # Weitere Seiten
├── docker-compose.yml           # Docker-Compose Konfiguration
├── Dockerfile                   # Docker-Image Definition
├── requirements.txt             # Python-Abhängigkeiten
├── run.py                       # Flask-Anwendungsstart
└── README.md                    # Diese Datei
```

## Design & Features

### Sidebar-Funktionalität
- **Auto-Expand**: Sidebar erweitert sich automatisch beim Hover
- **Auto-Collapse**: Sidebar kollabiert automatisch beim Verlassen
- **Icons Only**: Im kollabierten Zustand werden nur Icons angezeigt
- **Icons + Text**: Im expandierten Zustand werden Icons mit Beschriftung angezeigt

### Farbschema (von v036 übernommen)
- **Hauptfarbe**: #0CC0DF (Türkis)
- **Sidebar**: Dunkelgrauer Gradient mit weißen Icons/Text
- **Hover-Effekte**: Icons wechseln von weiß zu schwarz
- **Background**: #ffffff für Content-Bereiche

### Navigation
- Dashboard
- My Insights
- My Workflows
- Tools
- Integrations
- Profile
- Company

### Context Area
- **Toggle-Button** in der Sidebar
- **Expand/Collapse** mit smooth Animationen
- **LocalStorage** für persistente Zustandsspeicherung

## Entwicklung

### Docker Commands

```bash
# Anwendung starten
docker-compose up

# Anwendung mit Rebuild starten
docker-compose up --build

# Anwendung im Hintergrund starten
docker-compose up -d

# Anwendung stoppen
docker-compose down

# Logs anzeigen
docker-compose logs -f
```

### Lokale Entwicklung

```bash
# Python-Umgebung aktivieren
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate   # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
python run.py
```

## Technologie-Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **CSS Framework**: Tailwind CSS
- **Icons**: Bootstrap Icons
- **Containerization**: Docker & Docker-Compose
- **Port**: 5004

## Sprint 1 - Completed ✅

- [x] Docker-Compose Setup erstellen (basierend auf v036/docker-compose.yml)
- [x] Flask-Grundstruktur implementieren (app/__init__.py, config.py, run.py)
- [x] Ordnerstruktur von v036 übernehmen (app/templates/, app/static/, app/routes/)
- [x] Tailwind CSS integrieren + Bootstrap Icons
- [x] Basis-HTML-Template erstellen (base.html mit vntr-layout-wrapper)
- [x] Port 5004 konfigurieren
- [x] VNTRAI Logo und Branding Assets übertragen
- [x] README.md mit Setup-Anweisungen

## Nächste Schritte (Sprint 2)

- [ ] Sidebar HTML-Struktur von v036 vollständig übernehmen
- [ ] Auto-Expand/Collapse JavaScript implementieren
- [ ] Context Area Toggle Button funktional machen
- [ ] Hover-Animationen (weiß → schwarz bei Icons) optimieren
- [ ] Responsive Design für verschiedene Bildschirmgrößen

## Support

Bei Fragen oder Problemen wenden Sie sich an das Entwicklungsteam.

---

**VNTRAI** - Powered by Flask & Docker
