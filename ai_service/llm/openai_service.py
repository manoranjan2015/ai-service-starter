from openai import OpenAI
from ai_service.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def invoke_openai(prompt: str) -> str:
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )
    return response.output_text

