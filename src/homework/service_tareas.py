from 
from app.utils.responses import Response


class MiColegioService:
    """En este archivo puedes crear la consultas a la base de datos"""

    def __init__(self):
        self.helper = HelperSie()

    def asignaturas_estudiante(self, usuario: str, curso: str):
        """Metodo para consultar las asignaturas por estudiante"""
        try:
            query_estudiante_asignatura = self.helper.sie_cursor(
                """select ai.id as id_asignatura, ai.asignatura, ec.id_curso from estudiante_curso as ec
                inner join asignatura_institucion as ai on ec.id_curso = ai.id_curso
                where ec.id_usuario = %s and ec.id_curso = %s""",
                (usuario, curso),
                many=True,
            )
            return query_estudiante_asignatura

        except Exception as e:
            raise Exception(e.args[0])

    def docente_por_asignatura(self, id_asignatura: int):
        """Metodo para consultar las asignaturas por estudiante"""
        try:
            query_docente_por_asignatura = self.helper.sie_cursor(
                """SELECT am.id_asignatura,
                    IFNULL(am.id_docente, 'No hay docente asignado') as id_docente,
                IF(am.id_docente,(SELECT CONCAT(p.nombres, ' ', p.apellidos)
                    FROM usuarios AS u
                    INNER JOIN persona AS p ON u.id_persona = p.id
                WHERE u.id = am.id_docente),
                    'No hay docente asignado') AS nombre_profesor
                FROM asignar_materias AS am
                WHERE am.id_asignatura = %s""",
                (id_asignatura),
            )
            return query_docente_por_asignatura

        except Exception as e:
            raise Exception(e.args[0])
        
    def obtener_id_usuario(self, usuario: str):
        """Metodo para obtener el id del usuario"""
        try:
            query_obtener_id_usuario = self.helper.sie_cursor(
                """SELECT id FROM usuarios WHERE usuario = %s""", (usuario),)
            return query_obtener_id_usuario

        except Exception as e:
            raise Exception(e.args[0])
        
    def validar_existencia(self, asignatura: str, curso: str):
        """Metodo para validar la existencia asignatura y curso"""
        try:
            query_validar_existencia = self.helper.sie_cursor(
                """ SELECT IFNULL((SELECT COUNT(*) as asignatura from asignatura_institucion WHERE id = %s), 0) as asignatura, 
                    IFNULL((SELECT COUNT(*) as curso  from cursos WHERE id = %s), 0) as curso"""
                , (asignatura, curso),)
            return Response.tuple_response(query_validar_existencia, 200)

        except Exception as exc:
            return Response.tuple_response("Error al intentar validar la existencia de la asignatura y el curso", 400)

    def crear_tareas_docente(self, tareas):
        """Metodo para crear tareas"""
        try:
            query_crear_tarea = self.helper.sie_cursor(
                """INSERT INTO tareas (nombre, descripcion, id_docente, asignatura, id_curso, fecha_finalizacion)
                VALUES (%s, %s, %s, %s, %s, %s)""",(tareas['nombre'], tareas['descripcion'], tareas['docente'], tareas['asignatura'], tareas['curso'], tareas['fecha_finalizacion']), commit=True,)
            return query_crear_tarea

        except Exception as e:
            raise Exception(e.args[0])

    def consultar_tareas_creadas(self, usuario: str, curso: str, asignatura: str):
        try:
            query_consultar_tareas = self.helper.sie_cursor(
                """ SELECT t.id as id_tarea, t.nombre as nombre_tarea, t.descripcion as descripcion_tarea, t.id_docente, t.asignatura as id_asignatura,
                ai.asignatura as nombre_asignatura, CONCAT(p.nombres,' ', p.apellidos) as nombre_profesor, ifnull(tru.estado, 'Sin contestar') as estado,
                t.fecha_finalizacion FROM tareas AS t
                    INNER JOIN usuarios u on t.id_docente = u.id
                    INNER JOIN persona AS p ON u.id_persona = p.id
                    INNER JOIN asignatura_institucion as ai on t.asignatura = ai.id
                    LEFT JOIN tarea_relacion_usuario as tru on u.id = tru.id_usuario
                WHERE t.id_docente = %s AND t.id_curso = %s AND t.asignatura = %s""",
                (usuario, curso, asignatura), many=True, )
            return query_consultar_tareas
        except Exception as e:
            raise Exception("Error al intentar obtener las tareas del estudiante")
        

    def actualizar_tareas_existentes(self, tarea):
        """Metodo para actualizar tareas"""
        try:
            query_actualizar_tarea = self.helper.sie_cursor(
                """UPDATE tareas SET nombre = IFNULL(%s, nombre), descripcion = IFNULL(%s, descripcion), 
                    ultima_modificacion = IFNULL(%s, ultima_modificacion), fecha_finalizacion = IFNULL(%s, fecha_finalizacion) WHERE id = %s""",
                (tarea["nombre"], tarea["descripcion"], tarea["ultima_modificacion"], tarea["fecha_finalizacion"], tarea["id_tarea"]), commit=True,)

            return Response.tuple_response(query_actualizar_tarea, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar actualizar la tarea", 400)
    
    def eliminar_tareas_existentes(self, tarea):
        """Metodo para eliminar tareas"""
        try:
            query_eliminar_tarea = self.helper.sie_cursor(
                """DELETE FROM tareas WHERE id = %s""", (tarea.id_tarea), commit=True,)
            return query_eliminar_tarea

        except Exception as e:
            raise Exception(e.args[0])
        
    def consultar_tarea_por_id(self, tarea: str):
        """Metodo para consultar las tareas por id"""
        try:
            query_consultar_tarea_por_id = self.helper.sie_cursor(
                """SELECT count(*) as cantidad_tareas FROM tareas WHERE id = %s""", (tarea.id_tarea),)
            return query_consultar_tarea_por_id

        except Exception as e:
            raise Exception(e.args[0])
        
    def guardar_recurso_tarea(self, docuemento: dict):
        """Metodo para guardar el recurso de la tarea"""
        try:
            query_guardar_recurso_tarea = self.helper.sie_cursor(
                """INSERT INTO url_tareas_storage (direccion_url, url_nombre, url_estudiante, url_docente)
                VALUES (%s, %s, %s, %s)""",(docuemento["direccion_url"], docuemento["url_nombre"], docuemento["url_estudiante"], docuemento["url_docente"]), commit=True,)
            return Response.tuple_response(query_guardar_recurso_tarea, 200)
        except Exception as e:
            return Response.new_error("Error al intentar guardar el recurso", 400)
        
    def contar_respuestas_tarea(self, id_tarea: int, id_usuario: int) -> tuple:
        """Saber si el estudiante ya ha contestado la tarea"""
        try:
            query_respuestas = self.helper.sie_cursor(
                """SELECT count(*) as cantidad_tareas, id_url_recurso FROM tarea_relacion_usuario 
                WHERE id_tarea = %s AND id_usuario = %s GROUP BY id_url_recurso""", (id_tarea, id_usuario))
            return Response.tuple_response(query_respuestas, 200)
        except Exception as e:
            return Response.tuple_response("Error al contar las respuesta", 400)
    
    def obtener_info_recurso (self, id:int) -> tuple:
        """Metodo para obtener la información del recurso de la tarea por su id"""
        try:
            query_info_recurso = self.helper.sie_cursor(
                """SELECT url_nombre, url_estudiante FROM url_tareas_storage WHERE id = %s""", (id))
            return Response.tuple_response(query_info_recurso, 200)
        except Exception as e:
            return Response.tuple_response("Error al obtener la información del recurso", 400)
        
    def eliminar_recurso (self, id:int) -> tuple:
        """Me todo para eliminar la fila del recurso de la tarea por su id"""
        try:
            print('message ', id)
            query_eliminar_recurso = self.helper.sie_cursor(
                """DELETE FROM url_tareas_storage WHERE id = %s""", (id), commit=True)
            return Response.tuple_response(query_eliminar_recurso, 200)
        except Exception as e:
            print('error 2', e)
            return Response.tuple_response("Error al eliminar el recurso", 400)

    def consultar_info_estudiante(self, estudiante_id: int, asignatura_id: int, curso_id: int):
        """Me todo para consultar la información del estudiante sobre la tarea"""
        try:
            query_consultar_info_estudiante = self.helper.sie_cursor(
                """ select ifnull(tru.id, NULL) as id_respuesta, concat(p.nombres,' ',p.apellidos) as docente, u.url as avatar_usuario, ai.id as id_asignatura, ai.asignatura as asignatura,
                    t.id as id_tarea, t.nombre as nombre_tarea, t.descripcion, ifnull(tru.estado, 'Sin contestar') as estado, tru.nota_tarea, t.fecha_finalizacion from tareas as t
                inner join estudiante_curso as ec on t.id_curso = ec.id_curso
                inner join usuarios as u on t.id_docente = u.id
                inner join persona as p on u.id_persona = p.id
                inner join asignatura_institucion as ai on t.asignatura = ai.id
                left join tarea_relacion_usuario as tru on t.id = tru.id_tarea and tru.id_usuario = %s
                where t.asignatura = %s and t.id_curso = %s group by tru.id, tru.estado, p.nombres, p.apellidos, u.url, ai.id, ai.asignatura, t.id, t.nombre, t.descripcion """, (estudiante_id, asignatura_id, curso_id), many=True,)
            
            return Response.tuple_response(query_consultar_info_estudiante, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar obtener la información del estudiante", 400)
    
    def carpetas_compartidas(self, estudiante_id: int, asignatura_id: int, curso_id: int) -> tuple:
        """Me todo para consultar las carpetas compartidas a ese estudiante"""
        try:
            query_carpetas_compartidas = self.helper.sie_cursor(
                """select dr.id_documento as id_carpeta, dr.nombre_carpeta, t.id as id_tarea from documentos_recursos_tareas as drt
            inner join tareas as t on drt.id_tarea = t.id
            inner join tareas_estudiantes_curso as tec on t.id = tec.id_tarea
            inner join documentos_recursos as dr on drt.id_documento = dr.id_documento
            where tec.id_estudiante = %s and t.asignatura = %s and tec.id_curso = %s""", (estudiante_id, asignatura_id, curso_id), many=True)

            return Response.tuple_response(query_carpetas_compartidas, 200)
        except Exception as exc:
            return Response.tuple_response("Error al intentar obtener las carpetas compartidas", 400)
    
    def tareas_info_estudiantes(self, estudiante_id: int) -> tuple:
        """Me todo para consultar todas las tareas asignadas al estudiante"""
        try:
            query_tareas = self.helper.sie_cursor(
                """ select concat(p.nombres,' ',p.apellidos) as docente, u.url as avatar_usuario, ai.id as id_asignatura, ai.asignatura as asignatura,
                t.id as id_tarea, t.nombre as nombre_tarea, t.descripcion, ifnull(tru.estado, 'Sin contestar') as estado, ifnull(tru.nota_tarea, 0) as nota_tarea, t.fecha_finalizacion
                from tareas as t
                inner join estudiante_curso as ec on t.id_curso = ec.id_curso
                inner join usuarios as u on t.id_docente = u.id
                inner join persona as p on u.id_persona = p.id
                inner join asignatura_institucion as ai on t.asignatura = ai.id
                left join tarea_relacion_usuario as tru on t.id = tru.id_tarea and ec.id_usuario = tru.id_usuario
                where ec.id_usuario = %s group by tru.estado, tru.nota_tarea, p.nombres, p.apellidos, u.url, ai.id, ai.asignatura, t.id, t.nombre, t.descripcion """, (estudiante_id), many=True,)

            return Response.tuple_response(query_tareas, 200)
        except Exception as exc:
            raise Response.tuple_response("Error al intentar obtener las tareas del estudiante", 400)

    def get_last_row(self, table: str):
        """Me todo para obtener la última fila de la tabla que se le pase como parametro"""
        try:
            query_last_row = self.helper.sie_cursor("""SELECT * FROM %s ORDER BY id DESC LIMIT 1""" % table,)
            return Response.tuple_response(query_last_row, 200)
        except Exception as exc:
            raise Response.tuple_response("Error al intentar obtener la última fila", 400)
        

    def actualizar_estado_tarea(self, dicctionary: dict):
        """Me todo para relacionar las tareas con los usuarios que suben la respuesta de la tarea"""
        try:
            query_actualizar_estado_tarea = self.helper.sie_cursor(
                """ insert into tarea_relacion_usuario (id_tarea, id_usuario, id_url_recurso, estado) values (%s, %s, %s, %s)""",
                (dicctionary["id_tarea"], dicctionary["id_usuario"], dicctionary["id_url_recurso"], dicctionary["estado"]), commit=True,)

            return Response.tuple_response(query_actualizar_estado_tarea, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar actualizar el estado de la tarea", 400)
        

    def consultar_estudiantes_por_curso(self, curso: str):
        """Me todo para consultar los estudiantes por curso"""
        try:
            query_consultar_estudiantes_por_curso = self.helper.sie_cursor(
                """SELECT ec.id_usuario, ec.id_curso FROM estudiante_curso as ec
                    WHERE ec.id_curso = %s""", (curso), many=True,)
            return Response.tuple_response(query_consultar_estudiantes_por_curso, 200)

        except Exception as e:
            return Response.tuple_response("Error al intentar obtener los estudiantes por curso", 400)
    
    def tareas_estudiantes_curso (self, id_tarea: int, id_usuario: int, id_curso: int):
        """Me todo para asignar tareas a los estudiantes de un curso"""
        try:
            query_asignar_tareas = self.helper.sie_cursor(
                """INSERT INTO tareas_estudiantes_curso (id_tarea, id_estudiante, id_curso) VALUES (%s, %s, %s)""",
                (id_tarea, id_usuario, id_curso), commit=True,)
            return Response.tuple_response(query_asignar_tareas, 200)

        except Exception as e:
            return Response.tuple_response("Error al asignar tareas a los estudiantes", 400)
        
    def consultar_tareas_enviadas(self, id_tarea: int):
        """Me todo para consultar las tareas enviadas por los estudiantes"""
        try:
            query_consultar_tareas_enviadas = self.helper.sie_cursor(
                """select tru.id as id_respuesta, id_usuario, concat(p.nombres,' ',p.apellidos) as nombre, t.nombre as nombre_tarea, tru.estado as estado_tarea, count(*) as respondida,
                    max(uts.url_nombre) as nombre_recurso, max(uts.url_estudiante) as url_recurso, ifnull(max(tru.nota_tarea),0) as nota_tarea, max(tru.fecha_creacion) as fecha_creacion
                from tarea_relacion_usuario as tru
                inner join tareas as t on tru.id_tarea = t.id
                inner join usuarios as u on tru.id_usuario = u.id
                inner join persona as p on u.id_persona = p.id
                inner join url_tareas_storage as uts on tru.id_url_recurso = uts.id
                where tru.id_tarea = %s group by tru.id, tru.id_tarea, tru.id_usuario, tru.estado order by respondida desc""",(id_tarea), many=True,)
            return Response.tuple_response(query_consultar_tareas_enviadas, 200)

        except Exception as e:
            return Response.tuple_response("Error al intentar consultar las tareas enviadas", 400)

    def calificando_tareas(self, dicct_calificacion: dict):
        """Me todo para calificar las tareas"""
        try:
            query_calificar_tareas = self.helper.sie_cursor(
                """UPDATE tarea_relacion_usuario SET nota_tarea = %s WHERE id = %s""",
                (dicct_calificacion["nota_tarea"], dicct_calificacion["id_respuesta"]), commit=True,)
            return Response.tuple_response(query_calificar_tareas, 200)

        except Exception as e:
            return Response.tuple_response("Error al intentar calificar las tareas", 400)
    
    def generar_comentario(self, dicct: dict) -> tuple:
        """Me todo para generar un comentario"""
        try:
            query_generar_comentario = self.helper.sie_cursor(
                """INSERT INTO tareas_comentarios (id_respuesta, id_usuario, comentario) VALUES (%s, %s, %s)""",
                (dicct["id_respuesta"], dicct["id_usuario"], dicct["comentario"]), commit=True,)
            return Response.tuple_response(query_generar_comentario, 201)
        
        except Exception as e:
            return Response.tuple_response("Error al intentar generar un comentario", 400)

    def consultar_comentarios(self, id_entrega:int) -> tuple:
        """Me todo para consultar los comentarios"""
        try:
            query_consultar_comentarios = self.helper.sie_cursor(
                """select tc.id as id_comentario, tc.comentario, concat(p.nombres,' ',p.apellidos) as usuario, u.url as url_avatar, tru.nota_tarea, tc.fecha_respuesta
            from tarea_relacion_usuario as tru
            inner join tareas_comentarios as tc on tru.id = tc.id_respuesta
            inner join usuarios as u on tc.id_usuario = u.id
            inner join persona as p on u.id_persona = p.id
            where tru.id = %s order by tc.id desc""", (id_entrega), many=True,)
            return Response.tuple_response(query_consultar_comentarios, 200)
        
        except Exception as e:
            return Response.tuple_response("Error al intentar consultar los comentarios", 400)

    def tarea_entregada(self, id_tarea: int, id_estudiante: int) -> tuple:
        """Me todo para recuperar la respuesta de la tarea entregada por un estudiante"""
        try:
            query_tarea_entregada = self.helper.sie_cursor(
                """select tru.id as id_entrega, tru.id_tarea, uts.url_nombre as nombre_recurso, uts.url_estudiante as url_recurso, tru.nota_tarea, tru.fecha_creacion
            from tarea_relacion_usuario as tru
            inner join url_tareas_storage uts on tru.id_url_recurso = uts.id
            where tru.id_usuario = %s and tru.id_tarea = %s order by tru.id desc limit 1""", (id_estudiante, id_tarea), many=True,)
            return Response.tuple_response(query_tarea_entregada, 200)
        
        except Exception as e:
            return Response.tuple_response("Error al intentar recuperar la respuesta de la tarea entregada", 400)