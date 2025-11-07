"""
Database Setup Script
Setup PostgreSQL database for chatbot system
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment
load_dotenv()

def check_postgres_running():
    """Check if PostgreSQL is accessible"""
    print("🔍 Checking PostgreSQL connection...")
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            database="postgres",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "")
        )
        conn.close()
        print("✅ PostgreSQL is running!")
        return True
    except Exception as e:
        print(f"❌ Cannot connect to PostgreSQL: {e}")
        print("\n💡 Make sure:")
        print("   1. PostgreSQL is installed and running")
        print("   2. Credentials in .env are correct")
        return False

def create_database():
    """Create database if not exists"""
    db_name = os.getenv("POSTGRES_DB", "maggot_chatbot")
    print(f"\n📦 Creating database '{db_name}'...")
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            database="postgres",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "")
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        
        if exists:
            print(f"✅ Database '{db_name}' already exists")
        else:
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Database '{db_name}' created!")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def install_pgvector():
    """Install pgvector extension"""
    db_name = os.getenv("POSTGRES_DB", "maggot_chatbot")
    print(f"\n🔌 Installing pgvector extension...")
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            database=db_name,
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "")
        )
        cur = conn.cursor()
        
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        
        print("✅ pgvector extension installed!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error installing pgvector: {e}")
        print("\n💡 Make sure pgvector is installed on your system:")
        print("   Windows: Download from https://github.com/pgvector/pgvector/releases")
        print("   Linux: sudo apt install postgresql-*-pgvector")
        print("   macOS: brew install pgvector")
        return False

def setup_tables():
    """Setup database tables"""
    print(f"\n📋 Setting up tables...")
    
    try:
        # Import and run vector_db setup
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from models.vector_db import VectorDatabase
        
        vector_dim = int(os.getenv("VECTOR_DIMENSION", 3072))
        db = VectorDatabase(vector_dimension=vector_dim)
        
        if db.connect():
            db.create_extension()
            db.create_tables()
            
            stats = db.get_stats()
            print(f"\n📊 Database Statistics:")
            print(f"   Total documents: {stats.get('total_documents', 0)}")
            print(f"   Total chunks: {stats.get('total_chunks', 0)}")
            
            db.close()
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ Error setting up tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main setup function"""
    print("="*80)
    print("🚀 DATABASE SETUP FOR CHATBOT SYSTEM")
    print("="*80)
    
    # Step 1: Check PostgreSQL
    if not check_postgres_running():
        print("\n❌ Setup failed: PostgreSQL is not accessible")
        return 1
    
    # Step 2: Create database
    if not create_database():
        print("\n❌ Setup failed: Could not create database")
        return 1
    
    # Step 3: Install pgvector
    if not install_pgvector():
        print("\n❌ Setup failed: Could not install pgvector extension")
        return 1
    
    # Step 4: Setup tables
    if not setup_tables():
        print("\n❌ Setup failed: Could not setup tables")
        return 1
    
    # Success!
    print("\n" + "="*80)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*80)
    print("\n📋 Next steps:")
    print("   1. Start the server: python chatbot_api.py")
    print("   2. Test with Postman (see POSTMAN_TESTING_GUIDE.md)")
    print("\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
