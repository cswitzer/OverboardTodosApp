from typing import Any
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db


def get_context(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Returns a context dictionary for GraphQL resolvers.

    This function is used to provide the database session to the resolvers.
    It can be extended in the future to include other context values as needed.
    """
    return {"db": db}
