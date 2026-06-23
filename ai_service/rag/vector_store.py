from typing import List, Tuple

import faiss
import numpy as np


EMBEDDING_DIMENSION = 1536

index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
documents: List[str] = []


def add_documents(chunks: List[str], embeddings: List[List[float]]) -> None:
    vectors = np.array(embeddings).astype("float32")

    index.add(vectors)
    documents.extend(chunks)


def search_documents(
        query_embedding: List[float],
        top_k: int = 3
) -> List[Tuple[str, float]]:
    if index.ntotal == 0:
        return []

    query_vector = np.array([query_embedding]).astype("float32")

    distances, indices = index.search(query_vector, top_k)

    results = []

    for document_index, distance in zip(indices[0], distances[0]):
        if document_index == -1:
            continue

        results.append((documents[document_index], float(distance)))

    return results

def has_documents() -> bool:
    return index.ntotal > 0