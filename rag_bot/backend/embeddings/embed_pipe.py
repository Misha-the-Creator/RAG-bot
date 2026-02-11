import pprint
import tempfile
from typing import List
from fastapi import UploadFile
from sentence_transformers import SentenceTransformer
from rag_bot.backend.logger.logger_config import logger1
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker

from langchain_core.embeddings import Embeddings

class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model):
        self.model = model  # это ваш SentenceTransformer

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()


class FileHandler:
    def __init__(self):
        self.tmp_path = None
        self.logger = logger1
    
    async def create_tmp_path(self, file: UploadFile):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(await file.read())
                self.tmp_path = tmp.name
                return self.tmp_path
        except Exception as e:
            self.logger.error(f'Что-то пошло не так при формировании документа из вашего PDF-файла: {e}')
        
    # def chunk_cutter_semantic(self, embed_model):
    #     try:

    #         raw_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    #         # Оборачиваем
    #         embed_model = SentenceTransformerEmbeddings(raw_model)

    #         # Передаём в SemanticChunker
    #         text_splitter = SemanticChunker(
    #             embed_model,
    #             breakpoint_threshold_type='percentile',
    #             breakpoint_threshold_amount=90
    #         )

    #         loader = PyPDFLoader(self.tmp_path)
    #         doc = loader.load()
    #         pprint.pp(doc[0].metadata)
    #         print(f'{type(doc[0].metadata)=}')
    #         text = "\n".join(doc.page_content for doc in doc)
    #         text_splitter = SemanticChunker(embed_model,
    #                                         breakpoint_threshold_type='percentile',
    #                                         breakpoint_threshold_amount=90)
            
    #         splitted_text = text_splitter.split_text(text)
    #         return splitted_text, doc[0].metadata
    #     except Exception as e:
    #         self.logger.error(f'Что-то пошло не так при нарезке текста на чанки: {e}')
    
    def chunk_cutter_vanilla(self, chunk_div):
        try:
            loader = PyPDFLoader(self.tmp_path)
            doc = loader.load()
            pprint.pp(doc[0].metadata)
            print(f'{type(doc[0].metadata)=}')
            len_of_text = len("\n".join(doc.page_content for doc in doc))
            text = "\n".join(doc.page_content for doc in doc)
            chunk_size = int(len_of_text/chunk_div)
            text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " ", ""],
                                                        chunk_size=chunk_size,
                                                        length_function=len,
                                                        chunk_overlap=chunk_size/chunk_div)
            
            splitted_text = text_splitter.split_text(text)
            return splitted_text, doc[0].metadata
        except Exception as e:
            self.logger.error(f'Что-то пошло не так при нарезке текста на чанки: {e}')


class EmbedManager:
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = logger1
        self.model = None
    
    def load_model(self):
        self.logger.info('Загружаю модель-эмбеддер')
        try:
            self.model = SentenceTransformer(self.model_name)
            return self.model
        except Exception as e:
            self.logger.info(f'Проблемы при загрузке модели-эмбеддера: {e}')
    
    def generate_embeds(self, texts: List[str]):
        self.logger.info('Генерация эмбеддингов из входных чанков...')
        try:
            embeds = self.model.encode(texts)
        except Exception as e:
            self.logger.info(f'Проблемы при генерации эмбеддингов: {e}')
        return embeds
    
    def chunk_cutter_semantic(self, embed_model, tmp_path, threshold):
        try:
            embed_model = SentenceTransformerEmbeddings(self.model)
            text_splitter = SemanticChunker(
                embed_model,
                breakpoint_threshold_type='percentile',
                breakpoint_threshold_amount=threshold
            )
            loader = PyPDFLoader(tmp_path)
            doc = loader.load()
            pprint.pp(doc[0].metadata)
            print(f'{type(doc[0].metadata)=}')
            text = "\n".join(doc.page_content for doc in doc)
            text_splitter = SemanticChunker(embed_model,
                                            breakpoint_threshold_type='percentile',
                                            breakpoint_threshold_amount=90)
            splitted_text = text_splitter.split_text(text)
            return splitted_text, doc[0].metadata
        except Exception as e:
            self.logger.error(f'Что-то пошло не так при нарезке текста на чанки: {e}')