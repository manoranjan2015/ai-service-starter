from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from ai_service.models import (
    AgentRequest,
    AgentResponse,
    ChatRequest,
    ChatResponse,
    ModelInfoResponse,
    ServiceIndexResponse,
)
from ai_service.config import (
    AUTO_INDEX_ON_STARTUP,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_MODEL,
    PROMPT_VERSION,
    SERVICE_NAME,
    SERVICE_TITLE,
    SERVICE_VERSION,
)
from ai_service.agent.prompts import validate_mode
from ai_service.agent.service import run_agent
from ai_service.memory.conversation_store import clear_conversation, get_conversation
from ai_service.rag.index_documents import index_documents
from ai_service.rag.retrieval_service import retrieve_context


CHAT_TO_AGENT_MODE = {
    "simple": "quick",
    "detailed": "research",
    "interview": "interview",
    "summary": "summary",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    if AUTO_INDEX_ON_STARTUP:
        index_documents()
    yield

app = FastAPI(
    title=SERVICE_TITLE,
    description="Model-backed AI service with prompting, memory, RAG, citations, and reranking.",
    version=SERVICE_VERSION,
    lifespan=lifespan,
)

@app.get("/", response_model=ServiceIndexResponse)
def service_index():
    return ServiceIndexResponse(
        service=SERVICE_NAME,
        title=SERVICE_TITLE,
        version=SERVICE_VERSION,
        docs_url="/docs",
        endpoints=[
            "GET /health",
            "GET /models/info",
            "POST /chat",
            "POST /agent/run",
            "GET /chat/{conversation_id}/history",
            "DELETE /chat/{conversation_id}",
            "GET /rag/search",
        ],
    )

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": SERVICE_NAME
    }


@app.get("/models/info", response_model=ModelInfoResponse)
def model_info():
    return ModelInfoResponse(
        service=SERVICE_NAME,
        title=SERVICE_TITLE,
        version=SERVICE_VERSION,
        chat_model=OPENAI_MODEL,
        embedding_model=OPENAI_EMBEDDING_MODEL,
        prompt_version=PROMPT_VERSION,
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    try:

        validate_mode(request.mode)
        agent_result = run_agent(
            request.conversation_id,
            request.message,
            mode=CHAT_TO_AGENT_MODE[request.mode],
        )
        return ChatResponse(
            conversation_id=request.conversation_id,
            answer=agent_result["answer"],
            prompt_version=PROMPT_VERSION,
            citations=agent_result["citations"],
            steps=agent_result["steps"],
            mcp_results=agent_result["mcp_results"],
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat agent run failed: {str(e)}")
    

@app.post("/agent/run", response_model=AgentResponse)
def agent_run(request: AgentRequest):
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="task cannot be empty")

    try:
        return AgentResponse(**run_agent(
            request.conversation_id,
            request.task,
            request.use_rag,
            request.use_external,
            request.mode
        ))

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent run failed: {str(e)}")


@app.delete("/chat/{conversation_id}")
def delete_conversation(conversation_id: str):
    deleted = clear_conversation(conversation_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="conversation not found")

    return {
        "status": "deleted",
        "conversation_id": conversation_id
    }

@app.get("/chat/{conversation_id}/history")
def get_chat_history(conversation_id: str):
    history = get_conversation(conversation_id)

    if not history:
        raise HTTPException(status_code=404, detail="conversation not found")

    return {
        "conversation_id": conversation_id,
        "messages": history
    }

@app.get("/rag/search")
def rag_search(query: str):
    context = retrieve_context(query)

    if not context:
        return {
            "query": query,
            "context": ""
        }

    return {
        "query": query,
        "context": context
    }
