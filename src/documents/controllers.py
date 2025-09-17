from flask import Request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, UserRole
from src.models.document import Document
from src.database.database import SessionLocal
from typing import Dict, Any, List


@jwt_required()
def create_document_controller(request: Request) -> tuple[Dict[str, Any], int]:
    """Create a new document"""
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)

        if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()
        document = Document(
            title=data["title"], content=data["content"], author_id=user_id
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "author_id": document.author_id,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
        }, 201
    finally:
        db.close()


@jwt_required()
def get_documents_controller(
    request: Request,
) -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Get all documents"""
    db = SessionLocal()
    try:
        documents = db.query(Document).filter_by(is_active=True).all()
        return {
            "documents": [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "author_id": doc.author_id,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat(),
                }
                for doc in documents
            ]
        }, 200
    finally:
        db.close()


@jwt_required()
def get_document_controller(request: Request, id: int) -> tuple[Dict[str, Any], int]:
    """Get a specific document"""
    db = SessionLocal()
    try:
        document = db.query(Document).get(id)

        if not document or not document.is_active:
            return {"error": "Document not found"}, 404

        return {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "author_id": document.author_id,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
        }, 200
    finally:
        db.close()


@jwt_required()
def update_document_controller(request: Request, id: int) -> tuple[Dict[str, Any], int]:
    """Update a document"""
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        document = db.query(Document).get(id)

        if not document or not document.is_active:
            return {"error": "Document not found"}, 404

        if document.author_id != user_id:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()
        document.title = data.get("title", document.title)
        document.content = data.get("content", document.content)

        db.commit()

        return {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "author_id": document.author_id,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
        }, 200
    finally:
        db.close()


@jwt_required()
def delete_document_controller(request: Request, id: int) -> tuple[Dict[str, str], int]:
    """Delete a document (soft delete)"""
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        document = db.query(Document).get(id)

        if not document or not document.is_active:
            return {"error": "Document not found"}, 404

        if document.author_id != user_id:
            return {"error": "Unauthorized"}, 403

        document.is_active = False
        db.commit()

        return {"message": "Document deleted successfully"}, 200
    finally:
        db.close()
