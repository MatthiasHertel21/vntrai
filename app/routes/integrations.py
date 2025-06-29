"""
Integrations Management Routes für vntrai
Basiert auf neuer Datenhaltung mit individuellen JSON-Dateien
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
from app.utils import integrations_manager, validator, icon_manager

integrations_bp = Blueprint('integrations', __name__, url_prefix='/integrations')

@integrations_bp.route('/')
def list_integrations():
    """Zeigt Liste aller Integrations"""
    try:
        integrations = integrations_manager.load_all()
        stats = integrations_manager.get_stats()
        
        # Filter und Suche
        search_query = request.args.get('search', '')
        vendor_filter = request.args.get('vendor', '')
        status_filter = request.args.get('status', '')
        type_filter = request.args.get('type', '')
        
        if search_query:
            integrations = integrations_manager.search(search_query)
        
        if vendor_filter:
            integrations = [i for i in integrations if i.get('vendor', '').lower() == vendor_filter.lower()]
        
        if status_filter:
            integrations = [i for i in integrations if i.get('status') == status_filter]
            
        if type_filter:
            integrations = [i for i in integrations if i.get('type') == type_filter]
        
        # Icons hinzufügen
        for integration in integrations:
            integration['icon_url'] = icon_manager.get_icon_path(integration['id'])
        
        # Vendor-Liste für Filter
        all_integrations = integrations_manager.load_all()
        vendors = sorted(set(i.get('vendor', '') for i in all_integrations if i.get('vendor')))
        
        return render_template('integrations/list.html', 
                             integrations=integrations,
                             stats=stats,
                             vendors=vendors,
                             search_query=search_query,
                             vendor_filter=vendor_filter,
                             status_filter=status_filter,
                             type_filter=type_filter)
        
    except Exception as e:
        flash(f'Error loading integrations: {str(e)}', 'error')
        return render_template('integrations/list.html', integrations=[], stats={})

@integrations_bp.route('/view/<integration_id>')
def view_integration(integration_id):
    """Zeigt Details einer Integration"""
    try:
        integration = integrations_manager.load(integration_id)
        if not integration:
            flash('Integration not found', 'error')
            return redirect(url_for('integrations.list_integrations'))
        
        # Icon URL hinzufügen
        integration['icon_url'] = icon_manager.get_icon_path(integration_id)
        
        return render_template('integrations/view.html', integration=integration)
        
    except Exception as e:
        flash(f'Error loading integration: {str(e)}', 'error')
        return redirect(url_for('integrations.list_integrations'))

@integrations_bp.route('/create', methods=['GET', 'POST'])
def create_integration():
    """Erstellt neue Integration"""
    if request.method == 'GET':
        return render_template('integrations/create.html')
    
    try:
        # Form data extrahieren
        name = request.form.get('name', '').strip()
        vendor = request.form.get('vendor', '').strip()
        integration_type = request.form.get('type', 'api')
        description = request.form.get('description', '').strip()
        
        if not name or not vendor:
            flash('Name and vendor are required', 'error')
            return render_template('integrations/create.html')
        
        # Integration erstellen
        integration = integrations_manager.create_integration(name, vendor, integration_type)
        if integration:
            integration['description'] = description
            
            # Icon verarbeiten
            if 'icon' in request.files:
                icon_file = request.files['icon']
                if icon_file.filename:
                    filename = secure_filename(icon_file.filename)
                    icon_data = icon_file.read()
                    icon_manager.save_icon(integration['id'], icon_data, filename)
            
            # Speichern
            if integrations_manager.save(integration):
                flash(f'Integration "{name}" created successfully', 'success')
                return redirect(url_for('integrations.view_integration', integration_id=integration['id']))
            else:
                flash('Failed to save integration', 'error')
        else:
            flash('Failed to create integration', 'error')
            
    except Exception as e:
        flash(f'Error creating integration: {str(e)}', 'error')
    
    return render_template('integrations/create.html')

@integrations_bp.route('/edit/<integration_id>', methods=['GET', 'POST'])
def edit_integration(integration_id):
    """Bearbeitet bestehende Integration"""
    integration = integrations_manager.load(integration_id)
    if not integration:
        flash('Integration not found', 'error')
        return redirect(url_for('integrations.list_integrations'))
    
    if request.method == 'GET':
        integration['icon_url'] = icon_manager.get_icon_path(integration_id)
        return render_template('integrations/edit.html', integration=integration)
    
    try:
        # Form data extrahieren und validieren
        integration['name'] = request.form.get('name', '').strip()
        integration['vendor'] = request.form.get('vendor', '').strip()
        integration['type'] = request.form.get('type', 'api')
        integration['description'] = request.form.get('description', '').strip()
        integration['status'] = request.form.get('status', 'inactive')
        integration['version'] = request.form.get('version', '1.0.0')
        
        # JSON-Felder verarbeiten (v036 Format)
        config_params_data = request.form.get('config_params_data', '')
        input_params_data = request.form.get('input_params_data', '')
        output_params_data = request.form.get('output_params_data', '')
        
        if config_params_data:
            integration['config_params'] = json.loads(config_params_data)
        if input_params_data:
            integration['input_params'] = json.loads(input_params_data)
        if output_params_data:
            integration['output_params'] = json.loads(output_params_data)
        
        # Validierung
        is_valid, errors = validator.validate_integration(integration)
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('integrations/edit.html', integration=integration)
        
        # Sanitization
        integration = validator.sanitize_integration_data(integration)
        
        # Icon verarbeiten
        if 'icon' in request.files:
            icon_file = request.files['icon']
            if icon_file.filename:
                filename = secure_filename(icon_file.filename)
                icon_data = icon_file.read()
                icon_manager.save_icon(integration_id, icon_data, filename)
        
        # Speichern
        if integrations_manager.save(integration):
            flash(f'Integration "{integration["name"]}" updated successfully', 'success')
            return redirect(url_for('integrations.view_integration', integration_id=integration_id))
        else:
            flash('Failed to save integration', 'error')
            
    except Exception as e:
        flash(f'Error updating integration: {str(e)}', 'error')
    
    return render_template('integrations/edit.html', integration=integration)

@integrations_bp.route('/delete/<integration_id>', methods=['POST'])
def delete_integration(integration_id):
    """Löscht Integration"""
    try:
        integration = integrations_manager.load(integration_id)
        if not integration:
            flash('Integration not found', 'error')
            return redirect(url_for('integrations.list_integrations'))
        
        # Integration und Icon löschen
        if integrations_manager.delete(integration_id):
            icon_manager.delete_icon(integration_id)
            flash(f'Integration "{integration["name"]}" deleted successfully', 'success')
        else:
            flash('Failed to delete integration', 'error')
            
    except Exception as e:
        flash(f'Error deleting integration: {str(e)}', 'error')
    
    return redirect(url_for('integrations.list_integrations'))

@integrations_bp.route('/api/config/<integration_id>')
def get_integration_config(integration_id):
    """API: Konfiguration einer Integration abrufen"""
    try:
        integration = integrations_manager.load(integration_id)
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        return jsonify({
            'id': integration['id'],
            'name': integration['name'],
            'vendor': integration['vendor'],
            'type': integration['type'],
            'config_params': integration.get('config_params', []),
            'input_params': integration.get('input_params', []),
            'output_params': integration.get('output_params', []),
            'status': integration['status']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/api/config/<integration_id>', methods=['PUT'])
def update_integration_config(integration_id):
    """API: Konfiguration einer Integration aktualisieren"""
    try:
        integration = integrations_manager.load(integration_id)
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Config-Felder aktualisieren (v036 Format)
        if 'config_params' in data:
            integration['config_params'] = data['config_params']
        
        if 'input_params' in data:
            integration['input_params'] = data['input_params']
            
        if 'output_params' in data:
            integration['output_params'] = data['output_params']
        
        if 'status' in data:
            integration['status'] = data['status']
        
        # Validierung
        is_valid, errors = validator.validate_integration(integration)
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Speichern
        if integrations_manager.save(integration):
            return jsonify({'message': 'Configuration updated successfully'})
        else:
            return jsonify({'error': 'Failed to save configuration'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/api/test/<integration_id>', methods=['POST'])
def test_integration(integration_id):
    """API: Integration testen"""
    try:
        integration = integrations_manager.load(integration_id)
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # TODO: Implementiere spezifische Tests basierend auf Integration Type
        # Für jetzt nur basic validation
        
        config = integration.get('config', {})
        auth = integration.get('auth', {})
        
        # Basic checks
        test_results = {
            'config_valid': bool(config),
            'auth_configured': bool(auth),
            'endpoints_defined': bool(integration.get('endpoints', {})),
            'status': integration.get('status', 'unknown')
        }
        
        # Overall test result
        test_results['success'] = all([
            test_results['config_valid'],
            integration.get('status') != 'error'
        ])
        
        return jsonify(test_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/export')
def export_integrations():
    """Exportiert alle Integrations als JSON"""
    try:
        integrations = integrations_manager.load_all()
        
        # Remove sensitive data for export
        export_data = []
        for integration in integrations:
            export_item = integration.copy()
            # Remove auth data for security
            if 'auth' in export_item:
                export_item['auth'] = {}
            export_data.append(export_item)
        
        from flask import make_response
        response = make_response(jsonify(export_data))
        response.headers['Content-Disposition'] = 'attachment; filename=integrations_export.json'
        response.headers['Content-Type'] = 'application/json'
        
        return response
        
    except Exception as e:
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(url_for('integrations.list_integrations'))
