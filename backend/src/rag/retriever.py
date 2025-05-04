"""
Module for retrieving relevant case chunks based on queries.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import time

from backend.src.config import (
    RAG_LOG_FILE, VECTORS_DIR, SIMILARITY_TOP_K
)
from backend.src.utils.log_utils import setup_logging
from backend.src.embeddings.vectorizer import OpenAIEmbedder
from backend.src.embeddings.vector_store import load_vector_store, ChromaVectorStore

# Set up logging
logger = setup_logging(RAG_LOG_FILE)

class CaseRetriever:
    """
    Retriever for finding relevant case chunks based on queries.
    """
    
    def __init__(self, vector_store_dir: str = VECTORS_DIR):
        """
        Initialize the case retriever.
        
        Args:
            vector_store_dir: Directory containing the vector store files
        """
        # Load the vector store
        self.vector_store = load_vector_store(vector_store_dir)
        if not self.vector_store:
            raise ValueError(f"Failed to load vector store from {vector_store_dir}")
        
        # Initialize the embedder
        try:
            self.embedder = OpenAIEmbedder()
            logger.info("Initialized case retriever with OpenAI embedder")
        except Exception as e:
            logger.error(f"Error initializing embedder: {e}")
            raise
    
    def retrieve(self, query: str, top_k: int = SIMILARITY_TOP_K) -> List[Dict[str, Any]]:
        """
        Retrieve relevant case chunks for a query.
        
        Args:
            query: Query text
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing retrieved chunks with metadata and similarity scores
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedder.generate_embedding(query)
            
            # Search for similar chunks
            results = self.vector_store.search(query_embedding, top_k)
            
            logger.info(f"Retrieved {len(results)} chunks for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving chunks for query '{query[:50]}...': {e}")
            return []
    
    def retrieve_batch(self, queries: List[str], top_k: int = SIMILARITY_TOP_K) -> List[List[Dict[str, Any]]]:
        """
        Retrieve relevant case chunks for multiple queries.
        
        Args:
            queries: List of query texts
            top_k: Number of top results to return for each query
            
        Returns:
            List of lists, each containing retrieved chunks for a query
        """
        results = []
        
        for query in queries:
            query_results = self.retrieve(query, top_k)
            results.append(query_results)
        
        return results
    
    def get_case_context(self, case_number: str) -> Dict[str, Any]:
        """
        Get all chunks belonging to a specific case.
        
        Args:
            case_number: Case number to retrieve chunks for
            
        Returns:
            Dictionary with case metadata and all chunks
        """
        # Collect all chunks for the case
        case_chunks = []
        
        for i, metadata_entry in enumerate(self.vector_store.metadata):
            chunk_metadata = metadata_entry.get('metadata', {})
            if chunk_metadata.get('case_number') == case_number:
                chunk = {
                    'text': metadata_entry.get('text', ''),
                    'metadata': chunk_metadata,
                    'index': i
                }
                case_chunks.append(chunk)
        
        if not case_chunks:
            logger.warning(f"No chunks found for case {case_number}")
            return {'case_number': case_number, 'chunks': []}
        
        # Sort chunks by their chunk_index
        case_chunks.sort(key=lambda x: x.get('metadata', {}).get('chunk_index', 0))
        
        # Extract case metadata from the first chunk
        first_chunk_metadata = case_chunks[0].get('metadata', {})
        case_metadata = {
            'case_number': first_chunk_metadata.get('case_number'),
            'title': first_chunk_metadata.get('title'),
            'date': first_chunk_metadata.get('date'),
            'is_criminal': first_chunk_metadata.get('is_criminal', False),
            'chunk_count': len(case_chunks)
        }
        
        return {
            'metadata': case_metadata,
            'chunks': case_chunks
        }

def prepare_context(retrieved_chunks: List[Dict[str, Any]], include_metadata: bool = True) -> str:
    """
    Prepare a context string from retrieved chunks for use in generation.
    
    Args:
        retrieved_chunks: List of retrieved chunks with metadata
        include_metadata: Whether to include metadata in the context
        
    Returns:
        Formatted context string
    """
    if not retrieved_chunks:
        return ""
    
    context_parts = []
    
    for i, chunk in enumerate(retrieved_chunks):
        chunk_text = chunk.get('metadata', {}).get('text', '')
        if not chunk_text:
            chunk_text = chunk.get('text', '')
        
        # Skip empty chunks
        if not chunk_text.strip():
            continue
            
        chunk_metadata = chunk.get('metadata', {}).get('metadata', {})
        if not chunk_metadata:
            chunk_metadata = chunk.get('metadata', {})
        
        # Format metadata
        metadata_str = ""
        if include_metadata:
            metadata_fields = [
                f"Case: {chunk_metadata.get('title', 'Unknown')}",
                f"Case Number: {chunk_metadata.get('case_number', 'Unknown')}",
                f"Date: {chunk_metadata.get('date', 'Unknown')}"
            ]
            metadata_str = " | ".join(metadata_fields)
            
        # Add formatted chunk to context
        context_parts.append(f"[Context {i+1}]{' ' + metadata_str if metadata_str else ''}\n{chunk_text}\n")
    
    return "\n".join(context_parts) 