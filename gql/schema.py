import strawberry

from .queries import Mutation, Query

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
