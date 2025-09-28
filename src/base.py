"""
Base class for SQLAlchemy models
"""
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# Base class for all models
class Base(DeclarativeBase):
    metadata = MetaData()
