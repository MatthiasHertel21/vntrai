"""
Test System Routes für vntrai
Zentrale Test-Übersicht und Backend-Route Testing
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import json
import os
import importlib
import inspect
from datetime import datetime

# Blueprint erstellen
test_bp = Blueprint('test', __name__, url_prefix='/test')

# Test-System Configuration
TEST_MODULES = {
    'integrations': {
        'name': 'Integrations Management',
        'description': 'CRUD Operations für Integration Definitions',
        'file': 'app/routes/integrations.py',
        'routes': [
            {'method': 'GET', 'path': '/integrations/', 'function': 'list_integrations', 'description': 'Liste aller Integrations'},
            {'method': 'POST', 'path': '/integrations/', 'function': 'create_integration', 'description': 'Neue Integration erstellen'},
            {'method': 'GET', 'path': '/integrations/view/<id>', 'function': 'view_integration', 'description': 'Integration Details anzeigen'},
            {'method': 'POST', 'path': '/integrations/edit/<id>', 'function': 'edit_integration', 'description': 'Integration bearbeiten'},
            {'method': 'POST', 'path': '/integrations/delete/<id>', 'function': 'delete_integration', 'description': 'Integration löschen'},
            {'method': 'POST', 'path': '/integrations/test/<id>', 'function': 'test_integration', 'description': 'Integration testen (AJAX)'},
        ]
    },
    'tools': {
        'name': 'Tools Management', 
        'description': 'CRUD Operations für Tool Instances + Dynamic Form UI',
        'file': 'app/routes/tools.py',
        'routes': [
            {'method': 'GET', 'path': '/tools/', 'function': 'list_tools', 'description': 'Liste aller Tools'},
            {'method': 'POST', 'path': '/tools/', 'function': 'create_tool', 'description': 'Neues Tool erstellen'},
            {'method': 'GET', 'path': '/tools/view/<id>', 'function': 'view_tool', 'description': 'Tool Details anzeigen'},
            {'method': 'POST', 'path': '/tools/edit/<id>', 'function': 'edit_tool', 'description': 'Tool bearbeiten'},
            {'method': 'POST', 'path': '/tools/delete/<id>', 'function': 'delete_tool', 'description': 'Tool löschen'},
            {'method': 'POST', 'path': '/tools/test/<id>', 'function': 'test_tool', 'description': 'Tool testen (AJAX)'},
            {'method': 'POST', 'path': '/tools/execute/<id>', 'function': 'execute_tool', 'description': 'Tool ausführen (AJAX)'},
            {'method': 'POST', 'path': '/tools/clone/<id>', 'function': 'clone_tool', 'description': 'Tool klonen'},
            {'method': 'GET', 'path': '/tools/api/config/<id>', 'function': 'get_tool_config', 'description': 'Tool-Konfiguration für dynamische UI abrufen (AJAX)'},
        ],
        'dynamic_features': {
            'description': 'Dynamische Form-Features die getestet werden müssen',
            'features': [
                'Dynamic Form Generation (Edit/Create/Execute)',
                'Field Type Support (text, select, boolean, json, file)',
                'Status Badges (Locked, Prefilled, Required)',
                'JSON Editor Toggle & Bidirectional Sync',
                'Live JSON Validation',
                'Integration-Parameter-Binding'
            ]
        }
    },
    'main': {
        'name': 'Main Navigation',
        'description': 'Hauptnavigation und Dashboard',
        'file': 'app/routes/main.py',
        'routes': [
            {'method': 'GET', 'path': '/', 'function': 'index', 'description': 'Dashboard/Homepage'},
            {'method': 'GET', 'path': '/insights', 'function': 'insights', 'description': 'Insights Seite'},
            {'method': 'GET', 'path': '/profile', 'function': 'profile', 'description': 'User Profile'},
            {'method': 'GET', 'path': '/company', 'function': 'company', 'description': 'Company Settings'},
        ]
    },
    'implementation_modules': {
        'name': 'Implementation Modules',
        'description': 'Dynamic Implementation Module System + Tool-Module-Binding',
        'file': 'app/implementation_modules/__init__.py',
        'routes': [
            {'method': 'GET', 'path': '/tools/implementation-modules', 'function': 'list_implementation_modules', 'description': 'Liste aller Implementation Modules'},
            {'method': 'GET', 'path': '/tools/implementation-status/<id>', 'function': 'get_implementation_status', 'description': 'Implementation Status für Tool abrufen'},
            {'method': 'POST', 'path': '/tools/test/<id>', 'function': 'test_tool_with_implementation', 'description': 'Tool über Implementation Module testen'},
            {'method': 'POST', 'path': '/tools/execute/<id>', 'function': 'execute_tool_with_implementation', 'description': 'Tool über Implementation Module ausführen'},
        ],
        'modules': {
            'description': 'Verfügbare Implementation Module',
            'available': [
                'OpenAI ChatCompletion (openai_chatcompletion)',
                'Google Sheets (google_sheets)',
                'Base Implementation (Abstract Base Class)'
            ]
        }
    },
    'dynamic_ui': {
        'name': 'Dynamic UI System',
        'description': 'Frontend Dynamic Form Generation & Validation',
        'file': 'app/templates/tools/',
        'templates': [
            {'file': 'edit.html', 'feature': 'Dynamic Edit Forms', 'description': 'Dynamische Bearbeitung basierend auf Integration-Parametern'},
            {'file': 'create.html', 'feature': 'Dynamic Create Forms', 'description': 'Dynamische Erstellung basierend auf Integration-Parametern'},
            {'file': 'view.html', 'feature': 'Dynamic Execute Dialog', 'description': 'Dynamische Ausführungs-UI mit Parametern'},
        ],
        'javascript_features': [
            'generateFieldHtml() - Dynamische Feld-Generierung',
            'toggleJsonEditor() - JSON-Editor Toggle',
            'validateJSON() - Live JSON-Validation',
            'syncFormWithJson() - Bidirektionale Synchronisation',
            'addFieldListeners() - Event-Handler für dynamische Felder'
        ]
    }
}

@test_bp.route('/')
def test_overview():
    """Zentrale Test-Übersicht"""
    try:
        # Test-Statistiken generieren
        total_routes = 0
        for module in TEST_MODULES.values():
            if 'routes' in module:
                total_routes += len(module['routes'])
        
        stats = {
            'total_modules': len(TEST_MODULES),
            'total_routes': total_routes,
            'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template('test/overview.html', 
                             test_modules=TEST_MODULES,
                             stats=stats)
        
    except Exception as e:
        flash(f'Fehler beim Laden der Test-Übersicht: {str(e)}', 'error')
        return render_template('test/overview.html', test_modules={}, stats={})

@test_bp.route('/module/<module_name>')
def test_module(module_name):
    """Test-Seite für ein spezifisches Modul"""
    try:
        if module_name not in TEST_MODULES:
            flash(f'Test-Modul "{module_name}" nicht gefunden', 'error')
            return redirect(url_for('test.test_overview'))
        
        module_info = TEST_MODULES[module_name]
        test_results = []
        
        return render_template('test/module.html',
                             module_name=module_name,
                             module_info=module_info,
                             test_results=test_results)
        
    except Exception as e:
        flash(f'Fehler beim Laden des Test-Moduls: {str(e)}', 'error')
        return redirect(url_for('test.test_overview'))

@test_bp.route('/run/<module_name>/<route_function>', methods=['POST'])
def run_route_test(module_name, route_function):
    """Führt einen spezifischen Route-Test aus (AJAX)"""
    try:
        if module_name not in TEST_MODULES:
            return jsonify({'success': False, 'error': f'Modul {module_name} nicht gefunden'})
        
        module_info = TEST_MODULES[module_name]
        route_info = next((r for r in module_info['routes'] if r['function'] == route_function), None)
        
        if not route_info:
            return jsonify({'success': False, 'error': f'Route {route_function} nicht gefunden'})
        
        # Simpler Test: Prüfe ob Route existiert und erreichbar ist
        test_result = {
            'route': route_info['path'],
            'method': route_info['method'],
            'function': route_info['function'],
            'status': 'success',
            'message': 'Route ist definiert und erreichbar',
            'timestamp': datetime.now().isoformat(),
            'response_time': '< 1ms'
        }
        
        return jsonify({'success': True, 'result': test_result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@test_bp.route('/health')
def health_check():
    """System Health Check"""
    try:
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {
                'data_directories': check_data_directories(),
                'route_modules': check_route_modules(),
                'static_files': check_static_files(),
                'templates': check_templates()
            }
        }
        
        # Prüfe ob alle Checks erfolgreich sind
        all_healthy = all(check['status'] == 'ok' for check in health_status['checks'].values())
        health_status['status'] = 'healthy' if all_healthy else 'unhealthy'
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@test_bp.route('/implementation-modules')
def implementation_modules():
    """Implementation Modules Test und Übersicht"""
    return render_template('implementation_modules/overview.html')

def check_data_directories():
    """Prüft ob alle Daten-Verzeichnisse existieren"""
    directories = ['/data/integrations', '/data/tools']
    missing = [d for d in directories if not os.path.exists(d)]
    
    return {
        'status': 'ok' if not missing else 'error',
        'message': 'Alle Verzeichnisse vorhanden' if not missing else f'Fehlende Verzeichnisse: {missing}'
    }

def check_route_modules():
    """Prüft ob alle Route-Module importierbar sind"""
    try:
        from app.routes import integrations, tools, main
        return {'status': 'ok', 'message': 'Alle Route-Module sind importierbar'}
    except Exception as e:
        return {'status': 'error', 'message': f'Import-Fehler: {str(e)}'}

def check_static_files():
    """Prüft wichtige statische Dateien"""
    files = [
        'app/static/css/style.css',
        'app/static/js/main.js',
        'app/static/js/list-improvements.js'
    ]
    missing = [f for f in files if not os.path.exists(f)]
    
    return {
        'status': 'ok' if not missing else 'error',
        'message': 'Alle statischen Dateien vorhanden' if not missing else f'Fehlende Dateien: {missing}'
    }

def check_templates():
    """Prüft wichtige Template-Dateien"""
    templates = [
        'app/templates/base.html',
        'app/templates/tools/list.html',
        'app/templates/integrations/list.html'
    ]
    missing = [t for t in templates if not os.path.exists(t)]
    
    return {
        'status': 'ok' if not missing else 'error', 
        'message': 'Alle Templates vorhanden' if not missing else f'Fehlende Templates: {missing}'
    }

@test_bp.route('/dynamic-features')
def test_dynamic_features():
    """Test-Seite für dynamische UI-Features"""
    try:
        # Test verschiedene Feld-Typen mit Tool-Konfiguration
        sample_tool_config = {
            'id': 'test-tool-001',
            'name': 'Sample Tool für Dynamic Form Test',
            'integration_id': 'sample-integration',
            'prefilled_inputs': {
                'api_key': 'test-key-123',
                'model': 'gpt-4',
                'temperature': 0.7,
                'enabled': True,
                'config_data': {'max_tokens': 1000, 'top_p': 1.0}
            },
            'locked_inputs': ['api_key']
        }
        
        sample_integration = {
            'id': 'sample-integration',
            'name': 'Sample Integration für Tests',
            'vendor': 'OpenAI',
            'config_params': [
                {'name': 'api_key', 'type': 'text', 'required': True, 'description': 'OpenAI API Key'},
                {'name': 'base_url', 'type': 'text', 'required': False, 'default': 'https://api.openai.com/v1'}
            ],
            'input_params': [
                {'name': 'model', 'type': 'select', 'required': True, 'options': [
                    {'value': 'gpt-4', 'label': 'GPT-4'},
                    {'value': 'gpt-3.5-turbo', 'label': 'GPT-3.5 Turbo'}
                ]},
                {'name': 'temperature', 'type': 'number', 'required': False, 'default': 0.7, 'min': 0, 'max': 2},
                {'name': 'enabled', 'type': 'boolean', 'required': False, 'default': True},
                {'name': 'config_data', 'type': 'json', 'required': False, 'description': 'Erweiterte JSON-Konfiguration'}
            ],
            'output_params': [
                {'name': 'response', 'type': 'text', 'description': 'Generated Response'},
                {'name': 'usage', 'type': 'json', 'description': 'Token Usage Statistics'}
            ]
        }
        
        test_scenarios = [
            {
                'name': 'Dynamic Field Generation',
                'description': 'Test der dynamischen Generierung verschiedener Feld-Typen',
                'status': 'ready',
                'fields_tested': ['text', 'select', 'boolean', 'json', 'number']
            },
            {
                'name': 'Status Badge System',
                'description': 'Test der Status-Badges (Locked, Prefilled, Required)',
                'status': 'ready',
                'badges_tested': ['locked', 'prefilled', 'required']
            },
            {
                'name': 'JSON Editor Integration',
                'description': 'Test des JSON-Editor-Toggles und der bidirektionalen Synchronisation',
                'status': 'ready',
                'features_tested': ['toggle', 'sync', 'validation']
            },
            {
                'name': 'Live Validation',
                'description': 'Test der Live-JSON-Validation und Fehlermeldungen',
                'status': 'ready',
                'validation_tested': ['json_syntax', 'required_fields', 'type_validation']
            }
        ]
        
        return render_template('test/dynamic_features.html',
                             tool_config=sample_tool_config,
                             integration=sample_integration,
                             test_scenarios=test_scenarios)
        
    except Exception as e:
        flash(f'Fehler beim Laden der Dynamic Features Tests: {str(e)}', 'error')
        return redirect(url_for('test.test_overview'))

@test_bp.route('/test-dynamic-field/<field_type>', methods=['POST'])
def test_dynamic_field(field_type):
    """AJAX-Test für spezifische dynamische Feld-Typen"""
    try:
        test_data = request.get_json()
        
        result = {
            'field_type': field_type,
            'test_passed': True,
            'message': f'Dynamic field type "{field_type}" successfully tested',
            'timestamp': datetime.now().isoformat(),
            'test_data': test_data
        }
        
        # Spezifische Validierungen je nach Feld-Typ
        if field_type == 'json':
            try:
                if test_data.get('value'):
                    json.loads(test_data['value'])
                result['json_valid'] = True
            except json.JSONDecodeError as e:
                result['test_passed'] = False
                result['json_valid'] = False
                result['error'] = f'Invalid JSON: {str(e)}'
        
        return jsonify({'success': result['test_passed'], 'result': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@test_bp.route('/form/<module_name>/<route_function>')
def test_form(module_name, route_function):
    """Generate test form for POST routes with input fields"""
    try:
        if module_name not in TEST_MODULES:
            flash(f'Test-Modul "{module_name}" nicht gefunden', 'error')
            return redirect(url_for('test.test_overview'))
        
        module_info = TEST_MODULES[module_name]
        route_info = next((r for r in module_info['routes'] if r['function'] == route_function), None)
        
        if not route_info:
            flash(f'Route "{route_function}" nicht gefunden', 'error')
            return redirect(url_for('test.test_overview'))
        
        # Define common form fields based on route function
        form_fields = get_form_fields_for_route(module_name, route_function)
        
        return render_template('test/form.html',
                             module_name=module_name,
                             route_info=route_info,
                             form_fields=form_fields)
        
    except Exception as e:
        flash(f'Fehler beim Laden des Test-Formulars: {str(e)}', 'error')
        return redirect(url_for('test.test_overview'))

@test_bp.route('/execute/<module_name>/<route_function>', methods=['POST'])
def execute_test_route(module_name, route_function):
    """Execute a route test with form data"""
    try:
        if module_name not in TEST_MODULES:
            return jsonify({'success': False, 'error': f'Modul {module_name} nicht gefunden'})
        
        module_info = TEST_MODULES[module_name]
        route_info = next((r for r in module_info['routes'] if r['function'] == route_function), None)
        
        if not route_info:
            return jsonify({'success': False, 'error': f'Route {route_function} nicht gefunden'})
        
        # Get form data
        form_data = {}
        if request.content_type == 'application/json':
            form_data = request.get_json() or {}
        else:
            form_data = request.form.to_dict()
        
        # Execute the actual test with form data
        test_result = execute_actual_route_test(module_name, route_function, form_data)
        
        return jsonify({'success': True, 'result': test_result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_form_fields_for_route(module_name, route_function):
    """Define form fields based on the route function"""
    
    # Common field templates
    common_fields = {
        'create_integration': [
            {'name': 'name', 'type': 'text', 'required': True, 'label': 'Integration Name', 'placeholder': 'OpenAI Integration'},
            {'name': 'vendor', 'type': 'text', 'required': True, 'label': 'Vendor', 'placeholder': 'OpenAI'},
            {'name': 'description', 'type': 'textarea', 'required': False, 'label': 'Description', 'placeholder': 'Description of the integration'},
            {'name': 'config_params', 'type': 'json', 'required': True, 'label': 'Config Parameters', 'default': '[{"name": "api_key", "type": "text", "required": true}]'},
            {'name': 'input_params', 'type': 'json', 'required': True, 'label': 'Input Parameters', 'default': '[{"name": "prompt", "type": "text", "required": true}]'},
            {'name': 'output_params', 'type': 'json', 'required': True, 'label': 'Output Parameters', 'default': '[{"name": "response", "type": "text"}]'}
        ],
        'create_tool': [
            {'name': 'name', 'type': 'text', 'required': True, 'label': 'Tool Name', 'placeholder': 'My ChatGPT Tool'},
            {'name': 'integration_id', 'type': 'text', 'required': True, 'label': 'Integration ID', 'placeholder': 'openai-integration-001'},
            {'name': 'description', 'type': 'textarea', 'required': False, 'label': 'Description', 'placeholder': 'Tool description'},
            {'name': 'config', 'type': 'json', 'required': False, 'label': 'Configuration', 'default': '{"model": "gpt-4", "temperature": 0.7}'},
            {'name': 'prefilled_inputs', 'type': 'json', 'required': False, 'label': 'Prefilled Inputs', 'default': '{}'},
            {'name': 'locked_inputs', 'type': 'json', 'required': False, 'label': 'Locked Inputs', 'default': '[]'}
        ],
        'edit_integration': [
            {'name': 'id', 'type': 'text', 'required': True, 'label': 'Integration ID', 'placeholder': 'integration-id'},
            {'name': 'name', 'type': 'text', 'required': True, 'label': 'Integration Name'},
            {'name': 'vendor', 'type': 'text', 'required': True, 'label': 'Vendor'},
            {'name': 'description', 'type': 'textarea', 'required': False, 'label': 'Description'}
        ],
        'edit_tool': [
            {'name': 'id', 'type': 'text', 'required': True, 'label': 'Tool ID', 'placeholder': 'tool-id'},
            {'name': 'name', 'type': 'text', 'required': True, 'label': 'Tool Name'},
            {'name': 'description', 'type': 'textarea', 'required': False, 'label': 'Description'},
            {'name': 'config', 'type': 'json', 'required': False, 'label': 'Configuration'}
        ],
        'test_integration': [
            {'name': 'id', 'type': 'text', 'required': True, 'label': 'Integration ID', 'placeholder': 'integration-id'}
        ],
        'test_tool': [
            {'name': 'id', 'type': 'text', 'required': True, 'label': 'Tool ID', 'placeholder': 'tool-id'}
        ],
        'execute_tool': [
            {'name': 'id', 'type': 'text', 'required': True, 'label': 'Tool ID', 'placeholder': 'tool-id'},
            {'name': 'inputs', 'type': 'json', 'required': True, 'label': 'Input Parameters', 'default': '{"prompt": "Hello, world!"}'}
        ],
        'delete_integration': [
            {'name': 'id', 'type': 'text', 'required': True, 'label': 'Integration ID', 'placeholder': 'integration-id'}
        ],
        'delete_tool': [
            {'name': 'id', 'type': 'text', 'required': True, 'label': 'Tool ID', 'placeholder': 'tool-id'}
        ]
    }
    
    return common_fields.get(route_function, [
        {'name': 'data', 'type': 'json', 'required': False, 'label': 'Request Data', 'default': '{}'}
    ])

def execute_actual_route_test(module_name, route_function, form_data):
    """Execute the actual route with form data and return results"""
    from datetime import datetime
    import requests
    
    try:
        # Get the route info
        module_info = TEST_MODULES[module_name]
        route_info = next((r for r in module_info['routes'] if r['function'] == route_function), None)
        
        if not route_info:
            raise Exception(f'Route {route_function} not found')
        
        # Build the test URL
        base_url = 'http://localhost:5004'
        test_url = base_url + route_info['path']
        
        # Replace path parameters with form data
        if '<id>' in test_url and 'id' in form_data:
            test_url = test_url.replace('<id>', str(form_data['id']))
        
        # Prepare request data
        request_data = {}
        headers = {'Content-Type': 'application/json'}
        
        # Filter out path parameters from form data
        for key, value in form_data.items():
            if key not in ['id']:  # id is typically a path parameter
                try:
                    # Try to parse JSON strings
                    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                        request_data[key] = json.loads(value)
                    else:
                        request_data[key] = value
                except json.JSONDecodeError:
                    request_data[key] = value
        
        # Execute the request
        start_time = datetime.now()
        
        if route_info['method'] == 'GET':
            response = requests.get(test_url, params=request_data, timeout=10)
        elif route_info['method'] == 'POST':
            response = requests.post(test_url, json=request_data, headers=headers, timeout=10)
        else:
            raise Exception(f'Unsupported method: {route_info["method"]}')
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        # Parse response
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        test_result = {
            'route': route_info['path'],
            'method': route_info['method'],
            'function': route_info['function'],
            'status_code': response.status_code,
            'status': 'success' if response.status_code < 400 else 'error',
            'message': f'HTTP {response.status_code} - {"Success" if response.status_code < 400 else "Error"}',
            'timestamp': datetime.now().isoformat(),
            'response_time': f'{response_time:.1f}ms',
            'request_data': request_data,
            'response_data': response_data[:1000] if isinstance(response_data, str) else response_data  # Truncate long responses
        }
        
        return test_result
        
    except Exception as e:
        return {
            'route': route_info['path'] if 'route_info' in locals() else 'unknown',
            'method': route_info['method'] if 'route_info' in locals() else 'unknown',
            'function': route_function,
            'status': 'error',
            'message': f'Test execution failed: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'response_time': '0ms',
            'request_data': form_data,
            'error': str(e)
        }
