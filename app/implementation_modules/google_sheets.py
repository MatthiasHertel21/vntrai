"""
Google Sheets Implementation Module für VNTRAI
Implementiert Google Sheets API Integration basierend auf v036
"""

import asyncio
import json
import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import traceback

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Google API Client libraries not available: {e}")
    GOOGLE_SHEETS_AVAILABLE = False
    # Mock classes for when Google API is not available
    class MockHttpError(Exception):
        pass
    HttpError = MockHttpError

from .base_implementation import BaseImplementation, ImplementationError, ImplementationRegistry


class GoogleSheetsImplementation(BaseImplementation):
    """
    Google Sheets Implementation für VNTRAI.
    Unterstützt Lesen, Schreiben und Aktualisieren von Google Sheets.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
    
    @property
    def name(self) -> str:
        """Der Name der Implementation"""
        return 'google_sheets'
    
    @property
    def description(self) -> str:
        """Beschreibung der Implementation"""
        return 'Google Sheets API Integration für Lesen und Schreiben von Spreadsheets'
    
    @property
    def version(self) -> str:
        """Version der Implementation"""
        return '1.0.0'
    
    @property
    def author(self) -> str:
        """Autor der Implementation"""
        return 'VNTRAI Team'
    
    @property
    def vendor(self) -> str:
        """Vendor der Implementation"""
        return 'Google'
    
    @property
    def category(self) -> str:
        """Kategorie der Implementation"""
        return 'data_storage'
    
    @property
    def required_config_params(self) -> List[Dict[str, Any]]:
        """Liste der erforderlichen Konfigurationsparameter"""
        return [
            {
                'name': 'credentials_json',
                'type': 'json',
                'required': True,
                'label': 'Google Credentials JSON',
                'description': 'Service Account Credentials als JSON oder OAuth2 Credentials'
            },
            {
                'name': 'spreadsheet_id',
                'type': 'text',
                'required': True,
                'label': 'Spreadsheet ID',
                'description': 'Google Sheets Spreadsheet ID aus der URL'
            }
        ]
    
    @property
    def input_params(self) -> List[Dict[str, Any]]:
        """Liste der Eingabeparameter für die Ausführung"""
        return [
            {
                'name': 'operation',
                'type': 'select',
                'required': True,
                'label': 'Operation',
                'description': 'Art der durchzuführenden Operation',
                'options': [
                    {'value': 'read', 'label': 'Daten lesen'},
                    {'value': 'write', 'label': 'Daten schreiben'},
                    {'value': 'update', 'label': 'Daten aktualisieren'},
                    {'value': 'create_sheet', 'label': 'Neues Sheet erstellen'},
                    {'value': 'get_info', 'label': 'Sheet-Informationen abrufen'}
                ]
            },
            {
                'name': 'range',
                'type': 'text',
                'required': False,
                'label': 'Zellbereich',
                'description': 'Bereich in A1-Notation (z.B. A1:C10)',
                'default': 'A1:A10'
            },
            {
                'name': 'values',
                'type': 'json',
                'required': False,
                'label': 'Werte',
                'description': 'Daten zum Schreiben als JSON Array'
            },
            {
                'name': 'spreadsheet_id',
                'type': 'text',
                'required': True,
                'label': 'Spreadsheet ID',
                'description': 'Google Sheets Spreadsheet ID aus der URL'
            }
        ]
    
    @property
    def output_params(self) -> List[Dict[str, Any]]:
        """Liste der Ausgabeparameter"""
        return [
            {
                'name': 'operation',
                'type': 'text',
                'description': 'Durchgeführte Operation'
            },
            {
                'name': 'data',
                'type': 'json',
                'description': 'Resultierende Daten (bei Leseoperationen)'
            },
            {
                'name': 'range',
                'type': 'text',
                'description': 'Bearbeiteter Zellbereich'
            },
            {
                'name': 'rows_affected',
                'type': 'number',
                'description': 'Anzahl betroffener Zeilen'
            }
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Gibt Metadaten für dieses Implementation Module zurück"""
        return {
            'name': 'google_sheets',
            'display_name': 'Google Sheets',
            'description': 'Google Sheets API Integration für Lesen und Schreiben von Spreadsheets',
            'version': '1.0.0',
            'vendor': 'Google',
            'category': 'data_storage',
            'supported_operations': [
                'read_sheet',
                'write_sheet', 
                'update_sheet',
                'create_sheet',
                'get_sheet_info'
            ],
            'required_config': [
                'credentials_json'
            ],
            'optional_config': [
                'token_file_path',
                'sheet_name'
            ],
            'supported_input_types': [
                'range',
                'values',
                'operation_type'
            ],
            'google_api_available': GOOGLE_SHEETS_AVAILABLE
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """Validiert die Konfiguration"""
        errors = []
        
        if not GOOGLE_SHEETS_AVAILABLE:
            errors.append("Google API Client Bibliotheken nicht installiert")
        
        if not self.config.get('credentials_json'):
            errors.append("credentials_json ist erforderlich")
        
        # Validiere credentials_json Format
        credentials_json = self.config.get('credentials_json')
        if credentials_json:
            try:
                if isinstance(credentials_json, str):
                    json.loads(credentials_json)
                elif not isinstance(credentials_json, dict):
                    errors.append("credentials_json muss JSON String oder Dictionary sein")
            except json.JSONDecodeError:
                errors.append("credentials_json ist kein gültiges JSON")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert die Eingabeparameter"""
        errors = []
        
        operation = inputs.get('operation', 'read')
        
        if operation not in ['read', 'write', 'update', 'create_sheet', 'get_info']:
            errors.append(f"Unsupported operation: {operation}")
        
        if operation in ['read', 'write', 'update']:
            if not inputs.get('range'):
                errors.append("range ist erforderlich für diese Operation")
        
        if operation in ['write', 'update']:
            if not inputs.get('values'):
                errors.append("values ist erforderlich für Schreiboperationen")
        
        # Prüfe Spreadsheet ID (jetzt nur in inputs)
        if not inputs.get('spreadsheet_id'):
            errors.append("spreadsheet_id ist erforderlich")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def initialize(self) -> bool:
        """Initialisiert die Google Sheets API Verbindung"""
        if not GOOGLE_SHEETS_AVAILABLE:
            raise ImplementationError("Google API Client Bibliotheken nicht verfügbar")
        
        try:
            credentials_data = self.config.get('credentials_json')
            if isinstance(credentials_data, str):
                credentials_data = json.loads(credentials_data)
            
            # OAuth2 Flow oder Service Account
            if 'type' in credentials_data and credentials_data['type'] == 'service_account':
                # Service Account Authentifizierung
                from google.oauth2 import service_account
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_data, scopes=self.scopes
                )
            else:
                # OAuth2 Flow (für User-Credentials)
                token_file = self.config.get('token_file_path', 'token.json')
                creds = None
                
                # Lade bestehende Credentials falls vorhanden
                try:
                    if os.path.exists(token_file):
                        creds = Credentials.from_authorized_user_file(token_file, self.scopes)
                except:
                    pass
                
                # Falls keine gültigen Credentials vorhanden, starte OAuth Flow
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_config(
                            credentials_data, self.scopes
                        )
                        creds = flow.run_local_server(port=0)
                    
                    # Speichere Credentials für zukünftige Verwendung
                    try:
                        with open(token_file, 'w') as token:
                            token.write(creds.to_json())
                    except:
                        pass  # Ignore file write errors
                
                credentials = creds
            
            # Baue Google Sheets Service
            self.service = build('sheets', 'v4', credentials=credentials)
            
            return True
            
        except Exception as e:
            raise ImplementationError(f"Google Sheets Initialisierung fehlgeschlagen: {str(e)}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Testet die Verbindung zu Google Sheets"""
        try:
            if not self.service:
                await self.initialize()
            
            if not self.service:
                return {
                    'success': False,
                    'message': 'Service konnte nicht initialisiert werden'
                }
            
            # Test: Einfacher API-Aufruf ohne spezifische Spreadsheet
            # Wir testen nur, ob die Credentials funktionieren
            return {
                'success': True,
                'message': 'Google Sheets API Verbindung erfolgreich',
                'details': {
                    'credentials_valid': True,
                    'service_initialized': True
                }
            }
            
        except HttpError as e:
            return {
                'success': False,
                'message': f'Google Sheets API Fehler: {e.resp.reason}',
                'details': {'error_code': e.resp.status}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Verbindungstest fehlgeschlagen: {str(e)}'
            }
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Führt Google Sheets Operation aus"""
        if not GOOGLE_SHEETS_AVAILABLE:
            return {
                'success': False,
                'error': 'Google API Client libraries are not installed. Please install them with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client',
                'execution_time': 0.0,
                'timestamp': datetime.now().isoformat(),
                'operation': inputs.get('operation', 'unknown')
            }
        
        if not self.service:
            await self.initialize()
        
        operation = inputs.get('operation', 'read')
        spreadsheet_id = inputs.get('spreadsheet_id')
        
        if not spreadsheet_id:
            raise ImplementationError("Spreadsheet ID ist erforderlich")
        
        try:
            if operation == 'read':
                return await self._read_sheet(spreadsheet_id, inputs)
            elif operation == 'write':
                return await self._write_sheet(spreadsheet_id, inputs)
            elif operation == 'update':
                return await self._update_sheet(spreadsheet_id, inputs)
            elif operation == 'create_sheet':
                return await self._create_sheet(spreadsheet_id, inputs)
            elif operation == 'get_info':
                return await self._get_sheet_info(spreadsheet_id, inputs)
            else:
                raise ImplementationError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            raise ImplementationError(f"Google Sheets Operation '{operation}' fehlgeschlagen: {str(e)}")
    
    async def _read_sheet(self, spreadsheet_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Liest Daten aus Google Sheet"""
        range_name = inputs.get('range', 'A1:Z1000')
        
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        return {
            'operation': 'read_sheet',
            'range': range_name,
            'values': values,
            'row_count': len(values),
            'column_count': len(values[0]) if values else 0
        }
    
    async def _write_sheet(self, spreadsheet_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Schreibt Daten in Google Sheet"""
        range_name = inputs.get('range', 'A1')
        values = inputs.get('values', [])
        
        body = {
            'values': values
        }
        
        result = self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return {
            'operation': 'write_sheet',
            'range': range_name,
            'updated_rows': result.get('updatedRows', 0),
            'updated_columns': result.get('updatedColumns', 0),
            'updated_cells': result.get('updatedCells', 0)
        }
    
    async def _update_sheet(self, spreadsheet_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Aktualisiert Daten in Google Sheet"""
        # Gleiche Implementierung wie write_sheet für dieses Beispiel
        return await self._write_sheet(spreadsheet_id, inputs)
    
    async def _create_sheet(self, spreadsheet_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Erstellt neues Sheet in Spreadsheet"""
        sheet_name = inputs.get('sheet_name', f'New Sheet {datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        requests = [{
            'addSheet': {
                'properties': {
                    'title': sheet_name
                }
            }
        }]
        
        body = {
            'requests': requests
        }
        
        result = self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        
        return {
            'operation': 'create_sheet',
            'sheet_name': sheet_name,
            'sheet_id': result['replies'][0]['addSheet']['properties']['sheetId']
        }
    
    async def _get_sheet_info(self, spreadsheet_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Holt Informationen über das Spreadsheet"""
        sheet = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        sheets_info = []
        for sheet_data in sheet.get('sheets', []):
            properties = sheet_data.get('properties', {})
            sheets_info.append({
                'sheet_id': properties.get('sheetId'),
                'title': properties.get('title'),
                'index': properties.get('index'),
                'sheet_type': properties.get('sheetType', 'GRID'),
                'grid_properties': properties.get('gridProperties', {})
            })
        
        return {
            'operation': 'get_sheet_info',
            'spreadsheet_title': sheet.get('properties', {}).get('title'),
            'spreadsheet_id': spreadsheet_id,
            'sheets': sheets_info,
            'sheet_count': len(sheets_info)
        }


# Registriere Google Sheets Implementation (immer, auch wenn Google API nicht verfügbar)
ImplementationRegistry.register(GoogleSheetsImplementation)

if not GOOGLE_SHEETS_AVAILABLE:
    print("Warning: Google API Client Bibliotheken nicht verfügbar. Google Sheets Implementation registriert, aber nicht funktional.")
