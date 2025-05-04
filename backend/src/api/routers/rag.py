"""
API router for RAG functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
import time
import os

from backend.src.config import (
    API_LOG_FILE, VECTORS_DIR
)
from backend.src.utils.log_utils import setup_logging
from backend.src.rag.generator import RAGGenerator
from backend.src.rag.retriever import CaseRetriever
from backend.src.api.models.schemas import (
    QueryRequest, QueryResponseModel, CitationModel, ChunkModel
)

# Set up logging
logger = setup_logging(API_LOG_FILE)

# Create router
router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
    responses={404: {"description": "Not found"}},
)

# Create RAG generator instance
_rag_generator: Optional[RAGGenerator] = None

def get_rag_generator() -> RAGGenerator:
    """
    Get or create the RAG generator instance.
    """
    global _rag_generator
    if _rag_generator is None:
        try:
            _rag_generator = RAGGenerator(vector_store_dir=VECTORS_DIR)
            logger.info("RAG generator initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing RAG generator: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to initialize RAG system: {str(e)}"
            )
    return _rag_generator

@router.post("/query", response_model=QueryResponseModel)
async def query_rag(request: QueryRequest, rag_generator: RAGGenerator = Depends(get_rag_generator)) -> Dict[str, Any]:
    """
    Query the RAG system.
    """
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
            
        logger.info(f"Received query: {query}")
        
        # Answer the query
        result = rag_generator.answer_query(query, request.top_k)
        
        # Convert the result to the expected response format
        response = {
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
            "context": result.get("context", []),
            "retrieval_time": result.get("retrieval_time"),
            "total_time": result.get("total_time")
        }
        
        if "error" in result:
            response["error"] = result["error"]
        
        return response
        
    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing query: {str(e)}"
        )

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    """
    try:
        # Check if we can initialize the RAG generator
        rag_generator = get_rag_generator()
        return {
            "status": "ok",
            "message": "RAG system is healthy"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG system is not healthy: {str(e)}"
        ) 