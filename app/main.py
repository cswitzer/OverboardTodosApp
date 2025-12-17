from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

import app.models as models
from app.database import engine
from app.routers import admin, auth, tags, todos, users
from gql.context import get_context
from gql.schema import schema

# from .config import get_settings


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
