import os
import json
import pickle
import torch
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

DATA_DIR    = "data/json files"
COLLECTION  = "lyrics"
MODEL_NAME  = "multi-qa-mpnet-base-dot-v1"
OUTPUT_PKL  = "qdrant_data.pkl"
BATCH_SIZE  = 256

if torch.backends.mps.is_available() and torch.backends.mps.is_built():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

model = SentenceTransformer(MODEL_NAME, device=device)
client = QdrantClient(":memory:")
dim    = model.get_sentence_embedding_dimension()
client.recreate_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=dim, distance=Distance.DOT)
)

entries = []
for fname in sorted(os.listdir(DATA_DIR)):
    if not fname.endswith(".json"):
        continue
    artist = fname.replace("Lyrics_", "").replace(".json", "")
    path   = os.path.join(DATA_DIR, fname)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list) and all(isinstance(x, str) for x in data):
        for line in data:
            text = line.strip()
            if text:
                entries.append((artist, "", "", text))
    elif isinstance(data, dict) and isinstance(data.get("songs"), list):
        for song in data["songs"]:
            lyrics = song.get("lyrics")
            title  = song.get("title", "")
            img    = song.get("song_art_image_url") or song.get("header_image_url") or ""
            if isinstance(lyrics, str) and lyrics.strip():
                for line in lyrics.split("\n"):
                    text = line.strip()
                    if text:
                        entries.append((artist, title, img, text))

points = []
pid = 0
for batch_start in tqdm(range(0, len(entries), BATCH_SIZE), desc="Encoding batches"):
    batch  = entries[batch_start : batch_start + BATCH_SIZE]
    texts  = [t for (_, _, _, t) in batch]
    vectors = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=False)
    for (artist, title, img, text), vec in zip(batch, vectors):
        points.append(PointStruct(
            id=pid,
            vector=vec.tolist(),
            payload={
                "text":   text,
                "artist": artist,
                "title":  title,
                "image":  img
            }
        ))
        pid += 1

client.upsert(collection_name=COLLECTION, points=points)
with open(OUTPUT_PKL, "wb") as f:
    pickle.dump((client, model), f)
