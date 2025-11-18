from fastapi import FastAPI
from database import engine
import models
from routers import auth, todos, admin, users

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

# GraphQL endpoint
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")
