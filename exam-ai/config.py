from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class Settings:
    google_api_key: str
    chroma_persist_dir: str
    pass_marks_threshold: int
    top_n_students: int
    llm_model: str
    embedding_model: str
    rag_docs_dir: str
    rag_collection_name: str
    rag_top_k: int


def load_settings() -> Settings:
    key = os.getenv("GOOGLE_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "GOOGLE_API_KEY is not set. Please copy .env.example to .env and fill in your key."
        )
    return Settings(
        google_api_key=key,
        chroma_persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"),
        pass_marks_threshold=int(os.getenv("PASS_MARKS_THRESHOLD", "2")),
        top_n_students=int(os.getenv("TOP_N_STUDENTS", "5")),
        llm_model=os.getenv("LLM_MODEL", "gemini-2.0-flash"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "models/embedding-001"),
        rag_docs_dir=os.getenv("RAG_DOCS_DIR", "./agent/rag/docs"),
        rag_collection_name=os.getenv("RAG_COLLECTION_NAME", "pedagogy_knowledge_base"),
        rag_top_k=int(os.getenv("RAG_TOP_K", "4")),
    )


settings = load_settings()
