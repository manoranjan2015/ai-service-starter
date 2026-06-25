# High-Level Design: AI Student Study Tracker

## 1. Purpose

AI Student Study Tracker is the demo application for this starter project. It is intentionally scoped to one configured student, `STU-101`, rather than a full multi-student school platform.

The goal is to show how an AI service evolves from a simple model API into a practical backend that uses:

- prompt templates
- conversation memory
- RAG over study notes and teacher remarks
- reranking
- agent orchestration
- MCP tools
- a separate student data service

The end-user experience should stay simple:

```text
User -> POST /chat -> answer
```

The complexity stays inside the backend.

## 2. Main User Scenario

Primary scenario:

```text
What should I revise this weekend based on last week's lessons, upcoming exams, and recent scores?
```

System behavior:

```text
1. Receive the question through /chat.
2. Load memory for the conversation.
3. Search local study notes and teacher remarks through RAG.
4. Call MCP tools for the configured student's courses, exams, and recent scores.
5. Build a prompt with memory, RAG context, and MCP tool results.
6. Call the model.
7. Return a personalized study plan with citations and tool trace.
```

## 3. Concept Mapping

| Concept | Role In This Project |
| --- | --- |
| AI service | User-facing FastAPI API and model orchestration |
| Prompting | Controls response style, explanation depth, and study-plan format |
| Memory | Supports follow-up questions by `conversation_id` |
| RAG | Retrieves weekly notes, teacher remarks, and revision docs |
| Reranking | Improves selected context from retrieved candidates |
| Agent | Decides what data is needed for the student question |
| MCP | Standard interface for structured student-data tools |
| Student data service | Separate server that simulates structured records for one configured student |

## 4. Architecture

```text
Client
  |
  v
FastAPI AI Service
  |
  v
Agent Orchestrator
  |
  |-- Memory Store
  |
  |-- Local RAG
  |     |-- Weekly notes
  |     |-- Teacher remarks
  |     |-- Revision notes
  |     |-- Embeddings
  |     |-- FAISS vector store
  |     |-- Reranker
  |
  |-- MCP Client
        |
        v
      Student MCP Server
        |
        v
      Single-Student Data Service
```

## 5. API Roles

### 5.1 User-Facing API

`POST /chat`

The primary product endpoint. The user should not need to know whether the backend used plain chat, RAG, an agent, or MCP tools.

Request:

```json
{
  "conversation_id": "demo",
  "message": "What should I revise this weekend?",
  "mode": "detailed"
}
```

Response:

```json
{
  "conversation_id": "demo",
  "answer": "...",
  "prompt_version": "v1",
  "citations": [],
  "steps": [],
  "mcp_results": []
}
```

### 5.2 Demo And Debug APIs

`GET /rag/search`

Shows what local RAG retrieved.

`POST /agent/run`

Shows agent decisions, tool calls, and trace directly. This is useful for learning, but should not be treated as the normal end-user API.

`GET /chat/{conversation_id}/history`

Shows short-term memory for a conversation.

## 6. RAG Design

Documents:

```text
documents/weekly_lessons.md
documents/teacher_remarks.md
documents/revision_plan.md
documents/source.xls
```

RAG flow:

```text
document -> chunks -> embeddings -> vector search -> rerank -> selected context
```

RAG should provide:

- retrieved context
- citations
- retrieval scores
- rerank scores
- answerability signal

## 7. Agent Design

The agent is an internal orchestrator.

Agent flow:

```text
load memory
search local RAG
decide which structured data is needed for the configured student
call MCP tools if needed
build final prompt
call model
save memory
return answer and trace
```

Agent tools:

- memory read/write
- local RAG search
- MCP `get_student_profile`
- MCP `get_student_courses`
- MCP `get_upcoming_exams`
- MCP `get_recent_scores`
- model call

The agent trace should include:

```json
{
  "step": "call_mcp_tool",
  "tool": "get_recent_scores",
  "input": "configured_student",
  "output": "Mathematics Class Test 3: 72/100"
}
```

## 8. MCP Design

MCP should run as a separate server.

It should not duplicate the whole FastAPI API. Its job is to expose structured data tools for the configured student.

MCP tools:

```text
get_student_profile()
get_student_courses()
get_upcoming_exams()
get_recent_scores()
```

The AI service agent calls these through an MCP client abstraction.

Flow:

```text
Agent
  -> MCP Client
  -> MCP Server
  -> Single-Student Data Service
```

## 9. Student Data Service

The student data service is a separate simple service with fake structured school data for one configured student.

Endpoints:

```text
GET /student
GET /student/courses
GET /student/exams
GET /student/scores
```

Example response:

```json
{
  "student_id": "STU-101",
  "name": "Aarav Sharma",
  "grade": "8",
  "courses": [
    {
      "subject": "Mathematics",
      "teacher": "Ms. Rao",
      "current_chapter": "Linear Equations"
    }
  ],
  "upcoming_exams": [
    {
      "subject": "Mathematics",
      "date": "2026-06-28",
      "topic": "Linear Equations"
    }
  ],
  "recent_scores": [
    {
      "subject": "Mathematics",
      "assessment": "Class Test 3",
      "score": 72,
      "max_score": 100
    }
  ]
}
```

This server keeps the MCP demonstration realistic without requiring a real school information system or a multi-student database.

### 9.1 Updating The Configured Student

There is no user creation or student onboarding flow in this starter project. The service is intentionally configured for one student.

Structured student records are stored in:

```text
student_service/data/student.json
```

The data is grouped by purpose:

```text
profile          -> identity and school metadata
courses          -> subjects, teachers, current chapters, schedules
upcoming_exams   -> exam dates, topics, exam types
recent_scores    -> scores, max scores, short remarks
```

These records are exposed by the student service and reached by the agent through MCP tools.

Longer learning material belongs in RAG documents under:

```text
documents/
```

Use the student service for structured facts. Use RAG documents for lesson notes, longer teacher remarks, revision guidance, and explanatory content.

## 10. AI Service Concepts To Demonstrate

The starter project should demonstrate:

- prompt modes
- prompt versioning
- short-term memory
- local document ingestion
- embeddings
- vector search
- RAG citations
- reranking
- answerability or confidence signal
- agent tool choice
- MCP tool calls
- tool trace
- structured response fields
- personalized study guidance
- mocked tests for model and tool calls
- graceful fallback when RAG or MCP has no data

## 11. Current Implementation

The code implements the core starter-project flow:

- `/chat` is the user-facing endpoint and calls the agent internally.
- `/agent/run` remains available as a demo/debug endpoint with trace details.
- The agent loads memory, searches RAG, selects MCP student tools, builds a final prompt, calls the model, and saves memory.
- The MCP server exposes student data tools.
- The MCP tools call the separate single-student data service.
- RAG can load Markdown, text, and Excel documents from `documents/`.
- Responses include citations, agent steps, and MCP results.

## 12. Non-Goals

- No frontend UI for now.
- No real school information system.
- No authentication yet.
- No persistent database yet.
- No broad internet or shell access through MCP.
- No raw `curl` tool through MCP.

## 13. Recommended Build Order

Implemented:

1. Documentation alignment.
2. Sample study tracker data.
3. Single-student data service.
4. MCP server tools for student data.
5. MCP client abstraction.
6. Agent uses MCP tools.
7. `/chat` uses agent internally.

Recommended next improvements:

1. RAG inspection improvements.
2. Structured answerability/confidence signal.
3. Real MCP transport client instead of the current in-process adapter.
4. Persistent memory and student data storage.
