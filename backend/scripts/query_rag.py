#!/usr/bin/env python
"""
Script to query the RAG system from the command line.

This script provides a command-line interface to ask questions
about Canadian Supreme Court criminal cases.
"""
import sys
import os
import argparse
import logging
import json
from typing import Dict, Any, Optional

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)

from backend.src.rag.generator import RAGGenerator
from backend.src.rag.citation import enrich_answer_with_citations
from backend.src.config import (
    VECTORS_DIR, RAG_LOG_FILE
)
from backend.src.utils.log_utils import setup_logging

# Set up logging
logger = setup_logging(RAG_LOG_FILE)

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(description="Query the SCC Criminal Cases RAG system")
    parser.add_argument(
        "query", 
        type=str, 
        nargs="?",
        help="Question to ask the system (if not provided, interactive mode will be used)"
    )
    parser.add_argument(
        "--vector-store-dir", 
        type=str, 
        default=VECTORS_DIR, 
        help=f"Directory containing the vector store (default: {VECTORS_DIR})"
    )
    parser.add_argument(
        "--top-k", 
        type=int, 
        default=5, 
        help="Number of top chunks to retrieve (default: 5)"
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--with-citations",
        action="store_true",
        help="Include citations in the answer"
    )
    
    return parser.parse_args()

def format_output(result: Dict[str, Any], with_citations: bool = False, json_output: bool = False) -> str:
    """
    Format the result for display.
    
    Args:
        result: RAG result dictionary
        with_citations: Whether to include citations in the output
        json_output: Whether to output in JSON format
        
    Returns:
        Formatted output string
    """
    if json_output:
        return json.dumps(result, indent=2)
        
    answer = result["answer"]
    
    if with_citations and "citations" in result:
        answer = enrich_answer_with_citations(answer, result["citations"])
    
    if "error" in result:
        output = f"Error: {result['error']}\n\n{answer}"
    else:
        retrieval_time = result.get("retrieval_time", 0)
        total_time = result.get("total_time", 0)
        output = f"{answer}\n\n(Retrieved in {retrieval_time:.2f}s, total time: {total_time:.2f}s)"
    
    return output

def interactive_mode(rag_generator: RAGGenerator, top_k: int, with_citations: bool, json_output: bool) -> None:
    """
    Run the RAG system in interactive mode.
    
    Args:
        rag_generator: Initialized RAG generator
        top_k: Number of top chunks to retrieve
        with_citations: Whether to include citations in the output
        json_output: Whether to output in JSON format
    """
    print("SCC Criminal Cases RAG System")
    print("Enter your questions about Canadian Supreme Court criminal cases")
    print("Type 'exit', 'quit', or press Ctrl+C to exit")
    print("-" * 50)
    
    try:
        while True:
            query = input("\nQuestion: ").strip()
            
            if not query or query.lower() in ["exit", "quit"]:
                break
                
            result = rag_generator.answer_query(query, top_k)
            output = format_output(result, with_citations, json_output)
            
            print("\n" + output)
            
    except KeyboardInterrupt:
        print("\nExiting...")

def main() -> int:
    """
    Main entry point for the RAG query script.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    args = parse_args()
    
    try:
        # Initialize RAG generator
        rag_generator = RAGGenerator(vector_store_dir=args.vector_store_dir)
        
        # Check if we're in interactive mode or single query mode
        if args.query:
            # Single query mode
            result = rag_generator.answer_query(args.query, args.top_k)
            output = format_output(result, args.with_citations, args.json_output)
            print(output)
        else:
            # Interactive mode
            interactive_mode(rag_generator, args.top_k, args.with_citations, args.json_output)
        
        return 0
    except Exception as e:
        logger.exception(f"Error running RAG query: {e}")
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        print(f"Unhandled exception: {e}")
        sys.exit(1) 