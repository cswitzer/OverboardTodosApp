from __future__ import annotations

from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Users(Base):
    __tablename__ = "users"

    # Using SQLAlchemy 2.0 style with Mapped and mapped_column
    # the strengths here include better type checking and IDE support
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    todos: Mapped[List["Todos"]] = relationship("Todos", back_populates="owner")

    # Using old style for reference
    # id = Column(Integer, primary_key=True, index=True)
    # email = Column(String, unique=True)
    # username = Column(String, unique=True)
    # first_name = Column(String)
    # last_name = Column(String)
    # hashed_password = Column(String)
    # is_active = Column(Boolean, default=True)
    # role = Column(String)


# Association table that allows a convenient way to have m2m relationships
# # A todo can have many tags, and a tag can be on many todos
todo_tags = Table(
    "todo_tags",
    Base.metadata,
    Column("todo_id", ForeignKey("todos.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Todos(Base):
    __tablename__ = "todos"

    # Using SQLAlchemy 2.0 style with Mapped and mapped_column
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(500))
    priority: Mapped[int] = mapped_column()
    complete: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Does not relate to a column in the db. Provides convenient access to the related user object.
    owner: Mapped["Users"] = relationship("Users", back_populates="todos")

    # lets you access all tags for a todo
    tags: Mapped[List[Tags]] = relationship(secondary=todo_tags, back_populates="todos")

    # Using old style for reference
    # id = Column(Integer, primary_key=True, index=True)
    # title = Column(String)
    # description = Column(String)
    # priority = Column(Integer)
    # complete = Column(Boolean, default=False)
    # owner_id = Column(Integer, ForeignKey("users.id"))


class Tags(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    todos: Mapped[List[Todos]] = relationship(
        secondary=todo_tags, back_populates="tags"
    )
