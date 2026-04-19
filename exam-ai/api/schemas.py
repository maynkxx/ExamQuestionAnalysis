from pydantic import BaseModel, Field
from typing import Optional


class QuestionStats(BaseModel):
    avg_score: float
    pass_rate: float
    discrimination_index: float
    quality: str
    ml_difficulty: str


class ExamSummary(BaseModel):
    total_questions: int
    excellent_questions: int
    too_easy: int
    too_hard: int
    confusing: int
    good_percentage: float


class QuestionRecommendation(BaseModel):
    question_id: str
    current_quality: str
    issue: str
    recommendation: str
    bloom_level_suggestion: str
    priority: str


class AssessmentRecommendations(BaseModel):
    overall_verdict: str
    key_learning_gaps: list[str]
    per_question_recommendations: list[QuestionRecommendation]
    immediate_actions: list[str]
    long_term_suggestions: list[str]
    error: Optional[str] = None


class AnalysisResult(BaseModel):
    per_question_stats: dict[str, QuestionStats]
    exam_summary: ExamSummary
    weak_questions: list[str]
    top_students: list[str]
    bottom_students: list[str]
    teacher_report: str
    error: Optional[str] = None


class AnalyzeResponse(BaseModel):
    status: str = "success"
    analysis: Optional[AnalysisResult] = None
    recommendations: Optional[AssessmentRecommendations] = None
    error: Optional[str] = None


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user's question or request")
    context: Optional[str] = Field(
        default="",
        description="Optional additional context, e.g. pasted analysis results",
    )
