"""
Tools Management Routes für vntrai
Vollständige CRUD-Funktionalität für Tool-Instanzen basierend auf Integrations
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime

from app.utils.data_manager import ToolsManager, IntegrationsManager
from app.utils.validation import ToolValidator

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
        
        # Gruppierung nach Integration
        tools_by_integration = {}
        for tool in tools:
            integration_name = tool.get('tool_definition', 'Unknown')
            if integration_name not in tools_by_integration:
                tools_by_integration[integration_name] = []
            tools_by_integration[integration_name].append(tool)
        
        return render_template('tools/list.html', 
                             tools=tools,
                             tools_by_integration=tools_by_integration,
                             integrations=integrations,
                             search_query=search_query,
                             integration_filter=integration_filter,
                             status_filter=status_filter)
        
    except Exception as e:
        flash(f'Fehler beim Laden der Tools: {str(e)}', 'error')
        return render_template('tools/list.html', tools=[], tools_by_integration={})

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
        return render_template('tools/create.html', 
                             integrations=integrations,
                             selected_integration=selected_integration)
    
    try:
        # Form-Daten verarbeiten
        data = {
            'id': str(uuid.uuid4()),
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'tool_definition': request.form.get('tool_definition', '').strip(),
            'config': json.loads(request.form.get('config', '{}')),
            'prefilled_inputs': json.loads(request.form.get('prefilled_inputs', '{}')),
            'locked_inputs': json.loads(request.form.get('locked_inputs', '[]')),
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'updated_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'not_connected',
            'last_test': None,
            'last_execution': None
        }
        
        # Validation
        errors = validator.validate(data)
        if errors:
            flash(f'Validierungsfehler: {"; ".join(errors)}', 'error')
            integrations = integrations_manager.get_all()
            return render_template('tools/create.html', tool=data, integrations=integrations)
        
        # Tool speichern
        success = tools_manager.create(data)
        if success:
            flash('Tool erfolgreich erstellt', 'success')
            return redirect(url_for('tools.view_tool', tool_id=data['id']))
        else:
            flash('Fehler beim Speichern des Tools', 'error')
            integrations = integrations_manager.get_all()
            return render_template('tools/create.html', tool=data, integrations=integrations)
            
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
            return render_template('tools/edit.html', tool=tool, integrations=integrations)
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
        data.update({
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'tool_definition': request.form.get('tool_definition', '').strip(),
            'config': json.loads(request.form.get('config', '{}')),
            'prefilled_inputs': json.loads(request.form.get('prefilled_inputs', '{}')),
            'locked_inputs': json.loads(request.form.get('locked_inputs', '[]')),
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        })
        
        # Validation
        errors = validator.validate(data)
        if errors:
            flash(f'Validierungsfehler: {"; ".join(errors)}', 'error')
            integrations = integrations_manager.get_all()
            return render_template('tools/edit.html', tool=data, integrations=integrations)
        
        # Tool aktualisieren
        success = tools_manager.update(tool_id, data)
        if success:
            flash('Tool erfolgreich aktualisiert', 'success')
            return redirect(url_for('tools.view_tool', tool_id=tool_id))
        else:
            flash('Fehler beim Aktualisieren des Tools', 'error')
            integrations = integrations_manager.get_all()
            return render_template('tools/edit.html', tool=data, integrations=integrations)
            
    except json.JSONDecodeError as e:
        flash(f'JSON-Fehler: {str(e)}', 'error')
        integrations = integrations_manager.get_all()
        return render_template('tools/edit.html', tool=existing, integrations=integrations)
    except Exception as e:
        flash(f'Fehler beim Aktualisieren des Tools: {str(e)}', 'error')
        integrations = integrations_manager.get_all()
        return render_template('tools/edit.html', tool=existing, integrations=integrations)

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
    """Tool testen"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'success': False, 'message': 'Tool nicht gefunden'}), 404
        
        # Integration für dieses Tool finden
        integration = next(
            (i for i in integrations_manager.get_all() 
             if i['name'] == tool.get('tool_definition')), 
            None
        )
        
        if not integration:
            return jsonify({'success': False, 'message': 'Integration nicht gefunden'}), 404
        
        # Test-Daten aus Request extrahieren
        test_data = request.get_json() or {}
        
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
                'details': {'missing_params': missing_params}
            }
        else:
            # Erfolgreicher Test (vereinfacht)
            result = {
                'success': True,
                'message': 'Tool-Konfiguration ist gültig',
                'details': {
                    'config_valid': True,
                    'parameters_complete': True
                }
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
        return jsonify({'success': False, 'message': str(e)}), 500

@tools_bp.route('/execute/<tool_id>', methods=['POST'])
def execute_tool(tool_id):
    """Tool ausführen"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'success': False, 'message': 'Tool nicht gefunden'}), 404
        
        # Integration für dieses Tool finden
        integration = next(
            (i for i in integrations_manager.get_all() 
             if i['name'] == tool.get('tool_definition')), 
            None
        )
        
        if not integration:
            return jsonify({'success': False, 'message': 'Integration nicht gefunden'}), 404
        
        # Execution-Parameter aus Request extrahieren
        execution_data = request.get_json() or {}
        inputs = execution_data.get('inputs', {})
        
        # Prefilled und Locked Inputs berücksichtigen
        final_inputs = tool.get('prefilled_inputs', {}).copy()
        locked_inputs = tool.get('locked_inputs', [])
        
        for key, value in inputs.items():
            if key not in locked_inputs:
                final_inputs[key] = value
        
        # Simulated execution (hier würde die echte Tool-Ausführung stattfinden)
        execution_result = {
            'success': True,
            'message': 'Tool erfolgreich ausgeführt (simuliert)',
            'inputs': final_inputs,
            'outputs': {
                'result': f'Ergebnis von {tool["name"]}',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
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
    """API: Tool-Konfiguration abrufen"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'error': 'Tool nicht gefunden'}), 404
        
        return jsonify({
            'id': tool['id'],
            'name': tool['name'],
            'tool_definition': tool['tool_definition'],
            'config': tool.get('config', {}),
            'prefilled_inputs': tool.get('prefilled_inputs', {}),
            'locked_inputs': tool.get('locked_inputs', []),
            'status': tool['status']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
