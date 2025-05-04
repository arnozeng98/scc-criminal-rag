"""
Module for generating text embeddings from case chunks.
"""
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np
import requests
from tqdm import tqdm
import backoff

from backend.src.config import (
    EMBEDDINGS_LOG_FILE, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS
)
from backend.src.utils.log_utils import setup_logging
from backend.src.utils.file_utils import save_json_file

# Set up logging
logger = setup_logging(EMBEDDINGS_LOG_FILE)

class OpenAIEmbedder:
    """
    Class for generating embeddings using OpenAI's API.
    """
    
    def __init__(self, model_name: str = EMBEDDING_MODEL, api_key: Optional[str] = None):
        """
        Initialize the OpenAI embedder.
        
        Args:
            model_name: Name of the OpenAI embedding model to use
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and not found in environment variables")
        
        self.api_url = "https://api.openai.com/v1/embeddings"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        logger.info(f"Initialized OpenAI embedder with model: {model_name}")
    
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, Exception),
        max_tries=5,
        giveup=lambda e: "Invalid API key" in str(e)
    )
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text:
            return [0.0] * EMBEDDING_DIMENSIONS  # Return zero vector for empty text
        
        payload = {
            "input": text,
            "model": self.model_name
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            error_msg = f"Error from OpenAI API: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        result = response.json()
        embedding = result["data"][0]["embedding"]
        
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to generate embeddings for
            batch_size: Number of texts to process in each API call
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch = texts[i:i+batch_size]
            
            # Process each text individually with retry logic
            batch_embeddings = []
            for text in batch:
                try:
                    embedding = self.generate_embedding(text)
                    batch_embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"Error generating embedding: {e}")
                    # Use zero vector as fallback
                    batch_embeddings.append([0.0] * EMBEDDING_DIMENSIONS)
            
            embeddings.extend(batch_embeddings)
            
            # Throttle requests to avoid rate limits
            time.sleep(0.5)
        
        return embeddings

def generate_chunk_embeddings(chunks: List[Dict[str, Any]], output_file: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate embeddings for a list of case chunks.
    
    Args:
        chunks: List of chunk dictionaries with 'text' and 'metadata' fields
        output_file: Optional path to save the results
        
    Returns:
        List of chunk dictionaries with added embedding vectors
    """
    if not chunks:
        logger.warning("No chunks provided for embedding generation")
        return []
    
    # Check for OPENAI_API_KEY
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set")
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Initialize embedder
    embedder = OpenAIEmbedder()
    
    # Extract texts from chunks
    texts = [chunk.get('text', '') for chunk in chunks]
    logger.info(f"Generating embeddings for {len(texts)} chunks")
    
    # Generate embeddings
    embeddings = embedder.generate_embeddings_batch(texts)
    
    # Add embeddings to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk['embedding'] = embedding
    
    logger.info(f"Generated embeddings for {len(chunks)} chunks")
    
    # Save results if output file is specified
    if output_file:
        save_json_file(output_file, chunks)
        logger.info(f"Saved chunks with embeddings to {output_file}")
    
    return chunks 