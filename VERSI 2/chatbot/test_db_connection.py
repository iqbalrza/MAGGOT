"""
Quick Database Connection Test
Test PostgreSQL connection and pgvector extension
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection"""
    print("="*80)
    print("🔍 TESTING DATABASE CONNECTION")
    print("="*80)
    
    # Import vector database
    try:
        from models.vector_db import VectorDatabase
        print("✅ VectorDatabase module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import VectorDatabase: {e}")
        return False
    
    # Get configuration
    print("\n📋 Database Configuration:")
    print(f"   Host: {os.getenv('POSTGRES_HOST', 'localhost')}")
    print(f"   Port: {os.getenv('POSTGRES_PORT', '5432')}")
    print(f"   Database: {os.getenv('POSTGRES_DB', 'maggot_chatbot')}")
    print(f"   User: {os.getenv('POSTGRES_USER', 'postgres')}")
    print(f"   Vector Dimension: {os.getenv('VECTOR_DIMENSION', '3072')}")
    
    # Create database instance
    vector_dim = int(os.getenv("VECTOR_DIMENSION", 3072))
    db = VectorDatabase(vector_dimension=vector_dim)
    
    # Test connection
    print("\n🔌 Testing connection...")
    if not db.connect():
        print("❌ Connection failed!")
        return False
    
    # Get statistics
    print("\n📊 Database Statistics:")
    stats = db.get_stats()
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Total chunks: {stats.get('total_chunks', 0)}")
    print(f"   Total size: {stats.get('total_size', 0)} bytes")
    
    # List documents
    print("\n📁 Recent Documents:")
    docs = db.list_documents(limit=5)
    if docs:
        for doc in docs:
            print(f"   - {doc['filename']} ({doc['total_chunks']} chunks)")
    else:
        print("   (No documents uploaded yet)")
    
    # Close connection
    db.close()
    
    print("\n" + "="*80)
    print("✅ DATABASE CONNECTION TEST PASSED!")
    print("="*80)
    print("\n💡 Database is ready to use!")
    print("   Next: Start the chatbot API with 'python chatbot_api.py'")
    
    return True

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
