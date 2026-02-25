from sqlalchemy.orm import Session
from sqlalchemy import text
from geoalchemy2.shape import to_shape
from app.models.task import GigTask
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse
from fastapi import HTTPException


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
        created_at=task.created_at,
        creator_name=task.creator.name,
        creator_id=task.creator_id,
        accepted_by_id=task.accepted_by_id,
    )


def create_task(db: Session, payload: TaskCreate, creator: User) -> TaskResponse:
    point_wkt = f"SRID=4326;POINT({payload.longitude} {payload.latitude})"
    task = GigTask(
        title=payload.title,
        category=payload.category,
        description=payload.description,
        budget=payload.budget,
        is_negotiable=payload.is_negotiable,
        location=point_wkt,
        radius_metres=payload.radius_metres,
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
    category: str | None = None,
) -> list[TaskResponse]:
    """
    Uses raw SQL for the geospatial query to avoid SQLAlchemy
    casting issues with PostGIS functions.
    """
    sql = text("""
        SELECT id FROM tasks
        WHERE status = 'Active'
        AND ST_DWithin(
            location::geography,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
            radius_metres
        )
        ORDER BY created_at DESC
    """)

    result = db.execute(sql, {"lat": viewer_lat, "lon": viewer_lon})
    task_ids = [row[0] for row in result]

    if not task_ids:
        return []

    tasks = db.query(GigTask).filter(GigTask.id.in_(task_ids)).all()

    if category:
        tasks = [t for t in tasks if t.category == category]

    return [_task_to_response(t) for t in tasks]


def accept_task(db: Session, task_id: str, acceptor: User) -> GigTask:
    task = db.query(GigTask).filter(GigTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "Active":
        raise HTTPException(status_code=400, detail="Task is no longer available")
    if str(task.creator_id) == str(acceptor.id):
        raise HTTPException(status_code=400, detail="Cannot accept your own task")
    task.status = "Accepted"
    task.accepted_by_id = acceptor.id
    db.commit()
    db.refresh(task)
    return task


def complete_task(db: Session, task_id: str, requester: User) -> GigTask:
    task = db.query(GigTask).filter(GigTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if str(task.creator_id) != str(requester.id):
        raise HTTPException(status_code=403, detail="Only the task creator can mark it complete")
    task.status = "Completed"
    db.commit()
    return task