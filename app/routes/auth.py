from flask import Blueprint, request, jsonify
from app.models import db, User, Role
from flask_jwt_extended import create_access_token, jwt_required

bp = Blueprint('auth', __name__)

@bp.route('/roles', methods=['POST'])
def create_role():
    data = request.get_json()
    role_name = data.get('name')

    if Role.query.filter_by(name=role_name).first():
        return jsonify({'message': 'Role already exists'}), 400

    new_role = Role(name=role_name)
    db.session.add(new_role)
    db.session.commit()
    return jsonify({'message': 'Role created successfully'}), 201

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role_id = data.get('role_id')

    role = Role.query.get(role_id)
    if not role:
        return jsonify({'message': 'Role does not exist'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 400

    user = User(name=name, email=email, role_id=role_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity={'id': user.id, 'email': user.email, 'role': user.role.name})
        return jsonify({'access_token': access_token}), 200

    return jsonify({'message': 'Invalid email or password'}), 401

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    user_list = [{'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role.name} for u in users]
    return jsonify(user_list)

@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role.name})

@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.name = data.get('name', user.name) 
    user.email = data.get('email', user.email) 
    user.role_id = data.get('role_id', user.role_id) 
    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200
