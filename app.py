import os
from flask import Flask, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config_by_name

# Initialize Limiter for Security
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name=None):
    """
    Application Factory - Standard Flask Pattern.
    Focuses on Google GenAI & Maps integrations.
    """
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize Extensions for Security & Cross-Origin
    CORS(app)
    limiter.init_app(app)

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
