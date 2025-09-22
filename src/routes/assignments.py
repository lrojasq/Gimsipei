from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, UserRole
from src.models.assignment import Assignment
from src.models.submission import Submission
from typing import Dict, Any, List
from datetime import datetime

bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_assignment() -> tuple[Dict[str, Any], int]:
    """Create a new assignment
    
    Returns:
        tuple[Dict[str, Any], int]: Response with assignment data and status code
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        return {'error': 'Unauthorized'}, 403
    
    data = request.get_json()
    assignment = Assignment(
        title=data['title'],
        description=data['description'],
        author_id=user_id,
        due_date=datetime.fromisoformat(data['due_date'])
    )
    
    current_app.extensions['sqlalchemy'].session.add(assignment)
    current_app.extensions['sqlalchemy'].session.commit()
    
    return {
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'author_id': assignment.author_id,
        'due_date': assignment.due_date.isoformat(),
        'created_at': assignment.created_at.isoformat()
    }, 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_assignments() -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Get all assignments
    
    Returns:
        tuple[Dict[str, List[Dict[str, Any]]], int]: Response with list of assignments and status code
    """
    assignments = Assignment.query.filter_by(is_active=True).all()
    return {
        'assignments': [{
            'id': asg.id,
            'title': asg.title,
            'description': asg.description,
            'author_id': asg.author_id,
            'due_date': asg.due_date.isoformat(),
            'created_at': asg.created_at.isoformat()
        } for asg in assignments]
    }, 200

@bp.route('/<int:id>/submit', methods=['POST'])
@jwt_required()
def submit_assignment(id: int) -> tuple[Dict[str, Any], int]:
    """Submit an assignment
    
    Args:
        id (int): Assignment ID
        
    Returns:
        tuple[Dict[str, Any], int]: Response with submission data and status code
    """
    user_id = get_jwt_identity()
    assignment = Assignment.query.get(id)
    
    if not assignment or not assignment.is_active:
        return {'error': 'Assignment not found'}, 404
        
    if datetime.utcnow() > assignment.due_date:
        return {'error': 'Assignment due date has passed'}, 400
    
    data = request.get_json()
    submission = Submission(
        student_id=user_id,
        assignment_id=id,
        content=data['content']
    )
    
    current_app.extensions['sqlalchemy'].session.add(submission)
    current_app.extensions['sqlalchemy'].session.commit()
    
    return {
        'id': submission.id,
        'submitted_at': submission.submitted_at.isoformat()
    }, 201

@bp.route('/<int:id>/submissions', methods=['GET'])
@jwt_required()
def get_assignment_submissions(id: int) -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Get all submissions for an assignment
    
    Args:
        id (int): Assignment ID
        
    Returns:
        tuple[Dict[str, List[Dict[str, Any]]], int]: Response with list of submissions and status code
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        return {'error': 'Unauthorized'}, 403
    
    submissions = Submission.query.filter_by(assignment_id=id).all()
    return {
        'submissions': [{
            'id': sub.id,
            'student_id': sub.student_id,
            'content': sub.content,
            'score': sub.score,
            'feedback': sub.feedback,
            'submitted_at': sub.submitted_at.isoformat()
        } for sub in submissions]
    }, 200

@bp.route('/<int:id>/grade', methods=['POST'])
@jwt_required()
def grade_submission(id: int) -> tuple[Dict[str, Any], int]:
    """Grade a submission
    
    Args:
        id (int): Submission ID
        
    Returns:
        tuple[Dict[str, Any], int]: Response with updated submission data and status code
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        return {'error': 'Unauthorized'}, 403
    
    submission = Submission.query.get(id)
    if not submission:
        return {'error': 'Submission not found'}, 404
    
    data = request.get_json()
    submission.score = data['score']
    submission.feedback = data.get('feedback')
    
    db.session.commit()
    
    return {
        'id': submission.id,
        'score': submission.score,
        'feedback': submission.feedback
    }, 200
