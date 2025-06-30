"""
Integrations Management Routes für vntrai
Basiert auf neuer Datenhaltung mit individuellen JSON-Dateien
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
from app.utils import integrations_manager, validator, icon_manager
from datetime import datetime

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
        
        # KRITISCHER FIX: Datenstruktur-Migration für View-System
        # Migration: Daten aus metadata.original_data auf Root-Level kopieren
        if 'metadata' in integration and 'original_data' in integration['metadata']:
            original = integration['metadata']['original_data']
            
            # JSON-Parameter auf Root-Level migrieren wenn nicht vorhanden
            if 'config_params' not in integration:
                integration['config_params'] = original.get('config_params', [])
            if 'input_params' not in integration:
                integration['input_params'] = original.get('input_params', [])
            if 'output_params' not in integration:
                integration['output_params'] = original.get('output_params', [])
        
        # Sicherstellen, dass Implementation-Feld existiert + Auto-Migration
        if 'implementation' not in integration:
            integration['implementation'] = ''
            
        # AUTO-MIGRATION: ChatGPT → openai_chatcompletion (einmalig)
        if integration.get('name') == 'ChatGPT' and not integration.get('implementation'):
            integration['implementation'] = 'openai_chatcompletion'
            print(f"DEBUG View Auto-Migration - ChatGPT assigned to openai_chatcompletion")
            
        # AUTO-MIGRATION: GoogleSheets → google_sheets (einmalig)  
        if integration.get('name') == 'GoogleSheets' and not integration.get('implementation'):
            integration['implementation'] = 'google_sheets'
            print(f"DEBUG View Auto-Migration - GoogleSheets assigned to google_sheets")
            
        print(f"DEBUG View - Integration {integration_id}: implementation='{integration.get('implementation', 'MISSING')}'")
        
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
        # Lade verfügbare Implementations
        from app.implementation_modules import ImplementationManager
        impl_manager = ImplementationManager()
        available_implementations = impl_manager.list_available_implementations()
        
        # KRITISCHER FIX: Datenstruktur-Migration für Edit-System
        # Migration: Daten aus metadata.original_data auf Root-Level kopieren
        if 'metadata' in integration and 'original_data' in integration['metadata']:
            original = integration['metadata']['original_data']
            
            # JSON-Parameter auf Root-Level migrieren wenn nicht vorhanden
            if 'config_params' not in integration:
                integration['config_params'] = original.get('config_params', [])
            if 'input_params' not in integration:
                integration['input_params'] = original.get('input_params', [])
            if 'output_params' not in integration:
                integration['output_params'] = original.get('output_params', [])
        
        # Sicherstellen, dass alle erforderlichen Felder existieren
        if 'config_params' not in integration:
            integration['config_params'] = []
        if 'input_params' not in integration:
            integration['input_params'] = []
        if 'output_params' not in integration:
            integration['output_params'] = []
        if 'implementation' not in integration:
            integration['implementation'] = ''
            
        # AUTO-MIGRATION: ChatGPT → openai_chatcompletion (einmalig)
        if integration.get('name') == 'ChatGPT' and not integration.get('implementation'):
            integration['implementation'] = 'openai_chatcompletion'
            print(f"DEBUG Auto-Migration - ChatGPT assigned to openai_chatcompletion")
            
        # AUTO-MIGRATION: GoogleSheets → google_sheets (einmalig)  
        if integration.get('name') == 'GoogleSheets' and not integration.get('implementation'):
            integration['implementation'] = 'google_sheets'
            print(f"DEBUG Auto-Migration - GoogleSheets assigned to google_sheets")
            
        print(f"DEBUG Edit GET - Integration {integration_id}: implementation='{integration.get('implementation', 'MISSING')}'")
        print(f"DEBUG Edit GET - Available implementations: {[impl.get('name', 'Unknown') if isinstance(impl, dict) else getattr(impl, 'name', 'Unknown') for impl in available_implementations]}")
        
        integration['icon_url'] = icon_manager.get_icon_path(integration_id)
        return render_template('integrations/edit.html', 
                             integration=integration,
                             available_implementations=available_implementations)
    
    try:
        # KRITISCHER FIX: Migration AUCH beim POST durchführen
        # Migration: Daten aus metadata.original_data auf Root-Level kopieren
        if 'metadata' in integration and 'original_data' in integration['metadata']:
            original = integration['metadata']['original_data']
            
            # JSON-Parameter auf Root-Level migrieren wenn nicht vorhanden
            if 'config_params' not in integration:
                integration['config_params'] = original.get('config_params', [])
                print(f"DEBUG Edit POST - Migrated config_params: {len(integration['config_params'])} items")
            if 'input_params' not in integration:
                integration['input_params'] = original.get('input_params', [])
                print(f"DEBUG Edit POST - Migrated input_params: {len(integration['input_params'])} items")
            if 'output_params' not in integration:
                integration['output_params'] = original.get('output_params', [])
                print(f"DEBUG Edit POST - Migrated output_params: {len(integration['output_params'])} items")
        
        # Form data extrahieren und validieren - nur Basic Fields aktualisieren
        if 'name' in request.form:
            integration['name'] = request.form.get('name', '').strip()
        if 'vendor' in request.form:
            integration['vendor'] = request.form.get('vendor', '').strip()
        if 'type' in request.form:
            integration['type'] = request.form.get('type', 'api')
        if 'description' in request.form:
            integration['description'] = request.form.get('description', '').strip()
        if 'status' in request.form:
            integration['status'] = request.form.get('status', 'inactive')
        if 'version' in request.form:
            integration['version'] = request.form.get('version', '1.0.0')
        if 'implementation' in request.form:
            implementation_value = request.form.get('implementation', '').strip()
            integration['implementation'] = implementation_value
            print(f"DEBUG Edit POST - Setting implementation to: '{implementation_value}'")
        
        # JSON-Felder direkt verarbeiten - nur wenn übermittelt
        config_params = request.form.get('config_params', '')
        input_params = request.form.get('input_params', '')  
        output_params = request.form.get('output_params', '')
        
        print(f"DEBUG Edit POST - Form data received: config_params={bool(config_params.strip())}, input_params={bool(input_params.strip())}, output_params={bool(output_params.strip())}")
        
        # JSON-Felder nur verarbeiten wenn sie übermittelt wurden (nicht-leer)
        if config_params.strip():
            try:
                integration['config_params'] = json.loads(config_params)
                print(f"DEBUG Edit POST - config_params parsed successfully: {len(integration['config_params'])} items")
            except json.JSONDecodeError as e:
                flash(f'Invalid config_params JSON: {str(e)}', 'error')
                # Lade verfügbare Implementations für Fehlerfall
                from app.implementation_modules import ImplementationManager
                impl_manager = ImplementationManager()
                available_implementations = impl_manager.list_available_implementations()
                return render_template('integrations/edit.html', 
                                     integration=integration,
                                     available_implementations=available_implementations)
        # NICHT überschreiben wenn leer - bestehende Daten beibehalten
            
        if input_params.strip():
            try:
                integration['input_params'] = json.loads(input_params)
                print(f"DEBUG Edit POST - input_params parsed successfully: {len(integration['input_params'])} items")
            except json.JSONDecodeError as e:
                flash(f'Invalid input_params JSON: {str(e)}', 'error')
                # Lade verfügbare Implementations für Fehlerfall
                from app.implementation_modules import ImplementationManager
                impl_manager = ImplementationManager()
                available_implementations = impl_manager.list_available_implementations()
                return render_template('integrations/edit.html', 
                                     integration=integration,
                                     available_implementations=available_implementations)
        # NICHT überschreiben wenn leer - bestehende Daten beibehalten
            
        if output_params.strip():
            try:
                integration['output_params'] = json.loads(output_params)
                print(f"DEBUG Edit POST - output_params parsed successfully: {len(integration['output_params'])} items")
            except json.JSONDecodeError as e:
                flash(f'Invalid output_params JSON: {str(e)}', 'error')
                # Lade verfügbare Implementations für Fehlerfall
                from app.implementation_modules import ImplementationManager
                impl_manager = ImplementationManager()
                available_implementations = impl_manager.list_available_implementations()
                return render_template('integrations/edit.html', 
                                     integration=integration,
                                     available_implementations=available_implementations)
        # NICHT überschreiben wenn leer - bestehende Daten beibehalten
        
        # Validierung
        is_valid, errors = validator.validate_integration(integration)
        if not is_valid:
            # Lade verfügbare Implementations für Fehlerfall
            from app.implementation_modules import ImplementationManager
            impl_manager = ImplementationManager()
            available_implementations = impl_manager.list_available_implementations()
            
            for error in errors:
                flash(error, 'error')
            return render_template('integrations/edit.html', 
                                 integration=integration,
                                 available_implementations=available_implementations)
        
        # Sanitization
        integration = validator.sanitize_integration_data(integration)
        
        # Updated timestamp
        integration['updated_at'] = datetime.now().isoformat()
        
        # Icon verarbeiten
        if 'icon' in request.files:
            icon_file = request.files['icon']
            if icon_file.filename:
                filename = secure_filename(icon_file.filename)
                icon_data = icon_file.read()
                icon_manager.save_icon(integration_id, icon_data, filename)
        
        # Speichern
        print(f"DEBUG Edit POST - Before save: implementation='{integration.get('implementation', 'MISSING')}'")
        save_result = integrations_manager.save(integration)
        
        # Nach dem Speichern nochmal prüfen
        saved_integration = integrations_manager.load(integration_id)
        print(f"DEBUG Edit POST - After save reload: implementation='{saved_integration.get('implementation', 'MISSING') if saved_integration else 'NONE'}'")
        
        if save_result:
            print(f"DEBUG Edit POST - Integration saved successfully with implementation: '{integration.get('implementation', 'MISSING')}'")
            flash(f'Integration "{integration["name"]}" updated successfully', 'success')
            return redirect(url_for('integrations.view_integration', integration_id=integration_id))
        else:
            flash('Failed to save integration', 'error')
            
    except Exception as e:
        # Lade verfügbare Implementations für Fehlerfall
        from app.implementation_modules import ImplementationManager
        impl_manager = ImplementationManager()
        available_implementations = impl_manager.list_available_implementations()
        
        flash(f'Error updating integration: {str(e)}', 'error')
    
    return render_template('integrations/edit.html', 
                         integration=integration,
                         available_implementations=available_implementations)

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

@integrations_bp.route('/bind-implementation/<integration_id>', methods=['POST'])
def bind_implementation(integration_id):
    """Bindet eine Implementation an eine Integration"""
    try:
        implementation_name = request.form.get('implementation')
        
        if not implementation_name:
            flash('Bitte wählen Sie eine Implementation aus', 'error')
            return redirect(url_for('integrations.view_integration', integration_id=integration_id))
        
        # Lade Integration
        integration = integrations_manager.load_by_id(integration_id)
        if not integration:
            flash('Integration nicht gefunden', 'error')
            return redirect(url_for('integrations.list_integrations'))
        
        # Prüfe ob Implementation verfügbar ist
        from app.implementation_modules import ImplementationManager
        impl_manager = ImplementationManager()
        
        if implementation_name not in impl_manager.get_available_implementations():
            flash(f'Implementation "{implementation_name}" nicht verfügbar', 'error')
            return redirect(url_for('integrations.view_integration', integration_id=integration_id))
        
        # Binde Implementation
        integration['implementation'] = implementation_name
        integration['status'] = 'active' if implementation_name else 'inactive'
        integration['updated_at'] = datetime.now().isoformat()
        
        # Speichere Integration
        if integrations_manager.save(integration):
            flash(f'Implementation "{implementation_name}" erfolgreich zugewiesen', 'success')
        else:
            flash('Fehler beim Speichern der Integration', 'error')
            
    except Exception as e:
        flash(f'Fehler beim Zuweisen der Implementation: {str(e)}', 'error')
    
    return redirect(url_for('integrations.view_integration', integration_id=integration_id))

@integrations_bp.route('/unbind-implementation/<integration_id>', methods=['POST'])
def unbind_implementation(integration_id):
    """Entfernt Implementation-Binding von einer Integration"""
    try:
        # Lade Integration
        integration = integrations_manager.load_by_id(integration_id)
        if not integration:
            flash('Integration nicht gefunden', 'error')
            return redirect(url_for('integrations.list_integrations'))
        
        # Entferne Implementation
        if 'implementation' in integration:
            del integration['implementation']
        
        integration['status'] = 'inactive'
        integration['updated_at'] = datetime.now().isoformat()
        
        # Speichere Integration
        if integrations_manager.save(integration):
            flash('Implementation erfolgreich entfernt', 'success')
        else:
            flash('Fehler beim Speichern der Integration', 'error')
            
    except Exception as e:
        flash(f'Fehler beim Entfernen der Implementation: {str(e)}', 'error')
    
    return redirect(url_for('integrations.view_integration', integration_id=integration_id))
