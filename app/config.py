import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Basis-Konfiguration für die Flask-Anwendung."""
    
    # Flask basics
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Data directory
    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    
    # WTF Forms CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Bootstrap
    BOOTSTRAP_SERVE_LOCAL = True
