from logging import getLogger
from flask import Blueprint, request
from datetime import datetime

from app.mi_colegio.documentos.controller_documentos import  DocumentosController
from app.utils.responses import Response

logger = getLogger(__name__)
documentos_bp = Blueprint("documentos_bp", __name__, url_prefix="/api/documentos")
# Instancia del controlador
controller = DocumentosController()

# Ruts para el manejo de las carpetas

@documentos_bp.route("/carpetas", methods=["POST"])
def crear_documento_router():
    """Crear carpeta para almacenar documentos"""
    try:
        # Acceder a los parámetros de consulta
        dicct_documento = request.get_json()
        crear_documento = controller.crear_documento_controller(dicct_documento)

        if crear_documento:
            return Response.success(crear_documento[0], crear_documento[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la creación de la carpeta", 500)
    
@documentos_bp.route("/carpetas/usuario/<id_docente>/curso/<id_curso>", methods=["GET"])
def listar_documentos_router(id_docente: int, id_curso: int) -> tuple[dict, int]:
    """La idea es que se listen todos los recursos de ese usuario asi tenga carpetas o recursos individuales cargados"""
    try:
        listar_documentos = controller.listar_todos_documentos(id_docente, id_curso)
        if listar_documentos[1] != 200:
            return Response.new_error(listar_documentos[0], listar_documentos[1])

        return Response.new_success(listar_documentos[0], listar_documentos[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de las carpetas", 500)
    
@documentos_bp.route("/carpetas/<documento_id>", methods=["GET"])
def listar_documento_router(documento_id: int):
    """Listar una carpeta"""
    try:
        listar_documento = controller.listar_documentos(documento_id)

        if listar_documento:
            return Response.success(listar_documento[0], listar_documento[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de la carpeta", 500)
    
@documentos_bp.route("/carpetas/<documento_id>", methods=["PUT"])
def actualizar_documento_router(documento_id: int):
    """Actualizar valores de una carpeta"""
    try:
        # Acceder a los parámetros de consulta
        dicct_documento = request.get_json()
        dicct_documento["ultima_modificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        actualizar_documento = controller.actualizar_documento(dicct_documento, documento_id)

        if actualizar_documento:
            return Response.success(actualizar_documento[0], actualizar_documento[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la actualización de la carpeta", 500)
    
@documentos_bp.route("/carpetas/<documento_id>", methods=["DELETE"])
def eliminar_documento_router(documento_id: int):
    """Eliminar una carpeta"""
    try:
        eliminar_documento = controller.eliminar_documento(documento_id)

        if eliminar_documento:
            return Response.success(eliminar_documento[0], eliminar_documento[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la eliminación de la carpeta", 500)

@documentos_bp.route("/carga/recursos", methods=["POST"])
def cargar_recurso_router():
    """Carga de recurso en azure con quien se asoció a una carpeta, un estudiante o a todos los estudiantes del curso del docente"""
    try:
        # Acceder a los parámetros de consulta
        data = request.form
        id_documento = int(data['id_documento']) if data['id_documento'] else None
        id_docente = int(data['id_docente'])
        id_asignatura = int(data['id_asignatura'])
        descripcion = data['descripcion'] if data['descripcion'] else None
        compartido = int(data['compartido']) if data['compartido'] else None

        # Almacenar recursos en azure luego en DB
        cargar_recurso = controller.cargar_recurso_controller(id_documento, id_docente, id_asignatura, descripcion, compartido)
        if cargar_recurso[1] != 201:
            return Response.new_error(cargar_recurso[0], cargar_recurso[1])

        # Saber a quién se le quiere adjuntar el recurso.
        if not id_documento or compartido:
            relacion_documentos = controller.relacion_estudiantes(compartido, id_documento, id_asignatura)
            if relacion_documentos[1] != 201:
                return Response.new_error(relacion_documentos[0], relacion_documentos[1])
            return Response.success(relacion_documentos[0], relacion_documentos[1])

        # Dado el caso en que se asocie a un archivo
        return Response.success(cargar_recurso[0], cargar_recurso[1])
    except Exception as exc:
        return Response.new_error("Error en el servidor durante la carga de recursos", 500)

@documentos_bp.route("/carpeta/<id_carpeta>/recursos", methods=["GET"])
def listar_recurso_carpeta(id_carpeta:int):
    """Listar todos los recursos dentro de [X] carpeta"""
    try:
        listar_recurso = controller.listar_recurso_carpeta(id_carpeta)
        if listar_recurso[1] != 200:
            return Response.success(listar_recurso[0], listar_recurso[1])
        
        return Response.success(listar_recurso[0], listar_recurso[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los recursos", 500)

@documentos_bp.route("/recursos/<id_recurso>", methods=["DELETE"])
def eliminar_recurso_carpeta(id_recurso:int):
    """Eliminar recurso dentro de [X] carpeta"""
    try:
        eliminar_recurso = controller.eliminar_recurso_carpeta(id_recurso)
        if eliminar_recurso[1]!= 200:
            return Response.success(eliminar_recurso[0], eliminar_recurso[1])
        
        return Response.success(eliminar_recurso[0], eliminar_recurso[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la eliminación de los recursos", 500)
    
@documentos_bp.route("/asignatura/<id_asignatura>/estudiantes", methods=["GET"])
def listar_estudiantes_asignatura(id_asignatura:int):
    """Listar todos los estudiantes de una asignatura"""
    try:
        listar_estudiantes = controller.listar_estudiantes_por_asignatura(id_asignatura)
        if listar_estudiantes[1]!= 200:
            return Response.success(listar_estudiantes[0], listar_estudiantes[1])
        
        return Response.new_success(listar_estudiantes[0], listar_estudiantes[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los estudiantes", 500)
  
@documentos_bp.route("/recursos/asignados/", methods=["GET"])
def listar_recursos_asignados() -> tuple:
    """Listar todos los recursos asociados a un estudiante"""
    try:
        id_estudiante = request.args.get("estudiante")
        id_curso = request.args.get("curso")
        id_asignatura = request.args.get("asignatura")

        if not id_estudiante or not id_curso or not id_asignatura:
            return Response.new_error("Debes enviar los parámetros requeridos", 400)
        
        listar_recursos = controller.listar_recursos_asignados(id_estudiante, id_curso, id_asignatura)
        if listar_recursos[1]!= 200:
            return Response.success(listar_recursos[0], listar_recursos[1])
        
        return Response.new_success(listar_recursos[0], listar_recursos[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los recursos", 500)

@documentos_bp.route("/recursos/asignados/<id>", methods=["DELETE"])
def eliminar_recurso_asignado(id:int) -> tuple:
    """Eliminar recurso asociado a un estudiante"""
    try:
        recurso = controller.eliminar_recurso_asociado(id)
        if recurso[1]!= 201:
            return Response.success(recurso[0], recurso[1])
        
        return Response.new_success(recurso[0], recurso[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la eliminación de los recursos", 500)

@documentos_bp.route("/compartir/recursos/<id_carpeta>/tarea/<id_tarea>", methods=["POST"])
def compartir_recursos_docente(id_carpeta:int, id_tarea:int) -> tuple:
    """Compartir recursos con un docente"""
    try:
        compartir_recursos = controller.compartir_recursos(id_carpeta, id_tarea)
        if compartir_recursos[1]!= 201:
            return Response.success(compartir_recursos[0], compartir_recursos[1])
        
        return Response.new_success(compartir_recursos[0], compartir_recursos[1])
    except Exception as e:
        return Response.new_error("Error en el servidor al compartir los recursos",500)