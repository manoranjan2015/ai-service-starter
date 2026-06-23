import json
from typing import Dict, List, Optional

from ai_service.config import PROMPT_VERSION
from ai_service.memory.conversation_store import add_message, get_conversation
from ai_service.agent.external_knowledge import external_knowledge_search
from ai_service.agent.mcp_client import call_mcp_tool
from ai_service.llm.openai_service import invoke_openai
from ai_service.agent.prompts import build_agent_prompt, validate_agent_mode
from ai_service.rag.retrieval_service import retrieve_context_with_citations


RAG_KEYWORDS = (
    "document",
    "source",
    "citation",
    "context",
    "rag",
    "retrieval",
    "policy",
    "uploaded",
    "excel",
    "file",
    "knowledge base",
)


MCP_TOOL_KEYWORDS = {
    "get_student_courses": (
        "course",
        "courses",
        "subject",
        "subjects",
        "teacher",
        "chapter",
        "schedule",
        "taught",
        "lesson",
    ),
    "get_upcoming_exams": (
        "exam",
        "exams",
        "test",
        "tests",
        "date",
        "upcoming",
        "when",
    ),
    "get_recent_scores": (
        "score",
        "scores",
        "marks",
        "mark",
        "result",
        "grade",
        "assessment",
        "performance",
    ),
}


def should_use_rag(task: str) -> bool:
    normalized_task = task.lower()
    return any(keyword in normalized_task for keyword in RAG_KEYWORDS)


def choose_student_mcp_tools(task: str) -> List[str]:
    normalized_task = task.lower()
    selected_tools = ["get_student_profile"]

    for tool_name, keywords in MCP_TOOL_KEYWORDS.items():
        if any(keyword in normalized_task for keyword in keywords):
            selected_tools.append(tool_name)

    if any(keyword in normalized_task for keyword in ("revise", "revision", "study plan", "weekend")):
        selected_tools.extend([
            "get_student_courses",
            "get_upcoming_exams",
            "get_recent_scores",
        ])

    deduped_tools = []
    for tool_name in selected_tools:
        if tool_name not in deduped_tools:
            deduped_tools.append(tool_name)

    return deduped_tools


def run_agent(
    conversation_id: str,
    task: str,
    use_rag: Optional[bool] = None,
    use_external: Optional[bool] = None,
    mode: str = "research"
) -> Dict:
    validate_agent_mode(mode)
    history = get_conversation(conversation_id)
    steps: List[Dict[str, str]] = []
    context = ""
    citations = []
    external_context = ""
    external_results = []
    student_context = ""
    mcp_results = []
    selected_use_rag = True if use_rag is None else use_rag

    steps.append({
        "step": "load_memory",
        "tool": "conversation_store.get_conversation",
        "input": conversation_id,
        "output": f"Loaded {len(history)} previous messages.",
    })

    steps.append({
        "step": "choose_tools",
        "tool": "agent_service.should_use_rag",
        "input": f"task={task}; use_rag={use_rag}; use_external={use_external}",
        "output": f"RAG selected: {selected_use_rag}.",
    })

    if selected_use_rag:
        retrieval_data = retrieve_context_with_citations(task)
        context = retrieval_data["context"]
        citations = retrieval_data["citations"]
        steps.append({
            "step": "retrieve_context",
            "tool": "retrieval_service.retrieve_context_with_citations",
            "input": task,
            "output": f"Retrieved {len(citations)} citation chunks.",
        })
    else:
        steps.append({
            "step": "skip_rag",
            "tool": "rag_disabled",
            "input": task,
            "output": "RAG was disabled for this agent run.",
        })

    selected_mcp_tools = choose_student_mcp_tools(task)
    steps.append({
        "step": "choose_mcp_tools",
        "tool": "agent_service.choose_student_mcp_tools",
        "input": task,
        "output": f"Selected MCP tools: {', '.join(selected_mcp_tools)}.",
    })

    for tool_name in selected_mcp_tools:
        tool_result = call_mcp_tool(tool_name)
        mcp_results.append({
            "tool": tool_name,
            "result": tool_result,
        })
        steps.append({
            "step": "call_mcp_tool",
            "tool": tool_name,
            "input": "configured_student",
            "output": json.dumps(tool_result, default=str),
        })

    if mcp_results:
        student_context = json.dumps(mcp_results, indent=2, default=str)

    selected_use_external = (
        ((not selected_use_rag or len(citations) == 0) and len(mcp_results) == 0)
        if use_external is None
        else use_external
    )

    steps.append({
        "step": "choose_external_tool",
        "tool": "agent_service.external_fallback_policy",
        "input": f"citations={len(citations)}; mcp_results={len(mcp_results)}; use_external={use_external}",
        "output": f"External MCP-style tool selected: {selected_use_external}.",
    })

    if selected_use_external:
        external_data = external_knowledge_search(task)
        external_results = external_data["results"]
        external_context = "\n\n".join(
            f"{item['title']}: {item['content']} ({item['url']})"
            for item in external_results
        )
        steps.append({
            "step": "external_knowledge_search",
            "tool": "external_knowledge_service.external_knowledge_search",
            "input": task,
            "output": f"Retrieved {len(external_results)} external results.",
        })
    else:
        steps.append({
            "step": "skip_external_tool",
            "tool": "external_tool_disabled",
            "input": task,
            "output": "External MCP-style tool was not needed for this agent run.",
        })

    tool_trace = "\n".join(
        f"{step['step']} via {step['tool']} with input [{step['input']}]: {step['output']}"
        for step in steps
    )
    prompt = build_agent_prompt(
        task,
        mode,
        history,
        context,
        student_context,
        external_context,
        tool_trace,
    )
    answer = invoke_openai(prompt)

    add_message(conversation_id, "user", task)
    add_message(conversation_id, "assistant", answer)

    steps.append({
        "step": "final_answer",
        "tool": "openai_service.invoke_openai",
        "input": f"mode={mode}; prompt_version={PROMPT_VERSION}",
        "output": "Generated the final answer from memory, tool results, and prompt instructions.",
    })

    return {
        "conversation_id": conversation_id,
        "task": task,
        "mode": mode,
        "used_rag": selected_use_rag,
        "used_mcp": len(mcp_results) > 0,
        "used_external": selected_use_external,
        "answer": answer,
        "steps": steps,
        "prompt_version": PROMPT_VERSION,
        "citations": citations,
        "mcp_results": mcp_results,
        "external_results": external_results,
    }
