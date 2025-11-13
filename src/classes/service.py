from datetime import datetime
from werkzeug.utils import secure_filename
import os

from src.models.resource import Resource
from src.database.database import SessionLocal
from src.models.subject import Subject
from src.models.period import Period
from src.models.user import User, UserRole
from src.models.class_model import ClassModel
from src.models.course import Course
from src.classes.validation import (
    SubjectCreate,
    SubjectUpdate,
    PeriodCreate,
    PeriodUpdate,
    # ClassCreate,
    # ClassUpdate,
    # ResourceCreate,
    # ResourceUpdate,
    # AssignmentCreate,
    # AssignmentUpdate,
    # ClassViewCreate
)
from src.courses.service import (
    COURSE_NAME_ORDER,
    get_grade_number_from_course_name,
)
from src.models.course_subject import CourseSubject


# Subject Services
def create_subject(subject: SubjectCreate):
    db = SessionLocal()
    try:
        db_subject = Subject(**subject.dict())
        db.add(db_subject)
        db.commit()
        db.refresh(db_subject)
        return db_subject
    finally:
        db.close()


def get_subject(subject_id: int):
    db = SessionLocal()
    try:
        return db.query(Subject).get(subject_id)
    finally:
        db.close()


def get_subjects():
    db = SessionLocal()
    try:
        return db.query(Subject).all()
    finally:
        db.close()


def update_subject(subject_id: int, subject: SubjectUpdate):
    db = SessionLocal()
    try:
        db_subject = db.query(Subject).get(subject_id)
        if not db_subject:
            return None

        for key, value in subject.dict(exclude_unset=True).items():
            setattr(db_subject, key, value)

        db.commit()
        db.refresh(db_subject)
        return db_subject
    finally:
        db.close()


def delete_subject(subject_id: int, current_user_id: int):
    db = SessionLocal()
    try:
        current_user = db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            raise PermissionError("Usuario no encontrado")

        db_subject = db.query(Subject).get(subject_id)
        if not db_subject:
            return None

        # If user is a teacher, they can only delete subjects they are assigned to
        if current_user.role.name == UserRole.TEACHER.name:
            from src.models.course_subject import CourseSubject

            assignment = (
                db.query(CourseSubject)
                .filter(
                    CourseSubject.subject_id == subject_id,
                    CourseSubject.teacher_id == current_user.id,
                )
                .first()
            )
            if not assignment:
                raise PermissionError("No autorizado para eliminar esta materia")

        db.delete(db_subject)
        db.commit()
        return True
    finally:
        db.close()


# Period Services
def create_period(period: PeriodCreate, current_user_id: int):
    db = SessionLocal()
    try:
        # Verificar permisos
        current_user = db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            raise PermissionError("Usuario no encontrado")

        db_period = Period(**period.dict())
        db.add(db_period)
        db.commit()
        db.refresh(db_period)
        return db_period
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_period(period_id: int):
    db = SessionLocal()
    try:
        return db.query(Period).filter(Period.id == period_id).first()
    finally:
        db.close()


def get_periods():
    db = SessionLocal()
    try:
        return db.query(Period).all()
    finally:
        db.close()


def update_period(period_id: int, period: PeriodUpdate, current_user_id: int):
    db = SessionLocal()
    try:
        # Verificar permisos
        current_user = db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            raise PermissionError("Usuario no encontrado")

        if current_user.role.name not in [UserRole.TEACHER.name, UserRole.ADMIN.name]:
            raise PermissionError("No autorizado para actualizar periodos")

        db_period = db.query(Period).filter(Period.id == period_id).first()
        if not db_period:
            return None

        # Si es profesor, solo puede actualizar periodos de materias asignadas a él
        if current_user.role.name == UserRole.TEACHER.name:
            from src.models.course_subject import CourseSubject

            # Verificar si el profesor está asignado a esta materia en algún curso
            assignment = (
                db.query(CourseSubject)
                .filter(
                    CourseSubject.subject_id == db_period.subject_id,
                    CourseSubject.teacher_id == current_user.id,
                )
                .first()
            )
            if not assignment:
                raise PermissionError("No autorizado para actualizar este periodo")

        update_data = period.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_period, key, value)

        db.add(db_period)
        db.commit()
        db.refresh(db_period)
        return db_period
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def delete_period(period_id: int, current_user_id: int):
    db = SessionLocal()
    try:
        # Verificar permisos
        current_user = db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            raise PermissionError("Usuario no encontrado")

        if current_user.role.name not in [UserRole.TEACHER.name, UserRole.ADMIN.name]:
            raise PermissionError("No autorizado para eliminar periodos")

        db_period = db.query(Period).filter(Period.id == period_id).first()
        if not db_period:
            return None

        # Si es profesor, solo puede eliminar periodos de materias asignadas a él
        if current_user.role.name == UserRole.TEACHER.name:
            from src.models.course_subject import CourseSubject

            # Verificar si el profesor está asignado a esta materia en algún curso
            assignment = (
                db.query(CourseSubject)
                .filter(
                    CourseSubject.subject_id == db_period.subject_id,
                    CourseSubject.teacher_id == current_user.id,
                )
                .first()
            )
            if not assignment:
                raise PermissionError("No autorizado para eliminar este periodo")

        db.delete(db_period)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# # Class Services
# def create_class(class_: ClassCreate):
#     db = SessionLocal()
#     try:
#         db_class = ClassModel(**class_.dict())
#         db.add(db_class)
#         db.commit()
#         db.refresh(db_class)
#         return db_class
#     finally:
#         db.close()

# def get_class(class_id: int):
#     db = SessionLocal()
#     try:
#         return db.query(ClassModel).filter(ClassModel.id == class_id).first()
#     finally:
#         db.close()

# def get_classes():
#     db = SessionLocal()
#     try:
#         return db.query(ClassModel).all()
#     finally:
#         db.close()

# def update_class(class_id: int, class_: ClassUpdate):
#     db = SessionLocal()
#     try:
#         db_class = db.query(ClassModel).filter(ClassModel.id == class_id).first()
#         if not db_class:
#             return None

#         for key, value in class_.dict(exclude_unset=True).items():
#             setattr(db_class, key, value)

#         db.commit()
#         db.refresh(db_class)
#         return db_class
#     finally:
#         db.close()

# def delete_class(class_id: int):
#     db = SessionLocal()
#     try:
#         db_class = db.query(ClassModel).filter(ClassModel.id == class_id).first()
#         if not db_class:
#             return None

#         db.delete(db_class)
#         db.commit()
#         return True
#     finally:
#         db.close()

# # Resource Services
# def create_resource(db: Session, resource: ResourceCreate):
#     db_resource = Resource(**resource.dict())
#     db.add(db_resource)
#     db.commit()
#     db.refresh(db_resource)
#     return db_resource

# def get_resource(db: Session, resource_id: int):
#     return db.query(Resource).filter(Resource.id == resource_id).first()

# def get_resources(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(Resource).offset(skip).limit(limit).all()

# def update_resource(db: Session, resource_id: int, resource: ResourceUpdate):
#     db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
#     if db_resource:
#         for key, value in resource.dict(exclude_unset=True).items():
#             setattr(db_resource, key, value)
#         db_resource.updated_at = datetime.utcnow() # Update timestamp
#         db.add(db_resource)
#         db.commit()
#         db.refresh(db_resource)
#     return db_resource

# def delete_resource(db: Session, resource_id: int):
#     db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
#     if db_resource:
#         db.delete(db_resource)
#         db.commit()
#     return db_resource

# # Assignment Services
# def create_assignment(db: Session, assignment: AssignmentCreate):
#     db_assignment = Assignment(**assignment.dict())
#     db.add(db_assignment)
#     db.commit()
#     db.refresh(db_assignment)
#     return db_assignment

# def get_assignment(db: Session, assignment_id: int):
#     return db.query(Assignment).filter(Assignment.id == assignment_id).first()

# def get_assignments(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(Assignment).offset(skip).limit(limit).all()

# def update_assignment(db: Session, assignment_id: int, assignment: AssignmentUpdate):
#     db_assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
#     if db_assignment:
#         for key, value in assignment.dict(exclude_unset=True).items():
#             setattr(db_assignment, key, value)
#         db_assignment.updated_at = datetime.utcnow() # Update timestamp
#         db.add(db_assignment)
#         db.commit()
#         db.refresh(db_assignment)
#     return db_assignment

# def delete_assignment(db: Session, assignment_id: int):
#     db_assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
#     if db_assignment:
#         db.delete(db_assignment)
#         db.commit()
#     return db_assignment

# # ClassView Services
# def create_class_view(db: Session, class_view: ClassViewCreate):
#     db_class_view = ClassView(**class_view.dict(), viewed_at=datetime.utcnow())
#     db.add(db_class_view)
#     db.commit()
#     db.refresh(db_class_view)
#     return db_class_view

# def get_class_view(db: Session, class_view_id: int):
#     return db.query(ClassView).filter(ClassView.id == class_view_id).first()

# def get_class_views(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(ClassView).offset(skip).limit(limit).all()

# def delete_class_view(db: Session, class_view_id: int):
#     db_class_view = db.query(ClassView).filter(ClassView.id == class_view_id).first()
#     if db_class_view:
#         db.delete(db_class_view)
#         db.commit()
#     return db_class_view


# Teacher Classes View Service
def get_all_courses_with_subjects():
    """
    Obtener todos los cursos con sus materias asignadas.

    Returns:
        Tuple con lista de cursos y status code
    """
    db = SessionLocal()
    try:
        # Obtener todos los cursos
        courses = db.query(Course).all()

        courses_data = []

        for course in courses:
            # Obtener las materias asignadas al curso
            course_subjects = (
                db.query(CourseSubject, Subject)
                .join(Subject, CourseSubject.subject_id == Subject.id)
                .filter(CourseSubject.course_id == course.id)
                .order_by(Subject.name)
                .all()
            )

            subjects_list = []
            for course_subject, subject in course_subjects:
                subjects_list.append(
                    {
                        "id": subject.id,
                        "name": subject.name,
                        "teacher_id": course_subject.teacher_id,
                    }
                )

            grade_number = get_grade_number_from_course_name(course.name)

            courses_data.append(
                {
                    "id": course.id,
                    "name": course.name,
                    "academic_year": course.academic_year,
                    "grade_number": grade_number if grade_number else course.id,
                    "subjects": subjects_list,
                }
            )

        # Ordenar por grado
        courses_data.sort(key=lambda c: COURSE_NAME_ORDER.get(c["name"], 999))

        return courses_data, 200
    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en get_all_courses_with_subjects: {str(e)}\n{error_trace}")
        return [], 500
    finally:
        db.close()


def create_class_service(data: dict, cover_file=None, created_by_user_id=None):
    """
    Crea una nueva clase

    Args:
        data: Diccionario con los datos de la clase
        cover_file: Archivo de imagen de portada (opcional)
        created_by_user_id: ID del usuario que crea la clase (requerido)

    Returns:
        Tuple con (clase_creada, status_code)
    """
    db = SessionLocal()
    try:
        # Validar datos requeridos
        required_fields = ["course_id", "subject_id", "class_number", "title", "period"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {"error": f"El campo {field} es requerido"}, 400

        if not created_by_user_id:
            return {"error": "El ID del usuario creador es requerido"}, 400

        # Verificar que no exista una clase con el mismo número en el mismo curso, materia y periodo
        existing_class = (
            db.query(ClassModel)
            .filter(
                ClassModel.course_id == data["course_id"],
                ClassModel.subject_id == data["subject_id"],
                ClassModel.class_number == data["class_number"],
                ClassModel.period == data["period"],
            )
            .first()
        )

        if existing_class:
            return {
                "error": "Ya existe una clase con ese número en esta materia y periodo"
            }, 400

        # Procesar archivo de portada si existe
        cover_image_path = None
        if cover_file and cover_file.filename:
            filename = secure_filename(cover_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            # Crear directorio si no existe
            upload_folder = os.path.join("src", "static", "uploads", "classes")
            os.makedirs(upload_folder, exist_ok=True)

            # Guardar archivo
            file_path = os.path.join(upload_folder, filename)
            cover_file.save(file_path)
            cover_image_path = f"/static/uploads/classes/{filename}"

        # Crear la clase
        new_class = ClassModel(
            course_id=data["course_id"],
            subject_id=data["subject_id"],
            class_number=data["class_number"],
            title=data["title"],
            description=data.get("description", ""),
            period=data["period"],
            cover_image=cover_image_path,
            created_by=created_by_user_id,
        )

        db.add(new_class)
        db.commit()
        db.refresh(new_class)

        return {
            "message": "Clase creada exitosamente",
            "class": {
                "id": new_class.id,
                "title": new_class.title,
                "class_number": new_class.class_number,
            },
        }, 201

    except Exception as e:
        db.rollback()
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en create_class_service: {str(e)}\n{error_trace}")
        return {"error": "Error al crear la clase"}, 500
    finally:
        db.close()


def create_resource_service(data: dict, resource_file=None):
    """
    Crea un nuevo recurso para una clase

    Args:
        data: Diccionario con los datos del recurso
        resource_file: Archivo del recurso (opcional)

    Returns:
        Tuple con (recurso_creado, status_code)
    """
    db = SessionLocal()
    try:
        # Validar datos requeridos
        required_fields = ["class_id", "title"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {"error": f"El campo {field} es requerido"}, 400

        # Verificar que la clase existe
        class_exists = (
            db.query(ClassModel).filter(ClassModel.id == data["class_id"]).first()
        )
        if not class_exists:
            return {"error": "La clase especificada no existe"}, 404

        # Procesar archivo del recurso si existe
        file_path_str = None
        file_type = None

        if resource_file and resource_file.filename:
            filename = secure_filename(resource_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            # Determinar tipo de archivo
            extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
            file_types_map = {
                "pdf": "document",
                "doc": "document",
                "docx": "document",
                "ppt": "document",
                "pptx": "document",
                "jpg": "image",
                "jpeg": "image",
                "png": "image",
                "gif": "image",
                "mp4": "video",
                "avi": "video",
                "mov": "video",
                "mp3": "audio",
                "wav": "audio",
            }
            file_type = file_types_map.get(extension, "other")

            # Crear directorio si no existe
            upload_folder = os.path.join("src", "static", "uploads", "resources")
            os.makedirs(upload_folder, exist_ok=True)

            # Guardar archivo
            file_path = os.path.join(upload_folder, filename)
            resource_file.save(file_path)
            file_path_str = f"/static/uploads/resources/{filename}"

        # Crear el recurso
        new_resource = Resource(
            class_id=data["class_id"],
            title=data["title"],
            description=data.get("description", ""),
            file_path=file_path_str,
            file_type=file_type or "link",
            url=data.get("url"),
        )

        db.add(new_resource)
        db.commit()
        db.refresh(new_resource)

        return {
            "message": "Recurso creado exitosamente",
            "resource": {
                "id": new_resource.id,
                "title": new_resource.title,
                "file_type": new_resource.file_type,
            },
        }, 201

    except Exception as e:
        db.rollback()
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en create_resource_service: {str(e)}\n{error_trace}")
        return {"error": "Error al crear el recurso"}, 500
    finally:
        db.close()
