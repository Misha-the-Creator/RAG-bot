from .base import Base
from sqlalchemy import Column, Integer, Text, LargeBinary, BigInteger
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Files(Base):
    __tablename__ = 'uploaded_files'

    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=False)
    bytes = Column(LargeBinary, nullable=False)
    size = Column(BigInteger)
    qdrant_file_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=True)