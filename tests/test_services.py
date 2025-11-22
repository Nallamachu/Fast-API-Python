import pytest
from fastapi import HTTPException, status
from datetime import timedelta
import jwt

import services as _service
import model as _model
import schema as _schema
from config import get_settings


class TestUserServices:
    """Test user-related services."""
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, db_session, test_user):
        """Test retrieving an existing user by email."""
        user = await _service.get_user_by_email(email=test_user.email, db=db_session)
        assert user is not None
        assert user.email == test_user.email
        assert user.name == test_user.name
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, db_session):
        """Test retrieving a non-existent user."""
        user = await _service.get_user_by_email(email="nonexistent@example.com", db=db_session)
        assert user is None
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session):
        """Test successful user creation."""
        user_request = _schema.UserRequest(
            email="newuser@example.com",
            name="New User",
            phone="9876543210",
            password="securepassword123"
        )
        
        user = await _service.create_user(user=user_request, db=db_session)
        
        assert user.email == user_request.email
        assert user.name == user_request.name
        assert user.phone == user_request.phone
        assert user.id is not None
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, db_session, test_user):
        """Test creating a user with duplicate email."""
        user_request = _schema.UserRequest(
            email=test_user.email,
            name="Another User",
            phone="1111111111",
            password="password123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await _service.create_user(user=user_request, db=db_session)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_verify_password_correct(self, test_user):
        """Test password verification with correct password."""
        # The test user password hash is for "password"
        result = _service.verify_password("password", test_user.password)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_password_incorrect(self, test_user):
        """Test password verification with incorrect password."""
        result = _service.verify_password("wrongpassword", test_user.password)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_session, test_user):
        """Test successful user authentication."""
        user = await _service.authenticate_user(
            email=test_user.email,
            password="password",
            db=db_session
        )
        
        assert user is not None
        assert user.email == test_user.email
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session, test_user):
        """Test authentication with wrong password."""
        user = await _service.authenticate_user(
            email=test_user.email,
            password="wrongpassword",
            db=db_session
        )
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, db_session):
        """Test authentication with non-existent user."""
        user = await _service.authenticate_user(
            email="nonexistent@example.com",
            password="password",
            db=db_session
        )
        
        assert user is None


class TestTokenServices:
    """Test JWT token-related services."""
    
    @pytest.mark.asyncio
    async def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "test@example.com", "user_id": 1}
        token = _service.create_access_token(data=data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        settings = get_settings()
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == 1
    
    @pytest.mark.asyncio
    async def test_create_access_token_with_expiration(self):
        """Test access token creation with custom expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        token = _service.create_access_token(data=data, expires_delta=expires_delta)
        
        assert token is not None
        
        settings = get_settings()
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in decoded
    
    @pytest.mark.asyncio
    async def test_create_token(self, test_user):
        """Test token creation for user."""
        token_response = await _service.create_token(user=test_user)
        
        assert "access_token" in token_response
        assert token_response["token_type"] == "bearer"
        assert token_response["access_token"] is not None


class TestPostServices:
    """Test post-related services."""
    
    @pytest.mark.asyncio
    async def test_create_post_success(self, db_session, test_user):
        """Test successful post creation."""
        post_request = _schema.PostRequest(
            title="New Post",
            description="This is a new post"
        )
        
        post = await _service.create_post(
            user=test_user,
            post_request=post_request,
            db=db_session
        )
        
        assert post.title == post_request.title
        assert post.description == post_request.description
    
    @pytest.mark.asyncio
    async def test_get_all_posts(self, db_session, test_post):
        """Test retrieving all posts."""
        posts = await _service.get_all_posts(db=db_session)
        
        assert len(posts) > 0
        assert any(post.id == test_post.id for post in posts)
    
    @pytest.mark.asyncio
    async def test_get_post_success(self, db_session, test_post):
        """Test retrieving a specific post."""
        post = await _service.get_post(post_id=test_post.id, db=db_session)
        
        assert post is not None
        assert post.id == test_post.id
        assert post.title == test_post.title
    
    @pytest.mark.asyncio
    async def test_get_post_not_found(self, db_session):
        """Test retrieving a non-existent post."""
        post = await _service.get_post(post_id=9999, db=db_session)
        
        assert post is None
    
    @pytest.mark.asyncio
    async def test_get_posts_by_user(self, db_session, test_user, test_post):
        """Test retrieving posts by user."""
        posts = await _service.get_posts_by_user(id=test_user.id, db=db_session)
        
        assert len(posts) > 0
        assert any(post.id == test_post.id for post in posts)
    
    @pytest.mark.asyncio
    async def test_update_post_success(self, db_session, test_user, test_post):
        """Test successful post update."""
        post_request = _schema.PostRequest(
            title="Updated Title",
            description="Updated description"
        )
        
        updated_post = await _service.update_post(
            post_id=test_post.id,
            post_request=post_request,
            user=test_user,
            db=db_session
        )
        
        assert updated_post.title == post_request.title
        assert updated_post.description == post_request.description
    
    @pytest.mark.asyncio
    async def test_update_post_not_found(self, db_session, test_user):
        """Test updating a non-existent post."""
        post_request = _schema.PostRequest(
            title="Updated Title",
            description="Updated description"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await _service.update_post(
                post_id=9999,
                post_request=post_request,
                user=test_user,
                db=db_session
            )
        
        # Service wraps the error in a 500, but the detail contains the original error
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "404" in exc_info.value.detail or "not found" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_update_post_unauthorized(self, db_session, test_user):
        """Test updating a post by unauthorized user."""
        # Create another user with unique email
        import uuid
        other_user = _model.User(
            email=f"other{uuid.uuid4()}@example.com",
            name="Other User",
            phone="5555555555",
            password="hashedpassword"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        # Create a post by test_user
        post = _model.Post(
            title="Original Title",
            description="Original description",
            user_id=test_user.id
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        
        # Try to update with different user
        post_request = _schema.PostRequest(
            title="Updated Title",
            description="Updated description"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await _service.update_post(
                post_id=post.id,
                post_request=post_request,
                user=other_user,
                db=db_session
            )
        
        # Service wraps the error in a 500, but the detail contains the original error
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "403" in exc_info.value.detail or "not authorized" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_delete_post_success(self, db_session, test_user, test_post):
        """Test successful post deletion."""
        result = await _service.delete_post(
            post_id=test_post.id,
            user=test_user,
            db=db_session
        )
        
        assert result is True
        
        # Verify post is deleted
        post = await _service.get_post(post_id=test_post.id, db=db_session)
        assert post is None
    
    @pytest.mark.asyncio
    async def test_delete_post_not_found(self, db_session, test_user):
        """Test deleting a non-existent post."""
        with pytest.raises(HTTPException) as exc_info:
            await _service.delete_post(
                post_id=9999,
                user=test_user,
                db=db_session
            )
        
        # Service wraps the error in a 500, but the detail contains the original error
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "404" in exc_info.value.detail or "not found" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_delete_post_unauthorized(self, db_session, test_user):
        """Test deleting a post by unauthorized user."""
        # Create another user with unique email
        import uuid
        other_user = _model.User(
            email=f"other{uuid.uuid4()}@example.com",
            name="Other User",
            phone="5555555555",
            password="hashedpassword"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        # Create a post by test_user
        post = _model.Post(
            title="Test Post",
            description="Test description",
            user_id=test_user.id
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        
        # Try to delete with different user
        with pytest.raises(HTTPException) as exc_info:
            await _service.delete_post(
                post_id=post.id,
                user=other_user,
                db=db_session
            )
        
        # Service wraps the error in a 500, but the detail contains the original error
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "403" in exc_info.value.detail or "not authorized" in exc_info.value.detail.lower()
