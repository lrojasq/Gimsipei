from typing import Generator, Union, Any
from collections import defaultdict
from decimal import Decimal, ROUND_DOWN
import re
from flask import request
from werkzeug.datastructures import MultiDict

from app.mi_colegio.ejercicios.service_ejercicios import EjercicioService
from app.utils.responses import Response
from app.mi_colegio.tareas.model_miColegio import crearAejerciciosModel, crearPruebaModel
from app.mi_colegio.tareas.service_miColegio import MiColegioService
from app.mi_colegio.tareas.helper_miColegio import HelperSie

class EjerciciosController:
    def __init__(self) -> None:
        self.service = EjercicioService()
        self.mi_colegio = MiColegioService()
        self.folder_azure = "miColegio/ejercicios"

    def listar_opciones(self) -> tuple:
        """Método para listar ejercicios"""
        try:
            ejercicios = self.service.listar_opciones()
            if ejercicios[1] != 200:
                return Response.tuple_response(ejercicios[0], ejercicios[1])
            
            return Response.tuple_response(ejercicios[0], ejercicios[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron opciones para listar", 400)
        
    def listar_opcion(self, id_opcion: int) -> tuple:
        """Método para listar ejercicios por su id"""
        try:
            ejercicios = self.service.listar_opcion(id_opcion)
            if ejercicios[1] != 200:
                return Response.tuple_response(ejercicios[0], ejercicios[1])
            
            return Response.tuple_response(ejercicios[0], ejercicios[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios", 400)
        
    def crear_ejercicios(self, id_asignatura: int, dataRequest: dict) -> tuple:
        """Método para crear ejercicios"""
        try:
            # Validando datos entrada
            dict_validacion = crearAejerciciosModel(id_asignatura=id_asignatura, **dataRequest)
            dict_Request:dict = dict_validacion.model_dump()

            if len(dict_Request) == 0:
                return Response.tuple_response('Tiene errores en los valores ingresados', 200)

            # Create new ejercicio in table ejercicios
            ejercicios:tuple = self.service.crear_ejercicios(dict_Request)
            if ejercicios[0] is not None:
                return Response.tuple_response(ejercicios[0], ejercicios[1])
            
            # Access to table ejercicios to get the id of the last row inserted
            id_ejercicio = self.mi_colegio.get_last_row("ejercicios")
            if id_ejercicio[1] != 200:
                return Response.tuple_response(id_ejercicio[0], id_ejercicio[1])
            
            id = id_ejercicio[0]['id'] # Destruturing and accessing the first element of the tuple
            return Response.tuple_response([{"id": id, "message":"Ejercicio creado correctamente"}], 201)
        except Exception as e:
            return Response.tuple_response("Problemas al crear el ejercicio", 400)
    
    def de_bytes_a_str(self, intento: bytes) -> str:
        """Metodo para convertir bytes a string"""
        try:
            return intento.decode("utf-8")
        except Exception as e:
            return Response.tuple_response("Error al convertir bytes a string", 400)

    def listar_ejercicios(self, id_asignatura: int, id_usuario: int) -> tuple:
        """Metodo para listar ejercicios para estudiantes y docentes"""
        try:
            # Validate if the user is a student or other
            usuario_verficado: tuple = self.service.validar_usuario(id_usuario)
            if usuario_verficado[1] != 200:
                return Response.tuple_response(usuario_verficado[0], usuario_verficado[1])

            rol: str|None = usuario_verficado[0]['rol'] # Destructuring and acessing the first element of the tuple

            # List of exercises without attempts "for not student"
            ejercicios = self.service.listar_ejercicios(id_asignatura)
            if ejercicios[1] != 200:
                return Response.tuple_response(ejercicios[0], ejercicios[1])
            
            # List of exercises with attempts "for student"
            ejercicios_intentos: tuple = self.service.listar_ejercicios_intentos(id_asignatura, id_usuario)
            if ejercicios_intentos[1] != 200:
                return Response.tuple_response(ejercicios_intentos[0], ejercicios_intentos[1])
            
            # If the user is not a student, the list of exercises is returned
            if type(rol) is None:
                return Response.tuple_response(ejercicios[0], ejercicios[1])

            # Transforming the bytes to string
            for index in ejercicios_intentos[0]:
                for key, value in index.items():
                    if key in ["intentos"]:
                        index[key] = self.de_bytes_a_str(value)
                    continue

            return Response.tuple_response(ejercicios_intentos[0], ejercicios_intentos[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios", 400)
        
    def listar_ejercicio(self, id_ejercicio: int) -> tuple:
        """Método para listar ejercicios por su id"""
        try:
            ejercicios = self.service.listar_ejercicio(id_ejercicio)
            if ejercicios[1] != 200:
                return Response.tuple_response(ejercicios[0], ejercicios[1])
            
            return Response.tuple_response(ejercicios[0], ejercicios[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios", 400)
        
    def eliminar_ejercicio(self, id_ejercicio: int) -> tuple:
        """Método para eliminar ejercicios"""
        try:
            ejercicios = self.service.eliminar_ejercicio(id_ejercicio)
            if ejercicios[0] is not None:
                return Response.tuple_response(ejercicios[0], ejercicios[1])
            
            return Response.tuple_response("Ejercicio eliminado correctamente!", ejercicios[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios al eliminar")
        
    def actualizar_ejercicio_controller(self, id_ejercicio: int, data_request: dict) -> tuple:
        """Me todo para actualizar ejercicios"""
        try:
            # Validando datos entrados
            dict_validacion = crearAejerciciosModel(id_ejercicio=id_ejercicio, **data_request)
            dict_Request:dict = dict_validacion.model_dump()

            if len(dict_Request) == 0:
                return Response.tuple_response('Tiene errores en los valores ingresados', 200)
            
            ejercicios:tuple = self.service.actualizar_ejercicio_service(id_ejercicio, dict_Request)
            if ejercicios[0] is not None:
                return Response.tuple_response(ejercicios[0], ejercicios[1])
            
            return Response.tuple_response("Ejercicio actualizado correctamente", 201)
        except Exception as e:
            return Response.tuple_response("Problemas al actualizar el ejercicio", 400)
    
    def listar_formato_pregunta (self, id_formato: str|None) -> tuple:
        """Me todo para listar los formatos de pregunta"""
        try:
            # Saber si es un entero o llega vació
            id_formato = int(id_formato) if len(id_formato) > 0 else None
            formatos:tuple = self.service.listar_formato_pregunta()

            # Saber si nos llega un None (all data)
            if type(id_formato) != int:
                if formatos[1] != 200:
                    return Response.tuple_response(formatos[0], formatos[1])
                return Response.tuple_response(formatos[0], formatos[1])
            
            # Listar por id
            formato:tuple = self.service.listar_formato_pregunta_id(id_formato)
            if formato[1] != 200:
                return Response.tuple_response(formato[0], formato[1])

            return Response.tuple_response(formato[0], formato[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios", 400)

    def estructurar_informacion(self, dict_request: dict) -> tuple[str, int]:
        """Método para estructurar la información de las preguntas"""
        try:
            # Patrón de busqueda
            patron = r'\[(.*?)\]'

            # Estructurar la información
            estructura: dict = {
                "contenido": [],
                "correcta": [1],
                "puntuacion_respt": [1]
            }

            # Transformar la información según el formato
            estructura["contenido"] = list(re.findall(patron, dict_request["texto_completar"]))
            estructura["correcta"] = estructura["correcta"] * len(estructura["contenido"])

            """Se le aplica el calculo para obtener el valor deseado por cada respuesta y lo que hace el map() con la lambda es simplemente de aplicarle 
               un formato para quitarle algunos decimales a la nota eso nos devuelve los números como decimales entonces le aplicamos el float"""
            valor = [len(estructura["puntuacion_respt"])/len(estructura["correcta"])] * len(estructura["correcta"])
            estructura["puntuacion_respt"] = list(map(lambda x: float(Decimal(x).quantize(Decimal('0.00'), rounding=ROUND_DOWN)),valor))

            return Response.tuple_response(estructura, 200)
        except Exception as e:
            return Response.tuple_response("Error al transformar información en formato 3", 400)

    def transform_request_image(self, dict_request: request) -> tuple[str, int]:
        """Acceder a las imagenes enviadas en el request, validarlas y almacenarlas en una lista"""
        try:
            imagenes:list = []
            for i in range(1, 5):
                contenido_key:str = f"contenido{i}"

                if contenido_key in dict_request.files:
                    imagenes.append(dict_request.files.get(contenido_key)) # Add the image to the list
                else:
                    return Response.tuple_response("Nombre de imagen incorrecto", 400)

            return Response.tuple_response(imagenes, 200)
        except Exception as e:
            return Response.tuple_response("Error al formatiar las imagenes", 400)

    def crear_pregunta(self, id_ejercicio: int, id_formato: int, data_request: dict) -> tuple:
        """Método para crear preguntas"""
        try:
            # Validando datos entrados
            dict_validation = crearPruebaModel(id_ejercicio=id_ejercicio, id_formato=id_formato, **data_request)
            dict_request:dict|None = dict_validation.model_dump()

            # where questions have fourth responses
            if dict_validation.is_valid() is False:
                return Response.tuple_response(f'Deben ser 4 opciones de pregunta estas enviando {len(dict_request["contenido"])}', 200)

            if dict_validation.validar_cantidad_imagenes(dict_request["recursos"]) is False:
                return Response.tuple_response("Hacen falta mas imagenes", 200)

            # validar la longitud de la pregunta y la respuesta
            if dict_validation.validate_length_content() is False:
                return Response.tuple_response("Tanto el contenido como la respuesta deben tener una longitud mayor a 0 y menor 4,294,967,295 caracteres", 200)

            # validar que por lo menos me debe de enviar una puntuacion
            if dict_validation.validate_question_score() is False:
                return Response.tuple_response("Debe enviar una puntuación a la pregunta mayor a 0 y menor a 100", 200)

            # Save pregunta in db
            pregunta:tuple = self.service.crear_pregunta(id_ejercicio, id_formato, dict_request)
            if pregunta[0] is not None:
                return Response.tuple_response(pregunta[0], pregunta[1])

            ultima_pregunta:tuple = self.mi_colegio.get_last_row('preguntas_ejerc')
            if ultima_pregunta[1] != 200:
                return Response.tuple_response(ultima_pregunta[0], ultima_pregunta[1])
            dict_request["id_pregunta"] = ultima_pregunta[0]["id"]

            # Add property to dict_request for the images(url)
            if type(dict_request["recursos"]) == list:
                for image in dict_request["recursos"]: # Iterating over the list of images
                    dict_request['recurso'] = image
                    azure_image = self.upload_images_azure(dict_request)
                    if azure_image[1] != 201:
                        return Response.tuple_response(azure_image[0], azure_image[1])
                    dict_request["contenido"].append(azure_image[0]) # Add the url of the image to the list of content

            # Use the structure method to transform the information in format 3
            if dict_request["id_formato"] in [3]:
                dict_estructura:tuple = self.estructurar_informacion(dict_request)
                if dict_estructura[1] != 200:
                    return Response.tuple_response(dict_estructura[0], dict_estructura[1])

                # Asignar objeto a objeto principal
                dict_request["contenido"] = dict_estructura[0]["contenido"]
                dict_request["correcta"] = dict_estructura[0]["correcta"]
                dict_request["puntuacion_respt"] = dict_estructura[0]["puntuacion_respt"]

            # where questions have format seven
            if dict_request["id_formato"] in [7,8]:
                paired = sorted(zip(dict_request["contenido"], dict_request["correcta"]), key=lambda x: x[0])
                value_order, _ = zip(*paired) # Destructuring the list of tuples
                dict_request["contenido"]:tuple = value_order
                dict_request["init_position"]:list[int] = dict_request["correcta"]
                dict_request["correcta"] = [1]*4 # Generate a list of 1's

            # Asegurarnos que los campos dé las respuestas no sean iguales
            dict_pregunta = dict(zip(dict_request["contenido"], dict_request["correcta"]))
            # Quiero que la validacion afecte a ciertos formatos de pregunta
            if dict_request["id_formato"] in [1, 2, 5, 7, 8]:
                if len(dict_pregunta) != 4:
                    return Response.tuple_response("Las respuestas no pueden ser repetidas",400)

            # Transform response array and return one value
            def yield_punctuation() -> Generator[Any, None, None]:
                """Construimos un generador a partir de una lista, Para que siempre nos devuelva un solo valor por llamada"""
                for number in dict_request["puntuacion_respt"]:
                    yield number

            def init_position() -> Generator[Any, None, None]:
                """Retornar una posición inicial por cada llamado"""
                for number in dict_request["init_position"]:
                    yield number

            generador = yield_punctuation()
            generador_position = init_position()
            # Save options in db
            for key, value in dict_pregunta.items():
                # Correct is false
                if int(value) != 1:
                    respuestas = self.service.crear_respuesta(key, value, next(generador), dict_request["id_pregunta"] , next(generador_position))
                    if respuestas[0] is not None:
                        return Response.tuple_response(respuestas[0], respuestas[1])
                    continue

                # Correct is true
                respuestas = self.service.crear_respuesta(key, value, next(generador), dict_request["id_pregunta"], next(generador_position))
                if respuestas[0] is not None:
                    return Response.tuple_response(respuestas[0], respuestas[1])

            return Response.tuple_response("Pregunta creada correctamente", 201)
        except Exception as e:
            return Response.tuple_response("Problemas al crear la pregunta", 400)

    def upload_images_azure(self, dict_request:dict) -> tuple:
        """Método para validar extension, subir imagenes a azure y retornar un diccionario con la información de la imagenes"""
        try:
            # Generate a dictionary with the information of the images
            file_storage = dict_request['recurso'] # Getting the file
            file_dict = MultiDict()
            file_dict.add('recurso', file_storage)

            # Class FileRequest - Simulate the request object
            class FileRequest:
                def __init__(self, files_dict, content_type) -> None:
                    self.files = files_dict
                    self.content_type = content_type

            # Save images in azure
            content_type = HelperSie().get_content_type(file_storage.content_type) # Getting the content type of the file
            request_obj = FileRequest(file_dict, content_type) # Generate a request object
            resource = HelperSie().upload_file(request_obj)
            if resource[1] != 201:
                return Response.tuple_response(resource[0], resource[1])

            # Upload image to azure and return the url
            upload_azure = HelperSie().upload_file_to_azure(self.folder_azure, content_type, request_obj)
            if upload_azure[1] != 200:
                return Response.tuple_response(upload_azure[0], upload_azure[1])

            # Get the url of the image and return it
            (url, nombre) = upload_azure[0].values()
            return Response.tuple_response(url, 201)
        except Exception as e:
            return Response.tuple_response("Problemas al subir las imagenes", 400)

    def listar_preguntas_ejercicio(self, id_ejercicio: int) -> tuple:
        """Método para listar preguntas"""
        try:
            preguntas = self.service.listar_preguntas_ejercicio(id_ejercicio)
            if preguntas[1] != 200:
                return Response.tuple_response(preguntas[0], preguntas[1])
            
            return Response.tuple_response(preguntas[0], preguntas[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron preguntas", 400)
        
    def eliminar_pregunta (self, id_pregunta: int) -> tuple:
        """Método para eliminar preguntas"""
        try:
            preguntas = self.service.eliminar_pregunta(id_pregunta)
            if preguntas[0] is not None:
                return Response.tuple_response(preguntas[0], preguntas[1])
            
            return Response.tuple_response("Pregunta eliminada correctamente!", preguntas[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron preguntas al eliminar")

    def actualizar_pregunta_controller (self, id_pregunta: int, data_request: dict) -> tuple[str, int]:
        """Método para actualizar preguntas"""
        try:
            # Validate data sent in the request
            dict_validation = crearPruebaModel(id_pregunta=id_pregunta, **data_request)
            dict_request:dict = dict_validation.model_dump()
            
            # Validate if list have one correct answer
            if not dict_validation.is_correct():
                return Response.tuple_response("Debe haber una respuesta correcta", 200)
            
            # Check the score greater than 0 and less than 100
            if dict_validation.validate_question_score() is False:
                return Response.tuple_response("La puntuación debe ser mayor a 0 y menor a 100", 400)

            # Check if existing score and score is correct
            preguntas:tuple = self.service.actualizar_pregunta_service(dict_request["id_pregunta"], dict_request["pregunta"], dict_request["texto_completar"])
            if preguntas[0] is not None:
                return Response.tuple_response(preguntas[0], preguntas[1])
            
            # Tratar datos para formato 3
            if dict_request["id_formato"] in [3]:
                dict_estructura:tuple = self.estructurar_informacion(dict_request)
                if dict_estructura[1] != 200:
                    return Response.tuple_response(dict_estructura[0], dict_estructura[1])

                # Asignar objeto a objeto principal
                dict_request["contenido"] = dict_estructura[0]["contenido"]
                dict_request["correcta"] = dict_estructura[0]["correcta"]
                dict_request["puntuacion_respt"] = dict_estructura[0]["puntuacion_respt"]

                # Set score to zero
                puntuación:tuple = self.service.eliminar_respuestas(dict_request["id_pregunta"])
                if puntuación[0] is not None:
                    return Response.tuple_response(puntuación[0], puntuación[1])

            if dict_request["id_formato"] in [6]:
                # Count the number of images
                if dict_validation.validar_cantidad_imagenes(dict_request["recursos"]) is False:
                    return Response.tuple_response("Hacen falta mas imagenes", 200)

                # Get the data of answers
                response = self.get_url_image_delete(dict_request["id_pregunta"])
                if response[1] != 200:
                    return Response.tuple_response(response[0], response[1])

                for image in dict_request["recursos"]:
                    dict_request['recurso'] = image
                    azure_image = self.upload_images_azure(dict_request)
                    if azure_image[1] != 201:
                        return Response.tuple_response(azure_image[0], azure_image[1])
                    dict_request["contenido"].append(azure_image[0])

            # where questions have format seven
            if dict_request["id_formato"] in [7,8]:
                paired = sorted(zip(dict_request["contenido"], dict_request["correcta"]), key=lambda x: x[1])
                value_order, _ = zip(*paired) # Destructuring the list of tuples
                dict_request["contenido"] = value_order
                dict_request["init_position"]:list[int] = dict_request["correcta"]
                dict_request["correcta"] = [1 for _ in range(len(value_order))] # Generate a list of 1's

            dict_pregunta: dict = dict(zip(dict_request["contenido"], dict_request["correcta"])) # Generating dict with list content and correct
            if dict_request["id_formato"] in [1,2,5,6,7,8]:
                if len(dict_pregunta) != 4:
                    return Response.tuple_response("Las respuestas no pueden ser repetidas",400)

            # Transform response array and return one value
            def yield_punctuation() -> Generator[Union[int, any], None, Generator]:
                """Construimos un generador a partir de una lista, Para que siempre nos devuelva un solo valor por llamada"""
                for number in dict_request["puntuacion_respt"]:
                    yield number

            def init_position() -> Generator[Any, None, None]:
                """Retornar una posición inicial por cada llamado"""
                for number in dict_request["init_position"]:
                    yield number

            generador = yield_punctuation()
            generador_position = init_position()

            # Create options in db with format three
            if dict_request["id_formato"] in [3]:
                for key, value in dict_pregunta.items():
                    respuestas = self.service.crear_respuesta(key, value, next(generador), dict_request["id_pregunta"])
                    if respuestas[0] is not None:
                        return Response.tuple_response(respuestas[0], respuestas[1])

            # Convert the content(Null), correct(0) and punctuation(0) to a single value
            if dict_request["id_formato"] in [1,2,4,5,6,7,8]:
                responses = self.service.set_value_to_null(dict_request["id_pregunta"])
                if responses[0] is not None:
                    return Response.tuple_response(responses[0], responses[1])

            # Update responses with new values in db
            if dict_request["id_formato"] in [1,2,4,5,6,7,8]:
                for key, value in dict_pregunta.items():
                # Correct is false
                    if int(value) != 1:
                        actualizar_false: tuple = self.service.actualizar_respuetas_service(key, value, next(generador), dict_request["id_pregunta"], next(generador_position))
                        if actualizar_false[0] is not None:
                            return Response.tuple_response(actualizar_false[0], actualizar_false[1])

                        continue
                    # Correct is true
                    actualizar_true: tuple = self.service.actualizar_respuetas_service(key, value, next(generador), dict_request["id_pregunta"], next(generador_position))
                    if actualizar_true[0] is not None:
                        return Response.tuple_response(actualizar_true[0], actualizar_true[1])
                    continue
            
            return Response.tuple_response("Pregunta actualizada correctamente", 201)
        except Exception as e:
            return Response.tuple_response("Problemas al actualizar la pregunta", 400)

    def get_url_image_delete(self, id_pregunta: int) -> tuple:
        """Método para obtener la url de la imagen y eliminarlas de azure"""
        try:
            # Get the data of answers
            get_answer: tuple = self.service.obtener_respuestas_preg(id_pregunta)
            if get_answer[1] != 200:
                return Response.tuple_response(get_answer[0], get_answer[1])

            #  Iterate over the list of answers
            for answer in get_answer[0]:
                name_cheild = answer["contenido"].split("/").pop() # Get the name of the image
                # Delete image in azure
                delete_azure = HelperSie().delete_resource_azure(self.folder_azure, name_cheild)
                if delete_azure[1] != 200:
                    return Response.tuple_response(delete_azure[0], delete_azure[1])
            return Response.tuple_response("Imagenes eliminadas correctamente", 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron imagenes", 400)

    def responder_prueba(self, data_request: dict, id_estudiante: int) -> tuple:
        """Me todo para resolver ejercicio"""
        try:
            # Validando datos entrados
            dict_validacion = crearPruebaModel(**data_request)
            dict_request:dict|None = dict_validacion.model_dump()

            # Other formats            
            if dict_validacion.is_valid() is False:
                return Response.tuple_response("Debe enviar una respuesta a la pregunta", 200)
            
            # Only formats three
            if dict_validacion.transform_questions() is False:
                return Response.tuple_response("Error al validar datos enviados", 200)
            
            # ID of the last response between user and exercise
            ultima_pregunta: tuple = self.mi_colegio.get_last_row("estudiante_ejercicio")
            if ultima_pregunta[1] != 200:
                return Response.tuple_response(ultima_pregunta[0], ultima_pregunta[1])
            id_relacion: int = ultima_pregunta[0]["id"] # Getting id response user

            # Validate if the user has exercise with 'format 4'
            if dict_request["id_formato"] in [4]:
                respuesta:tuple = self.agregar_respuesta_estudiante(id_estudiante, dict_validacion, dict_request, id_relacion)
                if respuesta[1] != 201:
                    return Response.tuple_response(respuesta[0], respuesta[1])
                return Response.tuple_response(respuesta[0], respuesta[1])

            if dict_request["id_formato"] in [7,8]:
                respuesta = self.service.obtener_respuestas_preg(int(dict_request["id_pregunta"]))
                if respuesta[1] != 200:
                    return Response.tuple_response(respuesta[0], respuesta[1])
                dict_request["id_respuesta_db"]:list = [i["id"] for i in respuesta[0]] # Getting the id of the answers in the db
                dict_request["correcta"]:list = []

                # Compare the answers of the user with the answers of the db
                for i in range(len(dict_request["id_respuesta"])):
                    if dict_request["id_respuesta"][i] == dict_request["id_respuesta_db"][i]:
                        dict_request["correcta"].append(1)  # Correcto
                    else:
                        dict_request["correcta"].append(0)  # Incorrecto

            # If the user not selected anything, then do not save that value.
            if dict_request["id_formato"] in [3,5,6,7,8] and len(dict_request["id_respuesta"]) != 0 or dict_request["id_formato"] in [1,2]:
                def yield_correcta() -> Generator[Any, None, None]:
                    """Generador para obtener la respuesta correcta"""
                    for number in dict_request["correcta"]:
                        yield number
                generador = yield_correcta()

                # Access values of the array when user send multiple responses
                for id_respuesta in dict_request["id_respuesta"]:
                    # Save response in db
                    respuesta: tuple = self.service.respondiendo_prueba( id_estudiante ,dict_request["id_ejercicio"], dict_request["id_pregunta"], id_respuesta, id_relacion)
                    if respuesta[0] is not None:
                        return Response.tuple_response(respuesta[0], respuesta[1])

                    # Calcular puntuación
                    if dict_request["id_formato"] in [1,2,3,4,6]:
                        calculo_operation: tuple = self.calcular_operación_ejercicio()
                        if calculo_operation[1] != 200:
                            return Response.tuple_response(calculo_operation[0], calculo_operation[1])
                        continue

                    # Generate operation to calculate the score of the student with format 5
                    punctuation = self.validar_respuesta_estudiante_formato5(next(generador))
                    if punctuation[1] != 200:
                        return Response.tuple_response(punctuation[0], punctuation[1])

                return Response.tuple_response("Pregunta contestada correctamente", 201)
            return Response.tuple_response("Respondiste el ejercicio sin enviar una respuesta valida", 200)
        except Exception as e:
            return Response.tuple_response("Problemas al resolver el ejercicio", 400)
    
    def calcular_operación_ejercicio(self) -> tuple:
        """Mé todo para calcular puntuación y notas de ejercicio"""
        try:
            ultimo_insert: tuple = self.mi_colegio.get_last_row("usuario_respuesta_ejercicios")
            if ultimo_insert[1] != 200:
                return Response.tuple_response(ultimo_insert[0], ultimo_insert[1])
            
            id_respuesta = ultimo_insert[0]["id"] # Getting id response user

            notas = self.service.calcular_nota(id_respuesta)
            if notas[0] is not None:
                return Response.tuple_response(notas[0], notas[1])

            puntuación = self.service.calcular_puntuación(id_respuesta)
            if puntuación[0] is not None:
                return Response.tuple_response(puntuación[0], puntuación[1])
            
            return Response.tuple_response("Proceso realizado correctamente", 200)
        except Exception as e:
            return Response.tuple_response("Problemas al calcular la puntuación del ejercicio", 400)

    def validar_respuesta_estudiante_formato5(self, correcta: int) -> tuple:
        """Me todo para calcular puntuación y notas de ejercicio en formato 5"""
        try:
            ultimo_creation: tuple = self.mi_colegio.get_last_row("usuario_respuesta_ejercicios")
            if ultimo_creation[1] != 200:
                return Response.tuple_response(ultimo_creation[0], ultimo_creation[1])

            id_respuesta = int(ultimo_creation[0]["id"]) # Getting id response user generar_notas_ejercicio
            punctuation = self.service.notas_puntuacion_estudiante_formato5(id_respuesta, correcta)
            if punctuation[0] is not None:
                return Response.tuple_response(punctuation[0], punctuation[1])

            return Response.tuple_response("Proceso realizado correctamente", 200)
        except Exception as e:
            return Response.tuple_response("Problemas al calcular la puntuación del ejercicio", 400)

    def agregar_respuesta_estudiante(self, id_estudiante: int, dict_validacion: crearPruebaModel, dict_request: dict, id_relacion: int) -> tuple:
        """Cuando el estudiante esté dando respuesta al ejercicio número 4, agregar su respuesta en la base de datos actualizando el contenido"""
        try:
            if dict_validacion.validate_length_response() is False: # Validate length of response
                return Response.tuple_response("Debe enviar una respuesta a la pregunta", 200)

            # Update response in response_exercises table
            respuesta: tuple = self.service.actualizar_respuesta(dict_request["id_respuesta"], dict_request["id_pregunta"], dict_request["respuesta"])
            if respuesta[0] is not None:
                return Response.tuple_response(respuesta[0], respuesta[1])

            # Save information in the table usuario_respuesta_ejercicios
            respuesta_usuario: tuple = self.service.respondiendo_prueba( id_estudiante ,dict_request["id_ejercicio"], dict_request["id_pregunta"], dict_request["id_respuesta"], id_relacion)
            if respuesta[0] is not None:
                return Response.tuple_response(respuesta[0], respuesta[1])

            # Calculate the score of the student
            calculo_operación = self.calcular_operación_ejercicio()
            if calculo_operación[1] != 200:
                return Response.tuple_response(calculo_operación[0], calculo_operación[1])
            return Response.tuple_response("Pregunta contestada correctamente", 201)
        except Exception as e:
            return Response.tuple_response("Problemas al agregar la respuesta del estudiante", 400)
        
    def actualizar_notas_ejercicio(self, id_estudiante: int, id_ejercicio: int) -> tuple:
        """Método para actualizar las notas de un ejercicio de un estudiante"""
        try:
            relation: tuple = self.service.relacion_estudiante_ejercicio(id_estudiante, id_ejercicio)
            if relation[1] != 200:
                return Response.tuple_response(relation[0], relation[1])

            id_respuesta = relation[0]["id"] # Getting id response user
            notas = self.service.calcular_nota_estudiante(id_estudiante, id_ejercicio, id_respuesta)
            if notas[0] is not None:
                return Response.tuple_response(notas[0], notas[1])
            
            return Response.tuple_response("Proceso realizado correctamente", 200)
        except Exception as e:
            return Response.tuple_response("Problemas al calcular las notas del ejercicio", 400)

    def control_intentos_ejercicio(self, id_ejercicio: int, id_usuario, total_veces: int) -> tuple[str, int]:
        """Método para controlar los intentos de un ejercicio"""
        try:
            # Check if the user has exercise with status 'in execution'
            check_ejercicio: tuple = self.service.check_ejercicio(id_ejercicio, id_usuario)
            if check_ejercicio[1] != 200:
                return Response.tuple_response(check_ejercicio[0], check_ejercicio[1])
            existe_ejercicio: int = check_ejercicio[0]["exist"] # 0: False   1: True
            
            if total_veces != 0 and existe_ejercicio != 1:
                # Check the attempts is finish
                prueba_fin: tuple|None = self.service.prueba_finalizada(id_ejercicio, id_usuario)
                if prueba_fin[1] != 200:
                    return Response.tuple_response(prueba_fin[0], prueba_fin[1])            

                terminada: int = prueba_fin[0]["fin_intentos"]
                if terminada == 1:
                    return Response.tuple_response("No puedes intentar más ejercicios, ya has completado todos los intentos", 201)

            # Only if the user does not have exercise with status 'in execution'
            if existe_ejercicio != 1:
                # Create relation between user and ejercicio
                estudiante: tuple = self.service.almacenar_estudiante_ejercicio(id_ejercicio, id_usuario) # start exercise with status 'without start' 
                if estudiante[0] is not None:
                    return Response.tuple_response(estudiante[0], estudiante[1])
                return Response.tuple_response("Proceso realizado correctamente", 201)
            else:
                return Response.tuple_response("No puedes iniciar este ejercicio, ya tienes uno en ejecución", 201)
        except Exception as e:
            return Response.tuple_response("Problemas al controlar los intentos del ejercicio", 400)

    def validar_estudiante_ejercicio(self, id_ejercicio: int, id_usuario: int) -> tuple:
        """Método para validar y almacenar información del estudiante que va ha realizar el ejercicio"""
        try:
            # validate user exist in db
            exist_estudiante:tuple = self.service.existe_estudiante_ejercicio(id_usuario, id_ejercicio)
            if exist_estudiante[1] != 200:
                return Response.tuple_response(exist_estudiante[0], exist_estudiante[1])
            total_veces: int = exist_estudiante[0]["total"]  # Cuento cantidad de intentos realizados

            # validate range of attempts of exercise
            intentos: tuple = self.service.validar_intetos_ejercicio(id_ejercicio)
            if intentos[1] != 200:
                return Response.tuple_response(intentos[0], intentos[1])
            num_intentos: int = intentos[0]["num_intentos"] # Intentos permitidos por prueba

            # validate if the user has reached the limit of attempts
            if num_intentos in [0,1,2,3]:
                # Only with the user has one and two attempts
                if total_veces <= num_intentos: # Si le quedan por hacer ---- Entra
                    # Modularize exercise in other functions to control the attempts
                    respuesta_intento: tuple = self.control_intentos_ejercicio(id_ejercicio, id_usuario, total_veces)
                    if respuesta_intento[1] != 201:
                        return Response.tuple_response(respuesta_intento[0], respuesta_intento[1])
                    
                    return Response.tuple_response(respuesta_intento[0], respuesta_intento[1])

                # With the user has unlimited attempts 
                if num_intentos == 0:
                    # Modularize exercise in other functions to control the attempts.
                    respuesta_intento: tuple = self.control_intentos_ejercicio(id_ejercicio, id_usuario, total_veces)
                    if respuesta_intento[1] != 201:
                        return Response.tuple_response(respuesta_intento[0], respuesta_intento[1])
                    
                    return Response.tuple_response(respuesta_intento[0], respuesta_intento[1])
            return Response.tuple_response("Error al crearse la configuración avanzada", 400)
        except Exception as e:
            return Response.tuple_response("Problemas al validar el estudiante del ejercicio", 400)

    def listar_preguntas_estudiante(self, id_ejercicio: int) -> tuple:
        """Por medio del id_ejercicio se listará las preguntas(puntos) del ejercicio
        el cual esté relacionado con la asignatura y está relacionado con el usuario"""
        try:
            # Last relation between user and exercise
            relation: tuple = self.mi_colegio.get_last_row("estudiante_ejercicio")
            if relation[1] != 200:
                return Response.tuple_response(relation[0], relation[1])
            id_relation = relation[0]["id"] # Getting id user

            preguntas = self.service.listar_preguntas_estudiante(id_ejercicio, id_relation)
            if preguntas[1] != 200:
                return Response.tuple_response(preguntas[0], preguntas[1])

            # Listar respuestas de cada pregunta
            if len(preguntas[0]) != 0:
                for i in range(len(preguntas[0])):
                    respuestas = self.listar_puntos_pregunta(preguntas[0][i]["id"])
                    if respuestas[1]!= 200:
                        return Response.tuple_response(respuestas[0], respuestas[1])

                    preguntas[0][i]["respuestas"] = respuestas[0]
                    # Filter the answers
                    response_format = [
                        respuesta for respuesta in preguntas[0][i]["respuestas"]
                        if respuesta["id_formato"] in [7, 8]
                    ]

                    # Yes, the response_format is not empty proceed to order the answers
                    if len(response_format) != 0:
                        # Order the answers by the initial position
                        orderly_responses = sorted(response_format, key=lambda x: x["posicion_inicial"])

                        # Replace the original answers with the ordered ones
                        for idx, respuesta in enumerate(preguntas[0][i]["respuestas"]):
                            if respuesta["id_formato"] in [7, 8]:
                                preguntas[0][i]["respuestas"][idx] = orderly_responses.pop(0)

                        # Remove posicion_inicial and id_formato from all answers
                    for respuesta in preguntas[0][i]["respuestas"]:
                        respuesta.pop("posicion_inicial", None)
                        respuesta.pop("id_formato", None)

            return Response.tuple_response(preguntas[0], preguntas[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron preguntas", 400)
        
    def listar_puntos_pregunta (self, id_pregunta: int) -> tuple:
        """Método para listar puntos de pregunta"""
        try:
            puntos = self.service.listar_puntos_pregunta(id_pregunta)
            if puntos[1] != 200:
                return Response.tuple_response(puntos[0], puntos[1])
            
            return Response.tuple_response(puntos[0], puntos[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron puntos", 400)
        
    def terminar_prueba(self, id_relación: int) -> tuple:
        """Método para terminar ejercicio"""
        try:
            terminar = self.service.terminar_prueba(id_relación)
            if terminar[0] is not None:
                return Response.tuple_response(terminar[0], terminar[1])
            
            return Response.tuple_response("Ejercicio terminado correctamente", 201)
        except Exception as e:
            return Response.tuple_response("Problemas al terminar el ejercicio", 400)

    def list_feedback(self, id_relationship: int) -> tuple:
        try:
            # Verify if the id relation exists
            exists_relationship: tuple = self.service.exist_relationship(id_relationship)
            if exists_relationship[1] != 200:
                return Response.tuple_response(exists_relationship[0], exists_relationship[1])
            relationship: int = exists_relationship[0]["exist"]  # Getting id relation

            if relationship == 1:
                # If the state is finished, we can access the feedback data
                dict_feedback: tuple = self.service.listar_feedback(id_relationship)
                if dict_feedback[1] != 200:
                    return Response.tuple_response(dict_feedback[0], dict_feedback[1])

                # Procesar los resultados
                data_usuario = defaultdict(dict)
                value_end:int = 0
                # id_formater:int = 0
                for row in dict_feedback[0]:
                    pregunta:str = row["preguntas"]
                    respuesta_escogida = row["respuesta_escogida"]
                    respuestas_verdaderas = row["respuestas_verdaderas"].split(', ')
                    puntuacion = float(row["puntuacion"])

                    # Agrupar las respuestas por pregunta
                    if pregunta not in data_usuario:
                        # Generar formato
                        data_usuario[pregunta] = {
                            "respuesta_escogida": [],
                            "respuestas_verdaderas": [],
                            "puntuacion": []
                        }

                    # Añadir la respuesta escogida y las respuestas verdaderas a su correspondiente lista
                    data_usuario[pregunta]["respuesta_escogida"].append(respuesta_escogida)
                    data_usuario[pregunta]["puntuacion"].append(puntuacion)

                    # Adicionar todas las respuestas correctas
                    for respuesta in respuestas_verdaderas:
                        if respuesta not in data_usuario[pregunta]["respuestas_verdaderas"]:
                            data_usuario[pregunta]["respuestas_verdaderas"].append(respuesta)

                    # Order the answers when the format is 7 or 8
                    if row["id_pregunta"] != value_end:
                        value_end = row["id_pregunta"]
                        result_query:tuple = self.service.order_questions_true(row["id_pregunta"])
                        if result_query[1] != 200:
                            return Response.tuple_response(result_query[0], result_query[1])

                        id_formater:set = {dic.get("id_formato", 0) for dic in result_query[0]}
                        if id_formater & {7, 8}:
                             data_usuario[pregunta]["respuestas_verdaderas"] = [dic["contenido"] for dic in result_query[0]]

                # Generar diccionario final
                list_feedback = []
                for pregunta, valores in data_usuario.items():
                    item = {
                        "preguntas": pregunta,
                        "respuesta_escogida": valores["respuesta_escogida"],
                        "respuestas_verdaderas": [", ".join(valores["respuestas_verdaderas"])],
                        "puntuacion": sum(valores["puntuacion"]),
                    }
                    list_feedback.append(item)

                return Response.tuple_response(list_feedback, 200)

            return Response.tuple_response("Error el id debe existir y el estado debe ser terminado", 400)
        except Exception as e:
            return Response.tuple_response("Error al intentar acceder a la retroalimentación", 400)
    
    def listar_pregunta(self, id_pregunta: int) -> tuple:
        try:
            pregunta: tuple = self.service.listar_pregunta(id_pregunta)
            if pregunta[1] != 200:
                return Response.tuple_response(pregunta[0], pregunta[1])
            
            dict_respuesta = {
                'contenidos': list(),
                'correctas': list(),
            }

            list_point: list = list(float(dic["puntuacion_respt"]) for dic in pregunta[0]) # List of point only True
            # Generate list of questions with points
            for dic in pregunta[0]:
                dict_respuesta["pregunta"] = dic["preguntas"]
                dict_respuesta["texto_completar"] = dic["texto_completar"]
                dict_respuesta["contenidos"].append(dic["contenido"])
                dict_respuesta["correctas"].append(dic["correcta"])

                # Calculate the total point of each question with correct answers
                if dic["correcta"] != 0:
                    dict_respuesta["puntuacion_respt"] = list_point

            # Rest list of points in cero if the question is not correct
            if sum(dict_respuesta["correctas"]) == 0:
                dict_respuesta["puntuacion_respt"] = [0.0] * len(dict_respuesta["correctas"])

            if len(dict_respuesta["contenidos"]) == 0:
                return Response.tuple_response([], 200)

            # Where the question are in disarray
            if pregunta[0][0]["id_formato"] in [7, 8]:
                data_position: list = list(int(dic["posicion_inicial"]) for dic in pregunta[0]) # List of position only True
                dict_respuesta["contenidos"]:list = [x for _, x in sorted(zip(data_position, dict_respuesta["contenidos"]))]

            return Response.tuple_response(dict_respuesta, pregunta[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron preguntas", 400)