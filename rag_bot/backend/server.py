from fastapi import FastAPI
# import chromadb
from fastapi import UploadFile, File
from rag_bot.backend.logger.logger_config import logger1
from rag_bot.backend.embeddings.embed_pipe import FileHandler

app = FastAPI()

@app.post('/post-data-to-chroma/')
async def post_data_to_chroma(file: UploadFile = File(...)):
    file_handler = FileHandler()
    await file_handler.create_tmp_path(file)

    # Делим исходный файл на 5 частей (чанков)
    splitted_txt = file_handler.chunk_cutter(5)