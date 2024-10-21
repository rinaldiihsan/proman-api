from flask import Blueprint, request, jsonify
from app.models import db, Task, User, Project, Kelas
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from .decorators import role_required

bp = Blueprint('tasks', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_all_tasks():
    tasks = Task.query.all()
    task_list = [{
        'id': t.id,
        'project_id': t.project_id,
        'kelas_id': t.kelas_id,
        'title': t.title,
        'description': t.description,
        'status': t.status,
        'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
        'project_name': t.project.name,
        'kelas_name': t.kelas.name
    } for t in tasks]
    return jsonify(task_list)

@bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_tasks(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project_id).all()
    
    task_list = [{
        'id': t.id,
        'project_id': t.project_id,
        'kelas_id': t.kelas_id,
        'title': t.title,
        'description': t.description,
        'status': t.status,
        'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
        'kelas_name': t.kelas.name
    } for t in tasks]
    return jsonify(task_list)

@bp.route('/kelas/<int:kelas_id>', methods=['GET'])
@jwt_required()
def get_kelas_tasks(kelas_id):
    kelas = Kelas.query.get_or_404(kelas_id)
    tasks = Task.query.filter_by(kelas_id=kelas_id).all()
    
    task_list = [{
        'id': t.id,
        'project_id': t.project_id,
        'kelas_id': t.kelas_id,
        'title': t.title,
        'description': t.description,
        'status': t.status,
        'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
        'project_name': t.project.name
    } for t in tasks]
    return jsonify(task_list)

@bp.route('/', methods=['POST'])
@jwt_required()
@role_required('Admin')  # Hanya admin yang bisa membuat task
def create_task():
    data = request.get_json()
    
    # Validasi input
    required_fields = ['project_id', 'kelas_id', 'title', 'due_date']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Validasi project dan kelas exist
    project = Project.query.get(data['project_id'])
    kelas = Kelas.query.get(data['kelas_id'])
    
    if not project or not kelas:
        return jsonify({'message': 'Project or Kelas not found'}), 404
    
    try:
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

    new_task = Task(
        project_id=data['project_id'],
        kelas_id=data['kelas_id'],
        title=data['title'],
        description=data.get('description'),
        status=data.get('status', 'Belum Mulai'),
        due_date=due_date
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify({
        'message': 'Task created successfully',
        'task': {
            'id': new_task.id,
            'project_id': new_task.project_id,
            'kelas_id': new_task.kelas_id,
            'title': new_task.title,
            'description': new_task.description,
            'status': new_task.status,
            'due_date': new_task.due_date.strftime('%Y-%m-%d')
        }
    }), 201

@bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
@role_required('Admin')
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'project_id' in data:
        if not Project.query.get(data['project_id']):
            return jsonify({'message': 'Project not found'}), 404
        task.project_id = data['project_id']
        
    if 'kelas_id' in data:
        if not Kelas.query.get(data['kelas_id']):
            return jsonify({'message': 'Kelas not found'}), 404
        task.kelas_id = data['kelas_id']
    
    if 'title' in data:
        task.title = data['title']
    
    if 'description' in data:
        task.description = data['description']
    
    if 'status' in data:
        task.status = data['status']
    
    if 'due_date' in data:
        try:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': 'Task updated successfully',
        'task': {
            'id': task.id,
            'project_id': task.project_id,
            'kelas_id': task.kelas_id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'due_date': task.due_date.strftime('%Y-%m-%d')
        }
    })

@bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
@role_required('Admin')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'})

@bp.route('/<int:task_id>/status', methods=['PUT'])
@jwt_required()
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'message': 'Status is required'}), 400
        
    task.status = data['status']
    db.session.commit()
    
    return jsonify({
        'message': 'Task status updated successfully',
        'status': task.status
    })