import sqlalchemy as sqlalchemy
import sqlalchemy.ext.declarative as declarative
from sqlalchemy.orm import sessionmaker

DB_URL = 'mysql://root:MySQL$123@localhost:3306/pythonfastapi'
engine = sqlalchemy.create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative.declarative_base()