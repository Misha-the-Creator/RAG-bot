from .base import Base
from sqlalchemy import Column, Integer, Text, LargeBinary

class Files(Base):
    __tablename__ = 'uploaded_files'

    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=False)
    bytes = Column(LargeBinary, nullable=False)