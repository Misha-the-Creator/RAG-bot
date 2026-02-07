from fastapi import FastAPI
from fastapi import UploadFile, File
from rag_bot.backend.logger.logger_config import logger1
from rag_bot.backend.vector_db.qdrant import VectorDBManager
from rag_bot.backend.embeddings.embed_pipe import FileHandler
from rag_bot.backend.embeddings.embed_pipe import EmbedManager
from sqlalchemy.ext.asyncio import AsyncSession
from rag_bot.backend.api_v1.sql_queries.queries import Queries
from fastapi import Depends
from rag_bot.backend.db.engine import get_db

app = FastAPI()
# embed_manager = EmbedManager('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
# embed_manager.load_model()


@app.post('/post-data-to-qdrant/')
async def post_data_to_qdrant(file: UploadFile = File(...)):
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
    

@app.post('/post-data-to-psql/')
async def post_data_to_psql(db: AsyncSession = Depends(get_db),
                            file: UploadFile = File(...)):
    query = Queries()
    file_name = file.filename
    file_bytes = await file.read()

    load = await query.query_post_data_to_psql(file_name, file_bytes, db)

    if load:
        return {'msg': 'Успешно загрузил документ в базу данных'}
    
    return {'msg': 'Не получилось загрузить документ в базу данных'}  


@app.get('/get-data-from-psql/')
async def get_data_from_psql(input_filename: str,
                             db: AsyncSession = Depends(get_db)):
    query = Queries()

    load = await query.query_get_data_from_psql(input_filename, db)

    if load:
        return {'msg': 'Успешно нашел документ в базе данных'}
    elif not load:
        return {'msg': 'Такого документа нет в базе данных'}