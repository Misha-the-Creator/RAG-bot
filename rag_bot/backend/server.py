from fastapi import FastAPI
from fastapi import UploadFile, File
from rag_bot.backend.logger.logger_config import logger1
from rag_bot.backend.vector_db.qdrant import VectorDBManager
from rag_bot.backend.embeddings.embed_pipe import FileHandler
from rag_bot.backend.embeddings.embed_pipe import EmbedManager

app = FastAPI()
embed_manager = EmbedManager('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
embed_manager.load_model()


@app.post('/post-data-to-qdrant/')
async def post_data_to_chroma(file: UploadFile = File(...)):
    try:
        file_handler = FileHandler()
        await file_handler.create_tmp_path(file)

        splitted_txt, doc_metadata = file_handler.chunk_cutter(5)


        embeddings = embed_manager.generate_embeds(splitted_txt)

        db_manager = VectorDBManager()
        db_manager.init_db()
        db_manager.add_docs_to_db(splitted_txt, embeddings, doc_metadata)
        return {'message': True}
    except Exception as e:
        logger1.error(f'Неудачно загрузили данные в qdrant: {e}')
        return {'message': False}





    

    