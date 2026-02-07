from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()
db_url = f'postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}'

class DatabaseHelper:
    engine = create_async_engine(url=db_url)
    session_factory = async_sessionmaker(bind=engine,
                                         autoflush=False,
                                         autocommit=False,
                                         expire_on_commit=False)
        
db_helper = DatabaseHelper()