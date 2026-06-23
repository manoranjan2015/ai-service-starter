from pydantic import BaseModel
from typing import List, Optional

class ServiceIndexResponse(BaseModel):
    service: str
    title: str
    version: str
    docs_url: str
    endpoints: List[str]

class Citation(BaseModel):
    content: str
    score: Optional[float] = None

class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    mode: str = "simple"

class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    prompt_version: str
    citations: List[Citation] = []
    steps: List[dict] = []
    mcp_results: List[dict] = []

class AgentRequest(BaseModel):
    conversation_id: str
    task: str
    use_rag: Optional[bool] = None
    use_external: Optional[bool] = None
    mode: str = "research"

class AgentStep(BaseModel):
    step: str
    tool: str
    input: str
    output: str

class AgentResponse(BaseModel):
    conversation_id: str
    task: str
    mode: str
    used_rag: bool
    used_mcp: bool = False
    used_external: bool
    answer: str
    steps: List[AgentStep]
    prompt_version: str
    citations: List[Citation] = []
    mcp_results: List[dict] = []
    external_results: List[dict] = []

class ModelInfoResponse(BaseModel):
    service: str
    title: str
    version: str
    chat_model: str
    embedding_model: str
    prompt_version: str
