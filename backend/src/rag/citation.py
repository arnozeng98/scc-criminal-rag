"""
Module for managing citations in generated answers.
"""
import re
from typing import List, Dict, Any, Optional, Set, Tuple
import logging

from backend.src.config import RAG_LOG_FILE
from backend.src.utils.log_utils import setup_logging

# Set up logging
logger = setup_logging(RAG_LOG_FILE)

def extract_case_mentions(text: str) -> List[str]:
    """
    Extract case mentions from text.
    
    Args:
        text: Text to extract case mentions from
        
    Returns:
        List of extracted case mentions
    """
    # Pattern to match case citations like "R. v. Smith" or "Smith v. Jones"
    citation_pattern = r'([A-Z][a-z]+\.?\s+v\.\s+[A-Z][a-z]+)'
    
    # Find all matches
    matches = re.findall(citation_pattern, text)
    
    # Deduplicate
    return list(set(matches))

def match_case_mentions_to_chunks(
    case_mentions: List[str], 
    retrieved_chunks: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Match case mentions to their corresponding chunks.
    
    Args:
        case_mentions: List of case mentions extracted from text
        retrieved_chunks: List of retrieved chunks
        
    Returns:
        Dictionary mapping case mentions to their source chunks
    """
    matches = {}
    
    for mention in case_mentions:
        mention_matches = []
        
        for chunk in retrieved_chunks:
            chunk_text = chunk.get('metadata', {}).get('text', '')
            if not chunk_text:
                chunk_text = chunk.get('text', '')
                
            # Check if the mention appears in the chunk
            if mention.lower() in chunk_text.lower():
                # Get metadata for the citation
                metadata = chunk.get('metadata', {})
                if isinstance(metadata, dict):
                    chunk_metadata = metadata.get('metadata', {})
                    if not chunk_metadata:
                        chunk_metadata = metadata
                else:
                    chunk_metadata = {}
                
                citation_info = {
                    'case_number': chunk_metadata.get('case_number', 'Unknown'),
                    'title': chunk_metadata.get('title', 'Unknown'),
                    'date': chunk_metadata.get('date', 'Unknown'),
                    'score': chunk.get('score', 0.0),
                    'chunk_index': chunk_metadata.get('chunk_index', 0)
                }
                
                mention_matches.append(citation_info)
        
        if mention_matches:
            # Sort by relevance score
            mention_matches.sort(key=lambda x: x.get('score', 0.0), reverse=True)
            matches[mention] = mention_matches
    
    return matches

def format_citations(retrieved_chunks: List[Dict[str, Any]], answer_text: str) -> List[Dict[str, Any]]:
    """
    Format citations for an answer.
    
    Args:
        retrieved_chunks: List of retrieved chunks
        answer_text: Generated answer text
        
    Returns:
        List of citation dictionaries
    """
    # Extract case mentions from the answer
    case_mentions = extract_case_mentions(answer_text)
    
    if not case_mentions:
        # If no specific cases were mentioned, create citations based on source chunks
        citations = []
        seen_cases = set()
        
        for chunk in retrieved_chunks:
            chunk_metadata = chunk.get('metadata', {})
            if isinstance(chunk_metadata, dict):
                nested_metadata = chunk_metadata.get('metadata', {})
                if not nested_metadata:
                    nested_metadata = chunk_metadata
            else:
                nested_metadata = {}
            
            case_number = nested_metadata.get('case_number')
            if not case_number or case_number in seen_cases:
                continue
                
            seen_cases.add(case_number)
            
            citation = {
                'case_number': case_number,
                'title': nested_metadata.get('title', 'Unknown Case'),
                'date': nested_metadata.get('date', 'Unknown Date'),
                'citation_text': f"{nested_metadata.get('title', 'Unknown Case')} ({nested_metadata.get('date', 'n.d.')})",
                'score': chunk.get('score', 0.0)
            }
            
            citations.append(citation)
        
        # Sort by relevance score
        citations.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        return citations[:5]  # Limit to top 5 sources
    
    # Match case mentions to chunks
    case_matches = match_case_mentions_to_chunks(case_mentions, retrieved_chunks)
    
    # Format citations
    citations = []
    for mention, matches in case_matches.items():
        if not matches:
            continue
            
        # Use the top match for citation
        top_match = matches[0]
        
        # Format the citation text
        date = top_match.get('date', 'n.d.')
        title = top_match.get('title', 'Unknown Case')
        citation_text = f"{mention} ({date})"
        
        citation = {
            'mention': mention,
            'case_number': top_match.get('case_number', 'Unknown'),
            'title': title,
            'date': date,
            'citation_text': citation_text,
            'score': top_match.get('score', 0.0)
        }
        
        citations.append(citation)
    
    return citations

def enrich_answer_with_citations(answer: str, citations: List[Dict[str, Any]]) -> str:
    """
    Enrich an answer with formal citations.
    
    Args:
        answer: Generated answer text
        citations: List of citation dictionaries
        
    Returns:
        Answer text with added citations
    """
    if not citations:
        return answer
    
    # Add citations section
    citation_section = "\n\nSources:\n"
    for i, citation in enumerate(citations):
        citation_section += f"{i+1}. {citation['citation_text']}\n"
    
    return answer + citation_section 