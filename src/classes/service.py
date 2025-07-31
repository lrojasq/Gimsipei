from datetime import datetime
from sqlalchemy.orm import Session

from src.database.database import SessionLocal
from src.models.subject import Subject
from src.models.period import Period
from src.models.user import User, UserRole
from src.models.class_model import ClassModel
from src.models.resource import Resource
from src.models.assignment import Assignment
from src.models.class_view import ClassView
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

        # If user is a teacher, they can only delete their own subjects
        if (
            current_user.role.name == UserRole.TEACHER.name
            and db_subject.teacher_id != current_user.id
        ):
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

        # Si es profesor, solo puede actualizar sus propios periodos
        if current_user.role.name == UserRole.TEACHER.name:
            # Verificar si el periodo pertenece a una materia del profesor
            subject = db.query(Subject).get(db_period.subject_id)
            if not subject or subject.teacher_id != current_user.id:
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

        # Si es profesor, solo puede eliminar sus propios periodos
        if current_user.role.name == UserRole.TEACHER.name:
            # Verificar si el periodo pertenece a una materia del profesor
            subject = db.query(Subject).get(db_period.subject_id)
            if not subject or subject.teacher_id != current_user.id:
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
