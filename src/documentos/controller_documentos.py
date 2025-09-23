# from os import getenv
from dotenv import load_dotenv
from flask import request

from app.mi_colegio.documentos.service_documentos import DocumentosService
from app.mi_colegio.tareas.model_miColegio import DocumentoModel, UrlDocumentosRecursos, DocumentosCursoEstudiante
from app.utils.responses import Response
from app.mi_colegio.tareas.helper_miColegio import HelperSie
from app.mi_colegio.tareas.service_miColegio import MiColegioService

load_dotenv('../../documentos/config/.env.prod')

class DocumentosController:
    def __init__(self):
        self.service = DocumentosService()
        self.tarea = MiColegioService()

    def crear_documento_controller(self, documento: dict):
        """Crear documentos [carpetas]"""
        try:
            documento_validado = DocumentoModel(**documento)
            document_dict = documento_validado.model_dump() # Transformar el modelo a diccionario
            # Poder manejar los errores generados sobre el modelo

            if len(document_dict) == 0:
                return Response.tuple_response('Tiene errores en los valores ingresados', 200)
            
            # llamando al servicio para crear el documento
            documento_creado = self.service.crear_documento(document_dict)

            # Cuando falle la petición
            if documento_creado[0] is not None:
                return Response.tuple_response('Verifique los valores ingresados', 200)

            return Response.tuple_response('Documento creado exitosamente', documento_creado[1])
        except Exception as exc:
            return Response.tuple_response('Error en el servidor durante la creación del documento', 500)
        

    def listar_todos_documentos(self, id_docente: int, id_curso: int) -> tuple:
        """Listar todos los documentos [carpetas]"""
        try:
            usuario = self.service.buscar_usuario(id_docente)
            if usuario[1] != 200:
                return Response.tuple_response(usuario[0], usuario[1])
            (_, id_rol) = usuario[0][0].values()

            if id_rol != 2:
                # When the user have role admin or student
                return Response.tuple_response("Necesitas ser docente para acceder a esta información", 403)

            documentos_list = self.service.listar_todos_documentos(id_docente, id_curso)
            if len(documentos_list[0]) == 0:
                documentos_list = ([], documentos_list[1])
            
            # Recursos sin carpeta
            recursos = self.service.obtener_recursos_asignados_docentes(id_docente, id_curso)
            if recursos[1] != 200:
                return Response.tuple_response("No se encontraron recursos", 200)
            
            # Ordenar dict respuesta
            for valor in recursos[0]:
                valor["tipo"] = "recurso"
                valor["nombre_carpeta"] = valor["nombre_carpeta"].split("/")[-1].split(".")[0]
                documentos_list[0].append(valor)
            
            return Response.tuple_response(documentos_list[0], documentos_list[1])
        except Exception as e:
            return Response.tuple_response("Error en el servidor durante la consulta de los documentos", 500)
        
    def listar_documentos(self, documento_id: int):
        """Listar un documento [carpeta]"""
        try:
            documento_list = self.service.listar_documentos(documento_id)

            # Cuando falle la petición
            if not documento_list[0]:
                return Response.tuple_response("No se encontraron documentos para el usuario con ese id", 200)

            return Response.tuple_response(documento_list[0], documento_list[1])
        except Exception as e:
            return Response.tuple_response("Error en el servidor durante la consulta del documento", 500)
        
    def actualizar_documento(self, documento: dict, documento_id: int):
        """Actualizar documentos [carpetas]"""
        try:
            documento_validado = DocumentoModel(id_documento=documento_id, **documento)
            document_dict = documento_validado.model_dump() # Transformar el modelo a diccionario
            # Poder manejar los errores generados sobre el modelo

            if len(document_dict) == 0:
                return Response.tuple_response('Tiene errores en los valores ingresados', 200)
            
            # llamando al servicio para actualizar el documento
            documento_actualizado = self.service.actualizar_documento(document_dict)

            # Cuando falle la petición
            if documento_actualizado[0] is not None:
                return Response.tuple_response('Recuerda, el nombre debe ser unico', 200) 

            return Response.tuple_response('Documento actualizado exitosamente', documento_actualizado[1])
        except Exception as exc:
            return Response.tuple_response('Error en el servidor durante la actualización del documento', 500)
        
    def eliminar_documento(self, documento_id: int):
        """Eliminar documentos [carpetas]"""
        try:
            documento_eliminado = self.service.eliminar_documento(documento_id)

            # Cuando falle la petición
            if documento_eliminado[0] is not None:
                return Response.tuple_response(documento_eliminado[0], documento_eliminado[1])

            return Response.tuple_response('Documento eliminado exitosamente', 200)
        except Exception as e:
            return Response.tuple_response('Error en el servidor durante la eliminación del documento', 500)
    

    def cargar_recurso_controller(self, id_documento: int, id_docente:int, id_asignatura:int, descripcion:str, compartido:int):
        folder_azure = "miColegio/documentos"
        documento_validado = UrlDocumentosRecursos(id_docente=id_docente, id_asignatura=id_asignatura, id_documento=id_documento, descripcion=descripcion, compartido=compartido)
        document_dict = documento_validado.model_dump() # Transformar el modelo a diccionario

        if len(document_dict) == 0:
            return Response.tuple_response("Tienes errores en los valores ingresados", 400)

        try:
            resource_multi = HelperSie().upload_file(request)
            if resource_multi[1] != 201:
                return Response.tuple_response(resource_multi[0], resource_multi[1])
            
            # Para poder darle un conten type al recurso que se va ha subir
            file_name = request.files['recurso'].content_type
            content_type = HelperSie().get_content_type(file_name)

            if document_dict['id_documento']:
                listado = self.listar_documentos(documento_id=id_documento)[0]['nombre_carpeta']
                folder_azure = f"miColegio/documentos/{listado}"

            # Cargar el archivo al blob 
            upload_azure = HelperSie().upload_file_to_azure(folder_azure, content_type, request)
            if upload_azure[1] != 200:
                return Response.tuple_response(upload_azure[0], upload_azure[1])

            # Cargar la información del recurso a la base de datos
            (url, nombre) = upload_azure[0].values()
            document_dict.update({ "ruta_azure": f"{folder_azure}/{nombre}", "url_recurso": url})

            # Guardar en db
            save_resource = self.service.guardar_recursos(document_dict)
            if save_resource[0] is not None:
                return Response.tuple_response("Error al subir el archivo", 400)

            return Response.tuple_response("Archivo subido exitosamente", 201)
        except Exception as e:
            return Response.tuple_response("Error al subir el archivo", 400)
        
    def relacion_estudiantes (self, compartido:int, id_documento:None, id_asignatura:int) -> tuple[str, int]:
        """Adjuntar recurso a estudiantes por curso ya sea a uno a todos"""
        documento_valido = DocumentosCursoEstudiante(id_estudiante=compartido)
        documento_dict = documento_valido.model_dump()

        if len(documento_dict) == 0:
            return Response.tuple_response("Tienes errores en los valores ingresados", 200)

        try:
            recurso = self.tarea.get_last_row("url_documentos_recursos")
            if recurso is None:
                return Response.tuple_response("No se encontró ningún recurso", 200)
            id_recurso = recurso[0]["id"]
            documento_dict.update({'id_recurso':id_recurso})

            # Recurso compartido con un estudiante
            if compartido is not None:
                estudiante = self.service.estudiante_por_id(compartido)
                if estudiante[0] is None:
                    return Response.tuple_response("No se encontró ningún estudiante con ese id", 200)
                id_estudiante = estudiante[0][0]['id_usuario']
                id_curso = estudiante[0][0]['id_curso']
                documento_dict.update({'id_estudiante': id_estudiante, 'id_curso': id_curso, 'id_estudiante_curso': 0})

                # Almacenar relación en DB
                respuesta = self.service.documento_relacion_estudiante(documento_dict, id_asignatura, recurso_compartido=0)
                if respuesta[0] is not None:
                    return Response.tuple_response("Error al crear la relación", 400)

            #  Recurso compartido con todos los estudiantes de un curso
            if not id_documento and not compartido:
                cantidad_estudiantes = self.service.consultar_estudiantes_asignatura(id_asignatura)
                if not cantidad_estudiantes[0]:
                    return Response.tuple_response("No se encontró estudiantes en este curso!", 200)
                cantidad_estudiantes = cantidad_estudiantes[0]
                # Poder acceder al ID del curso por cada estudiante de un curso
                for index in cantidad_estudiantes:
                    id_estudiante = index["id_usuario"]
                    id_curso = index["id_curso"]
                    documento_dict.update({'id_estudiante': id_estudiante, 'id_curso': id_curso})

                    # Almacenar relación en DB
                    respuesta = self.service.documento_relacion_estudiante(documento_dict, id_asignatura, recurso_compartido=1)
                    if respuesta[0] is not None:
                        return Response.tuple_response("Error al crear la relación", 400)

            return Response.tuple_response("Recurso relacionado exitosamente", 201)
        except Exception as e:
            return Response.tuple_response("Error al crear la relación", 400)
        
    def listar_recurso_carpeta(self, id_carpeta:int):
        try:
            recurso = self.service.consultar_documentos_carpeta(id_carpeta)
            if len(recurso[0]) == 1 and recurso[0][0]["id_recurso"] == 0:
                return Response.tuple_response("No se encontró ningún recurso", 200)
        
            return Response.tuple_response(recurso[0], recurso[1])
        except Exception as e:
            return Response.tuple_response("No se encontró ningún recurso", 400)
        
    def eliminar_recurso_carpeta (self, id_recurso:int) -> tuple:
        """Eliminar recurso por su id tanto en el blob storage de azure como de base de datos"""
        try:
            # Obtener la ruta del recurso
            recurso_ruta = self.service.obtener_un_recurso(id_recurso)
            if not recurso_ruta[0]:
                return Response.tuple_response("No se encontró ningún recurso", 200)
            ruta_azure = recurso_ruta[0]["ruta_azure"]

            # Poder acceder a la ruta de un recurso en dos secciones
            list_ruta = ruta_azure.split("/")
            container_lambda = lambda x: "/".join(list_ruta[0:int(x)])
            container_name = str(container_lambda(3) if ruta_azure.count("/") > 2 else container_lambda(2))
            name_cheild = str(list_ruta.pop())

            # Borrar recurso de Azure
            recurso_azure = HelperSie().delete_resource_azure(container_name, name_cheild)
            if recurso_azure[1]!= 200:
                return Response.tuple_response(recurso_azure[0], recurso_azure[1])

            # Borrar recurso de base de datos
            recurso = self.service.eliminar_recurso(id_recurso)
            if recurso[0] is not None:
                return Response.tuple_response("No se encontró ningún recurso", 200)
        
            return Response.tuple_response("Recurso eliminado correctamente", 200)
        except Exception as e:
            return Response.tuple_response("Tenemos presentmos al intentar eliminar el recurso", 400)

    def listar_estudiantes_por_asignatura(self, id_asignatura:int) -> tuple:
        """Obtener todos los estudiantes de una asignatura"""
        try:
            estudiantes = self.service.consultar_estudiantes_asignatura(id_asignatura)
            if not estudiantes[0]:
                return Response.tuple_response("No se encontraron estudiantes", 200)
            
            return Response.tuple_response(estudiantes[0], estudiantes[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron estudiantes", 400)

    def listar_recursos_asignados(self, id_usuario: int, id_curso: int, id_asignatura: int) -> tuple[list[dict] | str, int]:
        """Obtain all resources assigned to a student"""
        try:
            usuario = self.service.buscar_usuario(id_usuario)
            if usuario[1] != 200:
                return Response.tuple_response(usuario[0], usuario[1])
            (_, id_rol) = usuario[0][0].values()

            if id_rol != 1:
                # When the user have role admin or teacher
                return Response.tuple_response("Necesitas ser estudiante para acceder a esta información", 403)

            # FIXME: Implementar query para obtener los recursos asignados a un estudiante por usuario, curso y asignatura. Dentro de 5 o 6 meses
            recursos = self.service.consultar_recursos_asignados(id_usuario, id_curso) # general
            if recursos[1] != 200:
                return Response.tuple_response(recursos[0], recursos[1])

            # If the list is empty, create a tuple with an empty list and the status code
            if not recursos[0]:
                recursos = ([], recursos[1])

            carpetas = self.service.obtener_recursos_individual(id_usuario, id_curso)
            if carpetas[1] != 200:
                return Response.tuple_response(carpetas[0], carpetas[1])

            for recurso in recursos[0]:
                recurso["nombre_recurso"] = recurso["nombre_recurso"].split("/")[-1].split(".")[0]

            recursos[0].extend(carpetas[0])
            return Response.tuple_response(recursos[0], recursos[1])
        except Exception as e:
            return Response.tuple_response("Presentamos problemas al intentar consultar los recursos", 400)
    
    def eliminar_recurso_asociado (self, id:int) -> tuple:
        """Eliminar recurso asociado a un estudiante de una asignatura"""
        try:
            recurso = self.service.eliminar_recurso_asociado_estudiantes(id)
            if recurso[0] is not None:
                return Response.tuple_response("No se encontraron recursos", 200)
            
            return Response.tuple_response("Recurso eliminado correctamente!", recurso[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron recursos al eliminar")

    def compartir_recursos (self, id_carpeta:int, id_tarea:int) -> tuple:
        """El docente podra compartir una carpeta con las tareas"""
        try:
            recurso = self.service.compartir_recursos(id_carpeta, id_tarea)
            if recurso[0] is not None:
                return Response.tuple_response(recurso[0], recurso[1])
            
            estado = self.service.cambio_estado_compartir(id_carpeta)
            if estado[0] is not None:
                return Response.tuple_response(estado[0], estado[1])
            
            return Response.tuple_response("Recurso compartido correctamente!", recurso[1])
        except Exception as e:
            return Response.tuple_response("No se encontraron recursos", 400)