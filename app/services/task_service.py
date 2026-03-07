# MARK: - services/task_service.py
from sqlalchemy.orm import Session
from sqlalchemy import text, or_
from geoalchemy2.shape import to_shape
from app.models.task import GigTask, TaskApplication
from app.models.user import User
from app.models.circle import CircleMember
from app.schemas.task import TaskCreate, TaskResponse, TaskApplicationCreate, TaskAcceptResponse
from fastapi import HTTPException
import random
import string

def _task_to_response(task: GigTask) -> TaskResponse:
    point = to_shape(task.location)
    return TaskResponse(
        id=task.id,
        title=task.title,
        category=task.category,
        description=task.description,
        budget=task.budget,
        is_negotiable=task.is_negotiable,
        latitude=point.y,
        longitude=point.x,
        radius_metres=task.radius_metres,
        status=task.status,
        completion_code=task.completion_code, 
        circle_id=task.circle_id, 
        requires_application=task.requires_application, 
        created_at=task.created_at,
        creator_name=task.creator.name,
        creator_id=task.creator_id,
        accepted_by_id=task.accepted_by_id,
    )

def create_task(db: Session, payload: TaskCreate, creator: User) -> TaskResponse:
    if payload.circle_id:
        member = db.query(CircleMember).filter(
            CircleMember.circle_id == payload.circle_id,
            CircleMember.user_id == creator.id
        ).first()
        if not member:
            raise HTTPException(status_code=403, detail="You can only post tasks to circles you are a member of.")

    point_wkt = f"SRID=4326;POINT({payload.longitude} {payload.latitude})"
    task = GigTask(
        title=payload.title,
        category=payload.category,
        description=payload.description,
        budget=payload.budget,
        is_negotiable=payload.is_negotiable,
        location=point_wkt,
        radius_metres=payload.radius_metres,
        circle_id=payload.circle_id, 
        requires_application=payload.requires_application, 
        creator_id=creator.id,
    )
    db.add(task)
    creator.tasks_posted += 1
    db.commit()
    db.refresh(task)
    return _task_to_response(task)

def get_tasks_in_radius(
    db: Session,
    viewer_lat: float,
    viewer_lon: float,
    category: str | None,
    current_user: User, 
) -> list[TaskResponse]:
    # ✅ FIXED: Replaced ::geography with standard CAST()
    sql = text("""
        SELECT id FROM tasks 
        WHERE status = 'Active' 
        AND ST_DWithin(
            CAST(location AS geography),
            CAST(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) AS geography),
            radius_metres
        )
        ORDER BY created_at DESC
    """)

    result = db.execute(sql, {"lat": viewer_lat, "lon": viewer_lon})
    task_ids = [row[0] for row in result]

    if not task_ids:
        return []

    user_circle_ids = [
        c.circle_id for c in db.query(CircleMember.circle_id).filter(
            CircleMember.user_id == current_user.id
        ).all()
    ]

    tasks_query = db.query(GigTask).filter(
        GigTask.id.in_(task_ids),
        or_(
            GigTask.circle_id.is_(None),
            GigTask.circle_id.in_(user_circle_ids)
        )
    )

    if category:
        tasks_query = tasks_query.filter(GigTask.category == category)

    tasks = tasks_query.all()
    return [_task_to_response(t) for t in tasks]

def get_user_tasks(db: Session, user: User) -> list[TaskResponse]:
    tasks = db.query(GigTask).filter(
        or_(
            GigTask.creator_id == user.id,
            GigTask.accepted_by_id == user.id
        )
    ).order_by(GigTask.created_at.desc()).all()
    
    return [_task_to_response(t) for t in tasks]

def accept_task(db: Session, task_id: str, acceptor: User) -> GigTask:
    task = db.query(GigTask).filter(GigTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "Active":
        raise HTTPException(status_code=400, detail="Task is no longer available")
    if str(task.creator_id) == str(acceptor.id):
        raise HTTPException(status_code=400, detail="Cannot accept your own task")
    
    if task.requires_application:
        raise HTTPException(status_code=400, detail="This task requires you to apply.")
        
    if task.circle_id:
        member = db.query(CircleMember).filter(
            CircleMember.circle_id == task.circle_id, 
            CircleMember.user_id == acceptor.id
        ).first()
        if not member:
            raise HTTPException(status_code=403, detail="You are not in this circle.")
    
    task.status = "Accepted"
    task.accepted_by_id = acceptor.id
    task.completion_code = ''.join(random.choices(string.digits, k=6))
    
    db.commit()
    db.refresh(task)
    return task

def complete_task(db: Session, task_id: str, requester: User, completion_code: str) -> GigTask:
    task = db.query(GigTask).filter(GigTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if str(task.creator_id) != str(requester.id):
        raise HTTPException(status_code=403, detail="Only the task creator can mark it complete")
    
    if task.completion_code != completion_code:
        raise HTTPException(status_code=400, detail="Invalid 6-digit verification code")
        
    task.status = "Completed"
    db.commit()
    return task

def delete_task(db: Session, task_id: str, user: User):
    task = db.query(GigTask).filter(GigTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if str(task.creator_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Only the task creator can delete this task")
    
    if user.tasks_posted > 0:
        user.tasks_posted -= 1
        
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}

# MARK: - NEW Application Logic

def apply_for_task(db: Session, task_id: str, applicant: User, payload: TaskApplicationCreate):
    task = db.query(GigTask).filter(GigTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.requires_application:
        raise HTTPException(status_code=400, detail="This task allows instant acceptance. Just accept it!")
    if task.status != "Active":
        raise HTTPException(status_code=400, detail="Task is no longer available")
    if str(task.creator_id) == str(applicant.id):
        raise HTTPException(status_code=400, detail="Cannot apply for your own task")

    if task.circle_id:
        member = db.query(CircleMember).filter(
            CircleMember.circle_id == task.circle_id, 
            CircleMember.user_id == applicant.id
        ).first()
        if not member:
            raise HTTPException(status_code=403, detail="You are not in this private circle.")

    existing = db.query(TaskApplication).filter(
        TaskApplication.task_id == task.id, 
        TaskApplication.applicant_id == applicant.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied for this task.")

    application = TaskApplication(
        task_id=task.id,
        applicant_id=applicant.id,
        cover_message=payload.cover_message
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

def get_task_applications(db: Session, task_id: str, user: User):
    task = db.query(GigTask).filter(GigTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if str(task.creator_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Only the task creator can view applications.")
        
    return db.query(TaskApplication).filter(TaskApplication.task_id == task_id).all()

def accept_application(db: Session, application_id: str, user: User) -> TaskAcceptResponse:
    application = db.query(TaskApplication).filter(TaskApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    task = application.task
    if str(task.creator_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Only the creator can accept an application.")
    if task.status != "Active":
        raise HTTPException(status_code=400, detail="Task is already fulfilled or closed.")

    application.status = "accepted"
    
    task.status = "Accepted"
    task.accepted_by_id = application.applicant_id
    task.completion_code = ''.join(random.choices(string.digits, k=6))

    other_apps = db.query(TaskApplication).filter(
        TaskApplication.task_id == task.id,
        TaskApplication.id != application_id
    ).all()
    for app in other_apps:
        app.status = "rejected"

    db.commit()
    
    return TaskAcceptResponse(
        task_id=task.id,
        accepted_by=application.applicant.name,
        status=task.status,
        chat_unlocked=True,
        completion_code=task.completion_code
    )