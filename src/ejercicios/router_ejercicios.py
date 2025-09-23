from logging import getLogger
from flask import Blueprint, request
from ast import literal_eval

from app.mi_colegio.ejercicios.controller_ejercicios import EjerciciosController
from app.utils.responses import Response

logger = getLogger(__name__)
ejercicios_bp = Blueprint("ejercicios_bp", __name__, url_prefix="/api/ejercicios")
controller = EjerciciosController()

@ejercicios_bp.route("/opciones", methods=["GET"])
def listar_opciones() -> tuple:
    """Listar todas las opciones disponibles"""
    try:
        opciones = controller.listar_opciones()
        if opciones[1]!= 200:
            return Response.success(opciones[0], opciones[1])

        return Response.new_success(opciones[0], opciones[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de las opciones", 500)
    
@ejercicios_bp.route("/opciones/<id_opcion>", methods=["GET"])
def listar_opcion(id_opcion: int) -> tuple:
    """Listar todas las opciones disponibles"""
    try:
        opcion = controller.listar_opcion(id_opcion)
        if opcion[1]!= 200:
            return Response.success(opcion[0], opcion[1])
        
        return Response.new_success(opcion[0], opcion[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de las opciones", 500)

@ejercicios_bp.route( '/crear_ejercicio/', methods=["POST"])
def crear_ejercicio() -> tuple:
    """Método para crear un ejercicio"""
    try:
        dataRequest = request.get_json()
        id_asignatura = request.args.get("asignatura")
        
        if id_asignatura is None:
            return Response.new_error("Faltan parámetros requeridos", 200)

        ejercicio = controller.crear_ejercicios(id_asignatura, dataRequest)
        if ejercicio[1]!= 201:
            return Response.success(ejercicio[0], ejercicio[1])

        return Response.new_success(ejercicio[0], ejercicio[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la creación de la tarea", 500)
    
@ejercicios_bp.route("/", methods=["GET"])
def listar_ejercicios() -> tuple:
    """Listar todos los ejercicios"""    
    try:
        id_asignatura:int = request.args.get("asignatura")
        id_usuario:int = request.args.get("usuario")

        if id_asignatura is None or id_usuario is None:
            return Response.new_error("Faltan parámetros requeridos", 200)

        ejercicios = controller.listar_ejercicios(id_asignatura, id_usuario)
        if ejercicios[1]!= 200:
            return Response.success(ejercicios[0], ejercicios[1])
        
        return Response.new_success(ejercicios[0], ejercicios[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los ejercicios", 500)
    
@ejercicios_bp.route("/<id_ejercicio>", methods=["GET"])
def listar_ejercicio(id_ejercicio: int) -> tuple:
    """Listar un ejercicio por su id"""
    try:
        ejercicio = controller.listar_ejercicio(id_ejercicio)
        if ejercicio[1]!= 200:
            return Response.success(ejercicio[0], ejercicio[1])
        
        return Response.new_success(ejercicio[0], ejercicio[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los ejercicios", 500)
    
@ejercicios_bp.route("/<id_ejercicio>", methods=["DELETE"])
def eliminar_ejercicio(id_ejercicio: int) -> tuple:
    """Eliminar un ejercicio por su id"""
    try:
        ejercicio = controller.eliminar_ejercicio(id_ejercicio)
        if ejercicio[1]!= 201:
            return Response.success(ejercicio[0], ejercicio[1])
        
        return Response.new_success(ejercicio[0], ejercicio[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los ejercicios", 500)

@ejercicios_bp.route("/<id_ejercicio>", methods=["PUT"])
def actualizar_ejercicio(id_ejercicio: int) -> tuple:
    """Actualizar un ejercicio por su id"""
    try:
        dataRequest = request.get_json()
        ejercicio = controller.actualizar_ejercicio_controller(id_ejercicio, dataRequest)
        if ejercicio[1]!= 201:
            return Response.success(ejercicio[0], ejercicio[1])
        
        return Response.new_success(ejercicio[0], ejercicio[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los ejercicios", 500)
    
@ejercicios_bp.route("/formato_pregunta/", methods=["GET"])
def listar_formato_pregunta() -> tuple:
    """Listar los formatos de pregunta"""
    try:
        id_formato = request.args.get("formato") # url_params
        formato_pregunta = controller.listar_formato_pregunta(id_formato)
        if formato_pregunta[1]!= 200:
            return Response.success(formato_pregunta[0], formato_pregunta[1])
        
        return Response.new_success(formato_pregunta[0], formato_pregunta[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los formatos de pregunta", 500)
    
@ejercicios_bp.route("/crear_pregunta/", methods=["POST"])
def creando_pregunta() -> tuple:
    """Método para crear una pregunta"""
    try:
        id_formato = request.args.get("formato")
        id_ejercicio = request.args.get("ejercicio")

        if id_formato in ["6"]:
            # Receive data from form-data
            data_request = request.form.to_dict()
            image_list:tuple = controller.transform_request_image(request)
            if image_list[1]!= 200:
                return Response.success(image_list[0], image_list[1])

            data_request["recursos"] = image_list[0]
            data_request["contenido"]:list = [] # Create a list to store the images
            # Transform the data to the correct format for the model [str -> list]
            data_request["correcta"] = literal_eval(data_request["correcta"])
            data_request["puntuacion_respt"] = literal_eval(data_request["puntuacion_respt"])
        else:
            if not request.get_json():
                return Response.new_error("Formato de petición incorrecto", 200)
            data_request = request.get_json()
            data_request["recursos"] = None

        pregunta = controller.crear_pregunta(id_ejercicio, id_formato, data_request)
        if pregunta[1]!= 201:
            return Response.success(pregunta[0], pregunta[1])

        return Response.new_success(pregunta[0], pregunta[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la creación de la pregunta", 500)
    
@ejercicios_bp.route("/listar_preguntas/ejercicio/<id_ejercicio>", methods=["GET"])
def listar_preguntas_ejercicio(id_ejercicio: int) -> tuple:
    """Listar todas las preguntas de un ejercicio"""
    try:
        preguntas = controller.listar_preguntas_ejercicio(id_ejercicio)
        if preguntas[1]!= 200:
            return Response.success(preguntas[0], preguntas[1])
        
        return Response.new_success(preguntas[0], preguntas[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de las preguntas", 500)

@ejercicios_bp.route("/preguntas/<id_pregunta>", methods=["DELETE"])
def eliminar_pregunta(id_pregunta: int) -> tuple:
    """Eliminar una pregunta por su id"""
    try:
        pregunta:tuple = controller.eliminar_pregunta(id_pregunta)
        if pregunta[1]!= 201:
            return Response.success(pregunta[0], pregunta[1])
        
        return Response.new_success(pregunta[0], pregunta[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los ejercicios", 500)
    
@ejercicios_bp.route("/preguntas/<id_pregunta>", methods=["PUT"])
def actualizar_pregunta(id_pregunta: int) -> tuple[str, int]:
    """Actualizar una pregunta por su id"""
    try:
        data_request = request.get_json(silent=True) # if the data is in json format
        # Get data in other format
        if data_request is None:
            data_request = request.form.to_dict()
            image_list:tuple = controller.transform_request_image(request)
            if image_list[1]!= 200:
                return Response.success(image_list[0], image_list[1])

            data_request["recursos"] = image_list[0]
            data_request["id_formato"] = int(data_request["id_formato"])
            data_request["correcta"] = literal_eval(data_request["correcta"])
            data_request["puntuacion_respt"] = literal_eval(data_request["puntuacion_respt"])
            data_request["contenido"] = [] # Create a list to store the images

            pregunta = controller.actualizar_pregunta_controller(id_pregunta, data_request)
            if pregunta[1]!= 201:
                return Response.success(pregunta[0], pregunta[1])
            return Response.new_success(pregunta[0], pregunta[1])

        data_request["recursos"] = None
        pregunta = controller.actualizar_pregunta_controller(id_pregunta, data_request)
        if pregunta[1]!= 201:
            return Response.success(pregunta[0], pregunta[1])
        return Response.new_success(pregunta[0], pregunta[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los ejercicios", 500)

@ejercicios_bp.route("/responder_prueba/estudiante/<id_estudiante>", methods=["POST"])
def responder_ejercicio(id_estudiante: int) -> tuple:
    """Método para que los estudiantes puedan responder un ejercicio"""
    try:
        data_request = request.get_json()
        ejercicio = controller.responder_prueba(data_request, id_estudiante)
        if ejercicio[1]!= 201:
            return Response.success(ejercicio[0], ejercicio[1])

        id_ejercicio = data_request.get("id_ejercicio")
        generar_notas = controller.actualizar_notas_ejercicio(id_estudiante, id_ejercicio)
        if generar_notas[1]!= 200:
            return Response.success(generar_notas[0], generar_notas[1])

        return Response.new_success(ejercicio[0], ejercicio[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los ejercicios", 500)

@ejercicios_bp.route("/resolver_prueba/<id_ejercicio>/usuario/<id_estudiante>", methods=["GET"])
def resolver_ejercicio(id_ejercicio: int, id_estudiante: int) -> tuple:
    """Método para estudiantes. Se listarán los puntos de un ejercicio"""
    try:
        # Create relationship between student and exercise
        estudiante_ejerc = controller.validar_estudiante_ejercicio(id_ejercicio, id_estudiante)
        if estudiante_ejerc[1]!= 201:
            return Response.success(estudiante_ejerc[0], estudiante_ejerc[1])

        # Get questions of one exercise with their answers
        ejercicio = controller.listar_preguntas_estudiante(id_ejercicio)
        if ejercicio[1]!= 200:
            return Response.success(ejercicio[0], ejercicio[1])
        
        return Response.new_success(ejercicio[0], ejercicio[1])
    except Exception as e:
        return Response.new_error("Error en el servidor al acceder a las preguntas", 500)

@ejercicios_bp.route("/terminar_prueba/<id_relacion>", methods=["PUT"])
def terminar_ejercicio(id_relacion: int) -> tuple:
    """Método para que los estudiantes puedan terminar un ejercicio"""
    try:
        respuesta = controller.terminar_prueba(id_relacion)
        if respuesta[1]!= 201:
            return Response.success(respuesta[0], respuesta[1])
        
        return Response.new_success(respuesta[0], respuesta[1])
    except Exception as e:
        return Response.new_error("Error en el servidor durante la consulta de los ejercicios", 500)

@ejercicios_bp.route("/retroalimentacion/<id_relation>", methods=["GET"])
def feedback_functions(id_relation: int) -> tuple:
    """Me todo para que los estudiantes puedan visualizar la retroalimentación del ejercicio realizado"""
    try:
        feedback: tuple = controller.list_feedback(id_relation)
        if feedback[1]!= 200:
            return Response.success(feedback[0], feedback[1])

        return Response.new_success(feedback[0], feedback[1])
    except Exception as e:
        return Response.new_error("Error en el servidor", 500)

@ejercicios_bp.route("/listar_pregunta/<id_pregunta>", methods=["GET"])
def listar_pregunta(id_pregunta: int) -> tuple:
    """Método para listar una pregunta por su id"""
    try:
        pregunta: tuple = controller.listar_pregunta(id_pregunta)
        if pregunta[1]!= 200:
            return Response.success(pregunta[0], pregunta[1])

        return Response.new_success(pregunta[0], pregunta[1])
    except Exception as e:
        return Response.new_error("Error en el servidor", 500)