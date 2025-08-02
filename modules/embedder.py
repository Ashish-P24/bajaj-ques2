from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from modules.extractor import chunk_text

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_faiss_index(text):
    chunks = chunk_text(text)
    embeddings = model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))
    return {"index": index, "chunks": chunks}

def get_top_chunks(index_data, query, original_text, top_k=3):
    chunks = index_data["chunks"]
    index = index_data["index"]
    query_embedding = model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)
    results = [chunks[i] for i in indices[0] if i < len(chunks)]
    return results
