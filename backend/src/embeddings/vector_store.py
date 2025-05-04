"""
Module for managing vector storage and retrieval.
"""
import os
import json
import pickle
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import time
import chromadb
from chromadb.utils import embedding_functions

from backend.src.config import (
    EMBEDDINGS_LOG_FILE, VECTORS_DIR, SIMILARITY_TOP_K, EMBEDDING_DIMENSIONS
)
from backend.src.utils.log_utils import setup_logging
from backend.src.utils.file_utils import ensure_dir_exists, save_json_file, load_json_file

# Set up logging
logger = setup_logging(EMBEDDINGS_LOG_FILE)

class ChromaVectorStore:
    """
    Vector store implementation using ChromaDB for efficient similarity search.
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the ChromaDB vector store.
        
        Args:
            persist_directory: Directory to persist the ChromaDB data (optional)
        """
        self.collection_name = "scc_criminal_cases"
        self.client = None
        self.collection = None
        self.metadata = []
        
        # Initialize ChromaDB
        if persist_directory:
            ensure_dir_exists(persist_directory)
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()
            
        # Get or create collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Initialized ChromaDB vector store with collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def add_embeddings(self, embeddings: List[List[float]], metadata_list: List[Dict[str, Any]]) -> None:
        """
        Add embeddings and their metadata to the vector store.
        
        Args:
            embeddings: List of embedding vectors
            metadata_list: List of metadata dictionaries corresponding to each embedding
        """
        if not self.collection:
            logger.error("Collection not initialized")
            return
        
        # Prepare document IDs
        doc_ids = [f"doc_{i}" for i in range(len(embeddings))]
        
        # Prepare document texts
        texts = [item.get('text', '') for item in metadata_list]
        
        # Prepare metadata
        chroma_metadata = []
        for meta in metadata_list:
            # Flatten metadata for ChromaDB
            case_metadata = meta.get('metadata', {})
            chroma_meta = {
                "case_number": case_metadata.get('case_number', ''),
                "title": case_metadata.get('title', ''),
                "date": case_metadata.get('date', ''),
                "is_criminal": case_metadata.get('is_criminal', False),
                "chunk_index": case_metadata.get('chunk_index', 0)
            }
            chroma_metadata.append(chroma_meta)
        
        # Store original metadata for compatibility
        self.metadata = metadata_list
        
        # Add embeddings to ChromaDB
        try:
            self.collection.add(
                ids=doc_ids,
                embeddings=embeddings,
                metadatas=chroma_metadata, 
                documents=texts
            )
            logger.info(f"Added {len(embeddings)} embeddings to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding embeddings to ChromaDB: {e}")
            raise
    
    def search(self, query_embedding: List[float], top_k: int = SIMILARITY_TOP_K) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in the vector store.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of dictionaries containing similarity scores and metadata
        """
        if not self.collection:
            logger.error("Collection not initialized for search")
            return []
        
        try:
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["metadatas", "documents", "distances"]
            )
            
            # Process results
            processed_results = []
            
            if results and results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    # Get index from doc_id
                    idx = int(doc_id.replace("doc_", ""))
                    
                    # Get metadata and distance
                    chroma_metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    document = results['documents'][0][i] if results['documents'] and results['documents'][0] else ""
                    
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity = 1.0 - distance
                    
                    # Create original metadata format for compatibility
                    metadata_entry = {
                        'text': document,
                        'metadata': {
                            'case_number': chroma_metadata.get('case_number', ''),
                            'title': chroma_metadata.get('title', ''),
                            'date': chroma_metadata.get('date', ''),
                            'is_criminal': chroma_metadata.get('is_criminal', False),
                            'chunk_index': chroma_metadata.get('chunk_index', 0)
                        }
                    }
                    
                    # Create result entry
                    result = {
                        "score": float(similarity),
                        "distance": float(distance),
                        "metadata": metadata_entry,
                        "index": idx
                    }
                    
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error searching in ChromaDB: {e}")
            return []
    
    def get_size(self) -> int:
        """
        Get the number of embeddings in the vector store.
        
        Returns:
            Number of embeddings
        """
        if self.collection:
            return self.collection.count()
        return 0

def build_vector_store(chunks_with_embeddings: List[Dict[str, Any]], output_dir: str = VECTORS_DIR) -> ChromaVectorStore:
    """
    Build a vector store from chunks with embeddings.
    
    Args:
        chunks_with_embeddings: List of chunk dictionaries with embedding vectors
        output_dir: Directory to save the vector store files
        
    Returns:
        Initialized ChromaVectorStore
    """
    # Extract embeddings and metadata
    embeddings = []
    metadata_list = []
    
    for chunk in chunks_with_embeddings:
        if 'embedding' not in chunk:
            logger.warning(f"Chunk missing embedding, skipping")
            continue
            
        embeddings.append(chunk['embedding'])
        
        # Create metadata entry (everything except the embedding)
        metadata = {
            'text': chunk.get('text', ''),
            'metadata': chunk.get('metadata', {})
        }
        metadata_list.append(metadata)
    
    logger.info(f"Building vector store with {len(embeddings)} embeddings")
    
    # Create and initialize vector store
    chroma_db_path = os.path.join(output_dir, "chroma_db")
    ensure_dir_exists(chroma_db_path)
    vector_store = ChromaVectorStore(persist_directory=chroma_db_path)
    
    # Add embeddings
    vector_store.add_embeddings(embeddings, metadata_list)
    
    # Also save metadata separately for compatibility
    metadata_path = os.path.join(output_dir, "metadata.pkl")
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata_list, f)
    
    logger.info(f"Vector store built and saved to {chroma_db_path}")
    return vector_store

def load_vector_store(vectors_dir: str = VECTORS_DIR) -> Optional[ChromaVectorStore]:
    """
    Load a vector store from files.
    
    Args:
        vectors_dir: Directory containing the vector store files
        
    Returns:
        Initialized ChromaVectorStore or None if files not found
    """
    chroma_db_path = os.path.join(vectors_dir, "chroma_db")
    
    if not os.path.exists(chroma_db_path):
        logger.error(f"ChromaDB directory not found at {chroma_db_path}")
        return None
    
    try:
        vector_store = ChromaVectorStore(persist_directory=chroma_db_path)
        logger.info(f"Loaded vector store with {vector_store.get_size()} embeddings")
        return vector_store
    except Exception as e:
        logger.error(f"Error loading vector store: {e}")
        return None 