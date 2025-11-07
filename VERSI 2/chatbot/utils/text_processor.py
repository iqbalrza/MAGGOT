"""
Text Chunking and Embedding
Split text into chunks and generate vector embeddings
"""

import os
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken


class TextChunker:
    """Split text into manageable chunks"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize text chunker
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with metadata
        
        Args:
            text: Text to split
            metadata: Additional metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries
        """
        chunks = self.splitter.split_text(text)
        
        chunk_data = []
        for i, chunk in enumerate(chunks):
            chunk_dict = {
                "chunk_id": i,
                "text": chunk,
                "char_count": len(chunk),
                "metadata": metadata or {}
            }
            chunk_data.append(chunk_dict)
        
        return chunk_data
    
    def get_token_count(self, text: str, model: str = "gpt-4") -> int:
        """
        Count tokens in text for a specific model
        
        Args:
            text: Input text
            model: Model name (gpt-4, gpt-3.5-turbo, etc.)
            
        Returns:
            Token count
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except:
            # Fallback: rough estimate (4 chars = 1 token)
            return len(text) // 4


class EmbeddingGenerator:
    """Generate vector embeddings for text chunks"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator
        
        Args:
            model_name: Sentence transformer model name
                       Options:
                       - "all-MiniLM-L6-v2" (384 dim, fast)
                       - "all-mpnet-base-v2" (768 dim, better quality)
                       - "paraphrase-multilingual-MiniLM-L12-v2" (384 dim, multilingual)
        """
        print(f"🔧 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"✅ Model loaded! Embedding dimension: {self.dimension}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Numpy array of embeddings
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batched for efficiency)
        
        Args:
            texts: List of texts
            batch_size: Number of texts to process at once
            
        Returns:
            Numpy array of embeddings
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        return embeddings
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Add embeddings to chunk dictionaries
        
        Args:
            chunks: List of chunk dictionaries from TextChunker
            
        Returns:
            List of chunks with embeddings added
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.generate_embeddings_batch(texts)
        
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()  # Convert to list for JSON serialization
        
        return chunks


class OpenAIEmbedding:
    """Alternative: Use OpenAI embeddings API"""
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedding
        
        Args:
            api_key: OpenAI API key
            model: Embedding model (text-embedding-3-small or text-embedding-3-large)
        """
        from openai import OpenAI
        
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        
        # Dimensions: text-embedding-3-small = 1536, text-embedding-3-large = 3072
        self.dimension = 1536 if "small" in model else 3072
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Add OpenAI embeddings to chunks"""
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.generate_embeddings_batch(texts)
        
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i]
        
        return chunks
