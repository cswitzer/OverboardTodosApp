from fastapi import Depends
from database import get_db


def get_context(db=Depends(get_db)):
    """Returns a context dictionary for GraphQL resolvers.

    This function is used to provide the database session to the resolvers.
    It can be extended in the future to include other context values as needed.
    """
    return {"db": db}
