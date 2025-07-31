import datetime

from app.mi_colegio.tareas.service_miColegio import MiColegioService
from app.mi_colegio.tareas.model_miColegio import TareaModel, UrlRecursosModel, TareaRelacionUsuario, TareasComentarios, TareasEstudianteCurso
from app.utils.responses import Response
from app.mi_colegio.tareas.helper_miColegio import HelperSie

from os import getenv
from dotenv import load_dotenv

load_dotenv('../../config/.env.prod')

class MiColegioController:
    """En este archivo puedes crear la logica de negocio"""

    def __init__(self):
        self.conector = MiColegioService()

    def consultar_asignaturas_estudiante(self, usuario: str, curso: str):
        """Obtener las asignaturas por estudiante"""
        try:
            asignaturas = self.conector.asignaturas_estudiante(usuario, curso)
            if asignaturas is None:
                return Response.tuple_response("No se encontraron asignaturas para el estudiante con ese usuario y curso", 200)

            for asignatura in asignaturas:
                id_asignatura = asignatura["id_asignatura"]
                docentes = self.conector.docente_por_asignatura(id_asignatura)

                # Un docente tambien puede no estar asignado a una asignatura 
                if docentes is None:
                    asignatura["info_docente"] = { "id_docente": None, "nombre_profesor": None, }
                    continue

                # Almacenar la información del docente en la asignatura
                asignatura["info_docente"] = {
                    "id_docente": docentes["id_docente"], "nombre_profesor": docentes["nombre_profesor"],
                }

            return asignaturas

        except Exception as e:
            return Response.new_error("Error al consultar las asignaturas del estudiante", 400)
        

    def crear_tareas(self, docente: str, asignatura: str, curso: str, objet_tarea: dict):
        """Crear tareas"""
        try:
            # Validar los parámetros de entrada
            tareas = TareaModel(asignatura=asignatura, curso=curso, docente=docente, **objet_tarea)
            validate_dicct_tarea = tareas.model_dump()

            # por si el diccionario esta vacio
            if len(validate_dicct_tarea) == 1:
                return Response.tuple_response(validate_dicct_tarea, 400)

            # Validar la existencia de la asignatura y el curso
            validar_existencia = self.conector.validar_existencia(asignatura, curso)
            response_data = validar_existencia[0] # Obtener el diccionario de la respuesta
            for key, value in response_data.items():
                if int(value) == 0:
                    return Response.tuple_response(f"El valor de {key} no existe", 400)
                
            # Crear la tarea
            crear_tarea = self.conector.crear_tareas_docente(validate_dicct_tarea)
            if crear_tarea != None:
                return Response.tuple_response("No se pudo crear la tarea", 400)
            
            return Response.success("Tarea creada exitosamente", 201)
        except Exception as e:
            return Response.tuple_response("Error al crear la tarea", 400)
        
    def asignar_tarea_estudiante(self, curso: str):
        """Cada vez que se crea una tarea se debe asignar a todos los estudiantes de ese curso"""
        try:
            # Acceder a la ultima tarea creada
            response_tareas = self.conector.get_last_row("tareas")
            if response_tareas is None:
                return Response.tuple_response("No se encontró la tarea", 200)
            id_tarea = response_tareas[0]["id"]

            search_students = self.conector.consultar_estudiantes_por_curso(curso)
            if search_students[0] is None:
                return Response.tuple_response("No se encontraron estudiantes para el curso", 200)

            # Asignar la tarea a los estudiantes de un curso
            for student in search_students[0]:
                save_relation = self.conector.tareas_estudiantes_curso(id_tarea, student["id_usuario"], student["id_curso"])
                if save_relation[0] is not None:
                    return Response.tuple_response(f"Al estudiante {student['id']} no se le asigno la tarea", 400)
                
            return Response.tuple_response("Tarea asignada exitosamente", 201)
        except Exception as e:
            return Response.tuple_response("Error al asignar la tarea", 400)

    def consultar_tareas(self, docente: str, curso: str, asignatura: str):
        """Obtener las tareas creadas por un docente en una asignatura"""
        try:
            # Consultar las tareas del estudiante
            tareas: tuple = self.conector.consultar_tareas_creadas(docente, curso, asignatura)

            # Formatear las fechas de las tareas
            for key, value in enumerate(tareas):
                tareas[key]["fecha_finalizacion"] = value["fecha_finalizacion"].strftime("%Y-%m-%d %H:%M:%S")
            
            if tareas is None:
                return Response.tuple_response("No se obtuvieron tareas", 200)

            return tareas
        except Exception as e:
            return Response.tuple_response("Error al consultar las tareas", 400)
        

    def actualizar_tareas_existentes(self, id_tarea: str, objet_tarea: dict):
        """Actualizar tareas existentes"""
        try:
            now = datetime.datetime.now() # Fecha actual
            objet_tarea["ultima_modificacion"] = now.strftime("%Y-%m-%d %H:%M:%S") # Formato de fecha

            # # Validar los parámetros de entrada
            validar_tarea = TareaModel(id_tarea=id_tarea, **objet_tarea)
            dicct_tarea = validar_tarea.model_dump()

            # Actualizar la tarea
            actualizar_tarea = self.conector.actualizar_tareas_existentes(dicct_tarea)

            if actualizar_tarea:
                return Response.tuple_response(actualizar_tarea[0], actualizar_tarea[1])
        except Exception as e:
            return Response.tuple_response("Error al actualizar la tarea")
        
    
    def eliminar_tareas_existentes(self, id_tarea: str):
        """Eliminar tareas existentes"""
        try:
            # Validar los parámetros frente al modelo
            validar_tarea = TareaModel(id_tarea=id_tarea)
            consultar_tarea = self.conector.consultar_tarea_por_id(validar_tarea)
            existencia = consultar_tarea["cantidad_tareas"]

            if existencia == 0:
                return Response.new_error("No se encontró la tarea", 404)

            # Eliminar la tarea
            eliminar_tarea = self.conector.eliminar_tareas_existentes(validar_tarea)
            if eliminar_tarea is not None:
                return Response.new_error("No se pudo eliminar la tarea", 400)
            
            return Response.success("Tarea eliminada exitosamente", 200)

        except Exception as e:
            return Response.new_error("Error al eliminar la tarea", 400)
        

    def consultar_info_estudiante(self, estudiante_id: int, asignatura_id: int, curso_id: int):
        """Consultar la información del estudiante"""
        try:
            info_estudiante = self.conector.consultar_info_estudiante(estudiante_id, asignatura_id, curso_id)
            if info_estudiante[1] != 200:
                return Response.tuple_response("El estudiante no tiene tareas asignadas", 200)
            
            # Recursos compartidos con un estudiante
            tareas = self.conector.carpetas_compartidas(estudiante_id, asignatura_id, curso_id)
            if tareas[1] != 200:
                return Response.tuple_response(tareas[0], tareas[1])
            
            # Poder adicionar la información de las carpetas compartidas a la información del estudiante
            for valor in info_estudiante[0]:
                for tarea in tareas[0]:
                    if valor["id_tarea"] == tarea["id_tarea"]:
                        valor["carpeta_compartida"] = {"id_carpeta": tarea["id_carpeta"], "nombre_carpeta": tarea["nombre_carpeta"]}

            return Response.tuple_response(info_estudiante[0], info_estudiante[1])
        except Exception as e:
            return Response.tuple_response("Error al consultar la información del estudiante", 400)
        
    def consultar_tareas_estudiantes(self, estudiante_id: int) -> tuple:
        """Consultar todas las tareas asignadas a un estudiante"""
        try:
            tareas = self.conector.tareas_info_estudiantes(estudiante_id)
            if tareas[1] != 200:
               return Response.tuple_response(tareas[0], tareas[1])
        
            return Response.tuple_response(tareas[0], tareas[1])
        except Exception as e:
            return Response.tuple_response("Error al consultar las tareas", 400)

    def carga_recurso_estudiante(self, request)-> tuple:
        """Cargar un recurso a una tarea por parte del docente"""
        folder_azure = getenv('AZURE_STORAGE_CONTAINER_NAME')

        try:
            documento_validado = UrlRecursosModel(direccion_url=folder_azure)
            document_dict = documento_validado.model_dump() # Transformar el modelo a diccionario

            if len(document_dict) == 0:
                return Response.tuple_response("Tienes errores en los valores ingresados", 400)

            # TODO: Mover toda esta logica a un helper para para que se puedan reutilizar en otros modelos
            resource_multi = HelperSie().upload_file(request)
            if resource_multi[1] != 201:
                return Response.tuple_response(resource_multi[0], resource_multi[1])
            
            # Para poder darle un content type al recurso que se va ha subir
            file_name = request.files['recurso'].content_type
            content_type = HelperSie().get_content_type(file_name)

            # Cargar el archivo al blob 
            upload_azure = HelperSie().upload_file_to_azure(folder_azure, content_type, request)
            if upload_azure[1] != 200:
                return Response.tuple_response(upload_azure[0], upload_azure[1])

            # Actualizar el diccionario con la información obtenida de la carga del recurso en azure (storage account)
            (url, nombre) = upload_azure[0].values()
            document_dict.update({ "url_nombre": nombre, "url_estudiante": url})

            # Guardar en db
            save_resource = self.conector.guardar_recurso_tarea(document_dict)
            if save_resource[0] is not None:
                return Response.tuple_response("Error al subir el archivo", 400)

            return Response.tuple_response("Archivo subido exitosamente", 201)
        except Exception as e:
            return Response.tuple_response("Error al subir el archivo", 400)
        
    def respondiendo_una_tarea(self, id_tarea: int, id_usuario: int) -> tuple:
        """Guardar la respuesta de una tarea por parte del usuario estudiante"""
        try:
            # existencia respuesta
            existencia = self.conector.contar_respuestas_tarea(id_tarea, id_usuario)
            if existencia[1] != 200:
                return Response.tuple_response(existencia[0], existencia[1])

            """Si existe una respuesta previa de ese usuario, se elimina el recurso y se actualiza la respuesta con el nuevo recurso cargado"""
            if existencia[0] is not None:
                id_recurso = existencia[0]["id_url_recurso"]

                # Eliminar recurso
                eliminar_recurso = self.eliminar_recursos_azure(id_recurso)
                if eliminar_recurso[1] != 201:
                    return Response.tuple_response(eliminar_recurso[0], eliminar_recurso[1])

                # Actualizar respuesta
                response_relacion = self.guardar_relacion_tarea_usuario(id_tarea, id_usuario)
                if response_relacion[1] != 201:
                    return Response.tuple_response(response_relacion[0], response_relacion[1])
                return Response.tuple_response("Tarea actualizada correctamente", 201)
            
            "Si no existe una respuesta, se crea una nueva respuesta"
            response_relacion = self.guardar_relacion_tarea_usuario(id_tarea, id_usuario)
            if response_relacion[1] != 201:
                return Response.tuple_response(response_relacion[0], response_relacion[1])
            
            return Response.tuple_response(response_relacion[0], response_relacion[1])
        except Exception as e:
            return Response.tuple_response("Error al guardar la respuesta", 400)
        
    def eliminar_recursos_azure(self, id_recurso: int) -> tuple:
        """Eliminar el recurso subido a Azure"""
        try:
            info_recurso = self.conector.obtener_info_recurso(id_recurso)
            if info_recurso[1] != 200:
                return Response.tuple_response(info_recurso[0], info_recurso[1])
            nombre_carpeta = getenv("AZURE_STORAGE_CONTAINER_NAME")
            nombre_recurso = info_recurso[0]["url_nombre"]

            delete_azure = HelperSie().delete_resource_azure(nombre_carpeta, nombre_recurso)
            if delete_azure[1] != 200:
                return Response.tuple_response(delete_azure[0], delete_azure[1])
            
            delete_local = self.conector.eliminar_recurso(id_recurso)
            if delete_local[1] != 200:
                return Response.tuple_response(delete_local[0], delete_local[1])
            
            return Response.tuple_response("Recurso eliminado exitosamente", 201)
        except Exception as e:
            return Response.tuple_response("Error al eliminar el recurso", 400)

    def guardar_relacion_tarea_usuario(self, id_tarea: int, id_usuario: int) -> tuple:
        """Guardar la relación tarea usuario"""
        try:
            documento_validado = TareaRelacionUsuario(id_tarea=id_tarea, id_usuario=id_usuario)
            document_dict = documento_validado.model_dump() # Transformar el modelo a diccionario

            if len(document_dict) == 0:
                return Response.tuple_response("Tienes errores en los valores ingresados", 400)

            # Recuperar ultimo recurso subido
            last_resource = self.conector.get_last_row("url_tareas_storage")
            if last_resource is None:
                return Response.tuple_response(last_resource, 200)
            document_dict.update({ "id_url_recurso": last_resource[0]["id"], "estado": "contestado"})

            # Guardar la relacion entre el recurso y el estudiante
            save_relation = self.conector.actualizar_estado_tarea(document_dict)
            if save_relation[0] is not None:
                return Response.tuple_response("No se pudo guardar la relación", 400)
            
            return Response.tuple_response("Archivo subido exitosamente", 201)
        except Exception as e:
            return Response.tuple_response("Error al guardar la relación", 400)

    def hilo_comentarios_tareas(self,id_respuesta:int|None, id_usuario:int, comentario:str) -> tuple:
        """Crear un hilo para enviar un comentario a una tarea"""
        try:
            # Validar los parámetros de entrada
            validar_comentario = TareasComentarios(id_respuesta=id_respuesta, id_usuario=id_usuario, comentario=comentario)
            document_dict = validar_comentario.model_dump() # Transformar el modelo a diccionario
            
            if len(document_dict) == 0:
                return Response.tuple_response("Tienes errores en los valores ingresados", 200)

            # Recuperar ultimo tarea creada
            if document_dict["id_respuesta"] is None:
                respuesta_id = self.conector.get_last_row("tarea_relacion_usuario")
                if respuesta_id[1] != 200:
                    return Response.tuple_response(respuesta_id[0], respuesta_id[1])
                document_dict.update({ "id_respuesta": respuesta_id[0]["id"]})

            # Enviar el comentario
            enviar_comentario = self.conector.generar_comentario(document_dict)
            if enviar_comentario[0] is not None:
                return Response.tuple_response(enviar_comentario[0], enviar_comentario[1])
            
            return Response.tuple_response("Comentario enviado exitosamente", enviar_comentario[1])
        except Exception as e:
            return Response.tuple_response("Error al guardar el comentario", 400)
        
    def tarea_entregada_estudiante(self, id_tarea: int, id_estudiante: int) -> tuple:
        """Consultar entrega de una tarea por un estudiante"""
        try:
            tarea_entregada = self.conector.tarea_entregada(id_tarea, id_estudiante)
            if tarea_entregada[1] != 200:
                return Response.tuple_response(tarea_entregada[0], tarea_entregada[1])
            
            return Response.tuple_response(tarea_entregada[0], tarea_entregada[1])
        except Exception as e:
            return Response.tuple_response("Error al consultar la tarea", 400)
        
    def consultar_comentarios_tareas(self, id_entrega:int) -> tuple:
        """Consultar todos los comentarios de una tarea por el id del trabajo realizado del estudiante"""
        try:
            comentarios = self.conector.consultar_comentarios(id_entrega)
            if comentarios[0] != 200:
                return Response.tuple_response(comentarios[0], comentarios[1])
            
            return Response.tuple_response(comentarios[0], comentarios[1])
        except Exception as e:
            return Response.tuple_response("Error al consultar los comentarios", 400)
            
    def consultar_tareas_enviadas(self, id_tarea:int) -> tuple:
        """Consultar las tareas enviadas por los estudiantes"""
        try:
            tareas = self.conector.consultar_tareas_enviadas(id_tarea)
            if tareas is None:
                return Response.tuple_response("Ningun estudiante ha enviado la tarea", 404)
            
            return Response.tuple_response(tareas[0], tareas[1])
        except Exception as e:
            return Response.tuple_response("Error al consultar la tarea", 400)


    def calificar_tareas_enviadas(self, id_respuesta: int, dicc_calificacion: dict):
        """Calificar las tareas enviadas por los estudiantes"""
        try:
           # Validar que la nota sea un número válido con máximo 5 dígitos y 2 decimales
           nota = dicc_calificacion.get("nota_tarea")
           if not isinstance(nota, (int, float)) or not (0 <= nota <= 999.99):
               return Response.tuple_response("La nota debe ser un número entre 0.00 y 999.99", 400)

           validate_qualification = TareasEstudianteCurso(id_respuesta=id_respuesta, **dicc_calificacion)
           dict_qualification = validate_qualification.model_dump()

           if len(dict_qualification) == 0:
               return Response.tuple_response("Tienes errores en los valores ingresados", 400)

           # Calificar la tarea
           calificar_tarea = self.conector.calificando_tareas(dict_qualification)
           if calificar_tarea[0] is not None:
             return Response.tuple_response("Error al calificar la tarea", 400)
            
           return Response.tuple_response("Tarea calificada exitosamente", 201)
        except Exception as e:
            return Response.tuple_response("Error al calificar la tarea", 400)