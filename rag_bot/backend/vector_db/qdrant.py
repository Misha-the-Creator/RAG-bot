import uuid
import numpy as np
from typing import List
from qdrant_client.http import models
from qdrant_client import QdrantClient
from rag_bot.backend.logger.logger_config import logger1

class VectorDBManager:
    def __init__(self, collection_name: str = 'knowledge_base'):
        self.logger = logger1
        self.collection_name = collection_name
        self.client = None
        self.collection = None
    
    def init_db(self):
        self.client = QdrantClient(host='localhost', port=6333)
        if self.client.collection_exists(collection_name=self.collection_name):
            self.logger.info('Векторная БД создана локально, просто заносим в нее данные')    
        else:
            self.logger.info('Создаем векторную БД')
            self.client.create_collection(collection_name=self.collection_name,
                                            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE))
            self.logger.info('Создали векторную БД')
    
    def add_docs_to_db(self, chunks: List[str], embeds: np.ndarray, metadata: dict):
        self.logger.info('Грузим эмбеды в БД')
        try:
            for chunk, embed in zip(chunks, embeds):
                point_id = str(uuid.uuid4())
                vector_list = embed.tolist()
                self.client.upsert(collection_name=self.collection_name,
                                points=[models.PointStruct(id=point_id,
                                                            vector=vector_list,
                                                            payload=metadata)])
            self.logger.info('Загрузка прошла успешно!')
        except Exception as e:
            self.logger.info(f'Возникла ошибка при загрузке эмбедов в БД: {e}')