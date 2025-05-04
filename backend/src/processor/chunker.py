"""
Module for splitting case text into chunks for embedding.
"""
from typing import List, Dict, Any, Tuple, Optional
import re
import logging
import numpy as np

from backend.src.config import PROCESSOR_LOG_FILE, CHUNK_SIZE, CHUNK_OVERLAP
from backend.src.utils.log_utils import setup_logging

# Set up logging
logger = setup_logging(PROCESSOR_LOG_FILE)

def split_by_sentence(text: str) -> List[str]:
    """
    Split text into sentences using regex.
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    if not text:
        return []
        
    # Pattern matches end of sentences with handling for abbreviations,
    # parentheses, quotations, and special cases in legal text
    pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\:)\s+(?=[A-Z])'
    sentences = re.split(pattern, text)
    
    # Filter out empty or very short sentences
    return [s.strip() for s in sentences if len(s.strip()) > 5]

def estimate_token_count(text: str) -> int:
    """
    Estimate the number of tokens in a text.
    
    This is a simple approximation based on whitespace and punctuation.
    For production use, you would use a more accurate tokenization method.
    
    Args:
        text: Text to estimate token count for
        
    Returns:
        Estimated token count
    """
    if not text:
        return 0
        
    # Very rough approximation: tokens are roughly words plus punctuation
    words = len(text.split())
    # Add an estimate for punctuation and special tokens
    return int(words * 1.3)

def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks of approximately equal token size.
    
    Args:
        text: Text to split
        chunk_size: Target size of each chunk in tokens
        chunk_overlap: Number of overlapping tokens between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
        
    sentences = split_by_sentence(text)
    if not sentences:
        return []
        
    # Estimate token count for each sentence
    sentence_token_counts = [estimate_token_count(sentence) for sentence in sentences]
    
    chunks = []
    current_chunk: List[str] = []
    current_size = 0
    
    for i, (sentence, token_count) in enumerate(zip(sentences, sentence_token_counts)):
        # If adding this sentence would exceed the chunk size and we have some content,
        # finish the current chunk and start a new one
        if current_size + token_count > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            
            # For the next chunk, include some overlap from the previous chunk
            overlap_token_count = 0
            overlap_sentences = []
            
            # Add sentences from the end of the previous chunk until we reach the desired overlap
            for prev_sentence in reversed(current_chunk):
                prev_token_count = estimate_token_count(prev_sentence)
                if overlap_token_count + prev_token_count <= chunk_overlap:
                    overlap_sentences.insert(0, prev_sentence)
                    overlap_token_count += prev_token_count
                else:
                    break
            
            # Start the new chunk with the overlap sentences
            current_chunk = overlap_sentences
            current_size = overlap_token_count
        
        # Add the current sentence to the chunk
        current_chunk.append(sentence)
        current_size += token_count
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def create_case_chunks(case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Create chunks from case data with appropriate metadata.
    
    Args:
        case_data: Dictionary containing case data
        
    Returns:
        List of dictionaries, each representing a chunk with metadata
    """
    if not case_data or 'facts' not in case_data or not case_data['facts']:
        logger.warning(f"Case data missing 'facts' field: {case_data.get('metadata', {}).get('case_number', 'unknown')}")
        return []
    
    # Extract metadata and facts
    metadata = case_data.get('metadata', {})
    facts_text = case_data['facts']
    
    # Split the facts into chunks
    facts_chunks = split_into_chunks(facts_text)
    
    if not facts_chunks:
        logger.warning(f"No chunks generated for case: {metadata.get('case_number', 'unknown')}")
        return []
    
    # Create a chunk document for each text chunk
    chunk_documents = []
    
    for i, chunk_text in enumerate(facts_chunks):
        # Create a metadata dictionary for the chunk
        chunk_metadata = {
            'case_number': metadata.get('case_number'),
            'title': metadata.get('title'),
            'date': metadata.get('date'),
            'chunk_index': i,
            'total_chunks': len(facts_chunks),
            'source': 'facts',
            'is_criminal': case_data.get('is_criminal', False)
        }
        
        # Create the chunk document
        chunk_document = {
            'text': chunk_text,
            'metadata': chunk_metadata
        }
        
        chunk_documents.append(chunk_document)
    
    logger.info(f"Created {len(chunk_documents)} chunks for case: {metadata.get('case_number', 'unknown')}")
    return chunk_documents 