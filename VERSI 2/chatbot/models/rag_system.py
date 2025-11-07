"""
RAG (Retrieval Augmented Generation) System
Combine vector search with LLM generation
Supports both OpenAI and Azure OpenAI
"""

import os
from typing import List, Dict
from openai import OpenAI, AzureOpenAI


class RAGSystem:
    """Retrieval Augmented Generation system"""
    
    def __init__(
        self,
        vector_db,
        embedder,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_azure: bool = None
    ):
        """
        Initialize RAG system
        
        Args:
            vector_db: VectorDatabase instance
            embedder: EmbeddingGenerator instance
            model: LLM model to use (ignored if use_azure=True)
            temperature: Generation temperature
            max_tokens: Maximum tokens in response
            use_azure: Use Azure OpenAI (reads from env if None)
        """
        self.vector_db = vector_db
        self.embedder = embedder
        
        # Check if using Azure OpenAI
        if use_azure is None:
            use_azure = os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
        
        # Initialize OpenAI client (Azure or Standard)
        if use_azure:
            print("🔵 Using Azure OpenAI for chatbot/LLM")
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_CHATBOT_API_KEY"),
                api_version=os.getenv("AZURE_CHATBOT_API_VERSION", "2024-02-01"),
                azure_endpoint=os.getenv("AZURE_CHATBOT_ENDPOINT")
            )
            self.model = os.getenv("AZURE_CHATBOT_DEPLOYMENT", "gpt-4o-mini-2")
        else:
            print("🟢 Using Standard OpenAI for chatbot/LLM")
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = model
        
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        print(f"✅ RAG System initialized with model: {self.model}")
    
    def retrieve_context(
        self, 
        query: str, 
        top_k: int = 5,
        document_id: int = None,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        Retrieve relevant context from vector database
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            document_id: Optional filter by document
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of relevant chunks
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_embedding(query)
        
        # Search vector database
        results = self.vector_db.similarity_search(
            query_embedding=query_embedding.tolist(),
            top_k=top_k,
            document_id=document_id
        )
        
        # Filter by similarity threshold
        filtered_results = [
            r for r in results 
            if r.get('similarity', 0) >= min_similarity
        ]
        
        return filtered_results
    
    def format_context(self, retrieved_chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into context string
        
        Args:
            retrieved_chunks: List of chunks from retrieval
            
        Returns:
            Formatted context string
        """
        if not retrieved_chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(
                f"[Context {i}] (from {chunk['filename']}, similarity: {chunk['similarity']:.2f})\n"
                f"{chunk['text']}\n"
            )
        
        return "\n".join(context_parts)
    
    def generate_answer(
        self,
        query: str,
        context: str,
        system_prompt: str = None,
        chat_history: List[Dict] = None
    ) -> Dict:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User query
            context: Retrieved context
            system_prompt: Custom system prompt
            chat_history: Previous conversation history
            
        Returns:
            Dictionary with answer and metadata
        """
        # Default system prompt (generic for any topic)
        if system_prompt is None:
            system_prompt = """You are a helpful AI assistant that answers questions based on provided documents.
Use the provided context to answer questions accurately and comprehensively.
If the context doesn't contain enough information, say so and provide what you can based on the available context.
Always cite the source when using information from the context.
Be clear, concise, and informative in your answers.
Answer in Indonesian or English based on the question language."""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)
        
        # Add current query with context
        user_message = f"""Context:
{context}

Question: {query}

Please provide a detailed answer based on the context above."""
        
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "model": self.model,
                "tokens_used": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason
            }
        
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "model": self.model,
                "tokens_used": 0,
                "finish_reason": "error"
            }
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        document_id: int = None,
        min_similarity: float = 0.3,
        system_prompt: str = None,
        chat_history: List[Dict] = None,
        return_sources: bool = True
    ) -> Dict:
        """
        Complete RAG pipeline: retrieve + generate
        
        Args:
            question: User question
            top_k: Number of chunks to retrieve
            document_id: Optional document filter
            min_similarity: Minimum similarity threshold
            system_prompt: Custom system prompt
            chat_history: Previous conversation
            return_sources: Include source chunks in response
            
        Returns:
            Complete response with answer and sources
        """
        print(f"🔍 Processing query: {question[:100]}...")
        
        # Step 1: Retrieve relevant context
        print(f"   Retrieving top {top_k} relevant chunks...")
        retrieved_chunks = self.retrieve_context(
            query=question,
            top_k=top_k,
            document_id=document_id,
            min_similarity=min_similarity
        )
        
        print(f"   Found {len(retrieved_chunks)} relevant chunks")
        
        # Step 2: Format context
        context = self.format_context(retrieved_chunks)
        
        # Step 3: Generate answer
        print(f"   Generating answer with {self.model}...")
        answer_data = self.generate_answer(
            query=question,
            context=context,
            system_prompt=system_prompt,
            chat_history=chat_history
        )
        
        # Build response
        response = {
            "question": question,
            "answer": answer_data["answer"],
            "model": answer_data["model"],
            "tokens_used": answer_data["tokens_used"],
            "num_sources": len(retrieved_chunks)
        }
        
        if return_sources:
            response["sources"] = [
                {
                    "text": chunk["text"],
                    "filename": chunk["filename"],
                    "similarity": chunk["similarity"],
                    "chunk_index": chunk["chunk_index"]
                }
                for chunk in retrieved_chunks
            ]
        
        print(f"✅ Query complete! Used {answer_data['tokens_used']} tokens")
        
        return response
    
    def chat(
        self,
        messages: List[Dict],
        top_k: int = 5,
        document_id: int = None,
        system_prompt: str = None
    ) -> Dict:
        """
        Multi-turn conversation with RAG
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            top_k: Number of chunks to retrieve
            document_id: Optional document filter
            system_prompt: Custom system prompt
            
        Returns:
            Response with answer
        """
        # Get the last user message as query
        user_messages = [m for m in messages if m["role"] == "user"]
        if not user_messages:
            return {"answer": "No user message found", "error": True}
        
        last_query = user_messages[-1]["content"]
        
        # Use query method with chat history
        chat_history = messages[:-1]  # All messages except the last one
        
        return self.query(
            question=last_query,
            top_k=top_k,
            document_id=document_id,
            system_prompt=system_prompt,
            chat_history=chat_history
        )
