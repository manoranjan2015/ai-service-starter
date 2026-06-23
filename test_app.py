from fastapi.testclient import TestClient
from ai_service.agent import mcp_client
from ai_service.agent.service import run_agent
from ai_service.rag.document_loader import load_documents
from mcp_service.mcp_tools import (
    get_recent_scores_tool,
    get_student_courses_tool,
    get_student_profile_tool,
    get_upcoming_exams_tool,
)
from ai_service.rag.reranker_service import rerank_documents

from ai_service.app import app
from ai_service.memory.conversation_store import clear_conversation, get_conversation

client = TestClient(app)


def test_service_index():
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()
    assert body["service"] == "ai-service-starter"
    assert body["title"] == "AI Service Starter"
    assert body["version"]
    assert body["docs_url"] == "/docs"
    assert "POST /chat" in body["endpoints"]
    assert "POST /agent/run" in body["endpoints"]
    assert "GET /rag/search" in body["endpoints"]


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ai-service-starter"
    }


def test_model_info():
    response = client.get("/models/info")

    assert response.status_code == 200

    body = response.json()
    assert body["service"] == "ai-service-starter"
    assert body["title"] == "AI Service Starter"
    assert body["version"]
    assert body["chat_model"]
    assert body["embedding_model"]
    assert body["prompt_version"]


def test_mcp_get_student_profile_tool(monkeypatch):
    def fake_fetch_student_service_json(path: str) -> dict:
        assert path == "/student"
        return {
            "student_id": "STU-101",
            "name": "Aarav Sharma",
            "grade": "8",
            "school": "Demo Public School",
            "academic_year": "2026",
            "courses": [],
            "upcoming_exams": [],
            "recent_scores": [],
        }

    monkeypatch.setattr(
        "mcp_service.mcp_tools.fetch_student_service_json",
        fake_fetch_student_service_json,
    )

    result = get_student_profile_tool()

    assert result == {
        "student_id": "STU-101",
        "name": "Aarav Sharma",
        "grade": "8",
        "school": "Demo Public School",
        "academic_year": "2026",
    }


def test_mcp_get_student_courses_tool(monkeypatch):
    def fake_fetch_student_service_json(path: str) -> dict:
        assert path == "/student/courses"
        return {
            "student_id": "STU-101",
            "courses": [
                {"subject": "Mathematics", "teacher": "Ms. Rao"}
            ],
        }

    monkeypatch.setattr(
        "mcp_service.mcp_tools.fetch_student_service_json",
        fake_fetch_student_service_json,
    )

    result = get_student_courses_tool()

    assert result["student_id"] == "STU-101"
    assert result["courses"][0]["subject"] == "Mathematics"


def test_mcp_get_upcoming_exams_tool(monkeypatch):
    def fake_fetch_student_service_json(path: str) -> dict:
        assert path == "/student/exams"
        return {
            "student_id": "STU-101",
            "upcoming_exams": [
                {"subject": "Science", "date": "2026-07-02"}
            ],
        }

    monkeypatch.setattr(
        "mcp_service.mcp_tools.fetch_student_service_json",
        fake_fetch_student_service_json,
    )

    result = get_upcoming_exams_tool()

    assert result["student_id"] == "STU-101"
    assert result["upcoming_exams"][0]["subject"] == "Science"


def test_mcp_get_recent_scores_tool(monkeypatch):
    def fake_fetch_student_service_json(path: str) -> dict:
        assert path == "/student/scores"
        return {
            "student_id": "STU-101",
            "recent_scores": [
                {"subject": "Mathematics", "score": 72, "max_score": 100}
            ],
        }

    monkeypatch.setattr(
        "mcp_service.mcp_tools.fetch_student_service_json",
        fake_fetch_student_service_json,
    )

    result = get_recent_scores_tool()

    assert result["student_id"] == "STU-101"
    assert result["recent_scores"][0]["score"] == 72


def test_ai_service_mcp_client_calls_student_tool(monkeypatch):
    def fake_get_student_courses_tool() -> dict:
        return {
            "student_id": "STU-101",
            "courses": [
                {"subject": "Mathematics", "teacher": "Ms. Rao"}
            ],
        }

    monkeypatch.setitem(
        mcp_client.STUDENT_MCP_TOOLS,
        "get_student_courses",
        fake_get_student_courses_tool,
    )

    result = mcp_client.get_student_courses()

    assert result["student_id"] == "STU-101"
    assert result["courses"][0]["teacher"] == "Ms. Rao"


def test_ai_service_mcp_client_returns_error_for_unknown_tool():
    result = mcp_client.call_mcp_tool("unknown_tool")

    assert result["error"] == "unsupported_mcp_tool"
    assert result["tool"] == "unknown_tool"
    assert "get_recent_scores" in result["available_tools"]


def test_study_tracker_documents_are_loadable():
    chunks = load_documents("documents")

    assert any("Weekly Lessons for STU-101" in chunk for chunk in chunks)
    assert any("Teacher Remarks for STU-101" in chunk for chunk in chunks)
    assert any("Revision Notes for STU-101" in chunk for chunk in chunks)


def test_empty_message_returns_400():
    response = client.post("/chat", json={
        "conversation_id": "test-chat",
        "message": "",
        "mode": "simple"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "message cannot be empty"


def test_empty_agent_task_returns_400():
    response = client.post("/agent/run", json={
        "conversation_id": "test-agent",
        "task": "",
        "use_rag": True
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "task cannot be empty"


def test_agent_run_success_returns_steps(monkeypatch):
    clear_conversation("test-agent-success")

    def fake_run_agent(
            conversation_id: str,
            task: str,
            use_rag=None,
            use_external=None,
            mode: str = "research"
    ) -> dict:
        return {
            "conversation_id": conversation_id,
            "task": task,
            "mode": mode,
            "used_rag": True,
            "used_mcp": True,
            "used_external": False,
            "answer": "Agent answer",
            "steps": [
                {
                    "step": "load_memory",
                    "tool": "conversation_store.get_conversation",
                    "input": conversation_id,
                    "output": "Loaded 0 previous messages.",
                },
                {
                    "step": "choose_tools",
                    "tool": "agent_service.should_use_rag",
                    "input": f"task={task}; use_rag={use_rag}; use_external={use_external}",
                    "output": "RAG selected: True.",
                },
                {
                    "step": "retrieve_context",
                    "tool": "retrieval_service.retrieve_context_with_citations",
                    "input": task,
                    "output": "Retrieved 1 citation chunks.",
                },
                {
                    "step": "final_answer",
                    "tool": "openai_service.invoke_openai",
                    "input": f"mode={mode}; prompt_version=v1",
                    "output": "Generated the final answer.",
                },
            ],
            "prompt_version": "v1",
            "citations": [
                {"content": "Agent citation", "score": 0.2}
            ],
            "mcp_results": [
                {"tool": "get_student_profile", "result": {"student_id": "STU-101"}}
            ],
            "external_results": [],
        }

    monkeypatch.setattr("ai_service.app.run_agent", fake_run_agent)

    response = client.post("/agent/run", json={
        "conversation_id": "test-agent-success",
        "task": "Summarize RAG",
        "use_rag": True,
        "mode": "interview"
    })

    assert response.status_code == 200

    body = response.json()
    assert body["conversation_id"] == "test-agent-success"
    assert body["task"] == "Summarize RAG"
    assert body["mode"] == "interview"
    assert body["used_rag"] is True
    assert body["used_mcp"] is True
    assert body["used_external"] is False
    assert body["answer"] == "Agent answer"
    assert body["prompt_version"] == "v1"
    assert body["citations"] == [
        {"content": "Agent citation", "score": 0.2}
    ]
    assert body["mcp_results"] == [
        {"tool": "get_student_profile", "result": {"student_id": "STU-101"}}
    ]
    assert [step["step"] for step in body["steps"]] == [
        "load_memory",
        "choose_tools",
        "retrieve_context",
        "final_answer",
    ]
    assert body["steps"][1]["input"] == "task=Summarize RAG; use_rag=True; use_external=None"


def test_invalid_agent_mode_returns_400():
    response = client.post("/agent/run", json={
        "conversation_id": "test-agent",
        "task": "Summarize RAG",
        "mode": "wrong"
    })

    assert response.status_code == 400
    assert "unsupported agent mode" in response.json()["detail"]


def test_run_agent_uses_memory_rag_and_model(monkeypatch):
    clear_conversation("test-run-agent")

    def fake_retrieve_context_with_citations(query: str) -> dict:
        return {
            "context": "Agent RAG context",
            "citations": [
                {"content": "Agent RAG citation", "score": 0.3}
            ],
        }

    def fake_invoke_openai(prompt: str) -> str:
        assert "Agent RAG context" in prompt
        assert "STU-101" in prompt
        assert "Summarize agent memory" in prompt
        return "Final agent answer"

    def fake_call_mcp_tool(tool_name: str) -> dict:
        assert tool_name == "get_student_profile"
        return {"student_id": "STU-101", "name": "Aarav Sharma"}

    monkeypatch.setattr(
        "ai_service.agent.service.retrieve_context_with_citations",
        fake_retrieve_context_with_citations
    )
    monkeypatch.setattr("ai_service.agent.service.invoke_openai", fake_invoke_openai)
    monkeypatch.setattr("ai_service.agent.service.call_mcp_tool", fake_call_mcp_tool)

    result = run_agent("test-run-agent", "Summarize agent memory from source document")

    assert result["answer"] == "Final agent answer"
    assert result["mode"] == "research"
    assert result["used_rag"] is True
    assert result["used_mcp"] is True
    assert result["used_external"] is False
    assert result["citations"] == [
        {"content": "Agent RAG citation", "score": 0.3}
    ]
    assert [step["step"] for step in result["steps"]] == [
        "load_memory",
        "choose_tools",
        "retrieve_context",
        "choose_mcp_tools",
        "call_mcp_tool",
        "choose_external_tool",
        "skip_external_tool",
        "final_answer",
    ]
    assert get_conversation("test-run-agent") == [
        {"role": "user", "content": "Summarize agent memory from source document"},
        {"role": "assistant", "content": "Final agent answer"}
    ]


def test_run_agent_uses_external_when_local_rag_is_not_enough(monkeypatch):
    clear_conversation("test-run-agent-no-rag")

    def fake_retrieve_context_with_citations(query: str) -> dict:
        return {
            "context": "",
            "citations": [],
        }

    def fake_invoke_openai(prompt: str) -> str:
        assert "General external knowledge note" in prompt
        assert "What is an API?" in prompt
        return "API answer"

    monkeypatch.setattr(
        "ai_service.agent.service.retrieve_context_with_citations",
        fake_retrieve_context_with_citations
    )
    monkeypatch.setattr("ai_service.agent.service.invoke_openai", fake_invoke_openai)
    monkeypatch.setattr("ai_service.agent.service.choose_student_mcp_tools", lambda task: [])

    result = run_agent("test-run-agent-no-rag", "What is an API?", mode="quick")

    assert result["mode"] == "quick"
    assert result["used_rag"] is True
    assert result["used_external"] is True
    assert result["citations"] == []
    assert result["external_results"]
    assert [step["step"] for step in result["steps"]] == [
        "load_memory",
        "choose_tools",
        "retrieve_context",
        "choose_mcp_tools",
        "choose_external_tool",
        "external_knowledge_search",
        "final_answer",
    ]


def test_run_agent_uses_mcp_scores_for_score_question(monkeypatch):
    clear_conversation("test-run-agent-scores")

    def fake_retrieve_context_with_citations(query: str) -> dict:
        return {
            "context": "",
            "citations": [],
        }

    called_tools = []

    def fake_call_mcp_tool(tool_name: str) -> dict:
        called_tools.append(tool_name)
        if tool_name == "get_student_profile":
            return {"student_id": "STU-101", "name": "Aarav Sharma"}
        if tool_name == "get_recent_scores":
            return {
                "student_id": "STU-101",
                "recent_scores": [
                    {"subject": "Mathematics", "score": 72, "max_score": 100}
                ],
            }
        return {}

    def fake_invoke_openai(prompt: str) -> str:
        assert "get_recent_scores" in prompt
        assert "72" in prompt
        return "Aarav scored 72/100 in Mathematics."

    monkeypatch.setattr(
        "ai_service.agent.service.retrieve_context_with_citations",
        fake_retrieve_context_with_citations
    )
    monkeypatch.setattr("ai_service.agent.service.call_mcp_tool", fake_call_mcp_tool)
    monkeypatch.setattr("ai_service.agent.service.invoke_openai", fake_invoke_openai)

    result = run_agent("test-run-agent-scores", "What was my last class test score?")

    assert result["answer"] == "Aarav scored 72/100 in Mathematics."
    assert result["used_mcp"] is True
    assert result["used_external"] is False
    assert called_tools == ["get_student_profile", "get_upcoming_exams", "get_recent_scores"]
    assert [item["tool"] for item in result["mcp_results"]] == [
        "get_student_profile",
        "get_upcoming_exams",
        "get_recent_scores",
    ]


def test_invalid_mode_returns_400(monkeypatch):
    response = client.post("/chat", json={
        "conversation_id": "test-chat",
        "message": "Explain RAG",
        "mode": "wrong"
    })
    assert response.status_code == 400
    assert "unsupported mode" in response.json()["detail"]


def test_delete_missing_conversation_returns_404():
    clear_conversation("missing-chat")

    response = client.delete("/chat/missing-chat")

    assert response.status_code == 404
    assert response.json()["detail"] == "conversation not found"


def test_chat_success_stores_conversation(monkeypatch):
    clear_conversation("test-chat-success")

    def fake_run_agent(conversation_id: str, task: str, use_rag=None, use_external=None, mode: str = "research") -> dict:
        assert conversation_id == "test-chat-success"
        assert task == "What is RAG?"
        assert mode == "quick"
        return {
            "conversation_id": conversation_id,
            "task": task,
            "mode": mode,
            "used_rag": True,
            "used_mcp": True,
            "used_external": False,
            "answer": "Fake AI answer",
            "steps": [
                {"step": "final_answer", "tool": "openai_service.invoke_openai", "input": "mode=quick", "output": "done"}
            ],
            "prompt_version": "v1",
            "citations": [
                {"content": "Fake citation", "score": 0.1}
            ],
            "mcp_results": [
                {"tool": "get_student_profile", "result": {"student_id": "STU-101"}}
            ],
            "external_results": [],
        }

    monkeypatch.setattr("ai_service.app.run_agent", fake_run_agent)

    response = client.post("/chat", json={
        "conversation_id": "test-chat-success",
        "message": "What is RAG?",
        "mode": "simple"
    })

    assert response.status_code == 200

    body = response.json()
    assert body["conversation_id"] == "test-chat-success"
    assert body["answer"] == "Fake AI answer"
    assert body["prompt_version"]
    assert body["citations"] == [
        {"content": "Fake citation", "score": 0.1}
    ]
    assert body["mcp_results"] == [
        {"tool": "get_student_profile", "result": {"student_id": "STU-101"}}
    ]
    assert body["steps"][0]["step"] == "final_answer"



def test_rag_search_returns_context(monkeypatch):
    def fake_retrieve_context(query: str) -> str:
        return "Fake RAG context"

    monkeypatch.setattr("ai_service.app.retrieve_context", fake_retrieve_context)

    response = client.get("/rag/search", params={
        "query": "What is RAG?"
    })

    assert response.status_code == 200
    assert response.json() == {
        "query": "What is RAG?",
        "context": "Fake RAG context"
    }


def test_rag_search_returns_empty_context(monkeypatch):
    def fake_retrieve_context(query: str) -> str:
        return ""

    monkeypatch.setattr("ai_service.app.retrieve_context", fake_retrieve_context)

    response = client.get("/rag/search", params={
        "query": "Unknown question"
    })

    assert response.status_code == 200
    assert response.json() == {
        "query": "Unknown question",
        "context": ""
    }


def test_rerank_documents_sorts_by_llm_score(monkeypatch):
    scores = {
        "chunk low": "2",
        "chunk high": "9",
        "chunk mid": "5",
    }

    def fake_invoke_openai(prompt: str) -> str:
        for chunk, score in scores.items():
            if chunk in prompt:
                return score

        return "0"

    monkeypatch.setattr("ai_service.rag.reranker_service.invoke_openai", fake_invoke_openai)

    results = [
        ("chunk low", 0.1),
        ("chunk high", 0.9),
        ("chunk mid", 0.5),
    ]

    reranked = rerank_documents("test query", results, top_k=2)

    assert reranked == [
        ("chunk high", 0.9),
        ("chunk mid", 0.5),
    ]


def test_rerank_documents_handles_invalid_score(monkeypatch):
    def fake_invoke_openai(prompt: str) -> str:
        return "not a number"

    monkeypatch.setattr("ai_service.rag.reranker_service.invoke_openai", fake_invoke_openai)

    results = [
        ("chunk one", 0.1),
    ]

    reranked = rerank_documents("test query", results, top_k=1)

    assert reranked == [
        ("chunk one", 0.1),
    ]
