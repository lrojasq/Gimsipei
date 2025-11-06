from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, UserRole
from src.models.exercise import Exercise
from src.models.submission import Submission
from typing import Dict, Any, List
from datetime import datetime

bp = Blueprint('exercises', __name__, url_prefix='/api/exercises')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_exercise() -> tuple[Dict[str, Any], int]:
    """Create a new exercise
    
    Returns:
        tuple[Dict[str, Any], int]: Response with exercise data and status code
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        return {'error': 'Unauthorized'}, 403
    
    data = request.get_json()
    exercise = Exercise(
        title=data['title'],
        description=data['description'],
        questions=data['questions'],
        author_id=user_id,
        time_limit=data.get('time_limit')
    )
    
    current_app.extensions['sqlalchemy'].session.add(exercise)
    current_app.extensions['sqlalchemy'].session.commit()
    
    return {
        'id': exercise.id,
        'title': exercise.title,
        'description': exercise.description,
        'questions': exercise.questions,
        'author_id': exercise.author_id,
        'time_limit': exercise.time_limit,
        'created_at': exercise.created_at.isoformat()
    }, 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_exercises() -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Get all exercises
    
    Returns:
        tuple[Dict[str, List[Dict[str, Any]]], int]: Response with list of exercises and status code
    """
    exercises = Exercise.query.filter_by(is_active=True).all()
    return {
        'exercises': [{
            'id': ex.id,
            'title': ex.title,
            'description': ex.description,
            'author_id': ex.author_id,
            'time_limit': ex.time_limit,
            'created_at': ex.created_at.isoformat()
        } for ex in exercises]
    }, 200

@bp.route('/<int:id>/submit', methods=['POST'])
@jwt_required()
def submit_exercise(id: int) -> tuple[Dict[str, Any], int]:
    """Submit an exercise
    
    Args:
        id (int): Exercise ID
        
    Returns:
        tuple[Dict[str, Any], int]: Response with submission data and status code
    """
    user_id = get_jwt_identity()
    exercise = Exercise.query.get(id)
    
    if not exercise or not exercise.is_active:
        return {'error': 'Exercise not found'}, 404
    
    data = request.get_json()
    submission = Submission(
        student_id=user_id,
        exercise_id=id,
        content=data['answers']
    )
    
    # Here you would implement the logic to grade the submission
    correct_answers = 0
    total_questions = len(exercise.questions)
    
    for q_id, answer in data['answers'].items():
        if answer == exercise.questions[q_id]['correct_answer']:
            correct_answers += 1
    
    submission.score = (correct_answers / total_questions) * 100
    
    current_app.extensions['sqlalchemy'].session.add(submission)
    current_app.extensions['sqlalchemy'].session.commit()
    
    return {
        'id': submission.id,
        'score': submission.score,
        'submitted_at': submission.submitted_at.isoformat()
    }, 201

@bp.route('/<int:id>/submissions', methods=['GET'])
@jwt_required()
def get_exercise_submissions(id: int) -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Get all submissions for an exercise
    
    Args:
        id (int): Exercise ID
        
    Returns:
        tuple[Dict[str, List[Dict[str, Any]]], int]: Response with list of submissions and status code
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        return {'error': 'Unauthorized'}, 403
    
    submissions = Submission.query.filter_by(exercise_id=id).all()
    return {
        'submissions': [{
            'id': sub.id,
            'student_id': sub.student_id,
            'score': sub.score,
            'submitted_at': sub.submitted_at.isoformat()
        } for sub in submissions]
    }, 200
