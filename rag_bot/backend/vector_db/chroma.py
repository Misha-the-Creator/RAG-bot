import chromadb
from rag_bot.backend.logger.logger_config import logger1

class VectorDBManager:
    def __init__(self, logger, collection_name: str = 'docs', db_path: str = './vector_db'):
        self.logger = logger1
        self.collection_name = collection_name
        self.db_path = db_path
        self.client = None
        self.collection = None
    
    def init_db(self):
        self.logger.info('Создаем векторную БД')
        self.client = chromadb.PersistentClient(self.db_path)
        self.collection = self.client.get_or_create_collection(self.collection_name)
        self.logger.info('Создали векторную БД')
    
    def add_docs_to_db(self):

    
