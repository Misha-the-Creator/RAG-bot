import re
import uuid
import numpy as np
from typing import List
from qdrant_client.http import models
from qdrant_client import QdrantClient
from sentence_transformers import CrossEncoder
from rag_bot.backend.logger.logger_config import logger1
from qdrant_client.models import Filter, FieldCondition, MatchValue


class VectorDBManager:
    def __init__(self, collection_name_chunks: str = 'knowledge_base_chunks', 
                 collection_name_questions: str = 'knowledge_base_questions',
                 cross_encoder_model_name: str = 'cross-encoder/ms-marco-MiniLM-L6-v2'):
        self.logger = logger1
        self.collection_name_chunks = collection_name_chunks
        self.collection_name_questions = collection_name_questions
        self.cross_encoder_model_name = cross_encoder_model_name
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
    
    def add_docs_to_db(self, chunks: List[str], chunk_embeds: np.ndarray, metadata: dict, file_id: str):
        self.logger.info('Грузим эмбеды в БД')
        try:
            for chunk, chunk_embed in zip(chunks, chunk_embeds):
                point_id = str(uuid.uuid4())
                vector_list_chunk = chunk_embed.tolist()

                metadata['file_id'] = file_id
                metadata['chunk_text'] = chunk
                keys_to_remove = ["source", "page", "page_label"]

                for key in keys_to_remove:
                    metadata.pop(key, None)
                    
                self.client.upsert(collection_name=self.collection_name_chunks,
                                points=[models.PointStruct(id=point_id,
                                                            vector=vector_list_chunk,
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
        
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()
    
    def reranking(self, query_chunks_pairs, chunks, rerank_top_k):
        model = CrossEncoder(self.cross_encoder_model_name)
        scores = model.predict(query_chunks_pairs)
        scored_docs = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
        self.logger.debug("После реранкинга:")
        for doc, _ in scored_docs[:rerank_top_k]:
            self.logger.debug(f'{doc}')
        
        reranked_chunks = [doc for doc, _ in scored_docs[:rerank_top_k]]

        # Логируем результат
        self.logger.debug("После реранкинга:")
        for i, chunk in enumerate(reranked_chunks, start=1):
            self.logger.debug(f"{i}: {chunk[:100]}...")  # первые 100 символов

        # Строим маппинг: чанк → позиция до реранжировки
        original_positions = {chunk: idx + 1 for idx, chunk in enumerate(chunks)}

        # Теперь для каждого чанка в reranked_chunks выводим:
        self.logger.debug("Распределение позиций:")
        for new_pos, chunk in enumerate(reranked_chunks, start=1):
            old_pos = original_positions.get(chunk, -1)
            self.logger.debug(f"Чанк '{chunk[:50]}...' | Был на месте: {old_pos} → стал на месте: {new_pos}")
        
        self.logger.debug(f'{reranked_chunks=}')

        return reranked_chunks

    def search(self, query_embed, query, lim):
        searched_texts = self.client.query_points(collection_name=self.collection_name_chunks,
                                 query=query_embed,
                                 limit=lim)
        questions = []
        scores = []
        chunks = []
        self.logger.debug('До реранкинга')
        for point in searched_texts.points:
            score = point.score
            question = self.clean_text(point.payload.get("chunk_question", ""))
            chunk_text = self.clean_text(point.payload.get("chunk_text", ""))
            
            self.logger.debug(f"Score: {score}")
            self.logger.debug(f"Question: {question}")
            self.logger.debug(f"Chunk Text: {chunk_text}")
            self.logger.debug("-" * 80)
            
            questions.append(question)
            scores.append(score)
            chunks.append(chunk_text)

        pairs = [[query, chunk] for chunk in chunks]

        reranked = self.reranking(pairs, chunks, 3)

        return reranked