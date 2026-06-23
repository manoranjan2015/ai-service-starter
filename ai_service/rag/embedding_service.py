from typing import List

from openai import OpenAI

from ai_service.config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def create_embedding(text: str) -> List[float]:
    response = client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding


def create_embeddings(texts: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=texts
    )

    return [item.embedding for item in response.data]