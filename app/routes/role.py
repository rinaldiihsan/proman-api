from flask import Blueprint, request, jsonify
from app.models import db, Role
from flask_jwt_extended import jwt_required
from .decorators import role_required

bp = Blueprint('role', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_roles():
    roles = Role.query.all()
    return jsonify([{
        'id': role.id,
        'name': role.name
    } for role in roles])

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_role(id):
    role = Role.query.get_or_404(id)
    return jsonify({
        'id': role.id,
        'name': role.name
    })

@bp.route('/', methods=['POST'])
@jwt_required()
@role_required('Admin')
def create_role():
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'message': 'Role name is required'}), 400
        
    if Role.query.filter_by(name=name).first():
        return jsonify({'message': 'Role already exists'}), 400
        
    role = Role(name=name)
    db.session.add(role)
    db.session.commit()
    
    return jsonify({
        'message': 'Role created successfully',
        'role': {'id': role.id, 'name': role.name}
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required('Admin')
def update_role(id):
    role = Role.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        if Role.query.filter(Role.id != id, Role.name == data['name']).first():
            return jsonify({'message': 'Role name already exists'}), 400
        role.name = data['name']
        
    db.session.commit()
    return jsonify({
        'message': 'Role updated successfully',
        'role': {'id': role.id, 'name': role.name}
    })

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required('Admin')
def delete_role(id):
    role = Role.query.get_or_404(id)
    
    # Cek apakah role masih digunakan
    if role.users:
        return jsonify({'message': 'Cannot delete role that is still in use'}), 400
        
    db.session.delete(role)
    db.session.commit()
    return jsonify({'message': 'Role deleted successfully'})