from typing import Any, Coroutine, List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from email_validator import validate_email, EmailNotValidError
from fastapi.middleware.cors import CORSMiddleware
import services as _service
import schema as _schema
from model import User, Post
from schema import PostResponse

app = FastAPI(title="User Management API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    _service.create_db()


@app.post("/api/v1/user", response_model=_schema.UserResponse, tags=["Users"])
async def create_user(
    user: _schema.UserRequest,
    database: Session = Depends(_service.get_db)
) -> User:
    try:
        validate_email(user.email)
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email: {str(e)}"
        )

    db_user = await _service.create_user(user=user, db=database)
    return db_user


@app.post("/api/v1/login", tags=["Authentication"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    database: Session = Depends(_service.get_db)
) -> dict:
    db_user = await _service.authenticate_user(
        email=form_data.username,
        password=form_data.password,
        db=database
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _service.create_token(user=db_user)


@app.get("/api/v1/health", tags=["Health"])
async def health_check() -> dict:
    return {"status": "healthy"}


@app.get("/api/v1/current-user", response_model=_schema.UserResponse, tags=["Authentication"])
async def current_user(user: _schema.UserResponse = Depends(_service.current_user)):
    return user

@app.post("/api/v1/post", response_model=_schema.PostResponse, tags=["Posts"])
async def create_post(
    post_request: _schema.PostRequest,
    user: _schema.UserResponse = Depends(_service.current_user),
    database: Session = Depends(_service.get_db)
) -> PostResponse:
    db_post = await _service.create_post(user= user, post_request=post_request, db=database)
    return db_post

@app.get("/api/v1/posts", response_model=list[_schema.PostResponse], tags=["Posts"])
async def get_all_posts(
    user: _schema.UserResponse = Depends(_service.current_user),
    database: Session = Depends(_service.get_db)
) -> list[PostResponse]:
    db_posts = await _service.get_all_posts(db=database)
    return db_posts

@app.get("/api/v1/post/user", response_model=List[_schema.PostResponse], tags=["Posts"])
async def get_posts_by_user(
    user: _schema.UserResponse = Depends(_service.current_user),
    database: Session = Depends(_service.get_db)
) -> list[PostResponse]:
    return await _service.get_posts_by_user(id=user.id, db=database)

@app.get("/api/v1/post/{post_id}", response_model=_schema.PostResponse, tags=["Posts"])
async def get_post(
    post_id: int,
    user: _schema.UserResponse = Depends(_service.current_user),
    database: Session = Depends(_service.get_db)
) -> PostResponse:
    db_post = await _service.get_post(post_id=post_id, db=database)
    return _schema.PostResponse.from_orm(db_post)

@app.put("/api/v1/post/{post_id}", response_model=_schema.PostResponse, tags=["Posts"])
async def update_post(
    post_id: int,
    post_request: _schema.PostRequest,
    user: _schema.UserResponse = Depends(_service.current_user),
    database: Session = Depends(_service.get_db)
) -> PostResponse:
    db_post = await _service.update_post(post_id=post_id, post_request=post_request, user=user, db=database)
    return _schema.PostResponse.from_orm(db_post)

@app.delete("/api/v1/post/{post_id}", tags=["Posts"])
async def delete_post(
    post_id: int,
    user: _schema.UserResponse = Depends(_service.current_user),
    database: Session = Depends(_service.get_db)
) -> None:
    await _service.delete_post(post_id=post_id, user=user, db=database)
