from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import select

from app.dependencies.auth import CurrentUser, DbSession
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskPatch, TaskPut, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_owned_task_or_404(task_id: int, owner_id: int, db: DbSession) -> Task:
    task = db.scalar(
        select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    description="Create a task owned by the authenticated user.",
)
def create_task(
    payload: TaskCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Task:
    task = Task(**payload.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get(
    "",
    response_model=list[TaskResponse],
    summary="List current user's tasks",
    description="Return only tasks owned by the authenticated user.",
)
def list_tasks(
    current_user: CurrentUser,
    db: DbSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    completed: bool | None = Query(default=None),
) -> list[Task]:
    statement = select(Task).where(Task.owner_id == current_user.id)
    if completed is not None:
        statement = statement.where(Task.completed == completed)

    statement = statement.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get one task",
    description="Return a task only when it belongs to the authenticated user.",
)
def get_task(task_id: int, current_user: CurrentUser, db: DbSession) -> Task:
    return get_owned_task_or_404(task_id, current_user.id, db)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Replace a task",
    description="Fully update a task owned by the authenticated user.",
)
def update_task(
    task_id: int,
    payload: TaskPut,
    current_user: CurrentUser,
    db: DbSession,
) -> Task:
    task = get_owned_task_or_404(task_id, current_user.id, db)
    for field, value in payload.model_dump().items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partially update a task",
    description="Update only the task fields supplied in the request body.",
)
def patch_task(
    task_id: int,
    payload: TaskPatch,
    current_user: CurrentUser,
    db: DbSession,
) -> Task:
    task = get_owned_task_or_404(task_id, current_user.id, db)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task owned by the authenticated user.",
)
def delete_task(
    task_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    task = get_owned_task_or_404(task_id, current_user.id, db)
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
