"""
PostgreSQL with pgvector Database Manager
Handle vector storage and retrieval
"""

import os
from typing import List, Dict, Optional, Tuple
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from pgvector.psycopg2 import register_vector
import numpy as np
from datetime import datetime


class VectorDatabase:
    """Manage PostgreSQL database with pgvector extension"""
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        database: str = None,
        user: str = None,
        password: str = None,
        vector_dimension: int = 384
    ):
        """
        Initialize database connection
        
        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: Database name
            user: Username
            password: Password
            vector_dimension: Dimension of embeddings
        """
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.port = port or int(os.getenv("POSTGRES_PORT", 5432))
        self.database = database or os.getenv("POSTGRES_DB", "maggot_chatbot")
        self.user = user or os.getenv("POSTGRES_USER", "postgres")
        self.password = password or os.getenv("POSTGRES_PASSWORD", "")
        self.vector_dimension = vector_dimension
        
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            # Register pgvector type
            register_vector(self.conn)
            
            print(f"✅ Connected to PostgreSQL database: {self.database}")
            return True
        
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✅ Database connection closed")
    
    def create_extension(self):
        """Create pgvector extension"""
        try:
            self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            self.conn.commit()
            print("✅ pgvector extension enabled")
            return True
        except Exception as e:
            print(f"❌ Error creating extension: {e}")
            self.conn.rollback()
            return False
    
    def create_tables(self):
        """Create tables for document and chunk storage"""
        try:
            # Documents table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    filepath TEXT,
                    file_size INTEGER,
                    total_chunks INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB,
                    full_text TEXT
                );
            """)
            
            # Chunks table with vector embeddings
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS chunks (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    char_count INTEGER,
                    embedding vector({self.vector_dimension}),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create index for vector similarity search
            # Note: pgvector 0.5.0+ supports up to 16000 dimensions
            # Older versions limited to 2000 dimensions
            if self.vector_dimension <= 2000:
                # Use HNSW for dimensions <= 2000
                self.cursor.execute("""
                    CREATE INDEX IF NOT EXISTS chunks_embedding_idx 
                    ON chunks USING hnsw (embedding vector_cosine_ops);
                """)
                print(f"✅ Created HNSW index for {self.vector_dimension} dimensions")
            else:
                # For higher dimensions, skip index (will use sequential scan)
                # This is slower but works for any dimension
                print(f"⚠️  Skipping vector index (dimension {self.vector_dimension} > 2000)")
                print(f"   Queries will use sequential scan (slower but works)")
            
            # Create index for document lookup
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS chunks_document_id_idx 
                ON chunks(document_id);
            """)
            
            self.conn.commit()
            print("✅ Tables created successfully")
            return True
        
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            self.conn.rollback()
            return False
    
    def insert_document(self, filename: str, filepath: str, file_size: int, 
                       total_chunks: int, metadata: Dict = None, full_text: str = "") -> int:
        """
        Insert a new document record
        
        Returns:
            Document ID
        """
        try:
            self.cursor.execute("""
                INSERT INTO documents (filename, filepath, file_size, total_chunks, metadata, full_text)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (filename, filepath, file_size, total_chunks, psycopg2.extras.Json(metadata or {}), full_text))
            
            doc_id = self.cursor.fetchone()['id']
            self.conn.commit()
            
            print(f"✅ Document inserted with ID: {doc_id}")
            return doc_id
        
        except Exception as e:
            print(f"❌ Error inserting document: {e}")
            self.conn.rollback()
            return None
    
    def insert_chunks(self, document_id: int, chunks: List[Dict]):
        """
        Insert multiple chunks with embeddings
        
        Args:
            document_id: Parent document ID
            chunks: List of chunk dictionaries with 'text', 'embedding', etc.
        """
        try:
            values = [
                (
                    document_id,
                    chunk.get('chunk_id', i),
                    chunk['text'],
                    chunk.get('char_count', len(chunk['text'])),
                    chunk['embedding'],  # pgvector will handle the list
                    psycopg2.extras.Json(chunk.get('metadata', {}))
                )
                for i, chunk in enumerate(chunks)
            ]
            
            execute_values(
                self.cursor,
                """
                INSERT INTO chunks (document_id, chunk_index, text, char_count, embedding, metadata)
                VALUES %s
                """,
                values
            )
            
            self.conn.commit()
            print(f"✅ Inserted {len(chunks)} chunks for document {document_id}")
            return True
        
        except Exception as e:
            print(f"❌ Error inserting chunks: {e}")
            self.conn.rollback()
            return False
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5, 
                         document_id: int = None) -> List[Dict]:
        """
        Search for similar chunks using cosine similarity
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            document_id: Optional filter by document ID
            
        Returns:
            List of similar chunks with similarity scores
        """
        try:
            query = """
                SELECT 
                    c.id,
                    c.text,
                    c.chunk_index,
                    c.metadata,
                    d.filename,
                    d.filepath,
                    1 - (c.embedding <=> %s::vector) as similarity
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
            """
            
            params = [query_embedding]
            
            if document_id:
                query += " WHERE c.document_id = %s"
                params.append(document_id)
            
            query += " ORDER BY c.embedding <=> %s::vector LIMIT %s"
            params.extend([query_embedding, top_k])
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            return [dict(row) for row in results]
        
        except Exception as e:
            print(f"❌ Error in similarity search: {e}")
            return []
    
    def get_document(self, document_id: int) -> Optional[Dict]:
        """Get document by ID"""
        try:
            self.cursor.execute("""
                SELECT * FROM documents WHERE id = %s
            """, (document_id,))
            
            result = self.cursor.fetchone()
            return dict(result) if result else None
        
        except Exception as e:
            print(f"❌ Error getting document: {e}")
            return None
    
    def list_documents(self, limit: int = 100) -> List[Dict]:
        """List all documents"""
        try:
            self.cursor.execute("""
                SELECT id, filename, file_size, total_chunks, upload_date, metadata
                FROM documents
                ORDER BY upload_date DESC
                LIMIT %s
            """, (limit,))
            
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
            return []
    
    def delete_document(self, document_id: int) -> bool:
        """Delete document and all its chunks"""
        try:
            self.cursor.execute("""
                DELETE FROM documents WHERE id = %s
            """, (document_id,))
            
            self.conn.commit()
            print(f"✅ Document {document_id} deleted")
            return True
        
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
            self.conn.rollback()
            return False
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_documents,
                    SUM(total_chunks) as total_chunks,
                    SUM(file_size) as total_size
                FROM documents
            """)
            
            stats = dict(self.cursor.fetchone())
            return stats
        
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}
