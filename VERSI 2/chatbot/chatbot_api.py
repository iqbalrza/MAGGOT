"""
Chatbot API Server
REST API for PDF upload and RAG chatbot
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_processor import PDFProcessor
from utils.text_processor import TextChunker, EmbeddingGenerator
from utils.azure_embeddings import AzureOpenAIEmbedding
from models.vector_db import VectorDatabase
from models.rag_system import RAGSystem

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Flask configuration for large uploads and keep-alive
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Configuration
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./storage/uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50)) * 1024 * 1024  # MB to bytes
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize components (lazy loading)
pdf_processor = None
text_chunker = None
embedder = None
vector_db = None
rag_system = None


def init_components():
    """Initialize all components (call on first request)"""
    global pdf_processor, text_chunker, embedder, vector_db, rag_system
    
    if pdf_processor is None:
        print("🚀 Initializing chatbot components...")
        
        # PDF Processor with OCR
        tesseract_cmd = os.getenv("TESSERACT_CMD", None)
        ocr_lang = os.getenv("OCR_LANG", "eng+ind")  # English + Indonesian
        pdf_processor = PDFProcessor(tesseract_cmd=tesseract_cmd, lang=ocr_lang)
        
        # Text Chunker
        chunk_size = int(os.getenv("CHUNK_SIZE", 500))
        chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))
        text_chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # Embedder - Check if using Azure OpenAI
        use_azure = os.getenv("USE_AZURE_OPENAI", "False").lower() == "true"
        
        if use_azure:
            print("🔵 Using Azure OpenAI embeddings...")
            embedder = AzureOpenAIEmbedding()
        else:
            print("🟢 Using Sentence Transformers embeddings...")
            embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
        
        # Vector Database
        vector_dimension = int(os.getenv("VECTOR_DIMENSION", embedder.dimension))
        vector_db = VectorDatabase(vector_dimension=vector_dimension)
        if not vector_db.connect():
            raise Exception("Failed to connect to database")
        
        # RAG System - will auto-detect Azure chatbot settings
        temperature = float(os.getenv("TEMPERATURE", 0.7))
        max_tokens = int(os.getenv("MAX_TOKENS", 1000))
        
        rag_system = RAGSystem(
            vector_db=vector_db,
            embedder=embedder,
            temperature=temperature,
            max_tokens=max_tokens,
            use_azure=use_azure  # Will use Azure chatbot if True
        )
        
        print("✅ All components initialized!")


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Maggot BSF Chatbot API",
        "version": "1.0.0"
    })


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """
    Upload and process PDF file
    
    Returns:
        document_id and processing stats
    """
    import time
    start_time = time.time()
    
    try:
        init_components()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Only PDF allowed"}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        print(f"📄 Processing uploaded file: {filename}")
        print(f"   Saving file...")
        
        try:
            file.save(filepath)
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
        
        file_size = os.path.getsize(filepath)
        print(f"   File size: {file_size / 1024:.2f} KB")
        
        # Check if should skip OCR (for faster processing)
        skip_ocr = os.getenv("SKIP_OCR", "false").lower() == "true"
        
        # Process PDF with OCR
        if skip_ocr:
            print(f"   ⚡ Fast mode: Extracting text only (no OCR)...")
        else:
            print(f"   Extracting text with OCR (this may take a while)...")
        
        try:
            pdf_result = pdf_processor.process_pdf_full(filepath, skip_ocr=skip_ocr)
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            # Clean up file
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"Failed to process PDF: {str(e)}"}), 500
        
        # Chunk text
        print(f"   Chunking text ({len(pdf_result['combined_text'])} chars)...")
        try:
            chunks = text_chunker.chunk_text(
                text=pdf_result["combined_text"],
                metadata={
                    "filename": filename,
                    "num_images": pdf_result["num_images"]
                }
            )
            print(f"   Created {len(chunks)} chunks")
        except Exception as e:
            print(f"❌ Error chunking text: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"Failed to chunk text: {str(e)}"}), 500
        
        # Generate embeddings
        print(f"   Generating embeddings for {len(chunks)} chunks...")
        try:
            chunks_with_embeddings = embedder.embed_chunks(chunks)
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"Failed to generate embeddings: {str(e)}\nCheck Azure OpenAI connection"}), 500
        
        # Store in database
        print(f"   Storing in database...")
        try:
            doc_id = vector_db.insert_document(
                filename=filename,
                filepath=filepath,
                file_size=file_size,
                total_chunks=len(chunks_with_embeddings),
                metadata={
                    "num_images": pdf_result["num_images"],
                    "text_length": len(pdf_result["full_text"]),
                    "ocr_text_length": len(pdf_result.get("ocr_text", ""))
                },
                full_text=pdf_result["combined_text"]
            )
            
            vector_db.insert_chunks(doc_id, chunks_with_embeddings)
        except Exception as e:
            print(f"❌ Error storing in database: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"Failed to store in database: {str(e)}"}), 500
        
        processing_time = time.time() - start_time
        print(f"✅ Document processed successfully! ID: {doc_id}")
        print(f"   Processing time: {processing_time:.2f}s")
        
        return jsonify({
            "success": True,
            "document_id": doc_id,
            "filename": filename,
            "file_size": file_size,
            "total_chunks": len(chunks_with_embeddings),
            "processing_time": f"{processing_time:.2f}s",
            "metadata": {
                "num_images": pdf_result["num_images"],
                "text_length": len(pdf_result["full_text"]),
                "ocr_text_length": len(pdf_result.get("ocr_text", ""))
            }
        }), 201
    
    except Exception as e:
        print(f"❌ Error processing upload: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/query', methods=['POST'])
def query_chatbot():
    """
    Query the chatbot
    
    Request body:
        {
            "question": "Your question here",
            "top_k": 5,  # optional
            "document_id": 1,  # optional
            "min_similarity": 0.3  # optional
        }
    
    Returns:
        answer and sources
    """
    try:
        init_components()
        
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({"error": "No question provided"}), 400
        
        question = data['question']
        top_k = data.get('top_k', 5)
        document_id = data.get('document_id', None)
        min_similarity = data.get('min_similarity', 0.3)
        
        # Query RAG system
        response = rag_system.query(
            question=question,
            top_k=top_k,
            document_id=document_id,
            min_similarity=min_similarity,
            return_sources=True
        )
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"❌ Error processing query: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Multi-turn chat conversation
    
    Request body:
        {
            "messages": [
                {"role": "user", "content": "First question"},
                {"role": "assistant", "content": "First answer"},
                {"role": "user", "content": "Follow-up question"}
            ],
            "top_k": 5,  # optional
            "document_id": 1  # optional
        }
    """
    try:
        init_components()
        
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({"error": "No messages provided"}), 400
        
        messages = data['messages']
        top_k = data.get('top_k', 5)
        document_id = data.get('document_id', None)
        
        # Chat with RAG system
        response = rag_system.chat(
            messages=messages,
            top_k=top_k,
            document_id=document_id
        )
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"❌ Error processing chat: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    try:
        init_components()
        
        limit = request.args.get('limit', 100, type=int)
        documents = vector_db.list_documents(limit=limit)
        
        return jsonify({
            "documents": documents,
            "count": len(documents)
        }), 200
    
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get document details by ID"""
    try:
        init_components()
        
        document = vector_db.get_document(doc_id)
        
        if document:
            return jsonify(document), 200
        else:
            return jsonify({"error": "Document not found"}), 404
    
    except Exception as e:
        print(f"❌ Error getting document: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document and all its chunks"""
    try:
        init_components()
        
        success = vector_db.delete_document(doc_id)
        
        if success:
            return jsonify({"success": True, "message": f"Document {doc_id} deleted"}), 200
        else:
            return jsonify({"error": "Failed to delete document"}), 500
    
    except Exception as e:
        print(f"❌ Error deleting document: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        init_components()
        
        stats = vector_db.get_stats()
        
        return jsonify(stats), 200
    
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({"error": "File too large. Maximum size is 50MB"}), 413


if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    print("="*80)
    print("🤖 MAGGOT BSF CHATBOT API SERVER")
    print("="*80)
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print("="*80)
    print("\n✨ Starting server...\n")
    
    app.run(host=host, port=port, debug=debug)
