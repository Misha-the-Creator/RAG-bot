from fastapi import Depends
from fastapi import UploadFile, File
from fastapi import FastAPI, APIRouter
from rag_bot.backend.llm.llm import LLM
from rag_bot.backend.db.engine import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from rag_bot.backend.logger.logger_config import logger1
from rag_bot.backend.vector_db.qdrant import VectorDBManager
from rag_bot.backend.embeddings.embed_pipe import FileHandler
from rag_bot.backend.embeddings.embed_pipe import EmbedManager
from rag_bot.backend.api_v1.sql_queries.queries import CRUDPSQL

psql_router = APIRouter(prefix="/psql", tags=["PostgreSQL 🐘"])
qdrant_router = APIRouter(prefix="/qdrant", tags=["Qdrant 🟥"])

embed_manager = EmbedManager('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
embed_model = embed_manager.load_model()

llm = LLM('/home/misha/Desktop/RAG-bot/rag_bot/backend/llm/llm_path')
llm.load_model()


@qdrant_router.post('/post-data-to-qdrant/{file_id}', summary='Загрузка чанков в Qdrant')
async def post_data_to_qdrant(file_id: str,
                              file: UploadFile = File(...)):
    try:
        file_handler = FileHandler()
        db_manager = VectorDBManager()

        await file_handler.create_tmp_path(file)
        splitted_txt, doc_metadata = file_handler.chunk_cutter_vanilla(2)
        chunk_embeddings = embed_manager.generate_embeds(splitted_txt)
        db_manager.init_db()
        file_id = db_manager.add_docs_to_db(splitted_txt, chunk_embeddings, doc_metadata, file_id)
        return {'msg': True,
                'file_id': file_id}
    
    except Exception as e:
        logger1.error(f'Неудачно загрузили данные в qdrant: {e}')
        return {'msg': False}
    
    finally:
        file_handler.cleanup()
    

@qdrant_router.get('/search-qdrant/{query}', summary='Поиск в Qdrant по запросу')
async def search_qdrant(query: str):
    try:
        db_manager = VectorDBManager()

        db_manager.init_db()
        query_embedding = embed_manager.generate_embeds(query)
        reranked_results = db_manager.search(query_embedding, query, 5)
        llm_response = llm.generate(chunk_list=reranked_results, think=False, user_query=query)
        return {'llm_response': llm_response}
    
    except Exception as e:
        logger1.error(f'Что-то пошло не так при similarity search: {e}')
        return {'llm_response': False}
    

@qdrant_router.delete('/delete-data-from-qdrant/{file_id}', summary='Удаление чанков в Qdrant по uuid')
async def delete_data_from_qdrant(file_id: str):
    try:
        db_manager = VectorDBManager()

        db_manager.init_db()
        delete = db_manager.delete_docs_from_db(file_id)
        return {'delete': delete}

    except Exception as e:
        logger1.error(f'Неудачно загрузили данные в qdrant: {e}')
        return {'msg': False}
    

@psql_router.post('/post-data-to-psql/', summary='Загрузка файла в БД')
async def post_data_to_psql(db: AsyncSession = Depends(get_db),
                            file: UploadFile = File(...)):
    query = CRUDPSQL()
    file_name = file.filename
    file_bytes = await file.read()
    file_size = file.size

    load = await query.query_post_data_to_psql(file_name, 
                                               file_size, 
                                               file_bytes, 
                                               db)

    if load:
        return {'msg': 'Успешно загрузил документ в базу данных',
                'load': True,
                'file_id': load.qdrant_file_id}
    
    return {'msg': 'Не получилось загрузить документ в базу данных',
            'load': False}  


@psql_router.get('/get-data-from-psql/', summary='Получение всех файлов из БД')
async def get_data_from_psql(db: AsyncSession = Depends(get_db)):
    query = CRUDPSQL()

    load = await query.query_get_data_from_psql(db)

    if load:
        return {'msg': load}
    elif not load:
        return {'msg': 'Такого документа нет в базе данных'}
    

@psql_router.put('/update-data-in-psql/{file_name}', summary='Обновление файла по указанному имени в БД')
async def update_data_in_psql(file_name: str,
                              db: AsyncSession = Depends(get_db),
                              file: UploadFile = File(...)):
    query = CRUDPSQL()
    file_bytes = await file.read()
    file_size = file.size
    load = await query.query_update_data_in_psql(file_name,
                                                 file_size,
                                                 file_bytes,
                                                 db)

    if load:
        return {'msg': f'Обновили {load}'}
    elif not load:
        return {'msg': 'Такого документа нет в базе данных'}
    

@psql_router.delete('/delete-data-from-psql/{file_name}', summary='Удаление файла по указанному имени из БД')
async def delete_data_from_psql(file_name: str,
                                db: AsyncSession = Depends(get_db)):
    query = CRUDPSQL()
    delete = await query.query_delete_data_from_psql(file_name,
                                                     db)

    if delete:
        return {'msg': f'Удалили {delete.filename}',
                'delete': True,
                'qdrant_uuid': delete.qdrant_file_id}
    elif not delete:
        return {'msg': 'Такого документа нет в базе данных',
                'delete': False}
    

app = FastAPI()
app.include_router(psql_router)
app.include_router(qdrant_router)