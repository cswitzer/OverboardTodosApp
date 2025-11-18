import strawberry
from .queries import Query, Mutation

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
