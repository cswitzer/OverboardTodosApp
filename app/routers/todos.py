from typing import Annotated, Dict, List
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from app.models import Tags, Todos
from app.routers.tags import TagsResponse
from .auth import get_current_user


router = APIRouter()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)
    tags: List[int] = Field(default=[])

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, Bread, Eggs",
                "priority": 2,
                "complete": False,
            }
        }
    }


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    complete: bool
    owner_id: int
    tags: List[TagsResponse] = []

    model_config = ConfigDict(from_attributes=True)


@router.get(
    "/todos/{todo_id}/", status_code=status.HTTP_200_OK, response_model=TodoResponse
)
async def read_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
) -> TodoResponse:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if not todo_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return todo_model


@router.post("/todos/", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoRequest
) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )
    todo_request_dict = todo_request.model_dump()
    tag_ids = todo_request_dict.pop("tags", [])
    tag_objs = db.query(Tags).filter(Tags.id.in_(tag_ids)).all()
    todo_model = Todos(**todo_request_dict, owner_id=user.get("id"), tags=tag_objs)
    db.add(todo_model)
    db.commit()


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[TodoResponse])
async def read_all(user: user_dependency, db: db_dependency) -> List[Todos]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get(
    "/todos/", status_code=status.HTTP_200_OK, response_model=List[TodoResponse]
)
async def read_todos(
    user: user_dependency,
    db: db_dependency,
    complete: bool = Query(None, description="Filter by completion status"),
    priority: int = Query(None, gt=0, lt=6, description="Filter by priority"),
    search: str = Query(
        None, min_length=1, description="Search in title and description"
    ),
    limit: int = Query(10, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for results"),
) -> List[Todos]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    query = db.query(Todos).filter(Todos.owner_id == user.get("id"))

    if complete is not None:
        query = query.filter(Todos.complete == complete)
    if priority is not None:
        query = query.filter(Todos.priority == priority)
    if search:
        query = query.filter(
            (Todos.title.contains(search)) | (Todos.description.contains(search))
        )
    return query.offset(offset).limit(limit).all()


@router.post("/todos/bulk/create/", status_code=status.HTTP_201_CREATED)
async def create_todos_bulk(
    user: user_dependency, db: db_dependency, todo_requests: List[TodoRequest]
) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    todo_models = [
        Todos(**todo_request.model_dump(), owner_id=user.get("id"))
        for todo_request in todo_requests
    ]
    db.bulk_save_objects(todo_models)
    db.commit()


@router.delete("/todos/bulk/delete/", status_code=status.HTTP_200_OK)
async def delete_todos_bulk(
    db: db_dependency, todo_ids: List[int] = Query()
) -> Dict[str, str]:
    if not todo_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No IDs provided"
        )

    # remove duplicates and id's that don't exist
    no_duplicates = set(todo_ids)
    existing_tuples = db.query(Todos.id).filter(Todos.id.in_(no_duplicates)).all()
    existing_ids = {id_tuple[0] for id_tuple in existing_tuples}
    valid_ids = no_duplicates & existing_ids

    if not valid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No valid IDs found"
        )

    db.query(Todos).filter(Todos.id.in_(valid_ids)).delete(synchronize_session=False)
    db.commit()

    return {"message": f"Deleted {len(valid_ids)} todos"}


@router.put("/todos/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if not todo_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    db.commit()


@router.delete("/todos/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if not todo_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
