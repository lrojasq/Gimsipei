from flask import Request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, UserRole
from src.models.exercise import Exercise
from src.models.submission import Submission
from src.database.database import SessionLocal
from typing import Dict, Any, List
from datetime import datetime


@jwt_required()
def create_exercise_controller(request: Request) -> tuple[Dict[str, Any], int]:
    """Create a new exercise"""
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)

        if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()
        exercise = Exercise(
            title=data["title"],
            description=data["description"],
            questions=data["questions"],
            author_id=user_id,
            time_limit=data.get("time_limit"),
        )

        db.add(exercise)
        db.commit()
        db.refresh(exercise)

        return {
            "id": exercise.id,
            "title": exercise.title,
            "description": exercise.description,
            "questions": exercise.questions,
            "author_id": exercise.author_id,
            "time_limit": exercise.time_limit,
            "created_at": exercise.created_at.isoformat(),
        }, 201
    finally:
        db.close()


@jwt_required()
def get_exercises_controller(
    request: Request,
) -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Get all exercises"""
    db = SessionLocal()
    try:
        exercises = db.query(Exercise).filter_by(is_active=True).all()
        return {
            "exercises": [
                {
                    "id": ex.id,
                    "title": ex.title,
                    "description": ex.description,
                    "author_id": ex.author_id,
                    "time_limit": ex.time_limit,
                    "created_at": ex.created_at.isoformat(),
                }
                for ex in exercises
            ]
        }, 200
    finally:
        db.close()


@jwt_required()
def submit_exercise_controller(request: Request, id: int) -> tuple[Dict[str, Any], int]:
    """Submit an exercise"""
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        exercise = db.query(Exercise).get(id)

        if not exercise or not exercise.is_active:
            return {"error": "Exercise not found"}, 404

        data = request.get_json()
        submission = Submission(
            student_id=user_id, exercise_id=id, content=data["answers"]
        )

        # Here you would implement the logic to grade the submission
        correct_answers = 0
        total_questions = len(exercise.questions)

        for q_id, answer in data["answers"].items():
            if answer == exercise.questions[q_id]["correct_answer"]:
                correct_answers += 1

        submission.score = (correct_answers / total_questions) * 100

        db.add(submission)
        db.commit()
        db.refresh(submission)

        return {
            "id": submission.id,
            "score": submission.score,
            "submitted_at": submission.submitted_at.isoformat(),
        }, 201
    finally:
        db.close()


@jwt_required()
def get_exercise_submissions_controller(
    request: Request, id: int
) -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Get all submissions for an exercise"""
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)

        if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            return {"error": "Unauthorized"}, 403

        submissions = db.query(Submission).filter_by(exercise_id=id).all()
        return {
            "submissions": [
                {
                    "id": sub.id,
                    "student_id": sub.student_id,
                    "score": sub.score,
                    "submitted_at": sub.submitted_at.isoformat(),
                }
                for sub in submissions
            ]
        }, 200
    finally:
        db.close()
