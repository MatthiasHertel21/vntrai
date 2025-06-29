from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Dashboard - Hauptseite der Anwendung."""
    return render_template('index.html')

@bp.route('/insights')
def insights():
    """My Insights Seite."""
    return render_template('insights.html')

@bp.route('/flows')
def flows():
    """My Flows Seite."""
    return render_template('flows.html')

@bp.route('/agents')
def agents():
    """Agents Seite."""
    return render_template('agents.html')

@bp.route('/prompts')
def prompts():
    """Prompts Seite."""
    return render_template('prompts.html')

@bp.route('/tools')
def tools():
    """Leitet zur neuen Tools-Verwaltung weiter"""
    from flask import redirect, url_for
    return redirect(url_for('tools.list_tools'))

@bp.route('/integrations')
def integrations():
    """Leitet zur neuen Integrations-Verwaltung weiter"""
    from flask import redirect, url_for
    return redirect(url_for('integrations.list_integrations'))

@bp.route('/datasets')
def datasets():
    """Datasets Seite."""
    return render_template('datasets.html')

@bp.route('/flowboards')
def flowboards():
    """Flowboards Seite."""
    return render_template('flowboards.html')

@bp.route('/profile')
def profile():
    """User Profile Seite."""
    return render_template('profile.html')

@bp.route('/company')
def company():
    """Company Seite."""
    return render_template('company.html')

@bp.route('/routes')
def routes():
    """Routen-Übersicht - Liste aller verfügbaren Routen."""
    return render_template('routes.html')
