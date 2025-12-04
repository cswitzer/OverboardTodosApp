from fastapi import FastAPI
from app.database import engine
import app.models as models
from app.routers import auth, todos, admin, users, tags

# from .config import get_settings

from strawberry.fastapi import GraphQLRouter
from gql.schema import schema
from gql.context import get_context

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# REST API routes
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(tags.router)

# GraphQL endpoint
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")
