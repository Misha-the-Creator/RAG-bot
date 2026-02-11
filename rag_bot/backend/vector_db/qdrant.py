import uuid
import numpy as np
from typing import List
from qdrant_client.http import models
from qdrant_client import QdrantClient
from rag_bot.backend.logger.logger_config import logger1
from qdrant_client.models import Filter, FieldCondition, MatchValue


class VectorDBManager:
    def __init__(self, collection_name_chunks: str = 'knowledge_base_chunks', collection_name_questions: str = 'knowledge_base_questions'):
        self.logger = logger1
        self.collection_name_chunks = collection_name_chunks
        self.collection_name_questions = collection_name_questions
        self.client = None
        self.collection = None
    
    def init_db(self):
        self.client = QdrantClient(host='localhost', port=6333)
        if self.client.collection_exists(collection_name=self.collection_name_chunks):
            self.logger.info('Коллекция для чанков уже существует, просто заносим в нее данные')
        if self.client.collection_exists(collection_name=self.collection_name_questions):
            self.logger.info('Коллекция для вопросов уже существует, просто заносим в нее данные')    
        else:
            self.logger.info('Создаем коллекцию для чанков')
            self.client.create_collection(collection_name=self.collection_name_chunks,
                                            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE))
            self.logger.info('Создали коллекцию для чанков')

            self.logger.info('Создаем коллекцию для вопросов к чанкам')
            self.client.create_collection(collection_name=self.collection_name_questions,
                                            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE))
            self.logger.info('Создали векторную для вопросов к чанкам')
    
    def add_docs_to_db(self, chunks: List[str], chunk_embeds: np.ndarray, question_embeds: np.ndarray, chunk_questions: List[str], metadata: dict, file_id: str):
        self.logger.info('Грузим эмбеды в БД')
        try:
            for chunk, chunk_embed, question, question_embed in zip(chunks, chunk_embeds, chunk_questions, question_embeds):
                point_id = str(uuid.uuid4())
                vector_list_chunk = chunk_embed.tolist()
                vector_list_question = question_embed.tolist()

                metadata['file_id'] = file_id
                metadata['chunk_text'] = chunk
                metadata['chunk_question'] = question
                keys_to_remove = ["source", "page", "page_label"]

                for key in keys_to_remove:
                    metadata.pop(key, None)
                    
                self.client.upsert(collection_name=self.collection_name_chunks,
                                points=[models.PointStruct(id=point_id,
                                                            vector=vector_list_chunk,
                                                            payload=metadata)])

                self.client.upsert(collection_name=self.collection_name_questions,
                                points=[models.PointStruct(id=point_id,
                                                            vector=vector_list_question,
                                                            payload=metadata)])    
            
            self.logger.info('Загрузка прошла успешно!')

            
            return file_id
        except Exception as e:
            self.logger.info(f'Возникла ошибка при загрузке эмбедов в БД: {e}')

    def delete_docs_from_db(self, file_uuid):
        self.logger.info('Удаляю чанки из векторной БД...')
        try:
            self.client.delete(
                    collection_name=self.collection_name_chunks,
                    points_selector=Filter(must=[FieldCondition(key="file_id",
                                                                match=MatchValue(value=file_uuid))]))
            
            self.client.delete(
                    collection_name=self.collection_name_questions,
                    points_selector=Filter(must=[FieldCondition(key="file_id",
                                                                match=MatchValue(value=file_uuid))]))

            self.logger.info(f'Чанки по {file_uuid} успешно удалены')
            return True
        except Exception as e:
            self.logger.info(f'Возникла ошибка при удалении эмбедов из qdrant: {e}')
            return False