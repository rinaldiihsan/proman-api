from flask import Blueprint, request, jsonify
from app.models import db, User, Mahasiswa
from flask_jwt_extended import jwt_required, get_jwt_identity
from .decorators import role_required

bp = Blueprint('mahasiswa', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_all_mahasiswa():
    mahasiswas = Mahasiswa.query.join(User).all()
    return jsonify([{
        'id': m.id,
        'nim': m.nim,
        'user': {
            'id': m.user.id,
            'name': m.user.name,
            'email': m.user.email
        }
    } for m in mahasiswas])

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_mahasiswa(id):
    mahasiswa = Mahasiswa.query.get_or_404(id)
    return jsonify({
        'id': mahasiswa.id,
        'nim': mahasiswa.nim,
        'user': {
            'id': mahasiswa.user.id,
            'name': mahasiswa.user.name,
            'email': mahasiswa.user.email
        }
    })

@bp.route('/', methods=['POST'])
@jwt_required()
@role_required('Admin')
def create_mahasiswa():
    data = request.get_json()
    user_id = data.get('user_id')
    nim = data.get('nim')
    
    if not all([user_id, nim]):
        return jsonify({'message': 'User ID and NIM are required'}), 400
        
    # Cek apakah user exists dan belum memiliki profil mahasiswa
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    if user.mahasiswa_profile:
        return jsonify({'message': 'User already has a student profile'}), 400
        
    # Cek apakah NIM sudah digunakan
    if Mahasiswa.query.filter_by(nim=nim).first():
        return jsonify({'message': 'NIM already exists'}), 400
        
    mahasiswa = Mahasiswa(user_id=user_id, nim=nim)
    db.session.add(mahasiswa)
    db.session.commit()
    
    return jsonify({
        'message': 'Student profile created successfully',
        'mahasiswa': {
            'id': mahasiswa.id,
            'nim': mahasiswa.nim,
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
def update_mahasiswa(id):
    mahasiswa = Mahasiswa.query.get_or_404(id)
    data = request.get_json()
    
    if 'nim' in data:
        if Mahasiswa.query.filter(Mahasiswa.id != id, Mahasiswa.nim == data['nim']).first():
            return jsonify({'message': 'NIM already exists'}), 400
        mahasiswa.nim = data['nim']
    
    db.session.commit()
    return jsonify({
        'message': 'Student profile updated successfully',
        'mahasiswa': {
            'id': mahasiswa.id,
            'nim': mahasiswa.nim,
            'user': {
                'id': mahasiswa.user.id,
                'name': mahasiswa.user.name,
                'email': mahasiswa.user.email
            }
        }
    })

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required('Admin')
def delete_mahasiswa(id):
    mahasiswa = Mahasiswa.query.get_or_404(id)
    db.session.delete(mahasiswa)
    db.session.commit()
    return jsonify({'message': 'Student profile deleted successfully'})