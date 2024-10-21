from flask import Blueprint, request, jsonify
from app.models import db, User, Dosen
from flask_jwt_extended import jwt_required, get_jwt_identity
from .decorators import role_required

bp = Blueprint('dosen', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_all_dosen():
    dosens = Dosen.query.join(User).all()
    return jsonify([{
        'id': d.id,
        'nip': d.nip,
        'user': {
            'id': d.user.id,
            'name': d.user.name,
            'email': d.user.email
        }
    } for d in dosens])

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_dosen(id):
    dosen = Dosen.query.get_or_404(id)
    return jsonify({
        'id': dosen.id,
        'nip': dosen.nip,
        'user': {
            'id': dosen.user.id,
            'name': dosen.user.name,
            'email': dosen.user.email
        }
    })

@bp.route('/', methods=['POST'])
@jwt_required()
@role_required('Admin')
def create_dosen():
    data = request.get_json()
    user_id = data.get('user_id')
    nip = data.get('nip')
    
    if not all([user_id, nip]):
        return jsonify({'message': 'User ID and NIP are required'}), 400
        
    # Cek apakah user exists dan belum memiliki profil dosen
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    if user.dosen_profile:
        return jsonify({'message': 'User already has a lecturer profile'}), 400
        
    # Cek apakah NIP sudah digunakan
    if Dosen.query.filter_by(nip=nip).first():
        return jsonify({'message': 'NIP already exists'}), 400
        
    dosen = Dosen(user_id=user_id, nip=nip)
    db.session.add(dosen)
    db.session.commit()
    
    return jsonify({
        'message': 'Lecturer profile created successfully',
        'dosen': {
            'id': dosen.id,
            'nip': dosen.nip,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required('Admin')
def update_dosen(id):
    dosen = Dosen.query.get_or_404(id)
    data = request.get_json()
    
    if 'nip' in data:
        if Dosen.query.filter(Dosen.id != id, Dosen.nip == data['nip']).first():
            return jsonify({'message': 'NIP already exists'}), 400
        dosen.nip = data['nip']
    
    db.session.commit()
    return jsonify({
        'message': 'Lecturer profile updated successfully',
        'dosen': {
            'id': dosen.id,
            'nip': dosen.nip,
            'user': {
                'id': dosen.user.id,
                'name': dosen.user.name,
                'email': dosen.user.email
            }
        }
    })

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required('Admin')
def delete_dosen(id):
    dosen = Dosen.query.get_or_404(id)
    db.session.delete(dosen)
    db.session.commit()
    return jsonify({'message': 'Lecturer profile deleted successfully'})