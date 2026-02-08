from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete
from rag_bot.backend.db.models.files import Files
from rag_bot.backend.api_v1.schemas.schemas import FileSchema
from rag_bot.backend.logger.logger_config import logger1
from typing import List
import uuid


class CRUDPSQL:
    
    @staticmethod
    async def query_select_by_input_filename(input_filename: str,
                                             db: AsyncSession) -> Files | None:
        stmt_1 = select(Files).where(Files.filename == input_filename)
        result = await db.execute(stmt_1)
        file_exists = result.scalar_one_or_none()

        return file_exists

    @staticmethod
    async def query_post_data_to_psql(
                                input_filename: str,
                                file_size: int,
                                file: bytes,
                                db: AsyncSession) -> FileSchema | None:
        try:
            file_exists = await CRUDPSQL.query_select_by_input_filename(input_filename, db)

            if file_exists:
                logger1.info('Файл с таким именем уже существует в базе данных, пожалуйста, загрузите другой')
                return None
            file_id = str(uuid.uuid4())
            stmt_2 = insert(Files).values(filename=input_filename,
                                          size = file_size,
                                          bytes=file,
                                          qdrant_file_id=file_id).returning(Files)
            
            result = await db.execute(stmt_2)
            db_file = result.scalar_one()
            await db.commit()
            logger1.info('Загрузка в PSQL прошла успешно')
            return FileSchema(filename=db_file.filename, size=file_size, qdrant_file_id=file_id)
            
        except Exception as e:
            await db.rollback()
            logger1.error(f'Неудачно загрузили данные в PostgreSQL: {e}')
            return None


    @staticmethod
    async def query_get_data_from_psql(db: AsyncSession) -> List | None:
        try:
            stmt = select(Files)
            
            result = await db.execute(stmt)
            db_files = result.scalars().all()
            if not db_files:
                logger1.warning('Файлов в базе данных нет')
                return None

            logger1.info('Файлы в базе данных найдены')
            filenames = [db_file.filename for db_file in db_files]
            sizes = [db_file.size for db_file in db_files]
            
            return (filenames, sizes)
            
        except Exception as e:
            logger1.error(f'Неудачно выгрузили данные по указанному названию файла из PostgreSQL: {e}')
            return None


    @staticmethod
    async def query_update_data_in_psql(input_filename: str,
                                        file_size: int,
                                        file: bytes,
                                        db: AsyncSession) -> FileSchema | None:
        try:
            file_exists = await CRUDPSQL.query_select_by_input_filename(input_filename, db)

            if file_exists:
                logger1.info('Обновляю содержимое файла по указанному имени...')
                stmt_1 = update(Files).values(bytes=file, size = file_size).where(Files.filename == input_filename)
                await db.execute(stmt_1)
                await db.commit()
                logger1.info('Обновление файла в PSQL прошло успешно')
                return FileSchema(filename=input_filename, size=file_size)
            
            logger1.warning(f'Файл с именем "{input_filename}" не найден в базе')
            return None
            
        except Exception as e:
            logger1.error(f'Неудачно обновили данные по указанному названию файла {input_filename} в PostgreSQL: {e}')
            return None
        

    @staticmethod
    async def query_delete_data_from_psql(input_filename: str,
                                          db: AsyncSession) -> FileSchema | None:
        try:
            file_exists = await CRUDPSQL.query_select_by_input_filename(input_filename, db)

            if file_exists:
                logger1.info('Удаляю содержимое файла по указанному имени...')
                file_uuid = file_exists.qdrant_file_id
                stmt_1 = delete(Files).where(Files.filename == input_filename)
                await db.execute(stmt_1)
                await db.commit()
                logger1.info('Удаление файла в PSQL прошло успешно')
                return FileSchema(filename=input_filename, qdrant_file_id=str(file_uuid))
            
            logger1.warning(f'Файл с именем "{input_filename}" не найден в базе')
            return None
            
        except Exception as e:
            await db.rollback()
            logger1.error(f'Неудачно удалили данные по указанному названию файла {input_filename} PostgreSQL: {e}')
            return None