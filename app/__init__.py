from flask import Flask
from flask_jwt_extended import JWTManager
from .models import db, bcrypt, Role, Mahasiswa, Dosen, Kelas
from .routes import auth, projects, tasks, mahasiswa, dosen, role, kelas
from config import Config
from flask_migrate import Migrate

def create_roles():
    roles = ['Admin', 'Dosen', 'Mahasiswa']
    with db.session.begin():
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                new_role = Role(name=role_name)
                db.session.add(new_role)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(role.bp, url_prefix='/roles')
    app.register_blueprint(projects.bp, url_prefix='/projects')
    app.register_blueprint(tasks.bp, url_prefix='/tasks')
    app.register_blueprint(mahasiswa.bp, url_prefix='/mahasiswa') 
    app.register_blueprint(dosen.bp, url_prefix='/dosen')
    app.register_blueprint(kelas.bp, url_prefix='/kelas')

    # Buat role saat aplikasi dijalankan
    with app.app_context():
        create_roles()

    return app
