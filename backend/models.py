from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=False)
    deadline = Column(String)
    priority = Column(String)
    status = Column(String, default='pending')
