# AI Service Starter

A FastAPI-based starter project for learning how to build an **AI Student Study Tracker** for one configured student.

The demo app answers study questions for one demo student, `STU-101`, by combining:

```text
AI Service
  -> Prompting
  -> Memory
  -> RAG over study notes and teacher remarks
  -> Agent orchestration
  -> MCP tools for structured student data
```

## Main Use Case

The end user only needs one main endpoint:

```text
POST /chat
```

Example user question:

```text
What should I revise this weekend based on last week's lessons, upcoming exams, and recent scores?
```

Backend flow:

```text
1. /chat receives the student question.
2. The AI service loads conversation memory.
3. The agent searches local RAG notes and teacher remarks.
4. The agent calls MCP tools for the configured student's structured data.
5. The MCP server talks to a separate single-student data service.
6. The model generates a final study-focused answer.
7. The service returns the answer, citations, and tool trace.
```

## Why This Starter Project Works

This use case gives each AI concept a clear job:

- **AI service**: exposes the user-facing API and owns model orchestration.
- **Prompting**: controls answer style, study-plan format, and explanation level.
- **Memory**: supports follow-up questions through `conversation_id`.
- **RAG**: retrieves class notes, weekly lesson summaries, teacher remarks, and revision notes.
- **Reranking**: improves which retrieved study notes are used as context.
- **Agent**: decides whether the question needs RAG, structured student data, or both.
- **MCP**: gives the agent a standard interface to a separate student data service.
- **Student data service**: represents structured school data for the configured student, such as courses, teachers, exams, and scores.

## Architecture

```text
Client / UI / Postman
  |
  v
FastAPI AI Service
  |
  v
Agent Orchestrator
  |
  |-- Memory
  |
  |-- Local RAG
  |     |-- documents/weekly_lessons.md
  |     |-- documents/teacher_remarks.md
  |     |-- documents/revision_plan.md
  |     |-- embeddings
  |     |-- FAISS vector search
  |     |-- reranker
  |
  |-- MCP Client
        |
        v
      Student MCP Server
        |
        v
      Single-Student Data Service
        |-- configured student profile
        |-- current courses
        |-- teacher details
        |-- upcoming exams
        |-- recent scores
```

## User Scenarios

### 1. Ask What Was Taught

User:

```text
What was taught last week?
```

System:

```text
/chat -> local RAG weekly notes -> model summary with citations
```

Concepts shown:

- document loading
- embeddings
- vector search
- reranking
- citations
- summarization prompt

### 2. Ask For Exam Dates

User:

```text
When is my next exam?
```

System:

```text
/chat -> agent -> MCP get_upcoming_exams() -> final answer
```

Concepts shown:

- agent tool choice
- MCP tool call
- separate backend service
- structured tool result

### 3. Ask For Recent Scores

User:

```text
What was my score in the last class test?
```

System:

```text
/chat -> agent -> MCP get_recent_scores() -> final answer
```

Concepts shown:

- MCP for structured data
- model formatting over factual records
- low-RAG path when docs are not needed

### 4. Combine Notes + Exams + Scores

User:

```text
What should I revise this weekend based on last week's lessons, upcoming exams, and recent scores?
```

System:

```text
/chat
  -> local RAG for weekly notes and teacher remarks
  -> MCP get_student_courses()
  -> MCP get_upcoming_exams()
  -> MCP get_recent_scores()
  -> final personalized study plan
```

Concepts shown:

- RAG + MCP together
- agent orchestration
- personalized answer
- tool trace
- structured output

### 5. Follow-Up With Memory

User:

```text
Can you make that revision plan shorter?
```

System:

```text
/chat -> memory -> final answer
```

Concepts shown:

- conversation memory
- stateful behavior over stateless HTTP

## API Roles

### User-Facing

```text
POST /chat
```

This should be the main endpoint for real users.

### Demo / Debug

```text
GET /rag/search
POST /agent/run
GET /chat/{conversation_id}/history
```

These are useful for learning and demos:

- `/rag/search` shows what local RAG retrieved.
- `/agent/run` shows agent steps and tool trace directly.
- `/chat/{conversation_id}/history` shows memory.

## MCP Tools

The MCP server should not duplicate every FastAPI endpoint.

For this starter project, MCP exposes structured data tools for the configured student:

```text
get_student_profile()
get_student_courses()
get_upcoming_exams()
get_recent_scores()
```

Optional later tools:

```text
get_assignments()
get_attendance()
```

The agent calls these MCP tools when the user asks for course, teacher, exam, score, or revision-planning data. The normal flow does not require a `student_id` parameter because the starter project is scoped to one configured student.

## Student Data Service

The separate student data service is small and uses fake data for one configured student.

Example endpoints:

```text
GET /student
GET /student/courses
GET /student/exams
GET /student/scores
```

Example data:

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

## Updating Student Data

There is no user creation flow in this starter project. The app assumes one configured student.

Structured student data is stored in:

```text
student_service/student_data.py
```

Update these objects when you want to change the demo student:

```text
STUDENT_PROFILE   -> student id, name, grade, school, academic year
STUDENT_COURSES   -> subjects, teachers, current chapters, schedules
UPCOMING_EXAMS    -> exam dates, topics, exam types
RECENT_SCORES     -> assessment scores and short teacher remarks
```

After changing structured data, restart the student service:

```bash
docker compose restart student-service
```

Longer unstructured study details belong in RAG documents:

```text
documents/weekly_lessons.md
documents/teacher_remarks.md
documents/revision_plan.md
```

Use structured data for facts the agent should retrieve through MCP, such as exam dates and scores. Use RAG documents for notes, explanations, lesson summaries, and longer teacher feedback.

If you change RAG documents, restart the AI service with indexing enabled:

```bash
AUTO_INDEX_ON_STARTUP=true docker compose up --build ai-service
```

## AI Concepts To Showcase

- AI service wrapper
- Prompt templates
- Prompt modes
- Prompt versioning
- Conversation memory
- Document ingestion
- Embeddings
- Vector search
- RAG
- Citations
- Reranking
- Retrieval quality signals
- Agent tool choice
- Tool trace
- MCP tool calls
- Structured tool outputs
- Personalized summarization
- Error handling and fallback
- Tests with mocked model/tool calls

## Current Implementation Status

Already present in the project:

- FastAPI service
- `/chat` as the user-facing agent endpoint
- `/rag/search`
- `/agent/run`
- prompt modes
- conversation memory
- OpenAI wrapper
- RAG with FAISS over Markdown, text, and Excel files
- reranking
- MCP server with student data tools
- MCP client abstraction inside the AI service
- separate single-student data service
- sample study tracker RAG documents
- agent tool trace with MCP results
- tests

Good next improvements:

- Add answerability/confidence metadata.
- Add persistent storage for memory and student records.
- Replace the in-process MCP adapter with a real MCP transport client.
- Improve `/rag/search` with citations and rerank details.

## Setup

Clone the repository:

```bash
git clone https://github.com/manoranjan2015/ai-service-starter.git
cd ai-service-starter
```

Create your environment file:

```bash
cp .env.example .env
```

Update `.env` with your real `OPENAI_API_KEY`.

### Option 1: Run With Docker

This is the recommended path for a fresh checkout because it starts all services together.

```bash
docker compose up --build
```

Open:

```text
AI service       http://127.0.0.1:8000/docs
Student service  http://127.0.0.1:8001/docs
```

Try the main chat API:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "demo",
    "message": "What should I revise this weekend based on last week lessons, upcoming exams, and recent scores?",
    "mode": "detailed"
  }'
```

Stop services:

```bash
docker compose down
```

### Option 2: Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the student service in one terminal:

```bash
source .venv/bin/activate
uvicorn student_service.student_data_server:app --reload --port 8001
```

Start the AI service in another terminal:

```bash
source .venv/bin/activate
uvicorn ai_service.app:app --reload --port 8000
```

Open the AI service:

```text
http://127.0.0.1:8000/docs
```

The MCP server can also be started separately for MCP demonstrations:

```bash
pip install -r requirements-mcp.txt
python -m mcp_service.mcp_server
```

## Explore The Project

Use these checks after starting the services with Docker or local commands.

### 1. Check Services

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8001/health
```

Expected result: both services return `status: ok`.

### 2. Inspect Student Data

```bash
curl http://127.0.0.1:8001/student
curl http://127.0.0.1:8001/student/courses
curl http://127.0.0.1:8001/student/exams
curl http://127.0.0.1:8001/student/scores
```

This shows the structured data that MCP tools expose to the agent.

### 3. Ask Student Questions Through `/chat`

Exam query:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"demo-exam","message":"When is my next exam?","mode":"simple"}'
```

Score query:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"demo-score","message":"What was my score in the last class test?","mode":"simple"}'
```

RAG query:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"demo-rag","message":"What was taught last week?","mode":"detailed"}'
```

Combined RAG + MCP query:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"demo-plan","message":"What should I revise this weekend based on last week lessons, upcoming exams, and recent scores?","mode":"detailed"}'
```

Follow-up memory query:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"demo-plan","message":"Make that revision plan shorter.","mode":"summary"}'
```

In the response, inspect:

```text
answer       -> final model answer
citations    -> RAG document chunks used
steps        -> agent trace
mcp_results  -> structured data returned through MCP tools
```

### 4. Inspect Agent Trace Directly

```bash
curl -X POST http://127.0.0.1:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"debug-1","task":"What should I revise this weekend?","mode":"research"}'
```

Look for trace steps such as `retrieve_context`, `choose_mcp_tools`, `call_mcp_tool`, and `final_answer`.

### 5. Inspect RAG Retrieval

```bash
curl "http://127.0.0.1:8000/rag/search?query=linear%20equations"
```

This shows what the local RAG layer retrieves from files in `documents/`.

## Service Layout

```text
ai_service/
  app.py          Main AI API entrypoint
  agent/          Agent orchestration, tool choice, prompt modes, external fallback
  rag/            Document loading, embeddings, vector store, retrieval, reranking
  memory/         Conversation history
  llm/            OpenAI model calls
student_service/  Separate single-student backend service with course/exam/score data
mcp_service/      MCP server and tools that the agent will use to reach external systems
documents/        RAG source documents
```

Run only one Docker service:

```bash
docker compose up --build ai-service
docker compose up --build student-service
docker compose up --build mcp-service
```

The Compose file reads `OPENAI_API_KEY` and model settings from your shell or `.env`.

## Test

```bash
.venv/bin/python -m pytest
```

## Recommended Next Build Order

Implemented:

- Single-student data service.
- MCP student tools.
- AI-service MCP client abstraction.
- Agent uses RAG plus MCP student tools.
- `/chat` calls the agent internally.
- Study tracker RAG documents.

Next useful improvements:

1. Add answerability/confidence metadata.
2. Add a real MCP transport client instead of the current in-process adapter.
3. Add persistent storage for memory and student data.
