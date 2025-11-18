import strawberry
from typing import Optional
from models import Todos, Users


# Types are used to define the shape of data in GraphQL
# that is returned to the client.


@strawberry.type
class TodoType:
    id: int
    title: str
    description: str
    priority: int
    complete: bool
    owner_id: Optional[int]

    @strawberry.field
    def owner(self, info: strawberry.Info) -> Optional["UserType"]:
        db = info.context["db"]
        if not self.owner_id:
            return None
        user = db.query(Users).filter(Users.id == self.owner_id).first()
        return UserType.from_orm(user) if user else None

    @classmethod
    def from_orm(cls, todo: Todos) -> "TodoType":
        """
        Strawberry does not know how to convert ORM models automatically,
        so this method helps with that.
        """
        return cls(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            priority=todo.priority,
            complete=todo.complete,
            owner_id=todo.owner_id,
        )


@strawberry.type
class UserType:
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str

    @classmethod
    def from_orm(cls, user: Users) -> "UserType":
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            role=user.role,
        )


# Inputs are used to define the shape of data that is accepted by the GraphQL API
# from the client.


@strawberry.input
class TodoInput:
    title: str
    description: str
    priority: int
    completed: bool = False
    owner_id: int


@strawberry.input
class TodoUpdateInput:
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    completed: Optional[bool] = None
