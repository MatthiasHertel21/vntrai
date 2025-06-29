from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect
from app.config import Config
import logging
import os
from datetime import datetime

csrf = CSRFProtect()

def create_app(config_class=Config):
    """Erstellt und konfiguriert die Flask-Anwendung."""
    app = Flask(__name__)
    
    # Config
    app.config.from_object(config_class)
    
    # Initialize extensions
    bootstrap = Bootstrap5(app)
    csrf.init_app(app)
    
    # Stelle sicher, dass das Data-Verzeichnis existiert
    data_dir = app.config['DATA_DIR']
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Stelle sicher, dass der Icons-Ordner existiert
    icons_dir = os.path.join(app.static_folder, 'icons')
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    
    # Template-Filter registrieren
    @app.template_filter('format_datetime')
    def format_datetime_filter(value):
        """Formatiert ein Datum im Format DD.MM.YYYY HH:MM:SS."""
        if not value:
            return ""
        try:
            if isinstance(value, datetime):
                return value.strftime("%d.%m.%Y %H:%M:%S")
            else:
                dt = datetime.fromisoformat(str(value))
                return dt.strftime("%d.%m.%Y %H:%M:%S")
        except (ValueError, TypeError):
            return str(value)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    # Registriere Blueprints
    from app.routes import main
    from app.routes.integrations import integrations_bp
    from app.routes.tools import tools_bp
    from app.routes.test import test_bp
    
    app.register_blueprint(main.bp)
    app.register_blueprint(integrations_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(test_bp)
    
    # Logging setup
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/vntrai.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('VNTRAI startup')
    
    return app
