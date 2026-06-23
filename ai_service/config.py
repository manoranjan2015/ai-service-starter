import os

from dotenv import load_dotenv

load_dotenv()

SERVICE_NAME = os.getenv("SERVICE_NAME", "ai-service-starter")
SERVICE_TITLE = os.getenv("SERVICE_TITLE", "AI Service Starter")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.1.0")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
AUTO_INDEX_ON_STARTUP = os.getenv("AUTO_INDEX_ON_STARTUP", "false").lower() == "true"
