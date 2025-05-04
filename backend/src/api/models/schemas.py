"""
API data models for the SCC Criminal Cases RAG system.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """
    Request model for querying the RAG system.
    """
    query: str = Field(..., description="Question to ask the system")
    top_k: int = Field(5, description="Number of top chunks to retrieve")

class CitationModel(BaseModel):
    """
    Model for a citation.
    """
    case_number: str = Field(..., description="Case number")
    title: str = Field(..., description="Case title")
    date: str = Field(..., description="Case date")
    citation_text: str = Field(..., description="Formatted citation text")
    score: float = Field(..., description="Relevance score")
    mention: Optional[str] = Field(None, description="Case mention in the answer")

class ChunkMetadataModel(BaseModel):
    """
    Model for chunk metadata.
    """
    case_number: Optional[str] = Field(None, description="Case number")
    title: Optional[str] = Field(None, description="Case title")
    date: Optional[str] = Field(None, description="Case date")
    chunk_index: Optional[int] = Field(None, description="Index of the chunk in the case")
    total_chunks: Optional[int] = Field(None, description="Total number of chunks in the case")
    source: Optional[str] = Field(None, description="Source of the chunk")
    is_criminal: Optional[bool] = Field(None, description="Whether the case is a criminal case")

class ChunkModel(BaseModel):
    """
    Model for a retrieved chunk.
    """
    text: str = Field(..., description="Chunk text")
    metadata: ChunkMetadataModel = Field(..., description="Chunk metadata")
    score: float = Field(..., description="Relevance score")

class QueryResponseModel(BaseModel):
    """
    Response model for a RAG query.
    """
    answer: str = Field(..., description="Generated answer")
    citations: List[CitationModel] = Field(default_factory=list, description="Citations used in the answer")
    context: Optional[List[Dict[str, Any]]] = Field(None, description="Context used to generate the answer")
    retrieval_time: Optional[float] = Field(None, description="Time taken for retrieval (seconds)")
    total_time: Optional[float] = Field(None, description="Total time taken (seconds)")
    error: Optional[str] = Field(None, description="Error message if any") 