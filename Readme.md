# Intelligent Exam Question Analysis — Agentic AI System

An AI-driven educational analytics system that analyzes exam questions and student responses,
identifies learning gaps, retrieves evidence-based pedagogical best practices via RAG,
and generates structured, actionable assessment improvement recommendations.

## Architecture

```
FastAPI (/analyze, /chat)
    └── LangGraph ReAct Agent
            ├── AnalysisTool   → wraps existing ML + stats analytics
            ├── RAGTool        → ChromaDB vector search (Gemini embeddings)
            └── RecommendTool  → Gemini structured output (Pydantic schema)
```

## Setup

### 1. Clone and install dependencies

```bash
cd exam-ai
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set:

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | **Yes** | Gemini API key from [Google AI Studio](https://aistudio.google.com/) |
| `CHROMA_PERSIST_DIR` | No | Local ChromaDB storage path (default: `./chroma_db`) |
| `PASS_MARKS_THRESHOLD` | No | Minimum marks to count as a pass (default: `2`) |
| `TOP_N_STUDENTS` | No | Number of top/bottom students to report (default: `5`) |
| `LLM_MODEL` | No | Gemini model name (default: `gemini-2.0-flash`) |
| `EMBEDDING_MODEL` | No | Gemini embedding model (default: `models/embedding-001`) |
| `RAG_TOP_K` | No | Number of RAG passages to retrieve (default: `4`) |

### 3. Start the server

```bash
uvicorn api.main:app --reload --port 8000
```

On first startup the RAG knowledge base is seeded automatically from `agent/rag/docs/`.

## API Endpoints

### `POST /analyze`
Upload a CSV file and receive a full AI-powered assessment report.

**CSV format:** columns `question`, `student_id`, `marks` are required.

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@student_responses.csv"
```

**Response JSON:**
```json
{
  "status": "success",
  "analysis": {
    "per_question_stats": { "Q1": { "avg_score": 1.8, "pass_rate": 0.6, ... } },
    "exam_summary": { "total_questions": 10, "excellent_questions": 3, ... },
    "weak_questions": ["Q3", "Q7"],
    "teacher_report": "..."
  },
  "recommendations": {
    "overall_verdict": "...",
    "key_learning_gaps": ["Q3", "Q7"],
    "per_question_recommendations": [
      { "question_id": "Q3", "issue": "...", "recommendation": "...", "priority": "High", ... }
    ],
    "immediate_actions": ["...", "...", "..."],
    "long_term_suggestions": ["...", "..."]
  }
}
```

### `POST /chat`
Ask ExamAI anything about assessment design. Streams response tokens.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I improve a question with a low discrimination index?"}'
```

### `GET /docs`
Interactive Swagger UI with full API documentation.

## Project Structure

```
exam-ai/
├── api/
│   ├── main.py              # FastAPI app, lifespan, CORS
│   ├── schemas.py           # Pydantic v2 request/response models
│   └── routes/
│       ├── analyze.py       # POST /analyze
│       └── chat.py          # POST /chat (streaming)
├── agent/
│   ├── assessment_agent.py  # LangGraph StateGraph agent
│   ├── prompts.py           # System & node prompts
│   ├── rag/
│   │   ├── knowledge_base.py  # ChromaDB seeding (idempotent)
│   │   ├── retriever.py       # Vector similarity retrieval
│   │   └── docs/              # Pedagogical knowledge documents
│   └── tools/
│       ├── analysis_tool.py       # Wraps analytics module
│       ├── rag_tool.py            # Wraps retriever
│       └── recommendation_tool.py # Structured LLM output
├── analytics/
│   └── performance_analysis.py  # Statistical exam analysis (ML + stats)
├── models/
│   ├── difficulty_model.pkl
│   └── vectorizer.pkl
├── config.py                # Settings loader (python-dotenv)
├── .env.example             # Environment variable template
└── requirements.txt
```