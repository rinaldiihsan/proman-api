from flask import Blueprint, request, jsonify
from app.models import db, Task, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import jwt_required, get_jwt

bp = Blueprint('tasks', __name__)

@bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_tasks(project_id):
    tasks = Task.query.filter_by(project_id=project_id).all()
    task_list = [{'id': t.id, 'title': t.title, 'description': t.description,
                  'status': t.status, 'due_date': t.due_date, 'assigned_to': t.assigned_to}
                 for t in tasks]
    return jsonify(task_list)

@bp.route('/<int:project_id>', methods=['POST'])
@jwt_required()
def create_task(project_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])

    if user.role.name not in ['Admin', 'Manager']:
        return jsonify({'message': 'Only admins and managers can create tasks'}), 403

    data = request.get_json()
    assigned_to = data.get('assigned_to')

    # Cek apakah assigned_to adalah user yang valid
    assignee = User.query.get(assigned_to)
    if not assignee:
        return jsonify({'message': 'User not found'}), 404

    new_task = Task(
        project_id=project_id,
        assigned_to=assigned_to,
        title=data['title'],
        description=data['description'],
        status=data['status'],
        due_date=data['due_date']
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201

@bp.route('/<int:project_id>/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(project_id, task_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])

    if user.role.name not in ['Admin', 'Manager']:
        return jsonify({'message': 'Only admins and managers can update tasks'}), 403

    data = request.get_json()
    task = Task.query.get(task_id)
    task.title = data['title']
    task.description = data['description']
    task.status = data['status']
    task.due_date = data['due_date']
    db.session.commit()
    return jsonify({'message': 'Task updated successfully'}), 200

@bp.route('/<int:project_id>/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(project_id, task_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])

    if user.role.name not in ['Admin', 'Manager']:
        return jsonify({'message': 'Only admins and managers can delete tasks'}), 403

    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200
