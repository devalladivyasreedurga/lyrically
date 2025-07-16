import os
import json
import pickle
import torch
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

DATA_DIR    = "data"
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

print(f"Loading model '{MODEL_NAME}' on {device}…")
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
    with open(os.path.join(DATA_DIR, fname), encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list) and all(isinstance(x, str) for x in data):
        lines = data
    elif isinstance(data, dict) and isinstance(data.get("songs"), list):
        lines = []
        for song in data["songs"]:
            txt = song.get("lyrics")
            if isinstance(txt, str) and txt.strip():
                lines.extend(txt.split("\n"))
    else:
        continue
    for line in lines:
        text = line.strip()
        if text:
            entries.append((artist, text))

print(f"🚀 Collected {len(entries)} lines to index.")

points = []
pid = 0
for batch_start in tqdm(range(0, len(entries), BATCH_SIZE), desc="Encoding batches"):
    batch = entries[batch_start: batch_start + BATCH_SIZE]
    texts = [text for (_, text) in batch]
    vectors = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=False)
    for (artist, text), vec in zip(batch, vectors):
        points.append(PointStruct(id=pid, vector=vec.tolist(), payload={"text": text, "artist": artist,  "title":  song.get("title", artist)}))
        pid += 1

print(f"⏫ Uploading {len(points)} vectors to Qdrant…")
client.upsert(collection_name=COLLECTION, points=points)

print(f"💾 Saving client + model to '{OUTPUT_PKL}'…")
with open(OUTPUT_PKL, "wb") as f:
    pickle.dump((client, model), f)

print("GPU‑accelerated ingestion complete!")
