import os
import base64
import uuid
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import mimetypes
import pickle

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB for large PDFs
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CHUNK_FOLDER'] = 'chunks'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CHUNK_FOLDER'], exist_ok=True)

# Initialize Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    print("="*50)
    print("⚠️  ERROR: GROQ_API_KEY not found!")
    print("Please create a .env file with your API key")
    print("="*50)
    exit(1)

try:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    print("✅ Groq client initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Groq: {e}")
    exit(1)

# Try to load embedding model for RAG
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    RAG_AVAILABLE = True
    print("✅ RAG (semantic search) initialized successfully")
except Exception as e:
    print(f"⚠️ RAG not available: {e}")
    print("   Install: pip install sentence-transformers faiss-cpu numpy")
    RAG_AVAILABLE = False

# Store conversations with chunked content
conversations = {}

def chunk_text(text, chunk_size=1500, overlap=300):
    """
    Split text into overlapping chunks for better retrieval.
    Chunk size ~1500 characters, overlap 300 characters between chunks.
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        
        # Only add non-empty chunks
        if chunk.strip():
            chunks.append(chunk.strip())
        
        start += chunk_size - overlap
    
    return chunks

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using multiple methods"""
    text = ""
    
    # Method 1: Try PyPDF2
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            print(f"📄 PDF has {num_pages} pages (PyPDF2)")
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    # Add page markers for reference
                    text += f"\n=== Page {page_num + 1} ===\n{page_text}\n"
        
        if text.strip():
            print(f"✅ Extracted {len(text)} characters using PyPDF2")
            return text
    except Exception as e:
        print(f"⚠️ PyPDF2 failed: {e}")
    
    # Method 2: Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            print(f"📄 PDF has {num_pages} pages (pdfplumber)")
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += f"\n=== Page {page_num} ===\n{page_text}\n"
        
        if text.strip():
            print(f"✅ Extracted {len(text)} characters using pdfplumber")
            return text
    except Exception as e:
        print(f"⚠️ pdfplumber failed: {e}")
    
    return None

def create_chunk_embeddings(chunks):
    """Create embeddings for chunks using sentence-transformers"""
    if not RAG_AVAILABLE:
        return None
    
    try:
        embeddings = embedding_model.encode(chunks, show_progress_bar=True)
        return embeddings
    except Exception as e:
        print(f"❌ Embedding creation failed: {e}")
        return None

def save_chunks_with_embeddings(session_id, file_id, filename, chunks, embeddings):
    """Save chunks and their embeddings to disk"""
    chunk_data = {
        'filename': filename,
        'chunks': chunks,
        'embeddings': embeddings.tolist() if embeddings is not None else None,
        'timestamp': datetime.now().isoformat()
    }
    
    chunk_file = os.path.join(app.config['CHUNK_FOLDER'], f"{session_id}_{file_id}.pkl")
    with open(chunk_file, 'wb') as f:
        pickle.dump(chunk_data, f)
    
    return chunk_file

def load_chunks_with_embeddings(session_id, file_id):
    """Load chunks and embeddings from disk"""
    chunk_file = os.path.join(app.config['CHUNK_FOLDER'], f"{session_id}_{file_id}.pkl")
    
    if not os.path.exists(chunk_file):
        return None
    
    with open(chunk_file, 'rb') as f:
        chunk_data = pickle.load(f)
    
    return chunk_data

def search_relevant_chunks(query, all_chunks_data, top_k=5):
    """Search for relevant chunks using semantic similarity"""
    if not RAG_AVAILABLE or not all_chunks_data:
        return []
    
    results = []
    
    for file_data in all_chunks_data:
        if file_data.get('embeddings') is None:
            continue
        
        # Encode the query
        query_embedding = embedding_model.encode([query])
        
        # Get chunks and embeddings
        chunks = file_data['chunks']
        embeddings = np.array(file_data['embeddings'])
        
        # Calculate cosine similarity
        from numpy.linalg import norm
        query_norm = query_embedding / norm(query_embedding)
        embeddings_norm = embeddings / norm(embeddings, axis=1, keepdims=True)
        similarities = np.dot(embeddings_norm, query_norm.T).flatten()
        
        # Get top-k indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Only include if similarity > 0.3
                results.append({
                    'filename': file_data['filename'],
                    'chunk': chunks[idx],
                    'similarity': float(similarities[idx])
                })
    
    # Sort by similarity and return top-k
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results[:top_k]

def retrieve_relevant_context(message, session_id):
    """Retrieve relevant chunks from all uploaded files for the session"""
    if session_id not in conversations:
        return ""
    
    all_chunks_data = []
    for file_info in conversations[session_id].get('uploaded_files', []):
        chunk_data = load_chunks_with_embeddings(session_id, file_info['file_id'])
        if chunk_data:
            all_chunks_data.append(chunk_data)
    
    if not all_chunks_data:
        return ""
    
    # Search for relevant chunks
    relevant_chunks = search_relevant_chunks(message, all_chunks_data, top_k=8)
    
    if not relevant_chunks:
        return ""
    
    # Build context string
    context = "\n\n=== RELEVANT INFORMATION FROM YOUR DOCUMENTS ===\n\n"
    for i, chunk_info in enumerate(relevant_chunks, 1):
        context += f"[Source: {chunk_info['filename']} - Relevance: {chunk_info['similarity']:.2%}]\n"
        context += f"{chunk_info['chunk'][:1000]}\n\n"
        context += "-" * 50 + "\n\n"
    
    return context

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        print("\n" + "="*60)
        print("📨 RECEIVED CHAT REQUEST")
        print("="*60)
        
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id
        print(f"📌 Session ID: {session_id[:20]}...")
        
        # Get form data
        message = request.form.get('message', '')
        model = request.form.get('model', 'llama-3.3-70b-versatile')
        print(f"💬 Message: {message[:100] if message else '(empty)'}")
        print(f"🤖 Model: {model}")
        
        # Initialize conversation if needed
        if session_id not in conversations:
            conversations[session_id] = {
                'messages': [],
                'uploaded_files': []
            }
            print("✨ New conversation created")
        
        # Check for file upload
        file = request.files.get('file')
        response_text = ""
        
        if file and file.filename:
            print(f"📎 New file received: {file.filename}")
            
            # Save file temporarily
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            saved_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
            file.save(filepath)
            
            file_size = os.path.getsize(filepath)
            print(f"💾 File saved: {filepath} ({file_size/1024/1024:.2f} MB)")
            
            # Extract text from PDF
            print("📄 Extracting text from PDF...")
            extracted_text = extract_text_from_pdf(filepath)
            
            if extracted_text and len(extracted_text) > 100:
                print(f"✅ Extracted {len(extracted_text)} characters")
                
                # Chunk the text
                print("🔪 Chunking text into smaller pieces...")
                chunks = chunk_text(extracted_text, chunk_size=1500, overlap=300)
                print(f"✅ Created {len(chunks)} chunks")
                
                # Create embeddings if RAG is available
                embeddings = None
                if RAG_AVAILABLE:
                    print("🔍 Creating embeddings for semantic search...")
                    embeddings = create_chunk_embeddings(chunks)
                    if embeddings is not None:
                        print(f"✅ Created {len(embeddings)} embeddings")
                
                # Save chunks with embeddings
                file_id = str(uuid.uuid4())[:8]
                save_chunks_with_embeddings(session_id, file_id, filename, chunks, embeddings)
                
                # Store file info in conversation
                conversations[session_id]['uploaded_files'].append({
                    'file_id': file_id,
                    'filename': filename,
                    'num_chunks': len(chunks),
                    'uploaded_at': datetime.now().isoformat()
                })
                
                response_text = f"""✅ **File '{filename}' successfully processed!**

📊 Statistics:
- Total size: {file_size/1024/1024:.2f} MB
- Pages extracted: {len(extracted_text.split('=== Page')) - 1}
- Total characters: {len(extracted_text):,}
- Chunks created: {len(chunks)}
- Semantic search: {'✅ Enabled' if RAG_AVAILABLE else '❌ Disabled'}

🔍 You can now ask questions about this document. The system will search for relevant sections and provide accurate answers based on the content.

💡 **Try asking:**
- "What are the course outcomes for Calculus?"
- "List all programming languages taught"
- "Summarize the program structure" """
                
            else:
                response_text = f"❌ Could not extract text from '{filename}'. Please ensure it's a text-based PDF (not scanned)."
            
            # Clean up temporary file
            try:
                os.remove(filepath)
                print("🗑️ Temporary file cleaned up")
            except Exception as e:
                print(f"⚠️ Could not delete temp file: {e}")
        
        else:
            # Regular text message - retrieve relevant context
            print("💬 Processing text message with RAG...")
            
            if not message:
                return jsonify({'success': False, 'error': 'No message provided'}), 400
            
            # Retrieve relevant context from uploaded documents
            relevant_context = retrieve_relevant_context(message, session_id)
            
            if relevant_context:
                print(f"📚 Retrieved relevant context from documents")
                # Build prompt with context
                full_prompt = f"""You are an AI assistant with access to the user's uploaded documents.

Use the following retrieved sections from their documents to answer the question. 
If the answer is found in the excerpts, provide it accurately. 
If the information is not in the excerpts, say so honestly.

{relevant_context}

User's question: {message}

Answer based ONLY on the provided excerpts. Be specific and cite which section the information comes from."""
            else:
                print("⚠️ No relevant context found, answering without document reference")
                full_prompt = message
            
            # Get response from Groq
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.3,  # Lower temperature for factual answers
                max_tokens=2048
            )
            response_text = completion.choices[0].message.content
            
            # Add note if context was used
            if relevant_context:
                response_text += "\n\n---\n📚 *Answer based on your uploaded documents*"
        
        # Store conversation
        user_message_content = message if not file else f"[Uploaded file: {file.filename if file else 'unknown'}] {message}"
        conversations[session_id]['messages'].append({
            'role': 'user',
            'content': user_message_content,
            'timestamp': datetime.now().isoformat()
        })
        conversations[session_id]['messages'].append({
            'role': 'assistant',
            'content': response_text,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"📝 Response length: {len(response_text)} characters")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ CHAT ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history and delete chunk files"""
    try:
        session_id = session.get('session_id')
        if session_id and session_id in conversations:
            # Delete chunk files
            for file_info in conversations[session_id].get('uploaded_files', []):
                chunk_file = os.path.join(app.config['CHUNK_FOLDER'], f"{session_id}_{file_info['file_id']}.pkl")
                if os.path.exists(chunk_file):
                    os.remove(chunk_file)
            
            conversations[session_id] = {
                'messages': [],
                'uploaded_files': []
            }
            print(f"🗑️ Cleared conversation and files for session {session_id[:20]}...")
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Error clearing: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    try:
        session_id = session.get('session_id')
        if session_id and session_id in conversations:
            return jsonify({
                'success': True, 
                'history': conversations[session_id]['messages'],
                'files': conversations[session_id]['uploaded_files']
            })
        return jsonify({'success': True, 'history': [], 'files': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    try:
        test_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'API works!'"}],
            max_tokens=20
        )
        return jsonify({
            'status': 'success', 
            'message': 'Groq API is working!',
            'response': test_completion.choices[0].message.content,
            'rag_available': RAG_AVAILABLE
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 GROQ CHATBOT WITH RAG (Document Q&A)")
    print("="*60)
    print(f"📍 Server: http://localhost:5000")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📦 Chunk folder: {app.config['CHUNK_FOLDER']}")
    print(f"🔍 RAG Available: {'✅ YES' if RAG_AVAILABLE else '❌ NO'}")
    if RAG_AVAILABLE:
        print("\n💡 RAG Features:")
        print("   - PDF chunking (1500 char chunks, 300 char overlap)")
        print("   - Semantic search with embeddings")
        print("   - Context-aware responses")
    else:
        print("\n⚠️ To enable RAG, install:")
        print("   pip install sentence-transformers faiss-cpu numpy")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, threaded=True)