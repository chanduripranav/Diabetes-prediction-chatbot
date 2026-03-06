from flask import Flask
from flask_cors import CORS
from .config import Config
from .ml_service import load_model

def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    app.config.from_object(Config)
    CORS(app)

    # Load ML model at startup
    load_model()

    # IMPORTANT: import and register the blueprint
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
