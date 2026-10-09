from datetime import datetime
from typing import Any

from pydantic import BaseModel, ValidationError
from werkzeug.datastructures import FileStorage


class TareaModel(BaseModel):
    id_tarea: str | None = None
    asignatura: str | None = None
    curso: str | None = None
    docente: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    fecha_finalizacion: datetime | None = None
    ultima_modificacion: datetime | None = None


    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception:
            return None


class DocumentoModel(BaseModel):
    id_documento: int | None = None
    nombre: str | None = None
    descripcion: str | None = None
    id_asignatura: int | None = None
    id_docente: int | None = None
    id_curso: int | None = None
    ultima_modificacion: str | None = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception:
            return None

""" Se utiliza cuando un estudiante o docente sube un recurso a la tabla de tarea"""
class UrlRecursosModel(BaseModel):
    direccion_url : str | None = None
    url_nombre: str | None = None
    url_estudiante: str | None = None
    url_docente: str | None = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception:
            return None

class TareaRelacionUsuario(BaseModel):
    id_tarea: int | None = None
    id_usuario: int | None = None
    id_url_recurso: int | None = None
    estado : str | None = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception:
            return None

""" Se utiliza para asignar una tarea a un estudiante"""
class TareasEstudianteCurso(BaseModel):
    id_respuesta: int | None = None
    nota_tarea: int | float | None = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception:
            return None

class UrlDocumentosRecursos(BaseModel):
    id_docente: int | None = None
    id_asignatura: int | None = None
    id_documento: int | None = None
    direccion_url: str | None = None
    nombre_recurso: str | None = None
    url_recurso: str | None = None
    descripcion: str | None = None
    compartido: int | None = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception:
            return None

class DocumentosCursoEstudiante(BaseModel):
    """Este modelo se implemento con el fin de que hiciera referecia a la tabla de
    documentos_curso_estudiantes la cual es para asociar documentos con los estudiantes de un curso"""
    id_recurso: int | None = None
    id_curso: int | None = None
    id_estudiante: int | None = None
    fecha_entrega: str | None = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """
    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception:
            return None

class TareasComentarios(BaseModel):
    id_respuesta: int | None = None
    id_usuario: int | None = None
    comentario: str | None = None

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception:
            return None

class crearAejerciciosModel(BaseModel):
    """Creacion del modelo para crear ejercicios"""
    id_asignatura: int | None = None
    nombre: str | None = None
    descripcion: str | None = None
    vista_retro_alimentacion: int | None = None
    seleccion_pregunta: int | None = None
    barajar_pregunta: int | None = None
    num_intentos: int | None = None
    fecha_publicacion: str | None = None
    fecha_finalizacion: str | None = None
    control_tiempo: str | None = None
    porcentaje_exito: int | None = None
    texto_final: str | None = None

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception:
            return None

class crearPruebaModel(BaseModel):
    """Creacion del modelo para crear preguntas"""
    pregunta: str | None = None
    id_formato: int | None = None
    id_ejercicio: int | None = None
    seleccionada: int | None = None
    puntuacion: str | None = None
    texto_completar: str | None = None
    contenido: list[str] | None = None
    correcta: list[int | str | bool] | None = None
    puntuacion_respt: list[int | float] | None = None
    id_pregunta: int | None = None
    id_respuesta: list[int | str] | None = None
    respuesta: str | None = None
    recursos: list | None = None
    init_position: list[int] | None = [0]*4

    """ Defini este metodo para poder manejar los errores generados sobre el modelo"""
    def __init__(self, **data: Any):
        """Callback para validar el modelo"""
        try:
            super().__init__(**data)
        except ValidationError as e:
            #error_message = {'errors': str(e)}
            raise ValueError({'errors': str(e)})

    def is_valid(self) -> bool:
        """Check if the models have one or more questions"""
        if self.id_formato in [1,2] and type(self.id_respuesta) == list:
            return len(self.id_respuesta) >=1
        return True

    def is_correct(self) -> bool:
        """Check if in list of correct answers is the correct answer (The correct have the value 1)"""
        if self.id_formato in [1,2,4,5,6,7,8]:
            for correct in self.correcta:
                if correct == 1 or correct in [1, 2, 3, 4]:
                    return True
            return False
        else:
            return len(self.correcta) == 0 and type(self.correcta) == list

    def validate_question_score(self) -> bool | None:
        """Check if the score of the question is valid"""
        if self.id_formato in [1,2,4,5,6,7,8]:
            for number in self.puntuacion_respt:
                if number is None and self.correcta is None or not (0 <= number <= 100) or len(self.correcta) not in [1,2,3,4]:
                    return False
                return True
        else:
            return len(self.puntuacion_respt) == 0 and type(self.puntuacion_respt) == list

    # def length_response(self) -> bool:
    #     """Check if the length of the response not empty"""
    #     if self.id_respuesta is None or len(self.id_respuesta) == 0:
    #         return False
    #     return True

    def transform_questions(self) -> None|bool:
        """Check format of answer"""
        if self.id_formato in [3]:
            for value in self.id_respuesta:
                if type(value) != int and value != 0:
                    return False
                return True

            if len(self.id_respuesta) == 0:
                return True

    def validate_length_content(self) -> bool:
        """Check if the length of the content and question is valid"""
        if self.pregunta is None or not (1 <= len(self.pregunta) <= 4294967295):
                return False
        if self.contenido is None:
            return False
        for value in self.contenido:
            if not (1 <= len(value) <= 4294967295):
                return False
        return True

    def validate_length_response(self) -> bool:
        """Check if the length of the array response is not empty"""
        if self.id_formato in [4] and len(self.id_respuesta) == 0 and self.respuesta is None:
            return False
        return True

    def validar_cantidad_imagenes(self, img: list[FileStorage] | None) -> bool | list[str]:
        """Validar que se suban al menos 4 imágenes y agregar un identificador único a cada una"""
        if self.id_formato in [6]:
            if img is None or len(img) < 4:
                return False
            # Agregar un identificador único a cada imagen
            for i, imagen in enumerate(img):
                if not isinstance(imagen, FileStorage):
                    return False
                nombre, extension = imagen.filename.rsplit('.', 1)
                imagen.filename = f"{nombre}_id_{i+1}.{extension}"
            return img
        return True
