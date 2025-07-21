import os
import pickle

BASE = os.path.dirname(os.path.dirname(__file__))
PKL  = os.path.join(BASE, "qdrant_data.pkl")
with open(PKL, "rb") as f:
    client, model = pickle.load(f)

COLLECTION = "lyrics"

def search_lyrics(query: str, top_k: int = 200):
    q_vec = model.encode(query).tolist()
    hits  = client.search(
        collection_name=COLLECTION,
        query_vector=q_vec,
        limit=top_k,
        with_payload=True
    )

    seen = set()
    raw_results = []
    for h in hits:
        text = h.payload["text"]
        if text in seen:
            continue
        seen.add(text)
        raw_results.append({
            "lyric":    text,
            "artist":   h.payload["artist"],
            "title":    h.payload.get("title", ""),
            "image":    h.payload.get("image", ""),
            "raw_score": h.score
        })

    if not raw_results:
        return []

    MAX_RAW = 36.0
    results = []
    for r in raw_results:
        pct = int(r["raw_score"] / MAX_RAW * 100)
        pct = max(0, min(100, pct))
        results.append({
            "lyric": r["lyric"],
            "artist": r["artist"],
            "title": r["title"],
            "image": r["image"],
            "score": pct   
        })

    return results


