"""
Azure OpenAI Embedding Generator
Support for Azure OpenAI embeddings API
"""

import os
import requests
from typing import List, Dict
import numpy as np


class AzureOpenAIEmbedding:
    """Generate embeddings using Azure OpenAI API"""
    
    def __init__(
        self,
        api_key: str = None,
        endpoint: str = None,
        deployment: str = None,
        api_version: str = None,
        dimension: int = 3072
    ):
        """
        Initialize Azure OpenAI embedding
        
        Args:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint URL
            deployment: Deployment name (e.g., text-embedding-3-large)
            api_version: API version (e.g., 2023-05-15)
            dimension: Embedding dimension (3072 for text-embedding-3-large)
        """
        self.api_key = api_key or os.getenv("AZURE_EMBEDDING_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_EMBEDDING_ENDPOINT")
        self.deployment = deployment or os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        self.api_version = api_version or os.getenv("AZURE_EMBEDDING_API_VERSION", "2023-05-15")
        self.dimension = dimension
        
        # Validate configuration
        if not self.api_key:
            raise ValueError("Azure OpenAI API key is required")
        
        # Build endpoint URL if not provided
        if not self.endpoint:
            base_url = os.getenv("AZURE_OPENAI_BASE_URL", "https://splace.openai.azure.com")
            self.endpoint = f"{base_url}/openai/deployments/{self.deployment}/embeddings?api-version={self.api_version}"
        
        print(f"✅ Azure OpenAI Embedding initialized")
        print(f"   Deployment: {self.deployment}")
        print(f"   Dimension: {self.dimension}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text using Azure OpenAI
        
        Args:
            text: Input text
            
        Returns:
            Numpy array of embedding
        """
        try:
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "input": text
            }
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            result = response.json()
            embedding = result["data"][0]["embedding"]
            
            return np.array(embedding)
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Azure OpenAI API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
            raise
        
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 16) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batched)
        
        Args:
            texts: List of texts
            batch_size: Number of texts to process at once (Azure limit: 16)
            
        Returns:
            Numpy array of embeddings
        """
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                headers = {
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "input": batch
                }
                
                response = requests.post(
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                response.raise_for_status()
                
                result = response.json()
                
                # Extract embeddings in order
                batch_embeddings = [item["embedding"] for item in result["data"]]
                all_embeddings.extend(batch_embeddings)
                
                print(f"   Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            except requests.exceptions.RequestException as e:
                print(f"❌ Azure OpenAI API error in batch {i//batch_size + 1}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"   Response: {e.response.text}")
                raise
        
        return np.array(all_embeddings)
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Add Azure OpenAI embeddings to chunks
        
        Args:
            chunks: List of chunk dictionaries from TextChunker
            
        Returns:
            List of chunks with embeddings added
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.generate_embeddings_batch(texts)
        
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()  # Convert to list for JSON
        
        return chunks
