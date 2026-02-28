# MARK: - routers/tasks.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskAcceptResponse
from app.services.task_service import (
    create_task, get_tasks_in_radius, accept_task,
    complete_task, _task_to_response, get_user_tasks
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
    return get_tasks_in_radius(db, lat, lon, category)

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
        completion_code=task.completion_code # ✅ Passes the newly generated code back
    )

@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete(
    task_id: UUID, 
    code: str = Query(..., min_length=6, max_length=6), # ✅ Requires the 6-digit code from Swift
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Passes the code to the service layer for strict validation
    task = complete_task(db, str(task_id), current_user, code)
    return _task_to_response(task)