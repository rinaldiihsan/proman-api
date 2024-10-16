from flask import Blueprint, request, jsonify
from app.models import db, Project
from flask_jwt_extended import jwt_required

bp = Blueprint('projects', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_projects():
    projects = Project.query.all()
    project_list = [{'id': p.id, 'name': p.name, 'description': p.description,
                     'start_date': p.start_date, 'end_date': p.end_date, 'status': p.status}
                    for p in projects]
    return jsonify(project_list)

@bp.route('/', methods=['POST'])
@jwt_required()
def create_project():
    data = request.get_json()
    new_project = Project(
        name=data['name'],
        description=data['description'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        status=data['status']
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify({'message': 'Project created successfully'}), 201

@bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    data = request.get_json()
    project = Project.query.get(project_id)
    project.name = data['name']
    project.description = data['description']
    project.start_date = data['start_date']
    project.end_date = data['end_date']
    project.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Project updated successfully'}), 200

@bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    project = Project.query.get(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted successfully'}), 200
