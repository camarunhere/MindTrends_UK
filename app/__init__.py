from datetime import datetime

from flask import Flask, render_template

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.extensions import init_mongo, login_manager

    init_mongo(app)
    login_manager.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    from app.admin import admin_bp
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.utcnow().year, "app_name": "MindTrends UK"}

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("errors/500.html"), 500

    from app.utils.seed import seed_defaults

    seed_defaults(app)

    return app
