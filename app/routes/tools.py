"""
Tools Management Routes für vntrai
Vollständige CRUD-Funktionalität für Tool-Instanzen basierend auf Integrations
Mit Implementation Module Integration für echte Tool-Ausführung
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
import uuid
import asyncio
from datetime import datetime

from app.utils.data_manager import ToolsManager, IntegrationsManager
from app.utils.validation import ToolValidator

# Implementation Module Integration
try:
    from app.implementation_modules import implementation_manager
    IMPLEMENTATION_MODULES_AVAILABLE = True
except ImportError:
    IMPLEMENTATION_MODULES_AVAILABLE = False
    implementation_manager = None

# Blueprint erstellen
tools_bp = Blueprint('tools', __name__, url_prefix='/tools')

# Manager-Instanzen
tools_manager = ToolsManager()
integrations_manager = IntegrationsManager()
validator = ToolValidator()

@tools_bp.route('/')
def list_tools():
    """Liste aller Tools anzeigen"""
    try:
        tools = tools_manager.get_all()
        integrations = integrations_manager.get_all()
        
        # Filter und Suche
        search_query = request.args.get('search', '')
        integration_filter = request.args.get('integration', '')
        status_filter = request.args.get('status', '')
        
        if search_query:
            tools = tools_manager.search(search_query)
        
        if integration_filter:
            tools = [t for t in tools if t.get('tool_definition') == integration_filter]
        
        if status_filter:
            tools = [t for t in tools if t.get('status') == status_filter]
        
        # Erweitere Tools mit Integration-Informationen
        for tool in tools:
            tool['integration'] = next(
                (i for i in integrations if i['name'] == tool.get('tool_definition')), 
                None
            )
        
        return render_template('tools/list.html', 
                             tools=tools,
                             integrations=integrations,
                             search_query=search_query,
                             integration_filter=integration_filter,
                             status_filter=status_filter)
        
    except Exception as e:
        print(f"ERROR in list_tools: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Fehler beim Laden der Tools: {str(e)}', 'error')
        return render_template('tools/list.html', tools=[], integrations=[])

@tools_bp.route('/view/<tool_id>')
def view_tool(tool_id):
    """Einzelnes Tool anzeigen"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            flash('Tool nicht gefunden', 'error')
            return redirect(url_for('tools.list_tools'))
        
        # Integration-Details laden
        integration = next(
            (i for i in integrations_manager.get_all() 
             if i['name'] == tool.get('tool_definition')), 
            None
        )
        
        return render_template('tools/view.html', tool=tool, integration=integration)
        
    except Exception as e:
        flash(f'Fehler beim Laden des Tools: {str(e)}', 'error')
        return redirect(url_for('tools.list_tools'))

@tools_bp.route('/create', methods=['GET', 'POST'])
def create_tool():
    """Neues Tool erstellen"""
    if request.method == 'GET':
        integrations = integrations_manager.get_all()
        selected_integration = request.args.get('integration')
        
        # Integration-Details für ausgewählte Integration laden
        integration = None
        if selected_integration:
            integration = next(
                (i for i in integrations if i['name'] == selected_integration), 
                None
            )
        
        return render_template('tools/create.html', 
                             integrations=integrations,
                             selected_integration=selected_integration,
                             integration=integration)
    
    try:
        # Form-Daten verarbeiten
        
        # Parse config fields (dynamic or JSON)
        config_data = {}
        if 'config' in request.form:
            try:
                config_data = json.loads(request.form.get('config', '{}'))
            except json.JSONDecodeError:
                pass
        
        # Parse dynamic config fields
        for key in request.form.keys():
            if key.startswith('config[') and key.endswith(']'):
                field_name = key[7:-1]  # Remove 'config[' and ']'
                value = request.form.get(key)
                if value:
                    config_data[field_name] = value
        
        # Parse prefilled inputs (dynamic or JSON)
        prefilled_data = {}
        if 'prefilled_inputs' in request.form:
            try:
                prefilled_data = json.loads(request.form.get('prefilled_inputs', '{}'))
            except json.JSONDecodeError:
                pass
        
        # Parse dynamic prefilled input fields
        for key in request.form.keys():
            if key.startswith('prefilled_inputs[') and key.endswith(']'):
                field_name = key[17:-1]  # Remove 'prefilled_inputs[' and ']'
                value = request.form.get(key)
                if value:
                    prefilled_data[field_name] = value
        
        # Parse locked inputs (checkboxes or JSON)
        locked_inputs = []
        if 'locked_inputs[]' in request.form:
            locked_inputs = request.form.getlist('locked_inputs[]')
        elif 'locked_inputs' in request.form:
            try:
                locked_inputs = json.loads(request.form.get('locked_inputs', '[]'))
            except json.JSONDecodeError:
                locked_inputs = []
        
        data = {
            'id': str(uuid.uuid4()),
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'tool_definition': request.form.get('tool_definition', '').strip(),
            'config': config_data,
            'prefilled_inputs': prefilled_data,
            'locked_inputs': locked_inputs,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'updated_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'not_connected',
            'last_test': None,
            'last_execution': None
        }
        
        # Integration ID automatisch setzen
        if data.get('tool_definition'):
            integration = next(
                (i for i in integrations_manager.get_all() 
                 if i['name'] == data['tool_definition']), 
                None
            )
            if integration and integration.get('id'):
                data['integration_id'] = integration['id']
        
        # Validation
        errors = validator.validate(data)
        if errors:
            flash(f'Validierungsfehler: {"; ".join(errors)}', 'error')
            integrations = integrations_manager.get_all()
            integration = next(
                (i for i in integrations if i['name'] == data.get('tool_definition')), 
                None
            )
            return render_template('tools/create.html', 
                                 tool=data, 
                                 integrations=integrations,
                                 integration=integration)
        
        # Tool speichern
        success = tools_manager.create(data)
        if success:
            flash('Tool erfolgreich erstellt', 'success')
            return redirect(url_for('tools.view_tool', tool_id=data['id']))
        else:
            flash('Fehler beim Speichern des Tools', 'error')
            integrations = integrations_manager.get_all()
            integration = next(
                (i for i in integrations if i['name'] == data.get('tool_definition')), 
                None
            )
            return render_template('tools/create.html', 
                                 tool=data, 
                                 integrations=integrations,
                                 integration=integration)
            
    except json.JSONDecodeError as e:
        flash(f'JSON-Fehler: {str(e)}', 'error')
        integrations = integrations_manager.get_all()
        return render_template('tools/create.html', integrations=integrations)
    except Exception as e:
        flash(f'Fehler beim Erstellen des Tools: {str(e)}', 'error')
        integrations = integrations_manager.get_all()
        return render_template('tools/create.html', integrations=integrations)

@tools_bp.route('/edit/<tool_id>', methods=['GET', 'POST'])
def edit_tool(tool_id):
    """Tool bearbeiten"""
    if request.method == 'GET':
        try:
            tool = tools_manager.get_by_id(tool_id)
            if not tool:
                flash('Tool nicht gefunden', 'error')
                return redirect(url_for('tools.list_tools'))
            
            integrations = integrations_manager.get_all()
            
            # Integration-Details für aktuelles Tool laden
            integration = next(
                (i for i in integrations if i['name'] == tool.get('tool_definition')), 
                None
            )
            
            return render_template('tools/edit.html', 
                                 tool=tool, 
                                 integrations=integrations,
                                 integration=integration)
        except Exception as e:
            flash(f'Fehler beim Laden des Tools: {str(e)}', 'error')
            return redirect(url_for('tools.list_tools'))
    
    try:
        # Bestehendes Tool laden
        existing = tools_manager.get_by_id(tool_id)
        if not existing:
            flash('Tool nicht gefunden', 'error')
            return redirect(url_for('tools.list_tools'))
        
        # Form-Daten verarbeiten
        data = existing.copy()
        
        # Parse config fields (dynamic or JSON)
        config_data = {}
        if 'config' in request.form:
            try:
                config_data = json.loads(request.form.get('config', '{}'))
            except json.JSONDecodeError:
                pass
        
        # Parse dynamic config fields
        for key in request.form.keys():
            if key.startswith('config[') and key.endswith(']'):
                field_name = key[7:-1]  # Remove 'config[' and ']'
                value = request.form.get(key)
                if value:
                    config_data[field_name] = value
        
        # Parse prefilled inputs (dynamic or JSON)
        prefilled_data = {}
        if 'prefilled_inputs' in request.form:
            try:
                prefilled_data = json.loads(request.form.get('prefilled_inputs', '{}'))
            except json.JSONDecodeError:
                pass
        
        # Parse dynamic prefilled input fields
        for key in request.form.keys():
            if key.startswith('prefilled_inputs[') and key.endswith(']'):
                field_name = key[17:-1]  # Remove 'prefilled_inputs[' and ']'
                value = request.form.get(key)
                if value:
                    prefilled_data[field_name] = value
        
        # Parse locked inputs (checkboxes or JSON)
        locked_inputs = []
        if 'locked_inputs[]' in request.form:
            locked_inputs = request.form.getlist('locked_inputs[]')
        elif 'locked_inputs' in request.form:
            try:
                locked_inputs = json.loads(request.form.get('locked_inputs', '[]'))
            except json.JSONDecodeError:
                locked_inputs = []
        
        # Parse assistant options
        options_data = existing.get('options', {}).copy()
        
        # Assistant configuration
        assistant_options = {}
        for key in request.form.keys():
            if key.startswith('options[assistant][') and key.endswith(']'):
                field_name = key[18:-1]  # Remove 'options[assistant][' and ']'
                value = request.form.get(key)
                
                # Convert checkbox values
                if field_name in ['enabled', 'auto_create']:
                    assistant_options[field_name] = value == 'true'
                else:
                    assistant_options[field_name] = value
        
        # Update options structure
        if assistant_options:
            options_data['assistant'] = assistant_options
        
        data.update({
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'tool_definition': request.form.get('tool_definition', '').strip(),
            'config': config_data,
            'prefilled_inputs': prefilled_data,
            'locked_inputs': locked_inputs,
            'options': options_data,
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        })
        
        # Integration ID automatisch setzen/aktualisieren
        if data.get('tool_definition'):
            integration = next(
                (i for i in integrations_manager.get_all() 
                 if i['name'] == data['tool_definition']), 
                None
            )
            if integration and integration.get('id'):
                data['integration_id'] = integration['id']
        
        # Validation
        errors = validator.validate(data)
        if errors:
            flash(f'Validierungsfehler: {"; ".join(errors)}', 'error')
            integrations = integrations_manager.get_all()
            integration = next(
                (i for i in integrations if i['name'] == data.get('tool_definition')), 
                None
            )
            return render_template('tools/edit.html', 
                                 tool=data, 
                                 integrations=integrations,
                                 integration=integration)
        
        # Tool aktualisieren
        success = tools_manager.update(tool_id, data)
        if success:
            flash('Tool erfolgreich aktualisiert', 'success')
            return redirect(url_for('tools.view_tool', tool_id=tool_id))
        else:
            flash('Fehler beim Aktualisieren des Tools', 'error')
            integrations = integrations_manager.get_all()
            integration = next(
                (i for i in integrations if i['name'] == data.get('tool_definition')), 
                None
            )
            return render_template('tools/edit.html', 
                                 tool=data, 
                                 integrations=integrations,
                                 integration=integration)
            
    except json.JSONDecodeError as e:
        flash(f'JSON-Fehler: {str(e)}', 'error')
        integrations = integrations_manager.get_all()
        integration = next(
            (i for i in integrations if i['name'] == existing.get('tool_definition')), 
            None
        )
        return render_template('tools/edit.html', 
                             tool=existing, 
                             integrations=integrations,
                             integration=integration)
    except Exception as e:
        flash(f'Fehler beim Aktualisieren des Tools: {str(e)}', 'error')
        integrations = integrations_manager.get_all()
        integration = next(
            (i for i in integrations if i['name'] == existing.get('tool_definition')), 
            None
        )
        return render_template('tools/edit.html', 
                             tool=existing, 
                             integrations=integrations,
                             integration=integration)

@tools_bp.route('/delete/<tool_id>', methods=['POST'])
def delete_tool(tool_id):
    """Tool löschen"""
    try:
        success = tools_manager.delete(tool_id)
        if success:
            flash('Tool erfolgreich gelöscht', 'success')
        else:
            flash('Fehler beim Löschen des Tools', 'error')
    except Exception as e:
        flash(f'Fehler beim Löschen des Tools: {str(e)}', 'error')
    
    return redirect(url_for('tools.list_tools'))

@tools_bp.route('/test/<tool_id>', methods=['POST'])
def test_tool(tool_id):
    """Tool testen - mit Implementation Module Integration"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'success': False, 'message': 'Tool nicht gefunden'}), 404
        
        # Test-Daten aus Request extrahieren (sicher)
        try:
            test_data = request.get_json() or {}
        except Exception:
            # Fallback falls kein JSON oder invalides JSON
            test_data = {}
        
        # Prüfe ob Implementation Module verfügbar ist
        if IMPLEMENTATION_MODULES_AVAILABLE:
            # Versuche echten Test über Implementation Module
            try:
                # Da Flask-Routes nicht async sind, führen wir das in einem Thread aus
                import threading
                import asyncio
                
                result_container = {}
                exception_container = {}
                
                def run_async_test():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            tools_manager.test_tool_with_implementation(tool_id, test_data)
                        )
                        result_container['result'] = result
                    except Exception as e:
                        exception_container['error'] = e
                    finally:
                        loop.close()
                
                thread = threading.Thread(target=run_async_test)
                thread.start()
                thread.join(timeout=30)  # 30 Sekunden Timeout
                
                if 'result' in result_container:
                    return jsonify(result_container['result'])
                elif 'error' in exception_container:
                    raise exception_container['error']
                else:
                    # Timeout
                    return jsonify({
                        'success': False, 
                        'message': 'Test-Timeout (30s überschritten)'
                    }), 500
                    
            except Exception as impl_error:
                print(f"Implementation Module Test Error: {impl_error}")
                # Fallback zu Basic-Test
                pass
        
        # Fallback: Basic-Test ohne Implementation Module
        integration = next(
            (i for i in integrations_manager.get_all() 
             if i['name'] == tool.get('tool_definition')), 
            None
        )
        
        if not integration:
            return jsonify({'success': False, 'message': 'Integration nicht gefunden'}), 404
        
        # Basis-Test: Konfiguration validieren
        config = tool.get('config', {})
        required_params = integration.get('config_params', [])
        
        missing_params = []
        for param in required_params:
            if param.get('required', False) and not config.get(param['name']):
                missing_params.append(param['name'])
        
        if missing_params:
            result = {
                'success': False,
                'message': f'Fehlende Parameter: {", ".join(missing_params)}',
                'details': {'missing_params': missing_params},
                'test_type': 'basic_validation'
            }
        else:
            # Erfolgreicher Basic-Test
            result = {
                'success': True,
                'message': 'Tool-Konfiguration ist gültig (Basic-Test)',
                'details': {
                    'config_valid': True,
                    'parameters_complete': True
                },
                'test_type': 'basic_validation'
            }
        
        # Test-Ergebnis im Tool speichern
        tool['last_test'] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'result': result
        }
        
        # Status aktualisieren
        tool['status'] = 'connected' if result['success'] else 'error'
        tool['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        tools_manager.update(tool_id, tool)
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print(f"Test Tool Error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@tools_bp.route('/execute/<tool_id>', methods=['POST'])
def execute_tool(tool_id):
    """Tool ausführen - mit Implementation Module Integration"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'success': False, 'message': 'Tool nicht gefunden'}), 404
        
        # Execution-Parameter aus Request extrahieren (sicher)
        try:
            execution_data = request.get_json() or {}
        except Exception:
            # Fallback falls kein JSON oder invalides JSON
            execution_data = {}
        inputs = execution_data.get('inputs', {})
        
        # Prüfe ob Implementation Module verfügbar ist
        if IMPLEMENTATION_MODULES_AVAILABLE:
            # Versuche echte Ausführung über Implementation Module
            try:
                import threading
                import asyncio
                
                result_container = {}
                exception_container = {}
                
                def run_async_execution():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            tools_manager.execute_tool_with_implementation(tool_id, inputs)
                        )
                        result_container['result'] = result
                    except Exception as e:
                        exception_container['error'] = e
                    finally:
                        loop.close()
                
                thread = threading.Thread(target=run_async_execution)
                thread.start()
                thread.join(timeout=60)  # 60 Sekunden Timeout für Execution
                
                if 'result' in result_container:
                    return jsonify(result_container['result'])
                elif 'error' in exception_container:
                    raise exception_container['error']
                else:
                    # Timeout
                    return jsonify({
                        'success': False, 
                        'message': 'Execution-Timeout (60s überschritten)'
                    }), 500
                    
            except Exception as impl_error:
                print(f"Implementation Module Execution Error: {impl_error}")
                # Fallback zu Simulation
                pass
        
        # Fallback: Simulierte Ausführung
        integration = next(
            (i for i in integrations_manager.get_all() 
             if i['name'] == tool.get('tool_definition')), 
            None
        )
        
        if not integration:
            return jsonify({'success': False, 'message': 'Integration nicht gefunden'}), 404
        
        # Prefilled und Locked Inputs berücksichtigen
        final_inputs = tool.get('prefilled_inputs', {}).copy()
        locked_inputs = tool.get('locked_inputs', [])
        
        for key, value in inputs.items():
            if key not in locked_inputs:
                final_inputs[key] = value
        
        # Simulierte Ausführung
        execution_result = {
            'success': True,
            'message': 'Tool erfolgreich ausgeführt (simuliert)',
            'inputs': final_inputs,
            'outputs': {
                'result': f'Simuliertes Ergebnis von {tool["name"]}',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            'execution_type': 'simulated'
        }
        
        # Execution-Ergebnis im Tool speichern
        tool['last_execution'] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'inputs': final_inputs,
            'result': execution_result
        }
        
        tool['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        tools_manager.update(tool_id, tool)
        
        return jsonify(execution_result)
        
    except Exception as e:
        import traceback
        print(f"Execute Tool Error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@tools_bp.route('/clone/<tool_id>', methods=['POST'])
def clone_tool(tool_id):
    """Tool klonen"""
    try:
        original = tools_manager.get_by_id(tool_id)
        if not original:
            flash('Tool nicht gefunden', 'error')
            return redirect(url_for('tools.list_tools'))
        
        # Neues Tool basierend auf Original erstellen
        cloned = original.copy()
        cloned['id'] = str(uuid.uuid4())
        cloned['name'] = f"{original['name']} (Kopie)"
        cloned['created_at'] = datetime.utcnow().isoformat() + 'Z'
        cloned['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        cloned['status'] = 'not_connected'
        cloned['last_test'] = None
        cloned['last_execution'] = None
        
        success = tools_manager.create(cloned)
        if success:
            flash('Tool erfolgreich geklont', 'success')
            return redirect(url_for('tools.view_tool', tool_id=cloned['id']))
        else:
            flash('Fehler beim Klonen des Tools', 'error')
            
    except Exception as e:
        flash(f'Fehler beim Klonen des Tools: {str(e)}', 'error')
    
    return redirect(url_for('tools.list_tools'))

@tools_bp.route('/api/config/<tool_id>')
def get_tool_config(tool_id):
    """API-Route für Tool-Konfiguration (für Execute-Modal)"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'success': False, 'message': 'Tool nicht gefunden'}), 404
        
        # Integration-Details laden
        integration = next(
            (i for i in integrations_manager.get_all() 
             if i['name'] == tool.get('tool_definition')), 
            None
        )
        
        return jsonify({
            'success': True,
            'tool': tool,
            'integration': integration
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@tools_bp.route('/search')
def search_tools():
    """Tools durchsuchen"""
    query = request.args.get('q', '').strip()
    try:
        if query:
            tools = tools_manager.search(query)
        else:
            tools = tools_manager.get_all()
        
        if request.headers.get('Accept') == 'application/json':
            return jsonify(tools)
        
        # Für normale Requests zu list_tools weiterleiten
        return redirect(url_for('tools.list_tools', search=query))
        
    except Exception as e:
        flash(f'Fehler bei der Suche: {str(e)}', 'error')
        return redirect(url_for('tools.list_tools'))

@tools_bp.route('/implementation-status/<tool_id>')
def get_implementation_status(tool_id):
    """Implementation Module Status für ein Tool abrufen"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'success': False, 'message': 'Tool nicht gefunden'}), 404
        
        # Implementation Status ermitteln
        impl_status = tools_manager.get_tool_implementation_status(tool)
        
        # Zusätzliche Informationen sammeln
        response = {
            'success': True,
            'tool_id': tool_id,
            'tool_name': tool.get('name'),
            'tool_definition': tool.get('tool_definition'),
            'implementation_status': impl_status,
            'modules_available': IMPLEMENTATION_MODULES_AVAILABLE
        }
        
        # Wenn Module verfügbar sind, zeige verfügbare Module
        if IMPLEMENTATION_MODULES_AVAILABLE:
            response['available_modules'] = tools_manager.get_available_implementation_modules()
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tools_bp.route('/test_assistant/<tool_id>', methods=['POST'])
def test_assistant_connection(tool_id):
    """Test assistant connection for a tool"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'success': False, 'message': 'Tool not found'}), 404
        
        # Check if assistant is enabled
        assistant_options = tools_manager.get_assistant_options(tool_id)
        if not assistant_options.get('enabled', False):
            return jsonify({'success': False, 'message': 'Assistant not enabled for this tool'}), 400
        
        if not IMPLEMENTATION_MODULES_AVAILABLE:
            return jsonify({'success': False, 'message': 'Implementation module system not available'}), 500
        
        # Test OpenAI Assistant API implementation
        try:
            # Use tool's config for testing
            config = tool.get('config', {})
            
            # Map tool config fields to implementation expected fields
            mapped_config = {}
            if 'openai_api_key' in config:
                mapped_config['api_key'] = config['openai_api_key']
            if 'organization_id' in config:
                mapped_config['organization'] = config['organization_id']
            if 'base_url' in config:
                mapped_config['base_url'] = config['base_url']
            if 'timeout' in config:
                mapped_config['timeout'] = config['timeout']
            
            # Get implementation with tool's configuration
            impl = implementation_manager.get_implementation('openai_assistant_api', mapped_config)
            if not impl:
                return jsonify({'success': False, 'message': 'OpenAI Assistant API implementation not found or configuration invalid'}), 500
            
            # Test connection
            test_result = impl.execute({'action': 'test'})
            
            return jsonify({
                'success': test_result.get('success', False),
                'message': test_result.get('message', 'Test completed'),
                'details': test_result
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Test failed: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tools_bp.route('/create_assistant/<tool_id>', methods=['POST'])
def create_assistant_for_tool(tool_id):
    """Create an OpenAI assistant for a tool"""
    try:
        if not IMPLEMENTATION_MODULES_AVAILABLE:
            return jsonify({'success': False, 'message': 'Implementation module system not available'}), 500
        
        # Run async function in thread
        import threading
        import asyncio
        
        result_container = {}
        exception_container = {}
        
        def run_async_create():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(tools_manager.create_assistant_for_tool(tool_id))
                result_container['result'] = result
            except Exception as e:
                exception_container['error'] = e
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_async_create)
        thread.start()
        thread.join(timeout=30)  # 30 second timeout
        
        if thread.is_alive():
            return jsonify({'success': False, 'message': 'Operation timed out'}), 500
        
        if 'error' in exception_container:
            raise exception_container['error']
        
        result = result_container.get('result', {'success': False, 'message': 'No result'})
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tools_bp.route('/sync_assistant/<tool_id>', methods=['POST'])
def sync_assistant_config(tool_id):
    """Sync assistant configuration with OpenAI"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'success': False, 'message': 'Tool not found'}), 404
        
        request_data = request.get_json() or {}
        assistant_id = request_data.get('assistant_id', '')
        
        if not assistant_id:
            return jsonify({'success': False, 'message': 'Assistant ID required'}), 400
        
        if not IMPLEMENTATION_MODULES_AVAILABLE:
            return jsonify({'success': False, 'message': 'Implementation module system not available'}), 500
        
        # Get assistant details from OpenAI
        try:
            # Use tool's config for getting assistant details
            config = tool.get('config', {})
            
            # Map tool config fields to implementation expected fields
            mapped_config = {}
            if 'openai_api_key' in config:
                mapped_config['api_key'] = config['openai_api_key']
            if 'organization_id' in config:
                mapped_config['organization'] = config['organization_id']
            if 'base_url' in config:
                mapped_config['base_url'] = config['base_url']
            if 'timeout' in config:
                mapped_config['timeout'] = config['timeout']
            
            # Get implementation with tool's configuration
            impl = implementation_manager.get_implementation('openai_assistant_api', mapped_config)
            if not impl:
                return jsonify({'success': False, 'message': 'OpenAI Assistant API implementation not found or configuration invalid'}), 500
            
            # Get assistant info
            get_result = impl.execute({
                'action': 'get_assistant',
                'assistant_id': assistant_id
            })
            
            if not get_result.get('success', False):
                return jsonify({'success': False, 'message': f'Failed to get assistant: {get_result.get("error", "Unknown error")}'}), 500
            
            assistant_data = get_result.get('data', {})
            
            # Update tool's assistant options with synced data
            assistant_options = tools_manager.get_assistant_options(tool_id)
            assistant_options.update({
                'assistant_id': assistant_id,
                'model': assistant_data.get('model', assistant_options.get('model', 'gpt-4-turbo-preview')),
                'instructions': assistant_data.get('instructions', assistant_options.get('instructions', '')),
                'enabled': True
            })
            
            # Save updated options
            success = tools_manager.update_assistant_options(tool_id, assistant_options)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Assistant configuration synced successfully',
                    'assistant_data': assistant_data
                })
            else:
                return jsonify({'success': False, 'message': 'Failed to save assistant configuration'}), 500
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Sync failed: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tools_bp.route('/chat_assistant/<tool_id>', methods=['POST'])
def chat_with_tool_assistant(tool_id):
    """Chat with a tool's assistant"""
    try:
        request_data = request.get_json() or {}
        message = request_data.get('message', '')
        thread_id = request_data.get('thread_id', None)
        
        if not message:
            return jsonify({'success': False, 'message': 'Message required'}), 400
        
        if not IMPLEMENTATION_MODULES_AVAILABLE:
            return jsonify({'success': False, 'message': 'Implementation module system not available'}), 500
        
        # Run async function in thread
        import threading
        import asyncio
        
        result_container = {}
        exception_container = {}
        
        def run_async_chat():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(tools_manager.chat_with_tool_assistant(tool_id, message, thread_id))
                result_container['result'] = result
            except Exception as e:
                exception_container['error'] = e
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_async_chat)
        thread.start()
        thread.join(timeout=60)  # 60 second timeout for chat
        
        if thread.is_alive():
            return jsonify({'success': False, 'message': 'Chat operation timed out'}), 500
        
        if 'error' in exception_container:
            raise exception_container['error']
        
        result = result_container.get('result', {'success': False, 'message': 'No result'})
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@tools_bp.route('/api/<tool_id>/assistant/enable', methods=['POST'])
def enable_tool_assistant(tool_id):
    """Enable assistant functionality for a tool"""
    try:
        data = request.get_json() or {}
        assistant_config = data.get('assistant_config', {})
        
        success = tools_manager.enable_assistant_for_tool(tool_id, assistant_config)
        if success:
            return jsonify({'success': True, 'message': 'Assistant functionality enabled'})
        else:
            return jsonify({'success': False, 'message': 'Failed to enable assistant'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@tools_bp.route('/api/<tool_id>/assistant/disable', methods=['POST'])
def disable_tool_assistant(tool_id):
    """Disable assistant functionality for a tool"""
    try:
        success = tools_manager.disable_assistant_for_tool(tool_id)
        if success:
            return jsonify({'success': True, 'message': 'Assistant functionality disabled'})
        else:
            return jsonify({'success': False, 'message': 'Failed to disable assistant'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@tools_bp.route('/api/<tool_id>/assistant/config', methods=['PUT'])
def update_tool_assistant_config(tool_id):
    """Update assistant configuration for a tool"""
    try:
        data = request.get_json() or {}
        assistant_config = data.get('assistant_config', {})
        
        success = tools_manager.update_assistant_config(tool_id, assistant_config)
        if success:
            return jsonify({'success': True, 'message': 'Assistant configuration updated'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update assistant config'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@tools_bp.route('/api/assistant-enabled')
def get_assistant_enabled_tools():
    """Get all tools with assistant functionality enabled"""
    try:
        tools = tools_manager.get_assistant_enabled_tools()
        return jsonify({
            'success': True,
            'tools': tools,
            'count': len(tools)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
