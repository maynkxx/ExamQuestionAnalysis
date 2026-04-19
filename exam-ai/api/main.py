from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(BASE_DIR, "web")
if os.path.isdir(WEB_DIR):
    app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")

@app.get("/", tags=["Health"])
async def root():
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"service": "ExamAI", "version": "2.0.0", "status": "running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
