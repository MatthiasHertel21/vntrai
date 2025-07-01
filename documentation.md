# 📚 VNTRAI System Documentation

This document contains comprehensive technical documentation, architecture guidelines, and development conventions for the VNTRAI Flask/Docker agent system.

---

## 🏗️ System Architecture

### Core Components

#### Flask Application Structure
```
app/
├── __init__.py              # Flask app factory
├── config.py               # Configuration management
├── routes/                 # Blueprint-based routing
│   ├── main.py            # Main routes
│   ├── agents.py          # Agent management
│   ├── assistants.py      # AI assistant integration
│   ├── integrations.py    # Integration management
│   ├── tools.py           # Tool management
│   ├── tasks.py           # Task management
│   └── test.py            # Testing interface
├── utils/                 # Utility modules
│   ├── data_manager.py    # Data persistence layer
│   ├── validation.py      # Data validation
│   └── helpers.py         # Helper functions
├── implementation_modules/ # API implementations
│   ├── base_implementation.py
│   ├── openai_chatcompletion.py
│   ├── openai_assistant_api.py
│   └── google_sheets.py
├── static/                # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript modules
│   ├── images/           # Images and icons
│   └── vendor/           # Third-party assets
└── templates/            # Jinja2 templates
    ├── base.html         # Base template
    ├── agents/           # Agent templates
    ├── integrations/     # Integration templates
    ├── tools/            # Tool templates
    └── assistants/       # Assistant templates
```

#### Data Storage Architecture
```
data/
├── agents/               # Agent definitions
│   └── {uuid}.json      # Individual agent files
├── integrations/         # Integration definitions
│   └── {uuid}.json      # Individual integration files
├── tools/               # Tool configurations
│   └── {uuid}.json      # Individual tool files
├── agentrun/            # Agent execution states
│   └── {uuid}.json      # Agent run instances
└── agentlogs/           # Execution logs
    └── {uuid}/          # Per-agent log directories
```

### Key Design Principles

1. **UUID-Based Storage**: All entities use UUIDs for unique identification
2. **JSON File Persistence**: Simple file-based storage for configuration data
3. **Blueprint Architecture**: Modular route organization
4. **Template Inheritance**: Consistent UI through base template system
5. **Implementation Modules**: Pluggable API integration system

---

## 🔧 Development Rules & Conventions

### Code Style Guidelines

#### Python Conventions
```python
# Function naming: snake_case
def validate_agent_data(agent_data):
    pass

# Class naming: PascalCase
class AgentManager:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_TASK_COUNT = 100

# File naming: snake_case.py
# Example: data_manager.py, openai_assistant_api.py
```

#### Template Conventions
```html
<!-- Template naming: lowercase.html -->
<!-- Example: agents/edit.html, tools/create.html -->

<!-- Block structure -->
{% extends "base.html" %}
{% block title %}Page Title{% endblock %}
{% block content %}
    <!-- Page content -->
{% endblock %}

<!-- CSRF tokens (required for all forms) -->
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
```

#### JavaScript Conventions
```javascript
// Function naming: camelCase
function toggleSidebar() {}

// Variable naming: camelCase
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Global variables: window object
window.csrfToken = csrfToken;
```

### Security Guidelines

#### CSRF Protection
**Mandatory for all forms and AJAX requests**

```html
<!-- HTML Forms -->
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
    <!-- form fields -->
</form>

<!-- Meta tag for JavaScript access -->
<meta name="csrf-token" content="{{ csrf_token() }}">
```

```javascript
// AJAX requests
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': window.csrfToken
    },
    body: JSON.stringify(data)
});
```

#### Input Validation
```python
# Backend validation (required)
def validate_agent_data(data):
    """Validate and sanitize agent data"""
    required_fields = ['name', 'category', 'description']
    for field in required_fields:
        if field not in data or not data[field].strip():
            raise ValueError(f"Missing required field: {field}")
    
    # Sanitize inputs
    data['name'] = data['name'].strip()[:100]
    return data

# Frontend validation (recommended)
function validateForm(formData) {
    if (!formData.name || formData.name.trim().length === 0) {
        throw new Error('Name is required');
    }
    return true;
}
```

---

## 📋 Component Documentation

### Data Manager Classes

#### AgentsManager
**Purpose**: Manage agent CRUD operations and data persistence

```python
class AgentsManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir
    
    def create_agent(self, agent_data):
        """Create new agent with UUID"""
        pass
    
    def get_agent(self, uuid):
        """Retrieve agent by UUID"""
        pass
    
    def update_agent(self, uuid, agent_data):
        """Update existing agent"""
        pass
    
    def delete_agent(self, uuid):
        """Delete agent and associated data"""
        pass
    
    def list_agents(self, filters=None):
        """List agents with optional filtering"""
        pass
```

**Key Methods**:
- `create_agent()`: Generates UUID, validates data, saves to file
- `get_agent()`: Loads and returns agent data by UUID
- `update_agent()`: Validates and updates existing agent
- `delete_agent()`: Removes agent file and references
- `list_agents()`: Returns filtered list of agents

#### ToolsManager
**Purpose**: Manage tool configurations and execution

```python
class ToolsManager:
    def test_tool(self, tool_uuid, test_params=None):
        """Test tool configuration"""
        pass
    
    def execute_tool(self, tool_uuid, execution_params):
        """Execute tool with parameters"""
        pass
    
    def get_tools_by_integration(self, integration_uuid):
        """Get tools for specific integration"""
        pass
```

#### IntegrationsManager
**Purpose**: Manage integration definitions and metadata

```python
class IntegrationsManager:
    def validate_integration_schema(self, integration_data):
        """Validate integration against schema"""
        pass
    
    def get_integration_by_name(self, name):
        """Find integration by name"""
        pass
```

### Implementation Modules System

#### Base Implementation
```python
class BaseImplementation:
    def __init__(self, config):
        self.config = config
    
    def execute(self, params):
        """Execute implementation with parameters"""
        raise NotImplementedError("Must implement execute method")
    
    def test_connection(self):
        """Test implementation connection"""
        raise NotImplementedError("Must implement test_connection method")
    
    def validate_config(self, config):
        """Validate implementation configuration"""
        return True
```

#### OpenAI ChatCompletion Implementation
```python
class OpenAIChatCompletionImplementation(BaseImplementation):
    def execute(self, params):
        """Execute OpenAI chat completion"""
        # Implementation details
        pass
    
    def test_connection(self):
        """Test OpenAI API connection"""
        # Test implementation
        pass
```

### UI Components

#### Sidebar Navigation
**Structure**:
```html
<div class="vntr-sidebar">
    <div class="vntr-nav-items">
        <a href="/" class="vntr-nav-item">
            <img src="/static/icons/dashboard.png" alt="Dashboard">
            <span>Dashboard</span>
        </a>
        <!-- Additional nav items -->
    </div>
</div>
```

**Behavior**:
- Auto-expand on hover
- Active state highlighting
- Responsive collapse on mobile

#### Dynamic Forms
**Pattern for integration/tool parameters**:
```html
<!-- Text input -->
<div class="form-group">
    <label for="{{ param.name }}">{{ param.label }}</label>
    <input type="text" 
           id="{{ param.name }}" 
           name="{{ param.name }}"
           value="{{ param.default or '' }}"
           {% if param.required %}required{% endif %}>
</div>

<!-- Select dropdown -->
<div class="form-group">
    <label for="{{ param.name }}">{{ param.label }}</label>
    <select id="{{ param.name }}" name="{{ param.name }}">
        {% for option in param.options %}
        <option value="{{ option.value }}">{{ option.label }}</option>
        {% endfor %}
    </select>
</div>
```

---

## 🎨 UI/UX Guidelines

### Color Scheme
```css
:root {
    --primary-color: #0CC0DF;      /* Cyan/Turquoise */
    --accent-color: #FA7100;       /* Orange */
    --success-color: #10B981;      /* Green */
    --error-color: #EF4444;        /* Red */
    --warning-color: #F59E0B;      /* Yellow */
    --neutral-color: #6B7280;      /* Gray */
    --background-color: #FFFFFF;   /* White */
}
```

### Typography
```css
/* Headings */
h1 { font-size: 2rem; font-weight: 700; }
h2 { font-size: 1.5rem; font-weight: 600; }
h3 { font-size: 1.25rem; font-weight: 600; }

/* Body text */
body { font-size: 1rem; line-height: 1.5; }
.text-sm { font-size: 0.875rem; }
.text-xs { font-size: 0.75rem; }
```

### Button Styles
```css
/* Primary button */
.btn-primary {
    @apply bg-cyan-500 hover:bg-cyan-600 text-white px-4 py-2 rounded;
}

/* Secondary button */
.btn-secondary {
    @apply bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded;
}

/* Danger button */
.btn-danger {
    @apply bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded;
}
```

### Layout Patterns

#### Two-Column Layout
```html
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div class="space-y-6">
        <!-- Left column content -->
    </div>
    <div class="space-y-6">
        <!-- Right column content -->
    </div>
</div>
```

#### Card Layout
```html
<div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Card Title</h3>
        <div class="flex space-x-2">
            <!-- Action buttons -->
        </div>
    </div>
    <div class="card-content">
        <!-- Card content -->
    </div>
</div>
```

---

## 🚀 Docker & Deployment

### Docker Configuration

#### docker-compose.yml
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5004:5004"
    volumes:
      - ./data:/app/data
      - ./app:/app/app
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    command: python run.py
```

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5004

CMD ["python", "run.py"]
```

### Development Workflow

#### Container Management
```bash
# Start development environment
sudo docker-compose up -d

# View logs
sudo docker-compose logs -f web

# Execute commands in container
sudo docker-compose exec web python3 script.py

# Restart after code changes
sudo docker-compose restart web

# Stop and cleanup
sudo docker-compose down
```

#### Migration Scripts
**CRITICAL**: All migration and management scripts must run in Docker container

```bash
# ✅ CORRECT: Run in Docker container
sudo docker-compose exec web python3 -c "
import sys; sys.path.append('/app')
from migration_script import migrate_data
migrate_data()
"

# ❌ WRONG: Direct execution on host
python3 migration_script.py
```

**Reasons for Docker requirement**:
1. **File Permissions**: Host system has different user IDs than container
2. **Python Environment**: Correct library versions and dependencies
3. **Path Mapping**: `/app` path only available in container
4. **Database Access**: Files only reachable in container volume

---

## 📊 Data Schemas

### Agent Schema
```json
{
    "uuid": "string (UUID)",
    "name": "string (required)",
    "category": "string (required)",
    "description": "string",
    "use_as": "agent|insight",
    "status": "active|inactive",
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime",
    "ai_assistant": {
        "assistant_id": "string",
        "model": "string",
        "instructions": "string",
        "tools": ["array of tool configs"],
        "files": ["array of file IDs"]
    },
    "tasks": [
        {
            "uuid": "string",
            "name": "string",
            "type": "ai|tool",
            "description": "string",
            "ai_config": {
                "instructions": "string",
                "goals": ["array of strings"],
                "input_fields": ["array of field configs"]
            },
            "tool_config": {
                "tool_uuid": "string",
                "parameters": "object"
            }
        }
    ],
    "knowledge_base": ["array of knowledge items"],
    "metadata": {
        "version": "string",
        "migration_notes": "string"
    }
}
```

### Integration Schema
```json
{
    "uuid": "string (UUID)",
    "name": "string (required)",
    "description": "string",
    "vendor": "string",
    "icon_url": "string",
    "category": "string",
    "version": "string",
    "config_params": [
        {
            "name": "string",
            "label": "string",
            "type": "text|select|boolean|json",
            "required": "boolean",
            "default": "any",
            "options": ["array for select type"]
        }
    ],
    "input_params": ["array of param configs"],
    "output_params": ["array of param configs"],
    "metadata": {
        "created_at": "ISO datetime",
        "updated_at": "ISO datetime"
    }
}
```

### Tool Schema
```json
{
    "uuid": "string (UUID)",
    "name": "string (required)",
    "description": "string",
    "integration_uuid": "string (required)",
    "config": "object (integration-specific)",
    "status": "connected|not_connected|error",
    "options": {
        "assistant": "boolean (default: false)"
    },
    "test_results": {
        "last_test": "ISO datetime",
        "status": "success|failure",
        "message": "string"
    },
    "metadata": {
        "created_at": "ISO datetime",
        "updated_at": "ISO datetime"
    }
}
```

---

## 🧪 Testing Guidelines

### Manual Testing Procedures

#### Test Plan Structure
```markdown
## Test Plan: [Feature Name]
**Goal**: [Description of functionality to test]

### Test Steps:
1. **Setup**: [Prerequisites]
2. **Step 1**: [Detailed instructions]
   - Expected Result: [What should happen]
3. **Step 2**: [Next action]
   - Expected Result: [What should happen]

### Acceptance Criteria:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

### Error Cases:
- [ ] [Error scenario 1]
- [ ] [Error scenario 2]
```

#### Testing Workflow
1. **Developer** creates detailed test plans
2. **User** executes tests manually and documents results
3. **Feedback loop** for quick iteration
4. **Critical workflows** tested first

### API Testing

#### Tool Testing
```python
# Test tool configuration
response = client.post(f'/tools/{tool_uuid}/test', 
                      json=test_params,
                      headers={'X-CSRFToken': csrf_token})

# Verify response
assert response.status_code == 200
assert response.json['status'] == 'success'
```

#### Integration Testing
```python
# Test integration creation
integration_data = {
    'name': 'Test Integration',
    'description': 'Test description',
    'vendor': 'Test Vendor'
}

response = client.post('/integrations/create',
                      data=integration_data,
                      headers={'X-CSRFToken': csrf_token})

assert response.status_code == 302  # Redirect after success
```

---

## 🔍 Debugging & Troubleshooting

### Common Issues

#### CSRF Token Problems
**Symptoms**: "Bad Request - The CSRF token is missing"
**Diagnosis**:
1. Check browser console for JavaScript errors
2. Verify CSRF token in network requests
3. Look for visible `{{ csrf_token() }}` in rendered HTML

**Solutions**:
```html
<!-- Ensure hidden input, not visible text -->
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />

<!-- Add meta tag for JavaScript -->
<meta name="csrf-token" content="{{ csrf_token() }}">
```

#### Docker Permission Issues
**Symptoms**: File access errors, permission denied
**Solution**: Always run scripts in Docker container:
```bash
sudo docker-compose exec web python3 script.py
```

#### Template Rendering Issues
**Symptoms**: Missing blocks, broken layout
**Diagnosis**: Check template inheritance and block structure
**Solution**: Ensure proper `{% extends %}` and `{% block %}` usage

### Logging & Monitoring

#### Application Logs
```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Agent created: {agent_uuid}")
logger.error(f"Failed to save agent: {error}")
```

#### Debug Mode
```python
# Enable debug mode in development
app.debug = True

# Use Flask debug toolbar for detailed debugging
from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)
```

---

## 📈 Performance Guidelines

### Frontend Optimization

#### JavaScript Performance
```javascript
// Debounce search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Use for search inputs
const debouncedSearch = debounce(performSearch, 300);
```

#### CSS Optimization
```css
/* Use efficient selectors */
.btn-primary { /* Good */ }
div > span > a.link { /* Avoid deep nesting */ }

/* Minimize reflows */
.transform { will-change: transform; }
.fade { transition: opacity 0.3s ease; }
```

### Backend Optimization

#### Data Loading
```python
# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=100)
def get_integration_by_uuid(uuid):
    # Expensive operation
    return load_integration(uuid)

# Batch operations when possible
def get_multiple_agents(uuids):
    return [get_agent(uuid) for uuid in uuids]
```

#### Database Queries
```python
# Minimize file I/O operations
def list_agents_with_cache():
    # Load all agents once, filter in memory
    all_agents = load_all_agents()
    return filter_agents(all_agents, criteria)
```

---

This documentation serves as the comprehensive reference for VNTRAI system development, covering architecture, conventions, components, and best practices. It should be updated regularly as the system evolves.
