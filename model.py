import _datetime as datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, orm
import database as database
import passlib.hash as hash

class User(database.Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), index=True)
    phone = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    posts = orm.relationship("Post", back_populates="user")

    def password_verification(self, password):
        return hash.bcrypt.verify(self.password, password)

class Post(database.Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    title = Column(String(255), index=True)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = orm.relationship("User", back_populates="posts")

