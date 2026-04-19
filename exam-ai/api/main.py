from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.analyze import router as analyze_router
from api.routes.chat import router as chat_router
from agent.rag.knowledge_base import seed_knowledge_base


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Seeding RAG knowledge base...")
    try:
        seed_knowledge_base()
    except Exception as exc:
        print(f"[Startup] RAG seeding failed (non-fatal): {exc}")
    yield
    print("[Shutdown] ExamAI server stopped.")


app = FastAPI(
    title="ExamAI — Agentic Assessment Analyzer",
    description=(
        "An agentic AI system that analyzes exam question difficulty distributions, "
        "identifies learning gaps, retrieves pedagogical best practices via RAG, "
        "and generates structured assessment improvement recommendations."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, tags=["Analysis"])
app.include_router(chat_router, tags=["Chat"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "ExamAI",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "POST /analyze — upload a CSV, get full AI-powered assessment report",
            "chat": "POST /chat — ask anything about assessment design (streaming)",
            "docs": "GET /docs — interactive API documentation",
        },
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
