import pprint
import tempfile
from typing import List
from fastapi import UploadFile
from sentence_transformers import SentenceTransformer
from rag_bot.backend.logger.logger_config import logger1
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class FileHandler:
    def __init__(self):
        self.tmp_path = None
        self.logger = logger1
    
    async def create_tmp_path(self, file: UploadFile):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(await file.read())
                self.tmp_path = tmp.name
        except Exception as e:
            self.logger.error(f'Что-то пошло не так при формировании документа из вашего PDF-файла: {e}')
        
    def chunk_cutter(self, chunk_div):
        try:
            loader = PyPDFLoader(self.tmp_path)
            doc = loader.load()
            # pprint.pp(f'{doc=}')
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
        except Exception as e:
            self.logger.info(f'Проблемы при загрузке модели-эмбеддера: {e}')
    
    def generate_embeds(self, texts: List[str]):
        self.logger.info('Генерация эмбеддингов из входных чанков...')
        try:
            embeds = self.model.encode(texts)
        except Exception as e:
            self.logger.info(f'Проблемы при генерация эмбеддингов: {e}')
        return embeds
    