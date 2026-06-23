from typing import List, Dict

from ai_service.rag.embedding_service import create_embedding
from ai_service.rag.reranker_service import rerank_documents
from ai_service.rag.vector_store import search_documents


def retrieve_context(query: str, top_k: int = 3) -> str:
    query_embedding = create_embedding(query)

    candidate_results = search_documents(query_embedding, top_k=10)
    results = rerank_documents(query, candidate_results, top_k=top_k)

    if not results:
        return ""

    context_parts: List[str] = []

    for document, distance in results:
        context_parts.append(
            f"Document chunk:\n{document}\nDistance: {distance}"
        )

    return "\n\n".join(context_parts)

def retrieve_context_with_citations(query: str, top_k: int = 3) -> Dict:
     query_embedding = create_embedding(query)

     candidate_results = search_documents(query_embedding, top_k=10)
     results = rerank_documents(query, candidate_results, top_k=top_k)

     if not results:
         return {
            "context":"",
            "citations":[]
         }

     context_parts: List[str] = []
     citations: List[Dict] = []

     for document, distance in results:
        context_parts.append(
            f"Document chunk:\n{document}\nDistance: {distance}"
        )

        citations.append({
             "content": document,
             "score": distance
        })

     return {
            "context": "\n\n".join(context_parts),
            "citations": citations
    }