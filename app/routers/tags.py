from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tags

router = APIRouter(prefix="/tags", tags=["tags"])


db_dependency = Annotated[Session, Depends(get_db)]


class TagsRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class TagsResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class TodosWithTagsResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    complete: bool
    tags: list[TagsResponse]

    class Config:
        orm_mode = True


@router.post("/", status_code=201, response_model=TagsResponse)
async def create_tag(
    tag: TagsRequest,
    db: db_dependency,
) -> Tags:
    tag_model = Tags(name=tag.name)
    db.add(tag_model)
    db.commit()
    db.refresh(tag_model)
    return tag_model


@router.get("/", status_code=200, response_model=list[TagsResponse])
async def read_all_tags(db: db_dependency) -> list[Tags]:
    return db.query(Tags).all()
