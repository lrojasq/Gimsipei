from flask import Blueprint, request
from .controllers import dashboard_controller, clases_recursos_controller, evaluaciones_controller, libros_controller, calificaciones_controller

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return dashboard_controller(request)


# @admin_bp.route("/materias", methods=["GET"])
# def materias():
#     return materias_controller(request)


@admin_bp.route("/clases", methods=["GET"])
def clases_recursos():
    return clases_recursos_controller(request)


@admin_bp.route("/evaluaciones", methods=["GET"])
def evaluaciones():
    return evaluaciones_controller(request)


@admin_bp.route("/libros", methods=["GET"])
def libros():
    return libros_controller(request)


@admin_bp.route("/calificaciones", methods=["GET"])
def calificaciones():
    return calificaciones_controller(request)