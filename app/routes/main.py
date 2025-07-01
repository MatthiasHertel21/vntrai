from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Dashboard - Hauptseite der Anwendung."""
    return render_template('index.html')

@bp.route('/insights')
def insights():
    """Insights - Interactive conversation agents."""
    from app.utils.data_manager import agents_manager
    
    try:
        # Get all agents
        all_agents = agents_manager.load_all()
        
        # Filter agents that are enabled for insights
        insight_agents = [
            agent for agent in all_agents 
            if agent.get('use_as_insight', False) and agent.get('status') == 'active'
        ]
        
        # Add statistics to each agent
        for agent in insight_agents:
            # Get agent statistics
            stats = agents_manager.get_single_agent_statistics(agent['id'])
            agent.update(stats)
            
            # Load quick actions
            quick_actions = agent.get('quick_actions', [])
            agent['quick_actions_count'] = len(quick_actions)
            
            # Calculate usage stats (placeholder)
            agent['total_conversations'] = stats.get('total_runs', 0)
            agent['avg_response_time'] = '1.2s'  # Placeholder
        
        return render_template('insights.html', agents=insight_agents)
        
    except Exception as e:
        return render_template('insights.html', agents=[], error=str(e))

@bp.route('/flows')
def flows():
    """My Flows Seite."""
    return render_template('flows.html')

@bp.route('/agents')
def agents():
    """Leitet zur neuen Agents-Verwaltung weiter"""
    from flask import redirect, url_for
    return redirect(url_for('agents.list_agents'))

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
    """Übersicht aller verfügbaren Routen"""
    
    # Sammle alle Routen-Informationen
    from app.routes.test import TEST_MODULES
    
    route_groups = {
        'main': {
            'name': 'Hauptnavigation',
            'description': 'Dashboard und grundlegende Seiten',
            'routes': [
                {'method': 'GET', 'path': '/', 'function': 'index', 'description': 'Dashboard/Homepage'},
                {'method': 'GET', 'path': '/insights', 'function': 'insights', 'description': 'Insights und Analytics'},
                {'method': 'GET', 'path': '/profile', 'function': 'profile', 'description': 'Benutzer-Profil'},
                {'method': 'GET', 'path': '/company', 'function': 'company', 'description': 'Firmen-Einstellungen'},
                {'method': 'GET', 'path': '/routes', 'function': 'routes', 'description': 'Diese Routen-Übersicht'},
            ]
        }
    }
    
    # Füge Test-Module hinzu
    for module_id, module_info in TEST_MODULES.items():
        if 'routes' in module_info:
            route_groups[module_id] = {
                'name': module_info['name'],
                'description': module_info['description'],
                'routes': module_info['routes'],
                'file': module_info.get('file', 'N/A')
            }
    
    # Statistiken berechnen
    total_routes = sum(len(group['routes']) for group in route_groups.values())
    get_routes = sum(len([r for r in group['routes'] if r['method'] == 'GET']) for group in route_groups.values())
    post_routes = sum(len([r for r in group['routes'] if r['method'] == 'POST']) for group in route_groups.values())
    
    stats = {
        'total_routes': total_routes,
        'get_routes': get_routes, 
        'post_routes': post_routes,
        'total_groups': len(route_groups)
    }
    
    return render_template('routes.html', route_groups=route_groups, stats=stats)
