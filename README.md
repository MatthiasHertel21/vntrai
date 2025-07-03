# 🚀 VNTRAI - Intelligent Agent System

**VNTRAI** is a modern Flask-based web application that provides an intelligent agent system with OpenAI integration, task management, and comprehensive tool ecosystem.

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

---

## 📋 Documentation Structure

This project uses a comprehensive documentation system organized as follows:

- **[📋 Backlog](./backlog.md)** - All requirements, features, and technical debt organized by function
- **[🗓️ Sprints](./sprints.md)** - Completed sprints history and project roadmap  
- **[📅 Current](./current.md)** - Current sprint status, incidents, tests, and daily activities
- **[📚 Documentation](./documentation.md)** - Technical architecture, rules, conventions, and component docs
- **[📖 README](./README.md)** - This file - project overview and quick start guide

---

## ✨ Key Features

### 🤖 **Agent System**
- **AI-Powered Agents**: Create and manage intelligent agents with OpenAI Assistant integration
- **Task Management**: Define and execute AI and tool-based tasks
- **Knowledge Base**: Persistent knowledge storage and retrieval
- **Agent Runs**: Track and monitor agent execution with detailed logging

### 🛠️ **Tools & Integrations**
- **Dynamic Tool System**: Create tools based on configurable integrations
- **13 Migrated Integrations**: Complete migration from v036 system
- **15 Production Tools**: Fully functional tool instances
- **Implementation Modules**: Pluggable API integration system (OpenAI, Google Sheets, etc.)

### 💬 **Insights & Chat**
- **Persistent Chat Interface**: Thread-based conversations with OpenAI Assistants
- **Real-time Streaming**: Live responses with quick actions
- **Chat History**: Complete conversation persistence and management
- **File Integration**: Upload and manage files within chat context

### 🎨 **Modern UI/UX**
- **Auto-Expand Sidebar**: Intelligent navigation with hover effects
- **Responsive Design**: Works seamlessly across all device sizes
- **Tailwind CSS**: Modern, utility-first styling
- **Dark/Light Themes**: Consistent color scheme and branding

### 🔧 **Developer Experience**
- **Docker Containerization**: Consistent development environment
- **Comprehensive Testing**: Manual and automated testing procedures
- **CSRF Security**: Complete security implementation
- **Blueprint Architecture**: Modular, maintainable code structure

---

## 🚀 Quick Start

### Prerequisites
- **Docker** and **Docker Compose**
- **Git** for repository management

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd vntrai
   ```

2. **Start the application:**
   ```bash
   sudo docker-compose up --build
   ```

3. **Access the application:**
   ```
   http://localhost:5004
   ```

4. **View logs (optional):**
   ```bash
   sudo docker-compose logs -f web
   ```

### Development Commands

```bash
# Start in background
sudo docker-compose up -d

# Restart after code changes
sudo docker-compose restart web

# Execute commands in container
sudo docker-compose exec web python3 script.py

# Stop and cleanup
sudo docker-compose down
```

---

## 📊 Project Status

### 📈 **Current Statistics** (July 2025)
- **Sprints Completed**: 17.5
- **Implementation Time**: ~24 days
- **Lines of Code**: 25,000+ LOC
- **Templates**: 40+ HTML templates
- **Backend Routes**: 85+ Flask routes
- **JavaScript Modules**: 18+ dynamic UI modules

### ✅ **Major Achievements**
- ✅ Complete v036 data migration (13 integrations, 15 tools, 12 icons)
- ✅ Agent system with OpenAI Assistant integration
- ✅ Persistent chat interface with streaming responses
- ✅ Task management revolution (Sprint 18)
- ✅ Modern UI/UX with Tailwind CSS
- ✅ Comprehensive testing system
- ✅ Production-ready Docker deployment

### 🎯 **Current Sprint**: Sprint 18 - Task Management Revolution
**Focus**: Advanced task management, agent enhancement, and demo preparation  
**Progress**: ~40% complete  
**Key Features**: Task editor integration, tool-agent bridge, agent run state management

---

## 🏗️ System Architecture

### **Core Components**
```
VNTRAI System
├── 🤖 Agent Management      # AI agents with tasks and knowledge
├── 🛠️ Tools & Integrations  # Configurable tool ecosystem  
├── 💬 Chat & Insights       # Persistent AI conversations
├── 📊 Implementation Modules # API integration layer
├── 🧪 Testing System        # Comprehensive testing suite
└── 📚 Documentation        # Complete project documentation
```

### **Technology Stack**
- **Backend**: Flask (Python 3.9+)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Storage**: JSON file-based persistence
- **Containerization**: Docker & Docker Compose
- **AI Integration**: OpenAI Assistant API v2
- **Security**: Flask-WTF CSRF protection

### **Data Architecture**
```
data/
├── agents/          # Agent configurations (UUID-based)
├── tools/           # Tool instances and configurations
├── integrations/    # Integration definitions
├── agentrun/        # Agent execution states
└── agentlogs/       # Detailed execution logs
```

---

## 🧭 Navigation Guide

### **For Users**
- Start with **[Current Sprint](./current.md)** to see what's happening now
- Check **[Backlog](./backlog.md)** for planned features and requirements
- Review **[Sprints](./sprints.md)** for project history and roadmap

### **For Developers**
- Read **[Documentation](./documentation.md)** for technical guidelines and architecture
- Follow development rules and conventions outlined in the documentation
- Use Docker for all development and migration activities

### **For Project Managers**
- Monitor **[Current Sprint](./current.md)** for progress and blockers
- Review **[Sprints](./sprints.md)** for velocity and planning insights
- Track requirements in **[Backlog](./backlog.md)**

---

## 🤝 Contributing

### **Development Workflow**
1. Read the **[Documentation](./documentation.md)** for coding standards
2. Check **[Current Sprint](./current.md)** for active work
3. Follow the established patterns and conventions
4. Test changes in Docker environment
5. Update documentation as needed

### **Key Guidelines**
- ⚠️ **All scripts must run in Docker container** (not on host system)
- 🔒 **CSRF tokens required** for all forms and AJAX requests
- 📝 **Document new features** in appropriate documentation files
- 🧪 **Test thoroughly** before marking features as complete
- 🎨 **Follow UI/UX patterns** established in the system

---

## 📞 Support & Resources

### **Getting Help**
- Check **[Documentation](./documentation.md)** for technical questions
- Review **[Current Sprint](./current.md)** for known issues
- Look at **[Sprints](./sprints.md)** for historical context

### **Development Resources**
- **Docker Commands**: See [Documentation](./documentation.md#docker--deployment)
- **API Testing**: Use the built-in testing system at `/test`
- **Security Guidelines**: Follow CSRF and validation rules in documentation
- **UI Patterns**: Reference existing templates and Tailwind CSS classes

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 🔗 Links

- **Application**: http://localhost:5004 (when running)
- **Test Interface**: http://localhost:5004/test
- **Agent Management**: http://localhost:5004/agents
- **Tools & Integrations**: http://localhost:5004/tools, http://localhost:5004/integrations
- **Insights Chat**: http://localhost:5004/insights

---

*For detailed information about any aspect of the system, please refer to the appropriate documentation file linked above.*
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

# Anwendung starten (über Docker)
sudo docker-compose exec web python run.py
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
