from flask import Request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, UserRole
from src.models.assignment import Assignment
from src.models.submission import Submission
from src.database.database import SessionLocal
from typing import Dict, Any, List
from datetime import datetime


@jwt_required()
def create_assignment_controller(request: Request) -> tuple[Dict[str, Any], int]:
    """Create a new assignment"""
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)

        if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()
        assignment = Assignment(
            title=data["title"],
            description=data["description"],
            author_id=user_id,
            due_date=datetime.fromisoformat(data["due_date"]),
        )

        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        return {
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "author_id": assignment.author_id,
            "due_date": assignment.due_date.isoformat(),
            "created_at": assignment.created_at.isoformat(),
        }, 201
    finally:
        db.close()


@jwt_required()
def get_assignments_controller(
    request: Request,
) -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Get all assignments"""
    db = SessionLocal()
    try:
        assignments = db.query(Assignment).filter_by(is_active=True).all()
        return {
            "assignments": [
                {
                    "id": asg.id,
                    "title": asg.title,
                    "description": asg.description,
                    "author_id": asg.author_id,
                    "due_date": asg.due_date.isoformat(),
                    "created_at": asg.created_at.isoformat(),
                }
                for asg in assignments
            ]
        }, 200
    finally:
        db.close()


@jwt_required()
def submit_assignment_controller(
    request: Request, id: int
) -> tuple[Dict[str, Any], int]:
    """Submit an assignment"""
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).get(id)

        if not assignment or not assignment.is_active:
            return {"error": "Assignment not found"}, 404

        if datetime.utcnow() > assignment.due_date:
            return {"error": "Assignment due date has passed"}, 400

        data = request.get_json()
        submission = Submission(
            student_id=user_id, assignment_id=id, content=data["content"]
        )

        db.add(submission)
        db.commit()
        db.refresh(submission)

        return {
            "id": submission.id,
            "submitted_at": submission.submitted_at.isoformat(),
        }, 201
    finally:
        db.close()


@jwt_required()
def get_assignment_submissions_controller(
    request: Request, id: int
) -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Get all submissions for an assignment"""
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)

        if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            return {"error": "Unauthorized"}, 403

        submissions = db.query(Submission).filter_by(assignment_id=id).all()
        return {
            "submissions": [
                {
                    "id": sub.id,
                    "student_id": sub.student_id,
                    "content": sub.content,
                    "score": sub.score,
                    "feedback": sub.feedback,
                    "submitted_at": sub.submitted_at.isoformat(),
                }
                for sub in submissions
            ]
        }, 200
    finally:
        db.close()


@jwt_required()
def grade_submission_controller(
    request: Request, id: int
) -> tuple[Dict[str, Any], int]:
    """Grade a submission"""
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)

        if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            return {"error": "Unauthorized"}, 403

        submission = db.query(Submission).get(id)
        if not submission:
            return {"error": "Submission not found"}, 404

        data = request.get_json()
        submission.score = data["score"]
        submission.feedback = data.get("feedback")

        db.commit()

        return {
            "id": submission.id,
            "score": submission.score,
            "feedback": submission.feedback,
        }, 200
    finally:
        db.close()
