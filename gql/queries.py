from typing import List, Optional

import strawberry
from sqlalchemy.orm import Session

from app.models import Todos, Users

from .types import TodoType, UserType


@strawberry.type
class Query:
    @strawberry.field
    def todos(
        self,
        info: strawberry.Info,
        complete: Optional[bool] = None,
        owner_id: Optional[int] = None,
    ) -> List[TodoType]:
        db: Session = info.context["db"]
        query = db.query(Todos)

        if complete is not None:
            query = query.filter(Todos.complete == complete)

        if owner_id is not None:
            query = query.filter(Todos.owner_id == owner_id)

        return [TodoType.from_orm(todo) for todo in query.all()]

    @strawberry.field
    def todo(
        self,
        info: strawberry.Info,
        id: int,
    ) -> Optional[TodoType]:
        db: Session = info.context["db"]
        todo = db.query(Todos).filter(Todos.id == id).first()
        return TodoType.from_orm(todo) if todo else None

    @strawberry.field
    def users(self, info: strawberry.Info) -> List[UserType]:
        db: Session = info.context["db"]
        query = db.query(Users)
        return [UserType.from_orm(user) for user in query.all()]

    @strawberry.field
    def user(self, info: strawberry.Info, id: int) -> Optional[UserType]:
        db: Session = info.context["db"]
        user = db.query(Users).filter(Users.id == id).first()
        return UserType.from_orm(user) if user else None


@strawberry.type
class Mutation:
    @strawberry.field
    def create_todo(
        self,
        info: strawberry.Info,
        title: str,
        description: str,
        priority: int,
        owner_id: Optional[int] = None,
    ) -> TodoType:
        db: Session = info.context["db"]
        new_todo = Todos(
            title=title,
            description=description,
            priority=priority,
            complete=False,
            owner_id=owner_id,
        )
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return TodoType.from_orm(new_todo)
