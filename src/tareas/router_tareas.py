from logging import getLogger
from flask import Blueprint, request

from app.mi_colegio.tareas.controller_miColegio import MiColegioController
from app.utils.responses import Response
# from app.mi_colegio.helper_miColegio import HelperSie

# from app.mi_colegio.schemas import AsignaturasEstudianteSchema
# from app.mi_colegio.auth import require_auth

logger = getLogger(__name__)
miColegio_bp = Blueprint("miColegio_bp", __name__, url_prefix="/api")
controller = MiColegioController()


@miColegio_bp.route("/mi_colegio/asignaturas_estudiante/", methods=["GET"])
def consultar_asignaturas_estudiante():
    """Listar las asignaturas por estudiante"""
    try:
        # Validar los parámetros de entrada
        usuario = request.args.get("usuario")
        curso = request.args.get("curso")
        if not usuario or not curso:
            return Response.factory_respuesta("Debe enviar el usuario y el curso"), 400

        # Consultar las asignaturas del estudiante
        dataResponse = controller.consultar_asignaturas_estudiante(usuario, curso)
        # Serializar los datos de salida
        # asignaturas_schema = AsignaturasEstudianteSchema(many=True)
        # asignaturas = asignaturas_schema.dump(data)
        return Response.success(dataResponse)
    except Exception as e:
        return Response.new_error("Error al consultar las asignaturas del estudiante")


@miColegio_bp.route("/mi_colegio/creacion/<docente>", methods=["POST"])
def creacion_tareas(docente: str):
    """Crear tareas"""
    try:
        # Acceder a los parámetros de consulta
        asignatura = request.args.get("asignatura")
        curso = request.args.get("curso")
        objet_tarea = request.get_json()

        # Validar los parámetros de entrada
        if not asignatura or not curso:
            return Response.new_error("Debe enviar el usuario y el curso", 400)

        # Crear la tarea
        crear_tarea = controller.crear_tareas(docente, asignatura, curso, objet_tarea)
        if crear_tarea[1] != 201 | crear_tarea[1] != 200:
            return Response.new_error(crear_tarea[0], crear_tarea[1])
        
        # Asignar la tarea a los estudiantes
        assign_task = controller.asignar_tarea_estudiante(curso)
        if assign_task[1] != 201:
            return Response.new_error(assign_task[0], assign_task[1])

        return Response.success("Tarea creada exitosamente", 201)
    except Exception as e:
        return Response.new_error("Error en el servidor durante la creación de la tarea")
    
    
@miColegio_bp.route("/mi_colegio/tareas/<docente>", methods=["GET"])
def consultar_tareas(docente: str):
    """Listar las tareas creadas por un docente en una asignatura"""
    try:
        asignatura = request.args.get("asignatura")
        curso = request.args.get("curso")

        # Validar los parámetros de entrada
        if None in (docente, asignatura, curso):
            return Response.new_error("Se debe enviar el docente, asignatura y curso", 400)

        # Consultar las tareas del estudiante
        dataResponse = controller.consultar_tareas(docente, curso, asignatura)

        if len(dataResponse) == 0:
            return Response.new_error("No se encontraron tareas para el estudiante con ese docente y asignatura", 200)

        return Response.success(dataResponse)
    except Exception as e:
        return Response.new_error(f"Error en el servidor durante la consulta de tareas", 500)
    

@miColegio_bp.route("/mi_colegio/tarea/<id_tarea>", methods=["PUT"])
def actualizar_tareas(id_tarea: str):
    """Actualizar tareas existentes"""
    try:
        # Acceder a los parámetros de consulta
        objet_tarea = request.get_json()

        # Validar los parámetros de entrada
        if id_tarea is None:
            return Response.new_error("Debe enviar el id de la tarea", 400)

        crear_tarea = controller.actualizar_tareas_existentes(id_tarea, objet_tarea)
        if crear_tarea[0] is None:
            return Response.success("Tarea actualizada exitosamente", 201)

        return Response.new_error("No se pudo actualizar la tarea", 400)
    except Exception as e:
        return Response.new_error("Error en el servidor durante la creación de la tarea", 500)


@miColegio_bp.route("/mi_colegio/tarea/", methods=["DELETE"])
def eliminar_tareas():
    """Eliminar tareas existentes por id"""
    try:
        # Acceder a los parámetros de consulta
        id_tarea = request.args.get("id_tarea")

        if not id_tarea:
            return Response.new_error("Debe enviar el id de la tarea", 400)

        crear_tarea = controller.eliminar_tareas_existentes(id_tarea)

        if crear_tarea[1] != 200:
            return Response.new_error("No se pudo eliminar la tarea", 400)

        return Response.success("Tarea eliminada exitosamente", 200)
    except Exception as e:
        return Response.new_error("Error en el servidor durante la creación de la tarea", 500)


@miColegio_bp.route("mi_colegio/consultar_estudiantes/<estudiante_id>/asignatura/<asignatura_id>/curso/<curso_id>", methods=["GET"])
def consultar_estudiantes(estudiante_id: int, asignatura_id: int, curso_id: int):
    """Consultar información de los estudiantes por asignatura y curso"""
    try:
        dataResponse = controller.consultar_info_estudiante(estudiante_id, asignatura_id, curso_id)
        if dataResponse[0] != 200:
            return Response.success(dataResponse[0], dataResponse[1])
        
        return Response.new_success(dataResponse[0], dataResponse[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de estudiantes", 500)

@miColegio_bp.route("/mi_colegio/consultar_tareas/<estudiante_id>", methods=["GET"])
def consultar_todas_tareas(estudiante_id: int) -> tuple:
    """Consultar todas las asignaturas de un estudiante"""
    try:
        # Consultar las tareas del estudiante
        dataResponse = controller.consultar_tareas_estudiantes(estudiante_id)
        if dataResponse[1] != 200:
            return Response.success(dataResponse[0], dataResponse[1])
        
        return Response.new_success(dataResponse[0], dataResponse[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de las asignaturas", 500)

@miColegio_bp.route("/mi_colegio/carga_recurso/<id_tarea>/usuario/<id_usuario>", methods=["POST"])
def carga_recurso(id_tarea: int, id_usuario: int) -> tuple:
    """Cargar recurso a la tarea"""
    # Validar method
    if request.method == 'POST':
        try:
            # !Antes de responder la tarea se debe validar si la fecha de entrega no ha expirado
            comentario = request.form.get("comentario")

            recurso = controller.carga_recurso_estudiante(request)
            if recurso[1] != 201:
                return Response.new_error(recurso[0], recurso[1])

            guardar_respuesta = controller.respondiendo_una_tarea(id_tarea, id_usuario)
            if guardar_respuesta[1] != 201:
                return Response.new_error(guardar_respuesta[0], guardar_respuesta[1])

            # Guardar comentario de la tarea
            comentarios = controller.hilo_comentarios_tareas(id_respuesta=None, id_usuario=id_usuario, comentario=str(comentario))
            if comentarios[1] != 201:
                return Response.new_error(comentarios[0], comentarios[1])

            return Response.success("Recurso cargado exitosamente", 201)
        except Exception as e:
            return Response.new_error("Error en el servidor durante la creación de la tarea", 500)
    else:
        return Response.new_error("Metodo no permitido", 405)
    
@miColegio_bp.route("/mi_colegio/comentar_tarea/<id_respuesta>/usuario/<id_usuario>", methods=["POST"])
def comentar_tarea(id_respuesta:int, id_usuario:int) -> tuple:
    """Realizar un comentario a una tarea pasando le como parámetro el id de la respuesta a la tarea"""
    try:
        # Acceder a los parámetros de consulta
        comentario = request.get_json()["comentario"]
        if not comentario:
            return Response.new_error("Debes enviar el comentario", 200)
        
        comentarios = controller.hilo_comentarios_tareas(id_respuesta, id_usuario, comentario)
        if comentarios[1] != 201:
            return Response.new_error(comentarios[0], comentarios[1])
        
        return Response.success(comentarios[0], comentarios[1])
    except Exception as e:
        return Response.new_error("Error en el servidor al almacenar el comentario", 500)

@miColegio_bp.route("/mi_colegio/trabajos_entregados/<id_tarea>", methods=["GET"])
def trabajos_entregados(id_tarea: str):
    """Consultar que estudiantes y cuantos han entregado la tarea"""
    try:
        task_delivered = controller.consultar_tareas_enviadas(id_tarea)
        if task_delivered[1] != 200:
            return Response.new_error(task_delivered[0], task_delivered[1])
        
        return Response.success(task_delivered[0], task_delivered[1])
    except Exception as exc:
        return Response.new_error("Error en el servidor durante la consulta de tareas", 500)
    
@miColegio_bp.route("/mi_colegio/tarea_entregada/<id_tarea>/estudiante/<id_estudiante>", methods=["GET"])
def tarea_entregada(id_tarea: int, id_estudiante:int) -> tuple:
    """Obtener información de la ultima tarea entregada por un estudiante"""
    try:
        info_estudiante = controller.tarea_entregada_estudiante(id_tarea, id_estudiante)
        if info_estudiante[1] != 200:
            return Response.new_error(info_estudiante[0], info_estudiante[1])
        
        return Response.success(info_estudiante[0], info_estudiante[1])
    except Exception as exc:
        return Response.new_error("Error en el servidor durante la consulta de la tarea", 500)

@miColegio_bp.route("/mi_colegio/calificar_trabajos/<id_respuesta>", methods=["PUT"])
def calificar_trabajos(id_respuesta: int):
    """Calificar los trabajos entregados por los estudiantes"""
    try:
        # Acceder a los paràmtros de consulta
        dicc_calificacion = request.get_json()
        if not dicc_calificacion:
            return Response.new_error("Debes enviar la calificación", 400)
        
        calificar_tareas = controller.calificar_tareas_enviadas(id_respuesta, dicc_calificacion)
        if calificar_tareas[1] != 201:
            return Response.new_error(calificar_tareas[0], calificar_tareas[1])
        
        return Response.success(calificar_tareas[0], calificar_tareas[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la calificación de tareas", 500)

@miColegio_bp.route("/mi_colegio/historial_comentarios/<id_entrega>", methods=["GET"])
def historial_comentarios(id_entrega: int) -> tuple:
    """Obtener el hilo de comentarios que se han realizado a una tarea"""
    try:
        comentario = controller.consultar_comentarios_tareas(id_entrega) 
        if comentario[1] != 200:
            return Response.new_error(comentario[0], comentario[1])
        
        return Response.success(comentario[0], comentario[1])
    except Exception as exc:
        return Response.new_error("Error en el servidor durante la consulta de los comentarios", 500)