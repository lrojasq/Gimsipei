from typing import Any, Dict, Optional, TypeVar, Generic
from flask import jsonify
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ApiResponse(Generic[T]):
    @staticmethod
    def success(
        data: Optional[T] = None,
        message: str = "Operación exitosa",
        status_code: int = 200,
    ) -> tuple:
        response = {
            "success": True,
            "message": message,
            "data": data.dict() if data else None,
        }
        return jsonify(response), status_code

    @staticmethod
    def error(
        message: str = "Error en la operación",
        details: Optional[Any] = None,
        status_code: int = 400,
    ) -> tuple:
        response = {"success": False, "message": message, "details": details}
        return jsonify(response), status_code

    @staticmethod
    def list_response(
        items: list,
        total: int,
        page: int = 1,
        per_page: int = 10,
        message: str = "Lista obtenida exitosamente",
    ) -> tuple:
        response = {
            "success": True,
            "message": message,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page,
            },
        }
        return jsonify(response), 200
