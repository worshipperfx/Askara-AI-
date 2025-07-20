from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from session import (
    generate_question, 
    show_answer, 
    clarify, 
    get_chat_history, 
    reset_session,
    state
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Exam Question Generator API",
    description="API for generating exam questions, showing answers, and handling clarifications",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class ClarifyRequest(BaseModel):
    follow_up: str
    
    class Config:
        schema_extra = {
            "example": {
                "follow_up": "Can you explain this in simpler terms?"
            }
        }

class PredictRequest(BaseModel):
    paper_code: str  # not used now, but reserved for future
    
    class Config:
        schema_extra = {
            "example": {
                "paper_code": "MATH101"
            }
        }

class QuestionResponse(BaseModel):
    question: str
    topic_id: int
    examples: List[str]
    status: str = "success"

class AnswerResponse(BaseModel):
    answer: str
    status: str = "success"

class ClarificationResponse(BaseModel):
    clarification: str
    status: str = "success"

class ChatHistoryResponse(BaseModel):
    chat_history: List[List[str]]
    status: str = "success"

class StatusResponse(BaseModel):
    message: str
    status: str = "success"

class ErrorResponse(BaseModel):
    error: str
    status: str = "error"

class SessionStatusResponse(BaseModel):
    has_current_question: bool
    has_current_answer: bool
    topic_id: Optional[int]
    clarification_count: int
    chat_history_length: int
    status: str = "success"

# API Endpoints
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Exam Question Generator API",
        "version": "1.0.0",
        "endpoints": {
            "generate_question": "/predict",
            "show_answer": "/answer",
            "clarify": "/clarify",
            "chat_history": "/history",
            "reset_session": "/reset",
            "session_status": "/status"
        }
    }

@app.post("/predict", response_model=QuestionResponse)
async def predict_qn(data: PredictRequest):
    """
    Generate a new exam question based on topic weights
    """
    try:
        logger.info(f"Generating question for paper_code: {data.paper_code}")
        result = generate_question()
        
        if "error" in result:
            logger.error(f"Error generating question: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        return QuestionResponse(
            question=result["question"],
            topic_id=result["topic_id"],
            examples=result["examples"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in predict_qn: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/answer", response_model=AnswerResponse)
async def get_answer():
    """
    Get the answer to the current question
    """
    try:
        logger.info("Getting answer for current question")
        result = show_answer()
        
        if "error" in result:
            logger.error(f"Error getting answer: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        return AnswerResponse(answer=result["answer"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_answer: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/clarify", response_model=ClarificationResponse)
async def clarify_answer(data: ClarifyRequest):
    """
    Get clarification on the current question/answer
    """
    try:
        logger.info(f"Processing clarification request: {data.follow_up}")
        result = clarify(data.follow_up)
        
        if "error" in result:
            logger.error(f"Error in clarification: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Handle both clarification and message responses
        if "clarification" in result:
            return ClarificationResponse(clarification=result["clarification"])
        elif "message" in result:
            return ClarificationResponse(clarification=result["message"])
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in clarify_answer: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/history", response_model=ChatHistoryResponse)
async def get_history():
    """
    Get the current chat history
    """
    try:
        logger.info("Retrieving chat history")
        result = get_chat_history()
        return ChatHistoryResponse(chat_history=result["chat_history"])
    
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/reset", response_model=StatusResponse)
async def reset_current_session():
    """
    Reset the current session state
    """
    try:
        logger.info("Resetting session")
        result = reset_session()
        return StatusResponse(message=result["message"])
    
    except Exception as e:
        logger.error(f"Error resetting session: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/status", response_model=SessionStatusResponse)
async def get_session_status():
    """
    Get current session status information
    """
    try:
        return SessionStatusResponse(
            has_current_question=state.get("current_question") is not None,
            has_current_answer=state.get("current_answer") is not None,
            topic_id=state.get("topic_id"),
            clarification_count=len(state.get("clarification_log", [])),
            chat_history_length=len(state.get("chat_history", []))
        )
    
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "exam-question-generator",
        "version": "1.0.0"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom HTTP exception handler
    """
    return {
        "error": exc.detail,
        "status": "error",
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    General exception handler for unexpected errors
    """
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "status": "error",
        "status_code": 500
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Initialize the application on startup
    """
    logger.info("Starting Exam Question Generator API")
    logger.info("API documentation available at /docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    logger.info("Shutting down Exam Question Generator API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fast_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )