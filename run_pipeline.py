#!/usr/bin/env python
"""
Script to run the complete SCC Criminal Cases RAG pipeline.

This script orchestrates the following steps:
1. Scrape SCC criminal cases
2. Process and extract structured data from raw case files
3. Generate embeddings and build the vector index

Usage:
  python run_pipeline.py [--max-cases N] [--skip-scraping] [--skip-processing] [--skip-embeddings]
"""
import sys
import os
import argparse
import subprocess
import logging
import time
from typing import List, Dict, Any, Optional

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(description="Run the SCC Criminal Cases RAG pipeline")
    parser.add_argument(
        "--max-cases", 
        type=int, 
        default=None, 
        help="Maximum number of cases to download per URL"
    )
    parser.add_argument(
        "--skip-scraping", 
        action="store_true",
        help="Skip the scraping step"
    )
    parser.add_argument(
        "--skip-processing", 
        action="store_true",
        help="Skip the processing step"
    )
    parser.add_argument(
        "--skip-embeddings", 
        action="store_true",
        help="Skip the embeddings step"
    )
    parser.add_argument(
        "--api-key", 
        type=str,
        help="OpenAI API key (optional, can also use OPENAI_API_KEY environment variable)"
    )
    
    return parser.parse_args()

def run_command(command: List[str], description: str) -> int:
    """
    Run a shell command and handle errors.
    
    Args:
        command: Command to run as a list of strings
        description: Description of the command for logging
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    print(f"\n{'='*80}\n{description}\n{'='*80}")
    print(f"Running: {' '.join(command)}\n")
    
    try:
        result = subprocess.run(command, check=True)
        print(f"\n✅ {description} completed successfully")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return e.returncode

def main() -> int:
    """
    Main entry point for the pipeline script.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    args = parse_args()
    
    # Set up environment
    env = os.environ.copy()
    if args.api_key:
        env["OPENAI_API_KEY"] = args.api_key
    
    # Check for OpenAI API key for embedding steps
    if not args.skip_embeddings and not env.get("OPENAI_API_KEY"):
        print("❌ ERROR: OpenAI API key not provided. Set it with --api-key or OPENAI_API_KEY environment variable.")
        return 1
    
    start_time = time.time()
    
    # Step 1: Scrape cases
    if not args.skip_scraping:
        command = ["python", "-m", "backend.scripts.run_scraper"]
        if args.max_cases:
            command.extend(["--max-cases", str(args.max_cases)])
        
        exit_code = run_command(command, "Step 1: Scraping SCC criminal cases")
        if exit_code != 0:
            return exit_code
    else:
        print("\n⏭️  Skipping Step 1: Scraping SCC criminal cases")
    
    # Step 2: Process and extract data
    if not args.skip_processing:
        exit_code = run_command(
            ["python", "-m", "backend.scripts.process_data"],
            "Step 2: Processing and extracting structured data"
        )
        if exit_code != 0:
            return exit_code
    else:
        print("\n⏭️  Skipping Step 2: Processing and extracting structured data")
    
    # Step 3: Generate embeddings and build index
    if not args.skip_embeddings:
        exit_code = run_command(
            ["python", "-m", "backend.scripts.build_index"],
            "Step 3: Generating embeddings and building vector index"
        )
        if exit_code != 0:
            return exit_code
    else:
        print("\n⏭️  Skipping Step 3: Generating embeddings and building vector index")
    
    elapsed_time = time.time() - start_time
    print(f"\n{'='*80}")
    print(f"🎉 Pipeline completed successfully in {elapsed_time:.2f} seconds")
    print(f"{'='*80}")
    
    # Print next steps
    print("\nNext steps:")
    print("1. Start the API server:")
    print("   uvicorn backend.src.api.app:app --reload")
    print("2. Start the frontend development server:")
    print("   cd frontend && npm start")
    print("3. Or run everything with Docker:")
    print("   docker-compose up -d")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unhandled exception: {e}")
        sys.exit(1) 