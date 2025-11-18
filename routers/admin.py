from typing import Annotated, List
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from models import Todos
from .todos import TodoResponse
from .auth import get_current_user


router = APIRouter(prefix="/admin", tags=["admin"])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK, response_model=list[TodoResponse])
async def read_all(user: user_dependency, db: db_dependency) -> List[Todos]:
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
) -> None:
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
