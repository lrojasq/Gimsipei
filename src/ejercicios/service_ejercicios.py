from app.mi_colegio.tareas.helper_miColegio import HelperSie
from app.utils.responses import Response

class EjercicioService:
    """Clase para el manejo de consultas a la base de datos"""

    def __init__(self) -> None:
        self.helper = HelperSie()
    
    def listar_opciones(self) -> tuple:
        """Metodo para listar las opciones con las que se puede crear un ejercicio"""
        try:
            query_listar_opciones = self.helper.sie_cursor("""SELECT * FROM opciones_ejercicios""", many=True)
            return Response.tuple_response(query_listar_opciones, 200)
        except Exception as exc:
            raise Response.tuple_response("Error al intentar listar las opciones", 400)
        
    def listar_opcion(self, id_opcion: int) -> tuple:
        """Opciones para listar una opcion por su id"""
        try:
            query_listar_opcion = self.helper.sie_cursor("""SELECT * FROM opciones_ejercicios WHERE id = %s""", (id_opcion))
            return Response.tuple_response(query_listar_opcion, 200)
        except Exception as exc:
            raise Response.tuple_response("Error al intentar listar la opcion", 400)
        
    def crear_ejercicios(self, dict_Request: dict) -> tuple:
        """Metodo para crear un ejercicio"""
        try:
            query_crear_ejercicio = self.helper.sie_cursor(
                """CALL almacenado_configuracion_ejercicio(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (dict_Request["nombre"], dict_Request["id_asignatura"], dict_Request["descripcion"], dict_Request["vista_retro_alimentacion"], dict_Request["seleccion_pregunta"],
                dict_Request["barajar_pregunta"], dict_Request["num_intentos"], dict_Request["fecha_publicacion"], dict_Request["fecha_finalizacion"], dict_Request["control_tiempo"], dict_Request["porcentaje_exito"], dict_Request["texto_final"]), commit=True,)
            return Response.tuple_response(query_crear_ejercicio, 201)
        except Exception as e:
            return Response.tuple_response("No se encontraron opciones para listar", 400)
    
    def listar_ejercicios(self, id_asignatura:int) -> tuple:
        """Método lista los ejercicios"""
        try:
            query_listar_ejercicios = self.helper.sie_cursor("""select id, nombre, asignatura, fecha_creacion from ejercicios where asignatura = %s""", (id_asignatura),many=True)
            return Response.tuple_response(query_listar_ejercicios, 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios para listar", 400)
        
    def validar_usuario(self, id_usuario: int) -> tuple:
        """Método en que valido si el usuario es estudiante o tiene otro rol"""
        try:
            query_validar_usuario = self.helper.sie_cursor("""select if(id_rol != 1, Null, 'Estudiante') as rol from usuarios as u where id = %s""", (id_usuario),)
            return Response.tuple_response(query_validar_usuario, 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios para listar", 400)

    def listar_ejercicios_intentos(self, id_asignatura: int, id_usuario: int) -> tuple:
        """Me todo para listar los ejercicios con los intentos"""
        try:
            query_intentos = self.helper.sie_cursor("""SELECT e.id, e.nombre, e.asignatura,
                    IF(ee.id_ejercicio,
                        (SELECT CONCAT(
                            (SELECT COUNT(*) FROM estudiante_ejercicio as ee2 WHERE ee2.id_estudiante = %s AND ee2.id_ejercicio = e.id),
                            '/',
                            if(pa.num_intentos = 0, 'Ilimitado', pa.num_intentos)
                        ) FROM parametros_avanzados as pa WHERE pa.id_ejercicio = e.id),
                        (SELECT CONCAT( 0 ,'/', if(pa2.num_intentos = 0, 'Ilimitado', pa2.num_intentos) ) FROM parametros_avanzados as pa2 where pa2.id_ejercicio = e.id)
                    ) AS intentos,
                    ifnull(NULL,(
                        select id from estudiante_ejercicio as ee3 where e.id = ee3.id_ejercicio AND ee3.id_estudiante = %s and ee3.estado = 'Terminada' order by id desc limit 1
                        )) as id_intento,
                     e.fecha_creacion
                FROM ejercicios e
                LEFT JOIN estudiante_ejercicio as ee ON e.id = ee.id_ejercicio AND ee.id_estudiante = %s
                WHERE asignatura = %s
                GROUP BY e.id, e.nombre, e.asignatura, ee.id_ejercicio, e.fecha_creacion""",(id_usuario, id_usuario, id_usuario, id_asignatura), many=True)
            return Response.tuple_response(query_intentos, 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios para listar", 400)

    def listar_ejercicio(self, id_ejercicio: int) -> tuple:
        """Me todo para listar ejercicios por su id"""
        try:
            query_listar_ejercicio = self.helper.sie_cursor("""select e.nombre, e.asignatura, e.fecha_creacion,
                ifnull(pa.descripcion, null) as descripcion,
                ifnull(pa.vista_retro_alimentacion, null) as vista_retro_alimentacion,
                ifnull(pa.seleccion_pregunta, null) as seleccion_pregunta,
                ifnull(pa.barajar_preguntas, null) as barajar_preguntas,
                ifnull(pa.num_intentos, null) as num_intentos,
                ifnull(pa.fecha_publicacion, null) as fecha_publicacion,
                ifnull(pa.fecha_finalizacion, null) as fecha_finalizacion,
                ifnull(pa.control_tiempo, null) as control_tiempo,
                ifnull(pa.porcentaje_exito, null) as porcentaje_exito,                                                            
                ifnull(pa.texto_final, null) as texto_final
                from ejercicios as e
                    inner join parametros_avanzados as pa on e.id = pa.id_ejercicio
                where e.id = %s""", (id_ejercicio))
            return Response.tuple_response(query_listar_ejercicio, 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios", 400)  
    
    def eliminar_ejercicio(self, id_ejercicio: int) -> tuple:
        """Metodo para eliminar un ejercicio"""
        try:
            query_eliminar_ejercicio = self.helper.sie_cursor(
                """DELETE FROM ejercicios where id = %s""", (id_ejercicio), commit=True,)
            return Response.tuple_response(query_eliminar_ejercicio, 201)
        except Exception as e:
            return Response.tuple_response("Error al eliminar el ejercicio", 400)
        
    def actualizar_ejercicio_service (self, id_ejercicio: int, dict_Request: dict) -> tuple:
        """Metodo para actualizar la configuracion de un ejercicio"""
        try:
            query_actualizar_configuracion = self.helper.sie_cursor(
                """CALL almacenado_actualizar_configuracion_ejercicio(%s ,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (dict_Request["nombre"], dict_Request["descripcion"], dict_Request["vista_retro_alimentacion"], dict_Request["seleccion_pregunta"], dict_Request["barajar_pregunta"], 
                dict_Request["num_intentos"], dict_Request["fecha_publicacion"], dict_Request["fecha_finalizacion"], dict_Request["control_tiempo"], dict_Request["porcentaje_exito"], dict_Request["texto_final"], id_ejercicio), commit=True,)
            return Response.tuple_response(query_actualizar_configuracion, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar actualizar la configuracion del ejercicio", 400)
        
    def listar_formato_pregunta(self) -> tuple:
        """Metodo para listar ejercicios"""
        try:
            query_listar_formato_pregunta = self.helper.sie_cursor("""SELECT * FROM formato_preguntas""", many=True)
            return Response.tuple_response(query_listar_formato_pregunta, 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios", 400)
        
    
    def listar_formato_pregunta_id(self, id_formato: int) -> tuple:
        """Metodo para listar ejercicios por su id"""
        try:
            query_listar_formato_pregunta = self.helper.sie_cursor("""SELECT * FROM formato_preguntas WHERE id = %s""", (id_formato))
            return Response.tuple_response(query_listar_formato_pregunta, 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron ejercicios", 400)
        
    def crear_pregunta(self, id_ejercicio: int, id_formato: int, dict_Request: dict) -> tuple:
        """Me todo para crear una pregunta"""
        try:
            query_crear_pregunta = self.helper.sie_cursor(
                """insert into preguntas_ejerc (preguntas, texto_completar, id_formato, id_ejercicio) VALUES (%s, %s, %s, %s)""", (dict_Request["pregunta"], dict_Request["texto_completar"], id_formato, id_ejercicio), commit=True,)
            return Response.tuple_response(query_crear_pregunta, 201)
        except Exception as e:
            return Response.tuple_response("Falla al crear la pregunta", 400)
    
    def crear_respuesta(self, contenido: str, correcta: int, puntuación: int, id_pregunta: int, init_position: int) -> tuple:
        """Me todo para crear las respuestas de una pregunta"""
        try:
            query_crear_respuesta = self.helper.sie_cursor(
                """insert into respuestas_ejerc (contenido, correcta, puntuacion_respt, id_pregunta, posicion_inicial) 
                values (%s, %s, %s, %s, %s)""", (contenido, correcta, puntuación, id_pregunta, init_position), commit=True,)
            return Response.tuple_response(query_crear_respuesta, 201)
        except Exception as e:
            return Response.tuple_response("Falla al crear la respuesta", 400)
        
    def listar_preguntas_ejercicio(self, id_ejercicio: int) -> tuple:
        """Me todo para listar las preguntas de un ejercicio"""
        try:
            query_listar_preguntas = self.helper.sie_cursor("""select pe.id as id_pregunta, pe.preguntas, pe.id_formato as tipo,
                ifnull(NULL, (select sum(re.puntuacion_respt) from respuestas_ejerc as re where re.id_pregunta = pe.id)) as 'Puntuacion_max' from ejercicios as e
                inner join preguntas_ejerc as pe on e.id = pe.id_ejercicio where e.id = %s""", (id_ejercicio), many=True)
            return Response.tuple_response(query_listar_preguntas, 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron preguntas", 400)
    
    def listar_puntos_pregunta(self, id_pregunta: int) -> tuple:
        """Me todo para listar los puntos de una pregunta"""
        try:
            query_listar_puntos_pregunta = self.helper.sie_cursor("""select pe.id as id_pregunta, re.id as id_respuesta, re.contenido, re.correcta, pe.id_formato, re.posicion_inicial from preguntas_ejerc as pe
            inner join respuestas_ejerc as re on pe.id = re.id_pregunta where pe.id = %s""", (id_pregunta,), many=True)
            return Response.tuple_response(query_listar_puntos_pregunta, 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron puntos", 400)
        
    def eliminar_pregunta(self, id_pregunta: int) -> tuple:
        """Me todo para eliminar una pregunta por su id"""
        try:
            query_eliminar_pregunta = self.helper.sie_cursor(
                """DELETE FROM preguntas_ejerc where id = %s""", (id_pregunta), commit=True,)
            return Response.tuple_response(query_eliminar_pregunta, 201)
        except Exception as e:
            return Response.tuple_response("Error al eliminar la pregunta", 400)
    
    def actualizar_pregunta_service(self, id_pregunta: int, pregunta: str, texto_completar: str) -> tuple:
        """Me todo para actualizar una pregunta"""
        try:
            query_actualizar_pregunta = self.helper.sie_cursor(
                """update preguntas_ejerc set preguntas = ifnull(%s, preguntas), texto_completar = ifnull(%s, texto_completar) where id = %s""",
                (pregunta, texto_completar, id_pregunta), commit=True,)
            return Response.tuple_response(query_actualizar_pregunta, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar actualizar la pregunta", 400)
        
    def eliminar_respuestas(self, id_prgunta: int) -> tuple[str, int]:
        """Me todo para eliminar las respuestas de una pregunta"""
        try:
            query_eliminar_respuestas = self.helper.sie_cursor("""DELETE FROM respuestas_ejerc WHERE id_pregunta = %s""", (id_prgunta), commit=True,)
            return Response.tuple_response(query_eliminar_respuestas, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar eliminar las respuestas", 400)
        
    def actualizar_puntuacion_service(self, id_pregunta: int) -> tuple:
        """Me todo para  setear la correcta y la puntuacion de una pregunta a cero"""
        try:
            query_update_puntos = self.helper.sie_cursor("""UPDATE respuestas_ejerc
                SET contenido = NULL, correcta = 0, puntuacion_respt = 0
            WHERE id_pregunta = %s AND contenido is NOT NULL""", (id_pregunta,), commit=True,)
            return Response.tuple_response(query_update_puntos, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar actualizar la puntuación", 400)
    
    def obtener_respuestas_preg(self, id_respuesta: int) -> tuple:
        """Obtener las cuatro opciones de respuestas"""
        try:
            query_obtener_respuestas = self.helper.sie_cursor("""select * from respuestas_ejerc where id_pregunta = %s order by posicion_inicial""", (id_respuesta,), many=True)
            return Response.tuple_response(query_obtener_respuestas, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar obtener las respuestas", 400)
    
    def actualizar_respuetas_service(self, contenido:str, correcta:int, score:float, id_pregunta:int, init_position:int) -> tuple:
        """Me todo para actualizar las respuestas de una pregunta"""
        try:
            query_actualizar_respuestas = self.helper.sie_cursor("""update respuestas_ejerc set contenido = %s , correcta = %s, puntuacion_respt = %s, posicion_inicial = %s
                where id_pregunta = %s and contenido is null limit 1""",(contenido, correcta, score, init_position, id_pregunta), commit=True)
            return Response.tuple_response(query_actualizar_respuestas, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar actualizar las respuestas", 400)

    def set_value_to_null(self, id_pregunta: int) -> tuple:
        """Pasar los valores de las respuestas a null"""
        try:
            query_set_value = self.helper.sie_cursor("""update respuestas_ejerc set contenido = NULL, correcta = 0, puntuacion_respt = 0.00, posicion_inicial = 0
                where id_pregunta = %s and contenido is not null""", (id_pregunta,), commit=True)
            return Response.tuple_response(query_set_value, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar actualizar las respuestas", 400)
        
    def respuesta_seleccionada(self, id_respuesta: str, id_pregunta: int) -> tuple:
        """Me todo para obtener la respuesta seleccionada por el usuario de una pregunta"""
        try:
            query_respuesta_seleccionada = self.helper.sie_cursor("""select re.id from preguntas_ejerc as pe
                inner join respuestas_ejerc as re on pe.id = re.id_pregunta
            where pe.id = %s and re.id = %s""",(id_pregunta, id_respuesta), many=True)
            return Response.tuple_response(query_respuesta_seleccionada, 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron respuestas", 400)
        
    def respondiendo_prueba(self, id_estudiante: int, id_ejercicio: int, id_pregunta: int, id_respuesta: int, id_intento: int) -> tuple:
        """Me todo para registrar la respuesta seleccionada por el usuario"""
        try:
            query_respondiendo_prueba = self.helper.sie_cursor(
                """insert into usuario_respuesta_ejercicios (id_estudiante, id_ejercicio, id_pregunta, seleccionada, id_intento) values (%s, %s, %s, %s, %s)""",
                (id_estudiante, id_ejercicio, id_pregunta, id_respuesta, id_intento), commit=True,)
            return Response.tuple_response(query_respondiendo_prueba, 201)
        except Exception as e:
            return Response.tuple_response("Error al registrar la respuesta", 400)

    def actualizar_respuesta(self, id_respuesta: int, id_pregunta: int, respuesta: str) -> tuple[str, int]:
        """Me  todo para actualizar la respuesta seleccionada por el usuario"""
        try:
            query_actualizar_respuesta = self.helper.sie_cursor(
                """update respuestas_ejerc set contenido=%s where id=%s and id_pregunta=%s""",
                (respuesta, id_respuesta, id_pregunta), commit=True,)
            return Response.tuple_response(query_actualizar_respuesta, 200)
        except Exception as e:
            return Response.tuple_response("Error al almacenar la respuesta", 400)
        
    def calcular_nota(self, id_respuesta: int) -> tuple:
        """Me todo para calcular la nota de un ejercicio"""
        try:
            query_calcular_nota = self.helper.sie_cursor("call actualizar_nota(%s)", (id_respuesta,), commit=True)
            return Response.tuple_response(query_calcular_nota, 200)
        except Exception as e:
            return Response.tuple_response("Error al calcular la nota", 400)
        
    def calcular_puntuación(self, id_respuesta: int) -> tuple:
        """Me todo para calcular la puntuacion de una pregunta"""
        try:
            query_calcular_puntuación = self.helper.sie_cursor("call actualizar_puntuacion(%s)", (id_respuesta), commit=True)
            return Response.tuple_response(query_calcular_puntuación, 200)
        except Exception as e:
            return Response.tuple_response("Error al calcular la puntuacion", 400)

    def notas_puntuacion_estudiante_formato5(self, id_respuesta: int, correcta: int) -> tuple[str, int]:
        """Me todo para calcular la nota, puntuacion de un ejercicio en formato 5"""
        try:
            query_nota = self.helper.sie_cursor("""CALL actualizar_nota_formato5(%s, %s)""", (id_respuesta, correcta), commit=True)
            query_puntuacion = self.helper.sie_cursor("""CALL generar_puntuacion_ejercicio_formato5(%s, %s)""", (id_respuesta, correcta), commit=True)

            if query_puntuacion is None and query_nota is None:
                return Response.tuple_response(None, 200)
            return Response.tuple_response("Error al calcular la puntuacion", 400)
        except Exception as e:
            return Response.tuple_response("Error al calcular la puntuacion", 400)
    
    def listar_preguntas_estudiante(self, id_ejercicio: int, id_relacion: int) -> tuple:
        """Me todo para listar las preguntas de un ejercicio"""
        try:
            query_listar_preguntas = self.helper.sie_cursor("""
                select pe.id, pe.preguntas, pe.texto_completar, pe.id_formato, pe.id_ejercicio, ee.id as id_intento, pe.fecha_creacion from ejercicios as e
                inner join asignatura_institucion as ai on e.asignatura = ai.id
                inner join preguntas_ejerc as pe on e.id = pe.id_ejercicio
                inner join estudiante_ejercicio as ee on e.id = ee.id_ejercicio
                where e.id = %s and ee.id = %s""", (id_ejercicio, id_relacion), many=True)
            return Response.tuple_response(query_listar_preguntas, 200)
        except Exception as e:
            return Response.tuple_response("No se encontraron preguntas", 400)
        
    def existe_estudiante_ejercicio(self, id_estudiante: int, id_ejercicio: int) -> tuple:
        """Me todo para validar si un estudiante ya esta registrado en un ejercicio"""
        try:
            query_existe_estudiante_ejercicio = self.helper.sie_cursor(
                """select count(*) as total from estudiante_ejercicio where id_estudiante = %s and id_ejercicio = %s""",
                (id_estudiante, id_ejercicio), many=False)
            return Response.tuple_response(query_existe_estudiante_ejercicio, 200)
        except Exception as e:
            return Response.tuple_response("Error al validar el estudiante", 400)

    def validar_intetos_ejercicio(self, id_ejercicio: int) -> tuple:
        """Método para validar el número de intentos que se tienen permitido por ejercicio"""
        try:
            query_intentos = self.helper.sie_cursor("""select ifnull(pa.num_intentos, null) as num_intentos
                from ejercicios as e
            left join parametros_avanzados as pa on e.id = pa.id_ejercicio where  e.id = %s""", (id_ejercicio,), many=False)
            return Response.tuple_response(query_intentos, 200)
        except Exception as e:
            return Response.tuple_response("Error al validar el estudiante", 400)
    
    def check_ejercicio(self, id_ejercicio: int, id_estudiante: int) -> tuple:
        """Me todo para validar si un estudiante ya realizo un intento por desarrollar un ejercicio
        y este tiene el estado de en ejecución"""
        try:
            query_check_ejercicio = self.helper.sie_cursor("""
                select count(*) as exist from estudiante_ejercicio where id_estudiante = %s and id_ejercicio = %s and estado = 'En ejecucion'""",
                (id_estudiante, id_ejercicio), many=False)
            return Response.tuple_response(query_check_ejercicio, 200)
        except Exception as e:
            return Response.tuple_response("Error al validar el estudiante", 400)
      
    def prueba_finalizada(self, id_ejercicio: int, id_estudiante: int) -> tuple:
        """Me todo para validar si un estudiante ya finalizo el ejercicio"""
        try:
            query_prueba_finalizada = self.helper.sie_cursor("""select if(count(ee.estado) = pa.num_intentos, TRUE, FALSE) as fin_intentos from estudiante_ejercicio as ee
            left join parametros_avanzados as pa on ee.id_ejercicio = pa.id_ejercicio where  ee.id_ejercicio = %s and ee.id_estudiante = %s 
            and ee.estado != 'En ejecucion' group by pa.num_intentos""",(id_ejercicio, id_estudiante), many=False)
            return Response.tuple_response(query_prueba_finalizada, 200)
        except Exception as e:
            return Response.tuple_response("Error intentos completados", 400)

    def almacenar_estudiante_ejercicio(self, id_ejercicio: int, id_estudiante: int) -> tuple:
        """Me todo para almacenar usuario en estudiante_ejercicio"""
        try:
            query_validar_estudiante_ejercicio = self.helper.sie_cursor(
                """insert into estudiante_ejercicio (id_estudiante, id_ejercicio) values (%s, %s)""",
                (id_estudiante, id_ejercicio), commit=True)
            return Response.tuple_response(query_validar_estudiante_ejercicio, 201)
        except Exception as e:
            return Response.tuple_response("Error al guardar el usuario en Db", 400)
    
    def terminar_prueba(self, id_relación: int) -> tuple:
        """Me todo para terminar una prueba"""
        try:
            query_terminar_prueba = self.helper.sie_cursor("""
                update estudiante_ejercicio set estado = 'Terminada', fecha_presentacion = current_time()
            where id = %s""", (id_relación,), commit=True)
            return Response.tuple_response(query_terminar_prueba, 200)
        except Exception as e:
            return Response.tuple_response("Error al actualizar el estado de la prueba", 400)
        
    def relacion_estudiante_ejercicio(self, id_estudiante: int, id_ejercicio: int) -> tuple:
        """Me todo para obtener el id de la relación entre un estudiante y un ejercicio"""
        try:
            query_relacion_estudiante_ejercicio = self.helper.sie_cursor("""
                select id from estudiante_ejercicio where id_estudiante = %s and id_ejercicio = %s order by id desc limit 1""",
                (id_estudiante, id_ejercicio),)
            return Response.tuple_response(query_relacion_estudiante_ejercicio, 200)
        except Exception as e:
            return Response.tuple_response("Error al obtener el id de la relación", 400)
        
    def calcular_nota_estudiante(self, id_estudiante: int, id_ejercicio: int, id_relacion: int) -> tuple:
        """Me todo para calcular la nota de un ejercicio"""
        try:
            query_calcular_nota = self.helper.sie_cursor("""
                CALL generar_notas_ejercicio(%s, %s, %s)""", (id_estudiante, id_ejercicio, id_relacion), commit=True)
            return Response.tuple_response(query_calcular_nota, 200)
        except Exception as e:
            return Response.tuple_response("Error al calcular la nota", 400)

    def listar_feedback(self, id_relationship: int) -> tuple:
        """Me todo para listar la retroalimentación de un ejercicio"""
        try:
            query_feedback = self.helper.sie_cursor("""SELECT pe.preguntas, pe.texto_completar, pe.id as id_pregunta,
            (SELECT re2.contenido FROM respuestas_ejerc AS re2 WHERE ure.seleccionada = re2.id) AS respuesta_escogida,
            (SELECT GROUP_CONCAT(re3.contenido SEPARATOR ', ') FROM respuestas_ejerc AS re3 WHERE re3.correcta = 1 AND ure.id_pregunta = re3.id_pregunta) AS respuestas_verdaderas,
            ure.nota as puntuacion
        FROM estudiante_ejercicio AS ee
            INNER JOIN usuario_respuesta_ejercicios AS ure ON ee.id_ejercicio = ure.id_ejercicio AND ee.id_estudiante = ure.id_estudiante AND ee.id = ure.id_intento
            INNER JOIN preguntas_ejerc AS pe ON ure.id_pregunta = pe.id AND ure.id_ejercicio = pe.id_ejercicio
        WHERE ee.id = %s AND ee.estado = 'Terminada'""", (id_relationship,), many=True)

            return Response.tuple_response(query_feedback, 200)
        except Exception as e:
            return Response.tuple_response("Error al listar la retroalimentación", 400)
    
    def order_questions_true(self, id_question: int) -> tuple[str, int]:
     """Me todo para ordenar las preguntas correctas en base a la posición inicial"""
     try:
         result_query = self.helper.sie_cursor(
             """SELECT pe.preguntas,
             IF(pe.id_formato IN (7, 8), re.contenido, '0') AS contenido,
             pe.id_formato
             FROM preguntas_ejerc AS pe
             INNER JOIN respuestas_ejerc AS re ON pe.id = re.id_pregunta
             WHERE pe.id = %s
             ORDER BY re.posicion_inicial""",
             (id_question,), many=True
         )
         return Response.tuple_response(result_query, 200)
     except Exception as e:
         return Response.tuple_response("Error al ordenar las preguntas", 400)

    def exist_relationship(self, id_relationship: int) -> tuple:
        """Me todo para validar si existe una relación entre un estudiante y un ejercicio con estado terminada"""
        try:
            query_existe_relacion = self.helper.sie_cursor("""select if(count(*) = 1 and e.estado = 'Terminada', (1), (0)) as exist 
                from estudiante_ejercicio as e where e.id = %s""", (id_relationship,), many=False)
            return Response.tuple_response(query_existe_relacion, 200)
        except Exception as e:
            return Response.tuple_response("Error al validar la relación", 400)
        
    def listar_pregunta(self, id_pregunta: int) -> tuple:
        try:
            query_listar_pregunta = self.helper.sie_cursor(""" select pe.preguntas, pe.texto_completar, re.contenido, re.correcta, re.puntuacion_respt, pe.id_formato, re.posicion_inicial from preguntas_ejerc as pe
                inner join respuestas_ejerc as re on pe.id = re.id_pregunta
                where pe.id = %s""", (id_pregunta,), many=True)

            return Response.tuple_response(query_listar_pregunta, 200)
        except Exception as e:
            return Response.tuple_response("Error al listar la pregunta", 400)
    
    def estado_ejercicio(self, id_usuario: int, id_ejercicio: int) -> tuple:
        """Me todo para obtener el estado de un ejercicio"""
        try:
            query_estado_ejercicio = self.helper.sie_cursor(""" select ee.estado from estudiante_ejercicio as ee
                where ee.id_estudiante = %s and ee.id_ejercicio = %s order by id limit 1
            """, (id_usuario, id_ejercicio), many=False)
            return Response.tuple_response(query_estado_ejercicio, 200)
        except Exception as e:
            return Response.tuple_response("Error al obtener el estado del ejercicio", 400)