"""
FastAPI application for the SCC Criminal Cases RAG system.
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
import os
from typing import List, Dict, Any

from backend.src.config import API_LOG_FILE
from backend.src.utils.log_utils import setup_logging
from backend.src.api.routers import rag

# Set up logging
logger = setup_logging(API_LOG_FILE)

# Create FastAPI app
app = FastAPI(
    title="SCC Criminal Cases RAG API",
    description="API for querying the SCC Criminal Cases RAG system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Log the request
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"status_code={response.status_code} "
        f"process_time={process_time:.4f} sec"
    )
    
    return response

# Register routers
app.include_router(rag.router)

@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint.
    """
    return {
        "message": "Welcome to the SCC Criminal Cases RAG API",
        "docs_url": "/docs",
        "health_check": "/health"
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for Docker.
    This endpoint is used by Docker health checks to verify
    that the API is running correctly.
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    } 