from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv
load_dotenv()

db_url = f'postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}'
engine = create_async_engine(url=db_url)