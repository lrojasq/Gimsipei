from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, UserRole
from src.models.document import Document
from typing import Dict, Any, List

bp = Blueprint('documents', __name__, url_prefix='/api/documents')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_document() -> tuple[Dict[str, Any], int]:
    """Create a new document
    
    Returns:
        tuple[Dict[str, Any], int]: Response with document data and status code
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        return {'error': 'Unauthorized'}, 403
    
    data = request.get_json()
    document = Document(
        title=data['title'],
        content=data['content'],
        author_id=user_id
    )
    
    current_app.extensions['sqlalchemy'].session.add(document)
    current_app.extensions['sqlalchemy'].session.commit()
    
    return {
        'id': document.id,
        'title': document.title,
        'content': document.content,
        'author_id': document.author_id,
        'created_at': document.created_at.isoformat(),
        'updated_at': document.updated_at.isoformat()
    }, 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_documents() -> tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Get all documents
    
    Returns:
        tuple[Dict[str, List[Dict[str, Any]]], int]: Response with list of documents and status code
    """
    documents = Document.query.filter_by(is_active=True).all()
    return {
        'documents': [{
            'id': doc.id,
            'title': doc.title,
            'content': doc.content,
            'author_id': doc.author_id,
            'created_at': doc.created_at.isoformat(),
            'updated_at': doc.updated_at.isoformat()
        } for doc in documents]
    }, 200

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_document(id: int) -> tuple[Dict[str, Any], int]:
    """Get a specific document
    
    Args:
        id (int): Document ID
        
    Returns:
        tuple[Dict[str, Any], int]: Response with document data and status code
    """
    document = Document.query.get(id)
    
    if not document or not document.is_active:
        return {'error': 'Document not found'}, 404
        
    return {
        'id': document.id,
        'title': document.title,
        'content': document.content,
        'author_id': document.author_id,
        'created_at': document.created_at.isoformat(),
        'updated_at': document.updated_at.isoformat()
    }, 200

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_document(id: int) -> tuple[Dict[str, Any], int]:
    """Update a document
    
    Args:
        id (int): Document ID
        
    Returns:
        tuple[Dict[str, Any], int]: Response with updated document data and status code
    """
    user_id = get_jwt_identity()
    document = Document.query.get(id)
    
    if not document or not document.is_active:
        return {'error': 'Document not found'}, 404
        
    if document.author_id != user_id:
        return {'error': 'Unauthorized'}, 403
        
    data = request.get_json()
    document.title = data.get('title', document.title)
    document.content = data.get('content', document.content)
    
    current_app.extensions['sqlalchemy'].session.commit()
    
    return {
        'id': document.id,
        'title': document.title,
        'content': document.content,
        'author_id': document.author_id,
        'created_at': document.created_at.isoformat(),
        'updated_at': document.updated_at.isoformat()
    }, 200

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_document(id: int) -> tuple[Dict[str, str], int]:
    """Delete a document (soft delete)
    
    Args:
        id (int): Document ID
        
    Returns:
        tuple[Dict[str, str], int]: Response with success message and status code
    """
    user_id = get_jwt_identity()
    document = Document.query.get(id)
    
    if not document or not document.is_active:
        return {'error': 'Document not found'}, 404
        
    if document.author_id != user_id:
        return {'error': 'Unauthorized'}, 403
        
    document.is_active = False
    current_app.extensions['sqlalchemy'].session.commit()
    
    return {'message': 'Document deleted successfully'}, 200
