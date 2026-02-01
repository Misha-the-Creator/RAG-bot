from fastapi import FastAPI
import chromadb

app = FastAPI()

@app.post('/post-data-to-chroma/')
async def post_data_to_chroma():
    