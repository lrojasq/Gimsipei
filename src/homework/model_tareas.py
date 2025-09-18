from pydantic import BaseModel, ValidationError, validator
from typing import Optional, Any, List, Union
from datetime import datetime
from werkzeug.datastructures import FileStorage

class TareaModel(BaseModel):
    id_tarea: Optional[str] = None
    asignatura: Optional[str] = None
    curso: Optional[str] = None
    docente: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_finalizacion: Optional[datetime] = None
    ultima_modificacion: Optional[datetime] = None


    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception as exc:
            return None


class DocumentoModel(BaseModel):
    id_documento: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    id_asignatura: Optional[int] = None
    id_docente: Optional[int] = None
    id_curso: Optional[int] = None
    ultima_modificacion: Optional[str] = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception as exc:
            return None

""" Se utiliza cuando un estudiante o docente sube un recurso a la tabla de tarea"""
class UrlRecursosModel(BaseModel):
    direccion_url : Optional[str] = None
    url_nombre: Optional[str] = None
    url_estudiante: Optional[str] = None
    url_docente: Optional[str] = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception as exc:
            return None
        
class TareaRelacionUsuario(BaseModel):
    id_tarea: Optional[int] = None
    id_usuario: Optional[int] = None
    id_url_recurso: Optional[int] = None
    estado : Optional[str] = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception as exc:
            return None
        
""" Se utiliza para asignar una tarea a un estudiante"""
class TareasEstudianteCurso(BaseModel):
    id_respuesta: Optional[int] = None
    nota_tarea: Optional[Union[int, float]] = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception as exc:
            return None
        
class UrlDocumentosRecursos(BaseModel):
    id_docente: Optional[int] = None
    id_asignatura: Optional[int] = None
    id_documento: Optional[int] = None
    direccion_url: Optional[str] = None
    nombre_recurso: Optional[str] = None
    url_recurso: Optional[str] = None
    descripcion: Optional[str] = None
    compartido: Optional[int] = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception as exc:
            return None
        
class DocumentosCursoEstudiante(BaseModel):
    """Este modelo se implemento con el fin de que hiciera referecia a la tabla de
    documentos_curso_estudiantes la cual es para asociar documentos con los estudiantes de un curso"""
    id_recurso: Optional[int] = None
    id_curso: Optional[int] = None
    id_estudiante: Optional[int] = None
    fecha_entrega: Optional[str] = None

    """ Defini este metodo para poder manejar los errores generados sobre el modelo
        y encapsularlos en un bloque try except, si falla me retorna None de lo contrario
        me retorna el modelo validado
    """
    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception as exc:
            return None
        
class TareasComentarios(BaseModel):
    id_respuesta: Optional[int] = None
    id_usuario: Optional[int] = None
    comentario: Optional[str] = None

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception as exc:
            return None
        
class crearAejerciciosModel(BaseModel):
    """Creacion del modelo para crear ejercicios"""
    id_asignatura: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    vista_retro_alimentacion: Optional[int] = None
    seleccion_pregunta: Optional[int] = None
    barajar_pregunta: Optional[int] = None
    num_intentos: Optional[int] = None
    fecha_publicacion: Optional[str] = None
    fecha_finalizacion: Optional[str] = None
    control_tiempo: Optional[str] = None
    porcentaje_exito: Optional[int] = None
    texto_final: Optional[str] = None

    def __init__(self, **data: Any):
        try:
            __tracebackhide__ = True
            self.__pydantic_validator__.validate_python(data, self_instance=self)
        except Exception as exc:
            return None
        
class crearPruebaModel(BaseModel):
    """Creacion del modelo para crear preguntas"""
    pregunta: Optional[str] = None
    id_formato: Optional[int] = None
    id_ejercicio: Optional[int] = None
    seleccionada: Optional[int] = None
    puntuacion: Optional[str] = None
    texto_completar: Optional[str] = None
    contenido: Optional[List[str]] = None
    correcta: Optional[List[Union[int, str, bool]]] = None
    puntuacion_respt: Optional[list[Union[int,float]]] = None
    id_pregunta: Optional[int] = None
    id_respuesta: Optional[list[Union[int, str]]] = None
    respuesta: Optional[str] = None
    recursos: Optional[list] = None
    init_position: Optional[List[int]] = [0]*4

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
                if correct == 1:
                    return True
                elif correct in [1, 2, 3, 4]:
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

    def validar_cantidad_imagenes(self, img: List[FileStorage] | None) -> bool | list[str]:
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