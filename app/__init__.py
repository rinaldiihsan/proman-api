from flask import Flask
from flask_jwt_extended import JWTManager
from .models import db, bcrypt
from .routes import auth, projects, tasks
from config import Config
from app.models import Role
from flask_migrate import Migrate

def create_roles():
    roles = ['Admin', 'Manager', 'User']
    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            new_role = Role(name=role_name)
            db.session.add(new_role)
    db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inisialisasi Database dan JWT
    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    # Registrasi Blueprints
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(projects.bp, url_prefix='/projects')
    app.register_blueprint(tasks.bp, url_prefix='/tasks')

    return app
