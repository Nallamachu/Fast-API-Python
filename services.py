from typing import Optional, Dict, Any
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import database as _database
import model as _model
import schema
import schema as _schema
from config import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

# Get settings
_settings = get_settings()

# JWT Configuration
JWT_SECRET = _settings.SECRET_KEY
JWT_ALGORITHM = _settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = _settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_db():
    """Create database tables."""
    return _database.Base.metadata.create_all(bind=_database.engine)

def get_db() -> Session:
    """Dependency to get DB session."""
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_user_by_email(email: str, db: Session) -> Optional[_model.User]:
    """Get user by email.
    
    Args:
        email: User's email address
        db: Database session
        
    Returns:
        User object if found, None otherwise
    """
    try:
        return db.query(_model.User).filter(_model.User.email == email).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}"
        )

async def create_user(user: _schema.UserRequest, db: Session) -> _model.User:
    """Create a new user.
    
    Args:
        user: User creation request
        db: Database session
        
    Returns:
        Newly created user object
        
    Raises:
        HTTPException: If user with email already exists or creation fails
    """
    try:
        # Check if user already exists
        db_user = await get_user_by_email(email=user.email, db=db)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
        
        # Create user object
        user_obj = _model.User(
            email=user.email,
            name=user.name,
            phone=user.phone,
            password=hashed_password.decode('utf-8'),  # Store as string
        )
        
        # Save user
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)
        return user_obj
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def create_token(user: _model.User) -> Dict[str, str]:
    """Create access token for user.
    
    Args:
        user: User object
        
    Returns:
        Dictionary containing access token and token type
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def authenticate_user(email: str, password: str, db: Session) -> Optional[_model.User]:
    """Authenticate a user.
    
    Args:
        email: User's email
        password: Plain text password
        db: Database session
        
    Returns:
        User object if authentication successful, None otherwise
    """
    user = await get_user_by_email(email=email, db=db)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

async def current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> _model.User:
    """Get current user from token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await get_user_by_email(email=email, db=db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def create_post(user, post_request, db):
    try:
        db_post = _model.Post(
            title=post_request.title,
            description=post_request.description,
            user_id= user.id
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return schema.PostResponse.from_orm(db_post)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating post: {str(e)}"
        )


async def get_all_posts(db):
    try:
        posts = db.query(_model.Post).all()
        return [schema.PostResponse.from_orm(post) for post in posts]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving posts: {str(e)}"
        )

async def get_post(post_id, db):
    try:
        return db.query(_model.Post).filter(_model.Post.id == post_id).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving post: {str(e)}"
        )

async def update_post(post_id, post_request, user, db):
    try:
        db_post = await get_post(post_id=post_id, db=db)
        if db_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        if db_post.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this post"
            )
        db_post.title = post_request.title
        db_post.description = post_request.description
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return schema.PostResponse.from_orm(db_post)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating post: {str(e)}"
        )

async def delete_post(post_id, user, db):
    try:
        db_post = await get_post(post_id=post_id, db=db)
        if db_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        if db_post.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this post"
            )
        db.delete(db_post)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting post: {str(e)}"
        )


async def get_posts_by_user(id, db):
    try:
        posts = db.query(_model.Post).filter(_model.Post.user_id == id).all()
        return [
            schema.PostResponse(
                id=post.id,
                title=post.title,
                description=post.description,
                created_at=post.created_at,
                user=None
            )
            for post in posts
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving posts: {str(e)}"
        )