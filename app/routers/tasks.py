# MARK: - routers/tasks.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskAcceptResponse, TaskApplicationCreate, TaskApplicationResponse
from app.services.task_service import (
    create_task, get_tasks_in_radius, accept_task,
    complete_task, _task_to_response, get_user_tasks, delete_task,
    apply_for_task, get_task_applications, accept_application # ✅ Added new imports
)
from app.services.auth_service import get_current_user
from app.models.user import User
from uuid import UUID

router = APIRouter(prefix="/tasks", tags=["Tasks"])

JAIPUR_LAT = 26.9124
JAIPUR_LON = 75.7873

@router.post("", response_model=TaskResponse, status_code=201)
def post_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_task(db, payload, current_user)

@router.get("", response_model=list[TaskResponse])
def list_tasks(
    lat: float = Query(default=JAIPUR_LAT),
    lon: float = Query(default=JAIPUR_LON),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ✅ Pass current_user to filter out private circles they aren't in
    return get_tasks_in_radius(db, lat, lon, category, current_user)

@router.get("/me", response_model=list[TaskResponse])
def my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_tasks(db, current_user)

@router.post("/{task_id}/accept", response_model=TaskAcceptResponse)
def accept(
    task_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = accept_task(db, str(task_id), current_user)
    return TaskAcceptResponse(
        task_id=task.id,
        accepted_by=current_user.name,
        status=task.status,
        chat_unlocked=True,
        completion_code=task.completion_code
    )

@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete(
    task_id: UUID, 
    code: str = Query(..., min_length=6, max_length=6),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = complete_task(db, str(task_id), current_user, code)
    return _task_to_response(task)

@router.delete("/{task_id}")
def remove_task(
    task_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_task(db, str(task_id), current_user)


# MARK: - NEW: Application Endpoints

@router.post("/{task_id}/apply", response_model=TaskApplicationResponse)
def apply_to_task(
    task_id: UUID,
    payload: TaskApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit an application for a task that requires review."""
    return apply_for_task(db, str(task_id), current_user, payload)

@router.get("/{task_id}/applications", response_model=list[TaskApplicationResponse])
def view_task_applications(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creator views all applications for their task."""
    return get_task_applications(db, str(task_id), current_user)

@router.post("/applications/{application_id}/accept", response_model=TaskAcceptResponse)
def approve_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creator approves one specific applicant to do the job."""
    return accept_application(db, str(application_id), current_user)