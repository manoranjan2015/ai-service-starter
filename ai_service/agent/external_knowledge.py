from typing import Dict, List


EXTERNAL_KNOWLEDGE = [
    {
        "keywords": ["rag", "retrieval", "embedding", "vector"],
        "title": "Public RAG best practices",
        "content": "Use retrieval evaluation, citations, chunk quality checks, and reranking to improve grounded answers.",
        "url": "https://example.com/rag-best-practices",
    },
    {
        "keywords": ["mcp", "model context protocol", "tool"],
        "title": "MCP integration pattern",
        "content": "MCP gives agents a standard interface for discovering and calling external tools.",
        "url": "https://example.com/mcp-pattern",
    },
    {
        "keywords": ["agent", "workflow", "memory"],
        "title": "Agent workflow pattern",
        "content": "Agents commonly combine memory, tool choice, tool calls, and a final model response.",
        "url": "https://example.com/agent-workflow",
    },
]


def external_knowledge_search(query: str, top_k: int = 3) -> Dict:
    normalized_query = query.lower()
    matches: List[Dict] = []

    for item in EXTERNAL_KNOWLEDGE:
        if any(keyword in normalized_query for keyword in item["keywords"]):
            matches.append({
                "title": item["title"],
                "content": item["content"],
                "url": item["url"],
            })

    if not matches:
        matches.append({
            "title": "General external knowledge note",
            "content": "No specific canned external result matched. Replace this demo tool with a real external search provider later.",
            "url": "https://example.com/general-external-knowledge",
        })

    return {
        "source": "external_knowledge_search",
        "query": query,
        "results": matches[:top_k],
    }
