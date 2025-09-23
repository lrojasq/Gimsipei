from flask import Blueprint, request
from .controllers import (
    create_document_controller,
    get_documents_controller,
    get_document_controller,
    update_document_controller,
    delete_document_controller,
)

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")


@documents_bp.route("/", methods=["POST"])
def create_document():
    return create_document_controller(request)


@documents_bp.route("/", methods=["GET"])
def get_documents():
    return get_documents_controller(request)


@documents_bp.route("/<int:id>", methods=["GET"])
def get_document(id):
    return get_document_controller(request, id)


@documents_bp.route("/<int:id>", methods=["PUT"])
def update_document(id):
    return update_document_controller(request, id)


@documents_bp.route("/<int:id>", methods=["DELETE"])
def delete_document(id):
    return delete_document_controller(request, id)
