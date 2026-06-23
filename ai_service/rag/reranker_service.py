from typing import List, Tuple

from ai_service.llm.openai_service import invoke_openai


def rerank_documents(
    query: str,
    results: List[Tuple[str, float]],
    top_k: int = 3
) -> List[Tuple[str, float]]:
    scored_results = []

    for document, distance in results:
        prompt = f"""
You are a relevance scoring assistant.

Score how relevant this document chunk is to the user query.
Return only a number from 0 to 10.

User query:
{query}

Document chunk:
{document}
"""

        score_text = invoke_openai(prompt)

        try:
            score = float(score_text.strip())
        except ValueError:
            score = 0.0

        scored_results.append((document, score, distance))

    scored_results.sort(key=lambda item: item[1], reverse=True)

    return [
        (document, distance)
        for document, score, distance in scored_results[:top_k]
    ]