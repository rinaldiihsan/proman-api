from flask import Blueprint, request, jsonify
from app.models import db, Project, Task
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from .decorators import role_required

bp = Blueprint('projects', __name__)

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

@bp.route('/', methods=['GET'])
@jwt_required()
def get_projects():
    projects = Project.query.all()
    project_list = []
    
    for project in projects:
        project_data = {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'end_date': project.end_date.strftime('%Y-%m-%d'),
            'status': project.status,
            'tasks': [{
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'due_date': task.due_date.strftime('%Y-%m-%d'),
            } for task in project.tasks]
        }
        project_list.append(project_data)
    
    return jsonify(project_list)

@bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    project_data = {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'start_date': project.start_date.strftime('%Y-%m-%d'),
        'end_date': project.end_date.strftime('%Y-%m-%d'),
        'status': project.status,
        'tasks': [{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'due_date': task.due_date.strftime('%Y-%m-%d'),
            'kelas': {
                'id': task.kelas.id,
                'name': task.kelas.name
            } if task.kelas else None
        } for task in project.tasks]
    }
    
    return jsonify(project_data)

@bp.route('/', methods=['POST'])
@jwt_required()
@role_required('Admin')  # Hanya admin yang bisa membuat project
def create_project():
    data = request.get_json()
    
    if not all(key in data for key in ['name', 'start_date', 'end_date', 'status']):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Validasi tanggal
    start_date = parse_date(data['start_date'])
    end_date = parse_date(data['end_date'])
    
    if not start_date or not end_date:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    if start_date > end_date:
        return jsonify({'message': 'End date must be after start date'}), 400
    
    # Validasi status
    valid_statuses = ['Not Started', 'In Progress', 'Completed', 'On Hold']
    if data['status'] not in valid_statuses:
        return jsonify({'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
    
    new_project = Project(
        name=data['name'],
        description=data.get('description'),
        start_date=start_date,
        end_date=end_date,
        status=data['status']
    )
    
    db.session.add(new_project)
    db.session.commit()
    
    return jsonify({
        'message': 'Project created successfully',
        'project': {
            'id': new_project.id,
            'name': new_project.name,
            'description': new_project.description,
            'start_date': new_project.start_date.strftime('%Y-%m-%d'),
            'end_date': new_project.end_date.strftime('%Y-%m-%d'),
            'status': new_project.status
        }
    }), 201

@bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
@role_required('Admin')
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    
    if 'name' in data:
        project.name = data['name']
    
    if 'description' in data:
        project.description = data['description']
    
    if 'start_date' in data:
        start_date = parse_date(data['start_date'])
        if not start_date:
            return jsonify({'message': 'Invalid start date format. Use YYYY-MM-DD'}), 400
        project.start_date = start_date
    
    if 'end_date' in data:
        end_date = parse_date(data['end_date'])
        if not end_date:
            return jsonify({'message': 'Invalid end date format. Use YYYY-MM-DD'}), 400
        project.end_date = end_date
    
    if project.start_date > project.end_date:
        return jsonify({'message': 'End date must be after start date'}), 400
    
    if 'status' in data:
        valid_statuses = ['Not Started', 'In Progress', 'Completed', 'On Hold']
        if data['status'] not in valid_statuses:
            return jsonify({'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        project.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Project updated successfully',
        'project': {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'end_date': project.end_date.strftime('%Y-%m-%d'),
            'status': project.status
        }
    })

@bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
@role_required('Admin')
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Cek apakah project memiliki tasks
    if project.tasks:
        return jsonify({
            'message': 'Cannot delete project with existing tasks. Delete tasks first.'
        }), 400
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': 'Project deleted successfully'})