import json
from typing import AsyncGenerator, TypedDict, Annotated
import operator

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END

from config import settings
from agent.prompts import SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT
from agent.tools.analysis_tool import run_analysis_tool
from agent.tools.rag_tool import rag_retrieval_tool
from agent.tools.recommendation_tool import generate_recommendations_tool


class AgentState(TypedDict):
    csv_content: str
    analysis_result: str
    pedagogy_context: str
    final_report: dict
    error: str


def _get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )


def _analyze_node(state: AgentState) -> AgentState:
    csv_content = state.get("csv_content", "")
    if not csv_content.strip():
        return {**state, "analysis_result": json.dumps({"error": "No CSV content provided", "status": "invalid_data"})}

    result = run_analysis_tool.invoke({"csv_content": csv_content})
    return {**state, "analysis_result": result}


def _rag_node(state: AgentState) -> AgentState:
    analysis_str = state.get("analysis_result", "{}")
    try:
        analysis = json.loads(analysis_str)
    except json.JSONDecodeError:
        analysis = {}

    if "error" in analysis:
        return {**state, "pedagogy_context": "Analysis failed; no context retrieved."}

    summary = analysis.get("exam_summary", {})
    weak = analysis.get("weak_questions", [])

    query_parts = ["assessment design best practices for exam quality improvement"]
    if summary.get("too_easy", 0) > 0:
        query_parts.append("questions that are too easy Bloom taxonomy improvement")
    if summary.get("too_hard", 0) > 0:
        query_parts.append("questions too hard difficulty reduction strategies")
    if summary.get("confusing", 0) > 0:
        query_parts.append("poor discrimination index confusing questions remediation")
    if weak:
        query_parts.append("learning gap identification and remediation strategies")

    query = ". ".join(query_parts)
    context = rag_retrieval_tool.invoke({"query": query})
    return {**state, "pedagogy_context": context}


def _recommend_node(state: AgentState) -> AgentState:
    analysis_str = state.get("analysis_result", "{}")
    pedagogy_context = state.get("pedagogy_context", "")

    result_str = generate_recommendations_tool.invoke(
        {"analysis_json": analysis_str, "pedagogy_context": pedagogy_context}
    )

    try:
        recommendations = json.loads(result_str)
    except json.JSONDecodeError:
        recommendations = {"error": "Failed to parse recommendation output"}

    try:
        analysis = json.loads(analysis_str)
    except json.JSONDecodeError:
        analysis = {}

    final_report = {
        "analysis": analysis,
        "recommendations": recommendations,
    }
    return {**state, "final_report": final_report}


def _should_continue(state: AgentState) -> str:
    analysis_str = state.get("analysis_result", "{}")
    try:
        analysis = json.loads(analysis_str)
        if analysis.get("status") in ("invalid_data", "error"):
            return "recommend"
    except json.JSONDecodeError:
        pass
    return "rag"


def _build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("analyze", _analyze_node)
    graph.add_node("rag", _rag_node)
    graph.add_node("recommend", _recommend_node)

    graph.set_entry_point("analyze")
    graph.add_conditional_edges("analyze", _should_continue, {"rag": "rag", "recommend": "recommend"})
    graph.add_edge("rag", "recommend")
    graph.add_edge("recommend", END)

    return graph.compile()


_graph = _build_graph()


def run_agent(csv_content: str) -> dict:
    initial_state: AgentState = {
        "csv_content": csv_content,
        "analysis_result": "",
        "pedagogy_context": "",
        "final_report": {},
        "error": "",
    }
    final_state = _graph.invoke(initial_state)
    return final_state.get("final_report", {"error": "Agent produced no output"})


async def stream_agent(query: str, context: str = "") -> AsyncGenerator[str, None]:
    llm = _get_llm()

    rag_context = rag_retrieval_tool.invoke({"query": query})

    messages = [
        SystemMessage(content=CHAT_SYSTEM_PROMPT),
    ]

    if context:
        messages.append(
            HumanMessage(
                content=f"Additional context from the user:\n{context}\n\nRelevant knowledge base passages:\n{rag_context}\n\nUser question: {query}"
            )
        )
    else:
        messages.append(
            HumanMessage(
                content=f"Relevant knowledge base passages:\n{rag_context}\n\nUser question: {query}"
            )
        )

    async for chunk in llm.astream(messages):
        token = chunk.content
        if token:
            yield token
