from app.mi_colegio.tareas.helper_miColegio import HelperSie
from app.utils.responses import Response

class DocumentosService:
    """En este archivo puedes crear las consultas a la base de datos"""

    def __init__(self):
        self.helper = HelperSie()

    def crear_documento(self, dicct_documento: dict):
        """Metodo para crear carpetas"""
        try:
            query_crear_documento = self.helper.sie_cursor(
                """INSERT INTO documentos_recursos (nombre_carpeta, descripcion, id_asignatura_documento, id_docente)
                   VALUES (%s, %s, %s, %s)""",
                (dicct_documento["nombre"], dicct_documento["descripcion"], dicct_documento["id_asignatura"], dicct_documento["id_docente"]),commit=True,)
            return Response.tuple_response(query_crear_documento, 201)
        
        except Exception as e:
            return Response.tuple_response('Error al generar la carpeta', 404)

    def listar_todos_documentos(self, id_docente: int, id_curso: int) -> tuple:
        """Me todo para listar las carpetas"""
        try:
            query_listar_documentos = self.helper.sie_cursor(
                """SELECT dr.id_documento, dr.nombre_carpeta, dr.descripcion, dr.id_asignatura_documento, dr.id_docente,
                dr.estado, dr.fecha_creacion, ifnull(dr.ultima_modificacion, '0000-00-00 00:00:00') as ultima_modificacion
            FROM documentos_recursos as dr
            INNER JOIN asignatura_institucion as ai on dr.id_asignatura_documento = ai.id
            WHERE id_docente = %s AND ai.id_curso = %s""", (id_docente, id_curso), many=True, )
            return Response.tuple_response(query_listar_documentos, 200)

        except Exception as e:
            return Response.tuple_response('Error al listar las carpetas', 404)

    def listar_documentos(self, documento_id: int):
        """Metodo para listar por carpeta"""
        try:
            query_listar_documento = self.helper.sie_cursor(
                """select id_documento, nombre_carpeta, descripcion, id_asignatura_documento, id_docente,
                    estado, fecha_creacion, ifnull(ultima_modificacion, '0000-00-00 00:00:00') as ultima_modificacion
                from documentos_recursos where id_documento = %s""", (documento_id))
            return Response.tuple_response(query_listar_documento, 200)

        except Exception as e:
            return Response.tuple_response('Error al listar las carpetas', 404)

    def actualizar_documento(self, dicct_documento: dict):
        """Metodo para actualizar las carpetas"""
        try:
            query_actualizar_documento = self.helper.sie_cursor(
                """UPDATE documentos_recursos SET nombre_carpeta = IFNULL(%s, nombre_carpeta), descripcion = IFNULL(%s, descripcion) WHERE id_documento = %s""",
                (dicct_documento["nombre"], dicct_documento["descripcion"], dicct_documento["id_documento"]),
                commit=True, )
            return Response.tuple_response(query_actualizar_documento, 201)

        except Exception as e:
            return Response.tuple_response('Error al actualizar la carpeta', 404)

    def eliminar_documento(self, id_documento: int):
        """Metodo para eliminar las carpetas"""
        try:
            query_eliminar_documento = self.helper.sie_cursor(
                """DELETE FROM documentos_recursos WHERE id_documento = %s""", (id_documento), commit=True, )
            return Response.tuple_response(query_eliminar_documento, 200)

        except Exception as e:
            return Response.tuple_response('Error al eliminar la carpeta', 400)

    def guardar_recursos(self, dicc_recursos: dict):
        """Metodo para guardar los recursos"""
        try:    
            query_guardar_recursos = self.helper.sie_cursor(
                """INSERT INTO url_documentos_recursos (id_documento, subido_por, ruta_azure, url_recurso, descripcion)
                    VALUES (%s, %s, %s, %s, %s)""",
                (dicc_recursos["id_documento"], dicc_recursos["id_docente"], dicc_recursos["ruta_azure"], dicc_recursos["url_recurso"], dicc_recursos["descripcion"]),commit=True,)
            return Response.tuple_response(query_guardar_recursos, 201)

        except Exception as e:
            return Response.tuple_response('Error al guardar los recursos', 400)
        
    def estudiante_por_id(self, id_usuario:int):
        """Me todo para obtener los estudiantes de estudiante_curso por su id"""
        try:
            query_consultar_estudiante = self.helper.sie_cursor(
                """SELECT id, id_usuario, id_curso FROM estudiante_curso
                    WHERE id_usuario = %s""", (id_usuario,), many=True,)
            return Response.tuple_response(query_consultar_estudiante, 200)
        
        except Exception as e:
            return Response.tuple_response("Error al intentar obtener los estudiantes por curso", 400)
        
    def documento_relacion_estudiante (self, dicc_recurso: dict, id_asignatura: int, recurso_compartido: int) -> tuple[dict, int]:
        """Me todo para relacionar documentos con estudiantes"""
        try:
            query_recurso = self.helper.sie_cursor(
                """INSERT INTO documentos_curso_estudiantes (id_recurso, id_estudiante, id_curso, id_asignatura, recurso_compartido) VALUES (%s, %s, %s, %s, %s)""",
                (dicc_recurso["id_recurso"], dicc_recurso["id_estudiante"], dicc_recurso["id_curso"], id_asignatura, recurso_compartido), commit=True,)

            return Response.tuple_response(query_recurso, 201)
        except Exception as e:
            return Response.tuple_response("Error al asignar el recurso al estudiante", 400)
        
    def consultar_estudiantes_asignatura(self, id_asignatura:int) -> tuple :
        """Me todo para obtener los estudiantes de estudiante_curso por medio de id_asignatura"""
        try:
            query_consultar_estudiantes = self.helper.sie_cursor(
            """select ec.id_usuario, ec.id_curso, concat(p.nombres,' ',p.apellidos) as estudiante from asignatura_institucion as ai
                inner join estudiante_curso as ec on ai.id_curso = ec.id_curso
                inner join usuarios as u on ec.id_usuario = u.id
                inner join persona as p on u.id_persona = p.id
            where ai.id = %s""", (id_asignatura,), many=True,)
            return Response.tuple_response(query_consultar_estudiantes, 200)
        
        except Exception as e:
            return Response.tuple_response("Error al intentar obtener los estudiantes por curso", 400)
        
    def consultar_documentos_carpeta(self, id_carpeta:int):
        """Me todo para obtener los recurso por id de carpeta"""
        try:
            query_consultar_documentos = self.helper.sie_cursor(
            """select dr.id_documento, dr.nombre_carpeta, dr.descripcion as descripcion_carpeta, dr.id_asignatura_documento, dr.id_docente,
                dr.estado, dr.fecha_creacion, ifnull(dr.ultima_modificacion, '0000-00-00 00:00:00') as ultima_modificacion,
                IF (udr.id_documento, udr.id, 0) AS id_recurso,
                IF (udr.id_documento, udr.url_recurso, 0) AS url_recurso,
                IF (udr.id_documento, udr.descripcion, 0) AS descripcion_recurso
            from documentos_recursos as dr
            left join url_documentos_recursos as udr on dr.id_documento = udr.id_documento
            where dr.id_documento = %s""", (id_carpeta,), many=True,)
        
            return Response.tuple_response(query_consultar_documentos, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar obtener los documentos por carpeta", 400)
        
    def eliminar_recurso(self, id_recurso:int):
        """Me todo para eliminar el recurso"""
        try:
            query_eliminar_recurso = self.helper.sie_cursor(
                """DELETE FROM url_documentos_recursos WHERE id = %s""", (id_recurso,), commit=True, )
        
            return Response.tuple_response(query_eliminar_recurso, 200)
        except Exception as e:
            return Response.tuple_response("Error al eliminar el recurso", 400)
        
    def obtener_un_recurso(self, id_recurso:int):
        """Me todo para obtener un recurso por su id"""
        try:
            query_consultar_recurso = self.helper.sie_cursor(
                """SELECT id as id_recurso, id_documento, ruta_azure, url_recurso, descripcion FROM url_documentos_recursos WHERE id = %s""", (id_recurso,), )
            return Response.tuple_response(query_consultar_recurso, 200)
        
        except Exception as e:
            return Response.tuple_response("Error al intentar obtener el recurso", 400)
        
    def  consultar_recursos_asignados(self, id_estudiante:int, id_curso:int) -> tuple[list[dict] |str, int]:
        """Me todo para obtener los recursos asignados a un estudiante, recursos individuales"""
        try:
            query_consultar_recursos = self.helper.sie_cursor(
            """SELECT udr.id AS id_recurso, udr.ruta_azure as nombre_recurso, udr.url_recurso, udr.descripcion AS descripcion_recurso
            FROM documentos_curso_estudiantes AS dce
            INNER JOIN url_documentos_recursos AS udr ON dce.id_recurso = udr.id
            WHERE dce.id_estudiante = %s AND dce.id_curso = %s""", (id_estudiante, id_curso),many=True)
            return Response.tuple_response(query_consultar_recursos, 200)
        
        except Exception as e:
            return Response.tuple_response("Error al intentar obtener los recursos asignados", 400)
    
    def obtener_recursos_individual(self, id_estudiante:int, id_curso:int) -> tuple[list[dict] |str, int]:
        """Me todo para obtener los recursos asignados a un estudiante solo carpetas"""
        try:
            query_carpetas = self.helper.sie_cursor(
                """select IF(udr.id_documento IS NOT NULL, dr.id_documento , 0) AS id_carpeta,
            IF(udr.id_documento IS NOT NULL, dr.nombre_carpeta , 0) AS nombre_carpeta,
            IF(udr.id_documento IS NOT NULL, dr.descripcion, 0) AS descripcion
            from documentos_curso_estudiantes as dce
            inner join asignatura_institucion as ai on dce.id_curso = ai.id_curso
            inner join documentos_recursos as dr on ai.id = dr.id_asignatura_documento
            inner join url_documentos_recursos as udr on dr.id_documento = udr.id_documento
            where dce.id_curso = %s and dce.id_estudiante = %s group by dr.nombre_carpeta, dr.descripcion, dr.estado, udr.id_documento""", (id_curso, id_estudiante), many=True)
            return Response.tuple_response(query_carpetas, 200)
        
        except Exception as e:
            return Response.tuple_response("Error al intentar obtener los recursos asignados", 400)

    def buscar_usuario(self, id_usuario:int) -> tuple[list[dict]|str, int]:
        """Me todo para buscar el usuario por su id"""
        try:
            query_usuario = self.helper.sie_cursor(
                """SELECT id, id_rol FROM usuarios WHERE id = %s""", (id_usuario,), many=True,)
            return Response.tuple_response(query_usuario, 200)

        except Exception as e:
            return Response.tuple_response("Error al intentar obtener el usuario", 400)

    def eliminar_recurso_asociado_estudiantes(self, id:int) -> tuple:
        """Me todo para eliminar el recurso asociado a un estudiante"""
        try:
            query_eliminar_recurso = self.helper.sie_cursor(
                """DELETE FROM documentos_curso_estudiantes WHERE id = %s""", (id,), commit=True, )
        
            return Response.tuple_response(query_eliminar_recurso, 201)
        except Exception as e:
            return Response.tuple_response("Error al eliminar el recurso asociado a un estudiante", 400)
    
    def obtener_recursos_asignados_docentes (self, id_docente:int, id_curso:int) -> tuple:
        """Me todo para obtener los recursos asignados a un docente"""
        try:
            query_recursos = self.helper.sie_cursor("""select udr.id as id_recurso, udr.ruta_azure as nombre_carpeta, udr.url_recurso, udr.descripcion
            from documentos_curso_estudiantes  as dce
            inner join url_documentos_recursos as udr on dce.id_recurso = udr.id
            where dce.id_curso = %s and udr.subido_por = %s and udr.id_documento is null group by udr.id, udr.ruta_azure , udr.url_recurso, udr.descripcion""", (id_curso, id_docente), many=True)

            return Response.tuple_response(query_recursos, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar obtener los recursos asignados", 400)
        
    def compartir_recursos(self, id_carpeta:int, id_tarea:int) -> tuple:
        """Poder relacionar una carpeta con una tarea"""
        try:
            query_compartir = self.helper.sie_cursor(
                """INSERT INTO documentos_recursos_tareas (id_documento, id_tarea) VALUES (%s, %s)""",
                (id_carpeta, id_tarea),commit=True,)
            return Response.tuple_response(query_compartir, 201)
        except Exception as e:
            return Response.tuple_response("Error al compartir el recurso", 400)
    
    def cambio_estado_compartir (self, id_carpeta:int) -> tuple:
        """Metodo para cambiar el estado del recurso compartido"""
        try:
            query_compartir = self.helper.sie_cursor(
                """UPDATE documentos_recursos SET estado = 'Compartido' WHERE id_documento = %s""", (id_carpeta,), commit=True,)
            return Response.tuple_response(query_compartir, 201)
        except Exception as e:
            return Response.tuple_response("Error al cambiar el estado del recurso compartido", 400)