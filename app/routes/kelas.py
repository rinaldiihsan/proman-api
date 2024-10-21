from flask import Blueprint, request, jsonify
from app.models import db, Kelas, Task
from flask_jwt_extended import jwt_required, get_jwt_identity
from .decorators import role_required

bp = Blueprint('kelas', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_all_kelas():
    """Get all kelas"""
    kelas_list = Kelas.query.all()
    result = [{
        'id': kelas.id,
        'name': kelas.name,
        'tasks_count': len(kelas.tasks)
    } for kelas in kelas_list]
    return jsonify(result)

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_kelas(id):
    """Get specific kelas by ID"""
    kelas = Kelas.query.get_or_404(id)
    
    # Get tasks for this kelas
    tasks = [{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'due_date': task.due_date.strftime('%Y-%m-%d'),
        'project_id': task.project_id
    } for task in kelas.tasks]
    
    return jsonify({
        'id': kelas.id,
        'name': kelas.name,
        'tasks': tasks
    })

@bp.route('/', methods=['POST'])
@jwt_required()
@role_required('Admin')
def create_kelas():
    """Create new kelas"""
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'message': 'Name is required'}), 400
        
    # Cek apakah nama kelas sudah ada
    if Kelas.query.filter_by(name=name).first():
        return jsonify({'message': 'Class name already exists'}), 400
        
    new_kelas = Kelas(name=name)
    db.session.add(new_kelas)
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Class created successfully',
            'kelas': {
                'id': new_kelas.id,
                'name': new_kelas.name
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating class', 'error': str(e)}), 500

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required('Admin')
def update_kelas(id):
    """Update existing kelas"""
    kelas = Kelas.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        # Cek apakah nama baru sudah ada di kelas lain
        existing_kelas = Kelas.query.filter(
            Kelas.name == data['name'], 
            Kelas.id != id
        ).first()
        if existing_kelas:
            return jsonify({'message': 'Class name already exists'}), 400
            
        kelas.name = data['name']
        
    try:
        db.session.commit()
        return jsonify({
            'message': 'Class updated successfully',
            'kelas': {
                'id': kelas.id,
                'name': kelas.name
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating class', 'error': str(e)}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required('Admin')  # Hanya admin yang bisa menghapus kelas
def delete_kelas(id):
    """Delete a kelas"""
    kelas = Kelas.query.get_or_404(id)
    
    # Cek apakah kelas masih memiliki tasks
    if kelas.tasks:
        return jsonify({
            'message': 'Cannot delete class with existing tasks. Please delete the tasks first'
        }), 400
    
    try:
        db.session.delete(kelas)
        db.session.commit()
        return jsonify({'message': 'Class deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting class', 'error': str(e)}), 500

@bp.route('/<int:id>/tasks', methods=['GET'])
@jwt_required()
def get_kelas_tasks(id):
    """Get all tasks for a specific kelas"""
    kelas = Kelas.query.get_or_404(id)
    
    tasks = [{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'due_date': task.due_date.strftime('%Y-%m-%d'),
        'project': {
            'id': task.project.id,
            'name': task.project.name
        } if task.project else None
    } for task in kelas.tasks]
    
    return jsonify({
        'kelas_id': kelas.id,
        'kelas_name': kelas.name,
        'tasks': tasks
    })

@bp.route('/<int:id>/tasks/status', methods=['GET'])
@jwt_required()
def get_kelas_tasks_status(id):
    """Get task statistics for a kelas"""
    kelas = Kelas.query.get_or_404(id)
    
    # Menghitung jumlah task berdasarkan status
    status_count = {
        'Belum Mulai': 0,
        'In Progress': 0,
        'Completed': 0
    }
    
    for task in kelas.tasks:
        if task.status in status_count:
            status_count[task.status] += 1
    
    return jsonify({
        'kelas_id': kelas.id,
        'kelas_name': kelas.name,
        'task_statistics': status_count,
        'total_tasks': len(kelas.tasks)
    })