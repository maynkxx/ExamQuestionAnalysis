import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.schemas import AnalyzeResponse
from agent.assessment_agent import run_agent

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse, summary="Analyze exam CSV and get AI recommendations")
async def analyze_exam_endpoint(file: UploadFile = File(..., description="CSV file with columns: question, student_id, marks")):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    raw_bytes = await file.read()
    if len(raw_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        csv_content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding must be UTF-8.")

    report = run_agent(csv_content)

    if not report:
        return AnalyzeResponse(status="error", error="Agent returned no output.")

    analysis_data = report.get("analysis", {})
    recommendations_data = report.get("recommendations", {})

    if "error" in analysis_data and analysis_data.get("status") in ("invalid_data", "error"):
        return AnalyzeResponse(
            status="error",
            error=analysis_data.get("error", "Analysis failed due to invalid or incomplete data."),
        )

    try:
        return AnalyzeResponse(
            status="success",
            analysis=analysis_data if analysis_data else None,
            recommendations=recommendations_data if recommendations_data else None,
        )
    except Exception as exc:
        return AnalyzeResponse(
            status="partial",
            error=f"Report generated but schema validation failed: {exc}",
            analysis=analysis_data,
            recommendations=recommendations_data,
        )
