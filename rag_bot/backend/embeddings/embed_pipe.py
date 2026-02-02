import tempfile
import pprint
from fastapi import UploadFile
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
            pprint.pp(doc[0].metadata)
            len_of_text = len("\n".join(doc.page_content for doc in doc))
            text = "\n".join(doc.page_content for doc in doc)
            chunk_size = int(len_of_text/chunk_div)
            text_spiltter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " ", ""],
                                                        chunk_size=chunk_size,
                                                        length_function=len,
                                                        chunk_overlap=chunk_size/chunk_div)
            
            splitted_text = text_spiltter.split_text(text)
            return splitted_text
        except Exception as e:
            self.logger.error(f'Что-то пошло не так при нарезке текста на чанки: {e}')




# class EmbedManager:
#     def __init__(self, embed_model, )