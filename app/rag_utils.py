import os, pickle

BASE = os.path.dirname(os.path.dirname(__file__))   # ../ from app/
PKL  = os.path.join(BASE, "qdrant_data.pkl")

with open(PKL, "rb") as f:
    client, model = pickle.load(f)

COLLECTION = "lyrics"

def search_lyrics(query: str, top_k: int = 5000):
    q_vec = model.encode(query).tolist()
    hits = client.search(
        collection_name=COLLECTION,
        query_vector=q_vec,
        limit=top_k,
        with_payload=True
    )
    return [
        {"lyric": h.payload["text"], "artist": h.payload["artist"], "score": h.score}
        for h in hits
    ]
