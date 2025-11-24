from datetime import datetime
from werkzeug.utils import secure_filename
import os

from src.models.resource import Resource
from src.database.database import SessionLocal
from src.models.subject import Subject
from src.models.user import User, UserRole
from src.models.class_model import ClassModel
from src.models.course import Course
from src.models.class_view import ClassView
from src.models.course_student import CourseStudent
from src.classes.validation import (
    SubjectCreate,
    SubjectUpdate,
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
    except Exception:
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

    except Exception:
        db.rollback()
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

    except Exception:
        db.rollback()
        return {"error": "Error al crear el recurso"}, 500
    finally:
        db.close()


def get_classes_by_subject_service(course_id: int, subject_id: int):
    """
    Obtiene las clases de una materia específica organizadas por periodo

    Args:
        course_id: ID del curso
        subject_id: ID de la materia

    Returns:
        Tuple con (datos, status_code)
    """
    db = SessionLocal()
    try:
        # Obtener información del curso
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return {"error": "Curso no encontrado"}, 404

        # Obtener información de la materia
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            return {"error": "Materia no encontrada"}, 404

        # Obtener el profesor asignado a esta materia en este curso
        course_subject = (
            db.query(CourseSubject)
            .filter(
                CourseSubject.course_id == course_id,
                CourseSubject.subject_id == subject_id,
            )
            .first()
        )

        teacher = None
        if course_subject and course_subject.teacher_id:
            teacher = (
                db.query(User).filter(User.id == course_subject.teacher_id).first()
            )

        # Obtener todas las clases de esta materia en este curso
        classes = (
            db.query(ClassModel)
            .filter(
                ClassModel.course_id == course_id, ClassModel.subject_id == subject_id
            )
            .order_by(ClassModel.period, ClassModel.class_number)
            .all()
        )

        # Organizar clases por periodo
        classes_by_period = {1: [], 2: [], 3: [], 4: []}
        for class_item in classes:
            if class_item.period in classes_by_period:
                classes_by_period[class_item.period].append(
                    {
                        "id": class_item.id,
                        "class_number": class_item.class_number,
                        "title": class_item.title,
                        "description": class_item.description,
                        "cover_image": class_item.cover_image,
                        "period": class_item.period,
                        "created_at": class_item.created_at.strftime("%Y-%m-%d")
                        if class_item.created_at
                        else None,
                    }
                )

        result = {
            "course": {
                "id": course.id,
                "academic_year": course.academic_year,
            },
            "subject": {"id": subject.id, "name": subject.name},
            "teacher": {
                "id": teacher.id,
                "full_name": teacher.full_name,
                "document": teacher.document,
            }
            if teacher
            else None,
            "classes_by_period": classes_by_period,
        }

        return result, 200

    except Exception:
        return {"error": "Error al obtener las clases"}, 500
    finally:
        db.close()


def update_class_service(class_id: int, data: dict, cover_file=None):
    """
    Actualiza una clase existente

    Args:
        class_id: ID de la clase a actualizar
        data: Diccionario con los datos actualizados
        cover_file: Archivo de imagen de portada (opcional)

    Returns:
        Tuple con (resultado, status_code)
    """
    db = SessionLocal()
    try:
        # Buscar la clase
        class_to_update = db.query(ClassModel).filter(ClassModel.id == class_id).first()
        if not class_to_update:
            return {"error": "Clase no encontrada"}, 404

        # Actualizar campos básicos
        if "class_number" in data:
            # Verificar que no exista otra clase con el mismo número
            existing = (
                db.query(ClassModel)
                .filter(
                    ClassModel.course_id == class_to_update.course_id,
                    ClassModel.subject_id == class_to_update.subject_id,
                    ClassModel.class_number == data["class_number"],
                    ClassModel.period == data.get("period", class_to_update.period),
                    ClassModel.id != class_id,
                )
                .first()
            )
            if existing:
                return {
                    "error": "Ya existe una clase con ese número en esta materia y periodo"
                }, 400

            class_to_update.class_number = data["class_number"]

        if "title" in data:
            class_to_update.title = data["title"]

        if "description" in data:
            class_to_update.description = data["description"]

        if "period" in data:
            class_to_update.period = data["period"]

        # Procesar nueva portada si existe
        if cover_file and cover_file.filename:
            # Eliminar la portada anterior si existe
            if class_to_update.cover_image:
                old_image_path = os.path.join(
                    "src", class_to_update.cover_image.lstrip("/")
                )
                if os.path.exists(old_image_path):
                    try:
                        os.remove(old_image_path)
                    except Exception:
                        pass

            # Guardar nueva portada
            filename = secure_filename(cover_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            upload_folder = os.path.join("src", "static", "uploads", "classes")
            os.makedirs(upload_folder, exist_ok=True)

            file_path = os.path.join(upload_folder, filename)
            cover_file.save(file_path)
            class_to_update.cover_image = f"/static/uploads/classes/{filename}"

        db.commit()
        db.refresh(class_to_update)

        return {
            "message": "Clase actualizada exitosamente",
            "class": {
                "id": class_to_update.id,
                "title": class_to_update.title,
                "class_number": class_to_update.class_number,
            },
        }, 200

    except Exception:
        db.rollback()
        return {"error": "Error al actualizar la clase"}, 500
    finally:
        db.close()


def delete_class_service(class_id: int, user_role: str):
    """
    Elimina una clase y su imagen de portada

    Args:
        class_id: ID de la clase a eliminar
        user_role: Rol del usuario

    Returns:
        Tuple con (resultado, status_code)
    """
    db = SessionLocal()
    try:
        # Search the class
        class_to_delete = db.query(ClassModel).filter(ClassModel.id == class_id).first()
        if not class_to_delete:
            return {"error": "Clase no encontrada"}, 404

        # Verify permissions
        if user_role:
            if user_role.lower() != UserRole.TEACHER.value:
                return {"error": "No tienes permisos para eliminar esta clase"}, 403

        # Save the image path before deleting the record
        cover_image_path = class_to_delete.cover_image

        # Delete related records first (to avoid integrity reference problems)
        resources = db.query(Resource).filter(Resource.class_id == class_id).all()
        for resource in resources:
            # Delete physical files of the resource if they exist
            if resource.cover_image:
                resource_cover_path = os.path.join(
                    "src", resource.cover_image.lstrip("/")
                )
                if os.path.exists(resource_cover_path):
                    try:
                        os.remove(resource_cover_path)
                    except Exception:
                        pass

            if resource.file_url:
                resource_file_path = os.path.join("src", resource.file_url.lstrip("/"))
                if os.path.exists(resource_file_path):
                    try:
                        os.remove(resource_file_path)
                    except Exception:
                        pass

            db.delete(resource)

        # Delete associated views
        views = db.query(ClassView).filter(ClassView.class_id == class_id).all()
        for view in views:
            db.delete(view)

        # Delete the class from the database
        db.delete(class_to_delete)
        db.commit()

        # Delete physical files after deleting the record
        files_deleted = []

        # Delete the cover image if it exists
        if cover_image_path:
            # Construir la ruta completa del archivo
            # cover_image_path comes as "/static/uploads/classes/filename.jpg"
            full_path = os.path.join("src", cover_image_path.lstrip("/"))

            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    files_deleted.append("portada")
                except Exception:
                    pass

        return {
            "message": "Clase eliminada exitosamente",
            "files_deleted": files_deleted,
        }, 200

    except Exception as e:
        db.rollback()
        return {"error": f"Error al eliminar la clase: {str(e)}"}, 500
    finally:
        db.close()


def get_class_by_id_service(class_id: int):
    """
    Obtiene los datos de una clase específica

    Args:
        class_id: ID de la clase

    Returns:
        Tuple con (datos, status_code)
    """
    db = SessionLocal()
    try:
        class_item = db.query(ClassModel).filter(ClassModel.id == class_id).first()
        if not class_item:
            return {"error": "Clase no encontrada"}, 404

        result = {
            "id": class_item.id,
            "course_id": class_item.course_id,
            "subject_id": class_item.subject_id,
            "class_number": class_item.class_number,
            "title": class_item.title,
            "description": class_item.description,
            "period": class_item.period,
            "cover_image": class_item.cover_image,
            "created_by": class_item.created_by,
        }

        return result, 200

    except Exception:
        return {"error": "Error al obtener la clase"}, 500
    finally:
        db.close()


# Student Services
def get_student_course_subjects_service(student_id: int):
    """
    Obtiene el curso y las materias del estudiante

    Args:
        student_id: ID del estudiante

    Returns:
        Tuple con (datos, status_code)
    """
    db = SessionLocal()
    try:
        # Get the student's enrollment
        enrollment = (
            db.query(CourseStudent)
            .filter(CourseStudent.student_id == student_id)
            .first()
        )

        if not enrollment:
            return {"error": "Estudiante no inscrito en ningún curso"}, 404

        # Get the course
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        if not course:
            return {"error": "Curso no encontrado"}, 404

        # Get the course subjects with their teachers
        course_subjects = (
            db.query(CourseSubject)
            .filter(
                CourseSubject.course_id == course.id, CourseSubject.is_active.is_(True)
            )
            .all()
        )

        subjects_data = []
        for cs in course_subjects:
            subject = db.query(Subject).filter(Subject.id == cs.subject_id).first()
            teacher = db.query(User).filter(User.id == cs.teacher_id).first()

            if subject:
                subjects_data.append(
                    {
                        "subject": subject,
                        "teacher": teacher,
                        "course_subject_id": cs.id,
                    }
                )

        return {
            "course": course,
            "subjects": subjects_data,
        }, 200

    except Exception as e:
        return {"error": f"Error al obtener las materias: {str(e)}"}, 500
    finally:
        db.close()


def get_student_subject_classes_service(
    student_id: int, course_id: int, subject_id: int
):
    """
    Obtiene las clases de una materia y el progreso del estudiante

    Args:
        student_id: ID del estudiante
        course_id: ID del curso
        subject_id: ID de la materia

    Returns:
        Tuple con (datos, status_code)
    """
    db = SessionLocal()
    try:
        # Verify that the student is enrolled in the course
        enrollment = (
            db.query(CourseStudent)
            .filter(
                CourseStudent.student_id == student_id,
                CourseStudent.course_id == course_id,
            )
            .first()
        )

        if not enrollment:
            return {"error": "No tienes acceso a este curso"}, 403

        # Get the course and subject
        course = db.query(Course).filter(Course.id == course_id).first()
        subject = db.query(Subject).filter(Subject.id == subject_id).first()

        if not course or not subject:
            return {"error": "Curso o materia no encontrada"}, 404

        # Get all the classes of the subject
        classes = (
            db.query(ClassModel)
            .filter(
                ClassModel.course_id == course_id, ClassModel.subject_id == subject_id
            )
            .order_by(ClassModel.period, ClassModel.class_number)
            .all()
        )

        # Organize classes by period
        classes_by_period = {1: [], 2: [], 3: [], 4: []}
        for class_item in classes:
            period = class_item.period or 1
            classes_by_period[period].append(class_item)

        # Get the classes viewed by the student
        viewed_classes_query = (
            db.query(ClassView.class_id)
            .filter(ClassView.student_id == student_id)
            .all()
        )
        viewed_class_ids = set([view.class_id for view in viewed_classes_query])

        # Calculate statistics
        total_classes = len(classes)
        viewed_classes = len(viewed_class_ids)
        viewed_percentage = (
            int((viewed_classes / total_classes) * 100) if total_classes > 0 else 0
        )

        return {
            "course": course,
            "subject": subject,
            "classes_by_period": classes_by_period,
            "viewed_class_ids": viewed_class_ids,
            "viewed_classes": viewed_classes,
            "total_classes": total_classes,
            "viewed_percentage": viewed_percentage,
        }, 200

    except Exception as e:
        return {"error": f"Error al obtener las clases: {str(e)}"}, 500
    finally:
        db.close()


def mark_class_as_viewed_service(
    user_id: int, class_id: int, course_id: int, subject_id: int, viewed: bool
):
    """
    Marca una clase como vista o no vista para un estudiante

    Args:
        user_id: ID del usuario (estudiante)
        class_id: ID de la clase
        course_id: ID del curso
        subject_id: ID de la materia
        viewed: True para marcar como vista, False para desmarcar

    Returns:
        Tuple con diccionario de resultado y código de estado
    """
    db = SessionLocal()
    try:
        # Verificar que el usuario está inscrito en el curso
        student_enrollment = (
            db.query(CourseStudent)
            .filter(
                CourseStudent.student_id == user_id,
                CourseStudent.course_id == course_id,
            )
            .first()
        )

        if not student_enrollment:
            return {
                "success": False,
                "error": "Estudiante no encontrado en el curso",
            }, 404

        student_id = user_id

        # Verificar que la clase existe
        class_exists = (
            db.query(ClassModel)
            .filter(
                ClassModel.id == class_id,
                ClassModel.course_id == course_id,
                ClassModel.subject_id == subject_id,
            )
            .first()
        )

        if not class_exists:
            return {"success": False, "error": "Clase no encontrada"}, 404

        if viewed:
            # Marcar como vista (crear registro si no existe)
            existing_view = (
                db.query(ClassView)
                .filter(
                    ClassView.student_id == student_id, ClassView.class_id == class_id
                )
                .first()
            )

            if not existing_view:
                new_view = ClassView(student_id=student_id, class_id=class_id)
                db.add(new_view)
                db.commit()
        else:
            # Desmarcar como vista (eliminar registro si existe)
            existing_view = (
                db.query(ClassView)
                .filter(
                    ClassView.student_id == student_id, ClassView.class_id == class_id
                )
                .first()
            )

            if existing_view:
                db.delete(existing_view)
                db.commit()

        return {"success": True, "viewed": viewed}, 200

    except Exception as e:
        db.rollback()
        return {"success": False, "error": f"Error al actualizar estado: {str(e)}"}, 500
    finally:
        db.close()


def get_student_progress_service(user_id: int, course_id: int, subject_id: int):
    """
    Obtiene el progreso de un estudiante en una materia específica

    Args:
        user_id: ID del usuario (estudiante)
        course_id: ID del curso
        subject_id: ID de la materia

    Returns:
        Tuple con diccionario de resultado y código de estado
    """
    db = SessionLocal()
    try:
        # Verificar que el usuario está inscrito en el curso
        student_enrollment = (
            db.query(CourseStudent)
            .filter(
                CourseStudent.student_id == user_id,
                CourseStudent.course_id == course_id,
            )
            .first()
        )

        if not student_enrollment:
            return {
                "success": False,
                "error": "Estudiante no encontrado en el curso",
            }, 404

        student_id = user_id

        # Obtener total de clases de la materia
        total_classes = (
            db.query(ClassModel)
            .filter(
                ClassModel.course_id == course_id, ClassModel.subject_id == subject_id
            )
            .count()
        )

        # Obtener clases vistas
        viewed_classes_query = (
            db.query(ClassView.class_id)
            .join(ClassModel, ClassModel.id == ClassView.class_id)
            .filter(
                ClassView.student_id == student_id,
                ClassModel.course_id == course_id,
                ClassModel.subject_id == subject_id,
            )
            .all()
        )

        viewed_count = len(viewed_classes_query)
        percentage = (
            int((viewed_count / total_classes) * 100) if total_classes > 0 else 0
        )

        return {
            "success": True,
            "total": total_classes,
            "viewed": viewed_count,
            "percentage": percentage,
        }, 200

    except Exception as e:
        return {"success": False, "error": f"Error al obtener progreso: {str(e)}"}, 500
    finally:
        db.close()
