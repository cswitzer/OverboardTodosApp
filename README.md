"# Fastapi-The-Complete-Course"

### Section 1: FastAPI Request Method Logic

#### These lines allow uvicorn to identify that we are creating a FastAPI app.

```python
from fastapi import FastAPI

app = FastAPI()
```

#### This command allows us to run the FastAPI application using Uvicorn, which is an ASGI server where

- `books` is the name of the file where the FastAPI app is defined.
- `app` is the FastAPI instance created in that file.

```bash
uvicorn books:app --reload
```

#### We can also use fastapi[standard]'s `run` command to start the server:

```bash
fastapi [run][dev] books:app --reload
```

#### FastAPI searches through each endpoint in chronological order, so the first endpoint that matches the request will be executed.

Notice that an endpoint call of `/books/mybooks` will be executed before `/books/{category}` because it is defined first.

```python
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/books/mybooks")
async def read_my_books():
    return [book for book in BOOKS if book["author"] == "Author 2"]


@app.get("/books/{category}")
async def read_books_by_category(category: str):
    return [book for book in BOOKS if book["category"] == category]
```

#### Paths in a URL are used to find specific resources. Query parameters are used to filter or modify the response of a resource.

```
path -> /books/mybooks
query -> ?author=Author+2
```

#### For post and put requests, we can use the `Body` class from FastAPI to define the request body.

```python
from fastapi import Body

@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)
    return new_book
```

#### We can also use Pydantic models to define the structure of the request body.

```python
from pydantic import BaseModel
class Book(BaseModel):
    id: int
    title: str
```

```python
@app.post("/books/create_book")
async def create_book(new_book: Book):
    BOOKS.append(new_book)
    return new_book
```

#### We can use the `Field` class from Pydantic to define additional validation rules for the request body.

```python
from pydantic import Field
class Book(BaseModel):
    id: int = Field(gt=0, description="The ID of the book must be greater than 0")
    title: str = Field(min_length=3, max_length=100, description="The title of the book must be between 3 and 100 characters")
    author: str = Field(min_length=3, max_length=100, description="The author of the book must be between 3 and 100 characters")
    description: str = Field(min_length=10, max_length=500, description="The description of the book must be between 10 and 500 characters")
    rating: int = Field(ge=1, le=5, description="The rating of the book must be between 1 and 5")
```

```python
@app.post("/books/create_book")
async def create_book(new_book: Book):
    BOOKS.append(new_book)
    return new_book
```

```python
@app.put("/books/update_book/{book_id}")
async def update_book(book_id: int, updated_book: Book):
    for book in BOOKS:
        if book.id == book_id:
            book.title = updated_book.title
            book.author = updated_book.author
            book.description = updated_book.description
            book.rating = updated_book.rating
            return book
    return {"error": "Book not found"}
```

#### Use the 'Path' class from FastAPI to define path parameters with validation.

```python
from fastapi import Path

@app.get("/books/{book_id}")
async def read_book(book_id: int = Path(gt=0):
    for book in BOOKS:
        if book.id == book_id:
            return book
    return {"error": "Book not found"}
```

#### Use the 'Query' class from FastAPI to define query parameters with validation.

```python
from fastapi import Query

@app.get("/books/rating/")
async def read_book_by_rating(rating: int = Query(ge=1, le=5):
    return [book for book in BOOKS if book.rating == rating]
```

#### Raise HTTP exceptions using the `HTTPException` class from FastAPI.

```python
from fastapi import HTTPException

@app.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")
```

#### Use the `status` module from FastAPI to define HTTP status codes.

```python
from fastapi import status

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(new_book)
    return new_book

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    ... # Update logic here
```

### Section 2: Databases, Authentication, and Authorization

#### Create a database using SQLite and SQLAlchemy.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

#### How to define a model using SQLAlchemy.

```python
from sqlalchemy import Column, Integer, String, ForeignKey

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = ForeignKey("users.id")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
```

#### How to create the database tables.

The following code creates the database tables defined by the models. It takes the `Base` class from SQLAlchemy and calls the `create_all` method on the engine, which is the connection to the database.

```python
from fastapi import FastAPI
import models
from database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
```

For now, we will delete the database after every update until we introduce a system for making migrations.

#### Interacting with the database using SQLAlchemy and DI

```python
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from typing import Annotated
from models import Base, Book

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/books/")
async def read_books(db: Annotated[Session, Depends(get_db)]):
    books = db.query(Book).all()
    return books
```

#### sqlalchemy has syntax much like the Django ORM

Uses verbs like `filter`, `all`, `first`, `get`, `update`, and `delete`.

#### Creating a new row in the database

```python
@app.post("/books/", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest, db: Annotated[Session, Depends(get_db)]):
    book = Book(**book_request.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book
```

#### Multiple routers in FastAPI

Look at how clean this makes our main application file. This is especially useful as the application grows in complexity.

```python
# inside todo/router/auth.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/auth/")
async def get_user():
    return {"user": "authenticated"}
```

```python
# inside todo/main.py
from fastapi import FastAPI
from routers import auth

app = FastAPI()
app.include_router(auth.router)
```

#### Routing specific before parameterized paths

```python
@app.get("/todos/mytodos")
async def read_my_todos():
    return {"todos": "my todos"}

@app.get("/todos/{todo_id}")
async def read_todo(todo_id: int):
    return {"todo_id": todo_id}
```

#### Bulk operations with SQLAlchemy

```python
@app.post("/todos/bulk/create/", status_code=status.HTTP_201_CREATED)
async def create_todos_bulk(db: Annotated[Session, Depends(get_db)], todo_requests: list[TodoRequest]):
    todo_models = [Todos(**todo_request.model_dump()) for todo_request in todo_requests]
    db.bulk_save_objects(todo_models)
    db.commit()
```

#### MIME types in FastAPI

```python
from fastapi import Form, File, UploadFile

# Example of application/json
@app.post("/create-todo-json/")
async def create_todo_json(todo_request: TodoRequest):
    pass

# Example of application/x-www-form-urlencoded
@app.post("/create-todo/")
async def create_todo(
    name: str = Form(...) # required form field,
    description: str = Form(None) # optional form field,
    category: str = Form("general") # form field with default value,
):
    pass

# Example of multipart/form-data
@app.post("/upload-file/")
async def upload_file(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    priority: int = Form(...),
):
    pass

# Another example of multipart/form-data
@app.post("/multi-upload/")
async def multi_upload(
    username: str = Form(...),
    tags: list[str] = Form([]) # defaults to empty list (no tags),
    files: list[UploadFile] = File(...),
):
    """
    example curl command:
    curl -X POST "http://localhost:8000/multi-upload/" \
        -F "username=cswitzer" \
        -F "tags=fun" \
        -F "tags=profiles" \
        -F "files=@file1.png" \
        -F "files=@/path/to/file2.jpg"
    """
    pass
```

#### JWT explanation

JSON Web Tokens (JWT) are a compact, URL-safe, and stateless way to represent claims between two parties. It
acts as an access card that allows users to access protected resources without needing to repeatedly authenticate themselves.

A JWT consists of 3 parts:

1. Header: Contains metadata about the token, such as the hashing algorithm used for signing and the token type (JWT).
2. Payload: Contains the claims or statements about an entity (typically, the user) and additional data. Claims can be standard (like issuer, subject, expiration) or custom-defined.
3. Signature: Ensures the integrity and authenticity of the token. It is created by using the following formula:

```
   base64UrlEncode(header) + "." + base64UrlEncode(payload) + "." + base64UrlEncode(signature)
   where signature = HMACSHA256(
        base64UrlEncode(header) + "." + base64UrlEncode(payload), secret
   )
```

The header and payload are not secure and can be decoded by anyone, so keep sensitive information out of them. The signature, however, ensures that the token has not been tampered with and can be trusted if verified with the correct secret key.

If the header or body get tampered with, the server will take the body and header (base64Url encoded of course),
the secret key, and re-generate the signature. If the newly generated signature does not match the signature
that came with the token, the server knows that the token has been tampered with and rejects the request.

For Python, "pyjwt" or "python-jose" are popular libraries for working with JWTs.

```python
from jose import jwt

# Use .env secret key in production!
SECRET_KEY = "f65da53e49581fc4b58ec88c6907fec197bddabd5619d91fc12e70e709f34903"
ALGORITHM = "HS256"

```

### Section 3: GraphQL with Strawberry

GraphQL is a query language for APIs that allows clients to request only the data they need. It provides a more efficient and flexible way to interact with APIs compared to REST.

In FastAPI, you can use the Strawberry library to create GraphQL APIs. Strawberry allows you to define your GraphQL schema using Python classes and decorators, making it easy to integrate with FastAPI.

```python
import strawberry
from .queries import Query, Mutation

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
```

In this example, we define a GraphQL schema with a `Query` and `Mutation` class. The `Query` class contains the fields that can be queried, while the `Mutation` class contains the fields that can be mutated (i.e., create, update, delete operations).

You can then use this schema in your FastAPI application to create a GraphQL endpoint.

```python
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .gql.schema import schema

app = FastAPI()

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```

This will create a GraphQL endpoint at `/graphql` where clients can send GraphQL queries and mutations to interact with your API.

```python
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
        ... # Convert the SQLAlchemy model instance to a GraphQL type instance


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
        ... # Convert the SQLAlchemy model instance to a GraphQL type instance

@strawberry.type
class Query:
    @strawberry.field
    def todo(
        self,
        info: strawberry.Info,
        id: int,
    ) -> Optional[TodoType]:
        db: Session = info.context["db"]
        todo = db.query(Todos).filter(Todos.id == id).first()
        return TodoType.from_orm(todo) if todo else None
```

This example defines two GraphQL types, `TodoType` and `UserType`, which represent the data structure of a todo item and a user, respectively. The `Query` class contains a field `todo` that allows clients to query for a specific todo item by its ID. The resolver function for this field retrieves the todo item from the database and returns it as a `TodoType` instance.

```python
query {
  todo(id: 1) {
    id
    title
    description
    priority
    complete
    owner {
      id
      email
      username
      first_name
      last_name
      is_active
      role
    }
  }
}
```

This GraphQL query requests a todo item with an ID of 1, along with its associated owner information. Any of these fields can be omitted if the client does not need them, which is one of the key benefits of using GraphQL. Notice how the query here matches up with the structure of the `TodoType` and `UserType` classes defined in the schema, and how todo is exposed as a field on the `Query` class.

### Section 4: Using uv to manage Python applications

`uv` is a tool for managing Python applications. It provides a simple interface for running and managing Python applications, including support for virtual environments, dependency management, and more.

```bash
# Create a new project with uv and a virtual environment
uv init myproj

# add deps to the project
uv add fastapi uvicorn sqlalchemy pydantic

# Run the application (by prepending uv, we do not need to explicitly activate the virtual environment)
uv run --reload main:app

# For pre-existing projects, just run the following commands
uv init --bare # creates pyproject.toml and uv.lock files without creating a new project directory
uv add -r requirements.txt # adds dependencies from an existing requirements.txt file

# Additionally, use uv sync to install packages from the uv.lock file,
# which ensures that the exact versions of dependencies are installed as specified in the lock file.
uv sync
```

These are use the basic commands to get started with `uv`. This was by far the easiest Python dependency management tool I have ever used!

### Section 5: OAuth2 and Social Authentication

OAuth2 is an open standard for accessing user data without exposing their credentials. It allows users to grant third-party applications limited access to
their resources on other services. For example, if I want to sign up for example.com without inputting an email and password, I can use my Google account
to authenticate me instead. This is called social authentication.

Here is a simple workflow for OAuth2 social authentication:

```
| Step | From → To          | HTTP Method                                   | Action / Purpose                                                                  |
| ---- | ------------------ | --------------------------------------------- | --------------------------------------------------------------------------------- |
| 1    | Browser → FastAPI  | GET /auth/google/login                        | User clicks “Sign in with Google”; browser requests login endpoint.               |
| 2    | FastAPI → Browser  | 302 Redirect → Google OAuth URL               | FastAPI redirects browser to Google login page.                                   |
| 3    | Browser → Google   | GET /accounts.google.com                      | Browser loads Google login page; user enters credentials.                         |
| 4    | Google → Browser   | 302 Redirect → /auth/google/callback?code=XYZ | After login, Google redirects browser to your callback with authorization code.   |
| 5    | Browser → FastAPI  | GET /auth/google/callback?code=XYZ            | Browser requests your callback endpoint; FastAPI receives the code.               |
| 6    | FastAPI → Google   | POST /oauth2/token                            | FastAPI exchanges code for access token, id token, and user profile.              |
| 7    | Google → FastAPI   | 200 OK                                        | Google returns tokens to FastAPI.                                                 |
| 8    | FastAPI → Browser  | 302 Redirect → /login-success?token=JWT       | FastAPI creates/fetches local user, generates JWT, redirects browser to frontend. |
| 9    | Browser → Frontend | GET /login-success?token=JWT                  | Frontend receives JWT, stores it, and logs in the user.                           |
```
