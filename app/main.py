from fastapi import FastAPI, Query
from app.rag_utils import search_lyrics

app = FastAPI(title="Lyrically")

@app.get("/search")
def search(query: str = Query(..., min_length=1, description="Enter a sentence")):
    results = search_lyrics(query)
    return {"query": query, "results": results}
