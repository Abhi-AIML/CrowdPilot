import os
from flask import Flask, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config_by_name
from flask_compress import Compress
import firebase_admin
from firebase_admin import credentials

# Initialize Limiter for Security
limiter = Limiter(key_func=get_remote_address)
compress = Compress()

def create_app(config_name: str = None) -> Flask:
    """
    Application Factory - Standard Flask Pattern.
    
    Initializes the Flask app with all security middlewares, global rate 
    limiting, Gzip compression, and integrates deeply with Google GenAI, 
    Google Maps, Firebase, and Google Cloud operations suite.
    
    Args:
        config_name (str, optional): The environment name to load config for.
        
    Returns:
        Flask: The fully configured Flask WSGI application.
    """
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize Extensions for Security, Cross-Origin, and Efficiency
    CORS(app)
    limiter.init_app(app)
    compress.init_app(app)

    # Initialize Google Cloud Logging (Google Services Integration)
    try:
        import google.cloud.logging
        client = google.cloud.logging.Client()
        client.setup_logging()
    except Exception as e:
        app.logger.warning(f"Google Cloud Logging skipped for local demo: {e}")

    # Initialize Firebase for robust Auth & Storage (Google Services Integration)
    try:
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {'projectId': 'prompt-wars-demo'})
    except Exception as e:
        app.logger.warning(f"Firebase initialization skipped for demo: {e}")

    # Register Blueprints for Modular Architecture
    from blueprints.crowd import crowd_bp
    from blueprints.concierge import concierge_bp
    from blueprints.auth import auth_bp
    from blueprints.alerts import alerts_bp
    
    app.register_blueprint(crowd_bp)
    app.register_blueprint(concierge_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(alerts_bp)

    @app.route('/')
    def landing():
        return render_template('landing.html')

    @app.route('/dashboard')
    def index():
        return render_template('index.html')

    @app.route('/staff')
    def staff():
        return render_template('staff.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
