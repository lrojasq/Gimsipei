from typing import List, Optional, Tuple
from datetime import datetime
import os

from flask import Request

# from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename

from src.database.database import SessionLocal
from src.models.resource import Resource, ResourceType
from src.models.class_model import ClassModel
from src.models.subject import Subject
from src.models.course_subject import CourseSubject

# from .validation import (
#     ResourceCreateSchema,
#     ResourceResponseSchema,
#     ResourceUpdateSchema,
# )


def get_resources_by_class_service(class_id: int) -> Tuple[List[dict], int]:
    """Obtener recursos de una clase específica"""
    db = SessionLocal()
    try:
        resources = (
            db.query(Resource)
            .filter(Resource.class_id == class_id)
            .order_by(Resource.created_at.desc())
            .all()
        )

        resources_list = []
        for resource in resources:
            resources_list.append(
                {
                    "id": resource.id,
                    "title": resource.title,
                    "cover_image": resource.cover_image,
                    "period": resource.period,
                    "file_url": resource.file_url,
                    "resource_type": resource.resource_type.value,
                    "created_at": resource.created_at.isoformat(),
                }
            )

        return resources_list, 200
    finally:
        db.close()


def get_resources_by_teacher_service(teacher_id: int) -> Tuple[Optional[dict], int]:
    """Obtener todos los recursos organizados por materia para un profesor"""
    db = SessionLocal()
    try:
        # Obtener las materias que enseña el profesor
        course_subjects = (
            db.query(CourseSubject, Subject)
            .join(Subject, CourseSubject.subject_id == Subject.id)
            .filter(CourseSubject.teacher_id == teacher_id)
            .distinct(Subject.id)
            .all()
        )

        if not course_subjects:
            return {"subjects": []}, 200

        subjects_data = []
        for _, subject in course_subjects:
            # Obtener todas las clases de esta materia donde el profesor enseña
            classes = (
                db.query(ClassModel)
                .join(
                    CourseSubject,
                    (CourseSubject.subject_id == ClassModel.subject_id)
                    & (CourseSubject.course_id == ClassModel.course_id),
                )
                .filter(
                    ClassModel.subject_id == subject.id,
                    CourseSubject.teacher_id == teacher_id,
                )
                .all()
            )

            # Obtener los recursos de estas clases
            class_ids = [c.id for c in classes]
            resources = (
                db.query(Resource)
                .filter(Resource.class_id.in_(class_ids))
                .order_by(Resource.period, Resource.class_id)
                .all()
            )

            # Agrupar recursos por período
            periods_data = {1: [], 2: [], 3: [], 4: []}
            for resource in resources:
                class_info = next(
                    (c for c in classes if c.id == resource.class_id), None
                )
                periods_data[resource.period].append(
                    {
                        "id": resource.id,
                        "title": resource.title,
                        "cover_image": resource.cover_image,
                        "period": resource.period,
                        "class_number": class_info.class_number if class_info else None,
                        "file_url": resource.file_url,
                        "resource_type": resource.resource_type.value,
                    }
                )

            # Obtener el course_id de la primera clase de esta materia (si existe)
            course_id = None
            if classes:
                course_id = classes[0].course_id

            subjects_data.append(
                {
                    "subject_id": subject.id,
                    "subject_name": subject.name,
                    "course_id": course_id,  # Agregar course_id
                    "periods": periods_data,
                    "total_resources": len(resources),
                }
            )

        return {"subjects": subjects_data}, 200
    finally:
        db.close()


def get_resource_service(
    resource_id: int, request: Request
) -> Tuple[Optional[dict], int]:
    """Obtener un recurso específico"""
    db = SessionLocal()
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            return None, 404

        return {
            "id": resource.id,
            "class_id": resource.class_id,
            "title": resource.title,
            "cover_image": resource.cover_image,
            "period": resource.period,
            "file_url": resource.file_url,
            "resource_type": resource.resource_type.value,
            "created_by": resource.created_by,
            "created_at": resource.created_at.isoformat(),
            "updated_at": resource.updated_at.isoformat(),
        }, 200
    finally:
        db.close()


def get_resource_file_path_service(
    resource_id: int,
) -> Tuple[Optional[str], Optional[str], int]:
    """
    Obtener la ruta del archivo de un recurso para descarga
    """
    db = SessionLocal()
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            return None, None, 404

        if not resource.file_url:
            return None, None, 404

        # Construir la ruta completa del archivo
        file_path = os.path.join("src", resource.file_url.lstrip("/"))

        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            return None, None, 404

        # Obtener el nombre del archivo original
        filename = os.path.basename(file_path)
        if resource.title:
            # Usar el título como nombre base y mantener la extensión del archivo
            file_ext = os.path.splitext(filename)[1]
            filename = f"{resource.title}{file_ext}"

        return file_path, filename, 200
    finally:
        db.close()


def create_resource_service(
    data: dict,
    cover_file=None,
    resource_file=None,
    created_by_user_id=None,
) -> Tuple[Optional[dict], int]:
    """Crear un nuevo recurso"""
    db = SessionLocal()
    try:
        class_number = data.get("class_id")
        course_id = data.get("course_id")
        subject_id = data.get("subject_id")
        period = data.get("period")

        try:
            class_number_int = int(class_number) if class_number else None
            course_id_int = int(course_id) if course_id else None
            subject_id_int = int(subject_id) if subject_id else None
            period_int = int(period) if period else None
        except (ValueError, TypeError):
            return {"error": "Valores inválidos en los datos del formulario"}, 400

        if not all([course_id_int, subject_id_int, class_number_int, period_int]):
            return {
                "error": "Faltan datos requeridos: curso, materia, número de clase y periodo"
            }, 400

        # Buscar la clase por número de clase, course_id, subject_id y period
        class_obj = (
            db.query(ClassModel)
            .filter(
                ClassModel.course_id == course_id_int,
                ClassModel.subject_id == subject_id_int,
                ClassModel.class_number == class_number_int,
                ClassModel.period == period_int,
            )
            .first()
        )

        if not class_obj:
            return {"error": "La clase especificada no existe"}, 404

        # Usar el ID real de la clase encontrada
        actual_class_id = class_obj.id

        # Procesar archivo de portada si existe
        cover_image_path = None
        if cover_file and cover_file.filename:
            filename = secure_filename(cover_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            # Crear directorio si no existe
            upload_folder = os.path.join(
                "src", "static", "uploads", "resources", "covers"
            )
            os.makedirs(upload_folder, exist_ok=True)

            # Guardar archivo
            file_path = os.path.join(upload_folder, filename)
            cover_file.save(file_path)
            cover_image_path = f"/static/uploads/resources/covers/{filename}"

        # Procesar archivo de recurso si existe
        file_url = None
        resource_type = ResourceType.FILE

        if resource_file and resource_file.filename:
            filename = secure_filename(resource_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            # Guardar archivo (todos los tipos van al mismo lugar)
            upload_folder = os.path.join(
                "src", "static", "uploads", "resources", "files"
            )
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            resource_file.save(file_path)
            file_url = f"/static/uploads/resources/files/{filename}"

        # Crear el recurso
        new_resource = Resource(
            class_id=actual_class_id,
            title=data["title"],
            cover_image=cover_image_path,
            period=data["period"],
            file_url=file_url,
            resource_type=resource_type,
            created_by=created_by_user_id,
        )

        db.add(new_resource)
        db.commit()
        db.refresh(new_resource)

        return {
            "message": "Recurso creado exitosamente",
            "resource": {
                "id": new_resource.id,
                "title": new_resource.title,
                "class_id": new_resource.class_id,
                "period": new_resource.period,
            },
        }, 201

    except Exception as e:
        db.rollback()
        return {"error": f"Error al crear el recurso: {str(e)}"}, 500
    finally:
        db.close()


def update_resource_service(
    resource_id: int,
    data: dict,
    cover_file=None,
    resource_file=None,
) -> Tuple[Optional[dict], int]:
    """Actualizar un recurso existente"""
    db = SessionLocal()
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            return None, 404

        # Actualizar campos básicos si se proporcionan
        if "title" in data and data["title"]:
            resource.title = data["title"]
        if "period" in data and data["period"]:
            resource.period = data["period"]

        # Procesar nueva portada si existe
        if cover_file and cover_file.filename:
            filename = secure_filename(cover_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            upload_folder = os.path.join(
                "src", "static", "uploads", "resources", "covers"
            )
            os.makedirs(upload_folder, exist_ok=True)

            file_path = os.path.join(upload_folder, filename)
            cover_file.save(file_path)
            resource.cover_image = f"/static/uploads/resources/covers/{filename}"

        # Procesar nuevo archivo de recurso si existe
        if resource_file and resource_file.filename:
            filename = secure_filename(resource_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            # Eliminar archivo anterior si existe
            if resource.file_url:
                old_file_path = os.path.join("src", resource.file_url.lstrip("/"))
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Guardar nuevo archivo
            upload_folder = os.path.join(
                "src", "static", "uploads", "resources", "files"
            )
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            resource_file.save(file_path)
            resource.file_url = f"/static/uploads/resources/files/{filename}"
            resource.resource_type = ResourceType.FILE

        db.commit()
        db.refresh(resource)

        return {
            "message": "Recurso actualizado exitosamente",
            "resource": {
                "id": resource.id,
                "title": resource.title,
                "cover_image": resource.cover_image,
            },
        }, 200

    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def delete_resource_service(
    resource_id: int, request: Request
) -> Tuple[Optional[dict], int]:
    """Eliminar un recurso"""
    db = SessionLocal()
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            return None, 404

        # Eliminar archivos físicos si existen
        if resource.cover_image:
            cover_path = os.path.join("src", resource.cover_image.lstrip("/"))
            if os.path.exists(cover_path):
                os.remove(cover_path)

        if resource.file_url:
            file_path = os.path.join("src", resource.file_url.lstrip("/"))
            if os.path.exists(file_path):
                os.remove(file_path)

        db.delete(resource)
        db.commit()

        return {"message": "Recurso eliminado exitosamente"}, 200
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()
