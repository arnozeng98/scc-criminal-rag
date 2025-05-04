"""
Module for generating answers using LLMs with retrieved context.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import time
import requests
import backoff

from backend.src.config import RAG_LOG_FILE
from backend.src.utils.log_utils import setup_logging
from .retriever import CaseRetriever, prepare_context
from .citation import format_citations

# Set up logging
logger = setup_logging(RAG_LOG_FILE)

class OpenAIGenerator:
    """
    Generator using OpenAI's models for answering with retrieved context.
    """
    
    def __init__(
        self, 
        model_name: str = "gpt-4-turbo", 
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1000
    ):
        """
        Initialize the OpenAI generator.
        
        Args:
            model_name: Name of the OpenAI model to use
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            temperature: Temperature for generation (lower = more deterministic)
            max_tokens: Maximum number of tokens to generate
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and not found in environment variables")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        logger.info(f"Initialized OpenAI generator with model: {model_name}")
    
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, Exception),
        max_tries=5,
        giveup=lambda e: "Invalid API key" in str(e)
    )
    def generate(self, prompt: str) -> str:
        """
        Generate a response using OpenAI's API.
        
        Args:
            prompt: Full prompt text including context and query
            
        Returns:
            Generated response text
        """
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            error_msg = f"Error from OpenAI API: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        return content

class AnthropicGenerator:
    """
    Generator using Anthropic's Claude models for answering with retrieved context.
    """
    
    def __init__(
        self, 
        model_name: str = "claude-3-opus-20240229", 
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1000
    ):
        """
        Initialize the Anthropic generator.
        
        Args:
            model_name: Name of the Anthropic model to use
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY environment variable)
            temperature: Temperature for generation (lower = more deterministic)
            max_tokens: Maximum number of tokens to generate
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if not self.api_key:
            raise ValueError("Anthropic API key not provided and not found in environment variables")
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        logger.info(f"Initialized Anthropic generator with model: {model_name}")
    
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, Exception),
        max_tries=5,
        giveup=lambda e: "Invalid API key" in str(e)
    )
    def generate(self, prompt: str) -> str:
        """
        Generate a response using Anthropic's API.
        
        Args:
            prompt: Full prompt text including context and query
            
        Returns:
            Generated response text
        """
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            error_msg = f"Error from Anthropic API: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        result = response.json()
        content = result["content"][0]["text"]
        
        return content

class RAGGenerator:
    """
    RAG generator combining retrieval and generation.
    """
    
    def __init__(
        self,
        retriever: Optional[CaseRetriever] = None,
        generator: Optional[Any] = None,
        vector_store_dir: Optional[str] = None
    ):
        """
        Initialize the RAG generator.
        
        Args:
            retriever: Case retriever instance (optional)
            generator: Text generator instance (optional)
            vector_store_dir: Directory containing the vector store (needed if retriever not provided)
        """
        # Initialize retriever
        if retriever:
            self.retriever = retriever
        else:
            if not vector_store_dir:
                raise ValueError("Must provide either a retriever or a vector_store_dir")
            self.retriever = CaseRetriever(vector_store_dir)
        
        # Initialize generator - prefer Claude if available, fallback to OpenAI
        if generator:
            self.generator = generator
        else:
            if os.environ.get("ANTHROPIC_API_KEY"):
                try:
                    self.generator = AnthropicGenerator()
                    logger.info("Using Anthropic Claude as generator")
                except Exception as e:
                    logger.warning(f"Failed to initialize Anthropic generator: {e}")
                    self.generator = OpenAIGenerator()
                    logger.info("Falling back to OpenAI as generator")
            else:
                self.generator = OpenAIGenerator()
                logger.info("Using OpenAI as generator")
    
    def generate_prompt(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate a prompt for the LLM using the query and retrieved chunks.
        
        Args:
            query: User query
            retrieved_chunks: Retrieved context chunks
            
        Returns:
            Formatted prompt
        """
        # Prepare context
        context = prepare_context(retrieved_chunks)
        
        # Create the system instructions
        system_instructions = """
You are a legal assistant specialized in Canadian Supreme Court criminal cases. Your role is to provide accurate, well-informed responses about Canadian criminal law and cases, based ONLY on the provided context.

Guidelines:
1. Base your answers EXCLUSIVELY on the information in the provided context sections
2. If the context doesn't contain enough information to answer the question fully, acknowledge this limitation explicitly
3. Do not invent or hallucinate information not present in the context
4. When referencing cases, include proper citations (case name, year, and court)
5. Maintain a professional, objective tone appropriate for legal analysis
6. Structure complex answers with clear headings and bullet points where appropriate

Remember, your credibility depends on the accuracy of your information and transparent acknowledgment of limitations in the provided context.
"""

        # Combine into the final prompt
        prompt = f"{system_instructions}\n\n{context}\n\nQuestion: {query}\n\nAnswer:"
        
        return prompt
    
    def answer_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Answer a query using RAG.
        
        Args:
            query: User query
            top_k: Number of context chunks to retrieve
            
        Returns:
            Dictionary containing the answer and source citations
        """
        start_time = time.time()
        
        try:
            # Retrieve relevant chunks
            retrieved_chunks = self.retriever.retrieve(query, top_k)
            retrieval_time = time.time() - start_time
            
            if not retrieved_chunks:
                logger.warning(f"No relevant chunks found for query: {query}")
                return {
                    "answer": "I couldn't find relevant information to answer your question about Canadian criminal law cases. Please try rephrasing your question or asking about a different topic.",
                    "citations": [],
                    "retrieval_time": retrieval_time,
                    "total_time": time.time() - start_time
                }
            
            # Generate prompt
            prompt = self.generate_prompt(query, retrieved_chunks)
            
            # Generate answer
            answer = self.generator.generate(prompt)
            
            # Format citations
            citations = format_citations(retrieved_chunks, answer)
            
            total_time = time.time() - start_time
            
            logger.info(f"Answered query in {total_time:.2f}s (retrieval: {retrieval_time:.2f}s)")
            
            return {
                "answer": answer,
                "citations": citations,
                "context": [c.get('metadata', {}) for c in retrieved_chunks],
                "retrieval_time": retrieval_time,
                "total_time": total_time
            }
            
        except Exception as e:
            logger.error(f"Error answering query '{query}': {e}")
            total_time = time.time() - start_time
            
            return {
                "answer": "I encountered an error while trying to answer your question. Please try again later.",
                "error": str(e),
                "total_time": total_time
            } 