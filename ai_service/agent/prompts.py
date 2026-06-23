from typing import Dict, List, Optional
from fastapi import HTTPException
from langchain_core.prompts import ChatPromptTemplate

PROMPT_MODES = {
    "simple": "Explain in simple and clear language.",
    "detailed": "Give a detailed explanation with useful context and examples.",
    "interview": "Explain this in a way that helps the user answer in an interview.",
    "summary": "Give a short summary with only the most important points.",
}

AGENT_MODES = {
    "quick": "Give a direct answer with only the essential details.",
    "research": "Use available tool results carefully and explain the answer with useful context.",
    "interview": "Shape the answer as interview-ready talking points.",
    "summary": "Return a concise summary with the most important points.",
}

def validate_mode(mode: str) -> None:
    if mode not in PROMPT_MODES:
        supported_modes = ", ".join(PROMPT_MODES.keys())
        raise HTTPException(
            status_code=400,
            detail=f"unsupported mode '{mode}'. Supported modes: {supported_modes}",
        )

def validate_agent_mode(mode: str) -> None:
    if mode not in AGENT_MODES:
        supported_modes = ", ".join(AGENT_MODES.keys())
        raise HTTPException(
            status_code=400,
            detail=f"unsupported agent mode '{mode}'. Supported modes: {supported_modes}",
        )

def build_prompt(
        user_message: str,
        mode: str = "simple",
        history: Optional[List[Dict[str, str]]] = None,
        context: str = ""
) -> str:
    
    validate_mode(mode)
    mode_instruction = PROMPT_MODES[mode]
    
    history = history or []
    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history
    )
    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a helpful AI assistant.
Be clear and concise.
Use simple words.
If you are not sure, say you are not sure.
Do not make up facts.

Response style:
{mode_instruction}
"""
        ),
        ("human", """
Relevant context:
{context}

Conversation history:
{history_text}

Current user question:
{user_message}
"""),
    ])

    prompt_value = prompt_template.invoke({
        "user_message": user_message,
        "mode_instruction": mode_instruction,
        "history_text": history_text,
        "context": context

    })

    return prompt_value.to_string()

def build_agent_prompt(
        task: str,
        mode: str = "research",
        history: Optional[List[Dict[str, str]]] = None,
        context: str = "",
        student_context: str = "",
        external_context: str = "",
        tool_trace: str = ""
) -> str:
    validate_agent_mode(mode)
    mode_instruction = AGENT_MODES[mode]
    history = history or []
    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history
    )

    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are an AI agent inside an API service.
Use the provided tool results and conversation memory to complete the task.
Be clear about the final answer.
Do not invent facts that are not supported by the tool results or context.

Agent response style:
{mode_instruction}
"""
        ),
        ("human", """
Task:
{task}

Conversation memory:
{history_text}

Retrieved context:
{context}

Structured student data from MCP:
{student_context}

External context:
{external_context}

Tool trace:
{tool_trace}

Final answer:
"""),
    ])

    prompt_value = prompt_template.invoke({
        "task": task,
        "mode_instruction": mode_instruction,
        "history_text": history_text,
        "context": context,
        "student_context": student_context,
        "external_context": external_context,
        "tool_trace": tool_trace,
    })

    return prompt_value.to_string()
