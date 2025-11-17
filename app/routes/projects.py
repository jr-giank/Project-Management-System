
from flask import Blueprint, jsonify, request

from app.models.projects import Project
from app.models.tasks import Task
from app.extensions import db
from app.auth import token_required, manager_required

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('', methods=['POST'])
@token_required
@manager_required
def create_project(current_user):
    """
    Create a new project
    ---
    tags:
      - Projects
    parameters:
      - in: body
        name: project
        description: The project to create
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      201:
        description: Project created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                description:
                  type: string
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    
    data_fields = ['name']

    for field in data_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
        
    new_project = Project(
        name=data['name'],
        description=data.get('description')
    )

    db.session.add(new_project)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({
        "id": new_project.id,
        "name": new_project.name,
        "description": new_project.description
    }), 201

@projects_bp.route('', methods=['GET'])
@token_required
def get_projects(current_user):
    """
    Get projects with pagination
    ---
    tags:
      - Projects
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
        description: Number of projects per page
    responses:
      200:
        description: Projects retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                total:
                  type: integer
                  description: Total number of projects
                page:
                  type: integer
                  description: Current page number
                per_page:
                  type: integer
                  description: Number of projects per page
                pages:
                  type: integer
                  description: Total number of pages
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      description:
                        type: string
    """

    page = request.args.get("page", 1, int)
    limit = request.args.get("per_page", 10, int)

    pagination = Project.query.paginate(page=page, per_page=limit, error_out=False)

    return jsonify({
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "data": [{
          "id": project.id, 
          "name": project.name, 
          "description": project.description} for project in pagination.items
        ]
    }), 200

@projects_bp.route('/<project_id>', methods=['GET'])
@token_required
def get_project(current_user, project_id):
    """
    Get project by ID
    ---
    tags:
      - Projects
    parameters:
      - in: path
        name: project_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Project retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                description:
                  type: string
      404:
        description: Project not found
    """

    try:
        project_id = int(project_id)
    except ValueError:
        return jsonify({'error': 'Invalid ID format'}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    return jsonify({
        "id": project.id,
        "name": project.name,
        "description": project.description
    }), 200

@projects_bp.route('/<project_id>', methods=['PUT'])
@token_required
@manager_required
def update_project(current_user, project_id):
    """
    Update project by ID
    ---
    tags:
      - Projects
    parameters:
      - in: path
        name: project_id
        required: true
        schema:
          type: integer
      - in: body
        name: project
        description: The project data to update
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      200:
        description: Project updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                description:
                  type: string
      404:
        description: Project not found
    """

    try:
        project_id = int(project_id)
    except ValueError:
        return jsonify({'error': 'Invalid ID format'}), 400
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    
    data_fields = ['name', 'description']

    for field in data_fields:
        if field in data:
            setattr(project, field, data[field])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({
        "id": project.id,
        "name": project.name,
        "description": project.description
    }), 200

@projects_bp.route('/<project_id>', methods=['DELETE'])
@token_required
@manager_required
def delete_project(current_user, project_id):
    """
    Delete project by ID
    ---
    tags:
      - Projects
    parameters:
      - in: path
        name: project_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Project deleted successfully
      404:
        description: Project not found
    """

    try:
        project_id = int(project_id)
    except ValueError:
        return jsonify({'error': 'Invalid ID format'}), 400
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    db.session.delete(project)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    return jsonify({'message': 'Project deleted successfully'}), 200

@projects_bp.route('/<project_id>/tasks', methods=['POST'])
@token_required
@manager_required
def create_task(current_user, project_id):
    """
    Create a new task under a project
    ---
    tags:
      - Tasks
    parameters:
      - in: path
        name: project_id
        required: true
        schema:
          type: integer
      - in: body
        name: task
        description: The task to create
        schema:
          type: object
          required:
            - title
          properties:  
            title:
              type: string
            description:
              type: string
    responses:
      201:
        description: Task created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                title:
                  type: string
                description:
                  type: string
                project_id:
                  type: integer
    """

    try:
        project_id = int(project_id)
    except ValueError:
        return jsonify({'error': 'Invalid ID format'}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    
    data_fields = ['title']

    for field in data_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
        
    new_task = Task(
        title=data['title'],
        description=data.get('description'),
        project_id=project_id
    )

    db.session.add(new_task)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "project_id": new_task.project_id
    }), 201

@projects_bp.route('/<project_id>/tasks', methods=['GET'])
@token_required
def get_tasks(current_user, project_id):
    """
    Get tasks under a project with pagination
    ---
    tags:
      - Tasks
    parameters:
      - in: path
        name: project_id
        required: true
        schema:
          type: integer
        description: ID of the project
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
        description: Number of tasks per page
    responses:
      200:
        description: Tasks retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                total:
                  type: integer
                  description: Total number of tasks
                page:
                  type: integer
                  description: Current page number
                per_page:
                  type: integer
                  description: Number of tasks per page
                pages:
                  type: integer
                  description: Total number of pages
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      title:
                        type: string
                      description:
                        type: string
                      project_id:
                        type: integer
                        description: ID of the project this task belongs to
    """
    page = request.args.get("page", 1, int)
    limit = request.args.get("per_page", 10, int)
    
    try:
        project_id = int(project_id)
    except ValueError:
        return jsonify({'error': 'Invalid ID format'}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    pagination = Task.query \
      .filter_by(project_id=project_id) \
      .paginate(page=page, per_page=limit, error_out=False)

    return jsonify({
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "data": [{
          "id": task.id,
          "title": task.title,
          "description": task.description,
          "project_id": task.project_id} for task in pagination.items
        ]
    }), 200