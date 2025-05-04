#!/usr/bin/env python
"""
Script to generate embeddings and build the vector index.

This script loads processed case chunks, generates embeddings,
and builds a ChromaDB index for similarity search.
"""
import sys
import os
import argparse
from typing import List, Dict, Any, Optional
import logging
import time
import json

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)

from backend.src.embeddings.vectorizer import generate_chunk_embeddings
from backend.src.embeddings.vector_store import build_vector_store, load_vector_store
from backend.src.config import (
    PROCESSED_DIR, VECTORS_DIR, EMBEDDINGS_LOG_FILE
)
from backend.src.utils.log_utils import setup_logging
from backend.src.utils.file_utils import load_json_file, ensure_dir_exists

# Set up logging
logger = setup_logging(EMBEDDINGS_LOG_FILE)

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(description="Generate embeddings and build vector index")
    parser.add_argument(
        "--chunks-file", 
        type=str, 
        default=os.path.join(PROCESSED_DIR, "case_chunks.json"), 
        help="Path to the case chunks JSON file"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default=VECTORS_DIR, 
        help=f"Directory to save vector index files (default: {VECTORS_DIR})"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force rebuilding the index even if it already exists"
    )
    
    return parser.parse_args()

def main() -> int:
    """
    Main entry point for the index building script.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    args = parse_args()
    
    logger.info("Starting embedding generation and vector index building...")
    logger.info(f"Chunks file: {args.chunks_file}")
    logger.info(f"Output directory: {args.output_dir}")
    
    # Check if vector store already exists
    chroma_db_path = os.path.join(args.output_dir, "chroma_db")
    
    if os.path.exists(chroma_db_path) and not args.rebuild:
        logger.info("Vector store already exists. Use --rebuild to force rebuilding")
        
        # Load the vector store to validate it
        vector_store = load_vector_store(args.output_dir)
        if vector_store:
            logger.info(f"Vector store loaded successfully with {vector_store.get_size()} embeddings")
            return 0
        else:
            logger.warning("Failed to load existing vector store. Will rebuild")
    
    # Load case chunks
    try:
        chunks = load_json_file(args.chunks_file)
        if not chunks:
            logger.error(f"No chunks found in {args.chunks_file}")
            return 1
            
        logger.info(f"Loaded {len(chunks)} chunks from {args.chunks_file}")
    except Exception as e:
        logger.exception(f"Error loading chunks file: {e}")
        return 1
    
    start_time = time.time()
    
    try:
        # Check if chunks already have embeddings
        if all('embedding' in chunk for chunk in chunks):
            logger.info("Chunks already have embeddings, skipping generation")
        else:
            # Generate embeddings
            logger.info("Generating embeddings for chunks...")
            embedded_chunks_file = os.path.join(args.output_dir, "chunks_with_embeddings.json")
            ensure_dir_exists(args.output_dir)
            chunks = generate_chunk_embeddings(chunks, embedded_chunks_file)
        
        # Build vector store
        logger.info("Building vector store...")
        vector_store = build_vector_store(chunks, args.output_dir)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Vector store built with {vector_store.get_size()} embeddings in {elapsed_time:.2f} seconds")
        
        return 0
        
    except Exception as e:
        logger.exception(f"Error during index building: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        sys.exit(1) 