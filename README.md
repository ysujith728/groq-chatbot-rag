<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Groq RAG Chatbot - Smart Document Q&A</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1a202c;
            background: #f7fafc;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        /* Header */
        .header {
            text-align: center;
            padding: 3rem 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 1rem;
            margin-bottom: 2rem;
            color: white;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        /* Badges */
        .badges {
            text-align: center;
            margin: 1.5rem 0;
        }

        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            margin: 0.25rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-decoration: none;
        }

        .badge-python { background: #3776AB; color: white; }
        .badge-groq { background: #FF6B00; color: white; }
        .badge-license { background: #0B5FA5; color: white; }
        .badge-rag { background: #48BB78; color: white; }

        /* Demo Screenshot */
        .demo {
            background: white;
            border-radius: 1rem;
            padding: 1rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }

        .demo img {
            max-width: 100%;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .demo-caption {
            margin-top: 0.5rem;
            color: #718096;
            font-size: 0.9rem;
        }

        /* Cards */
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }

        .feature-card {
            background: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .feature-card h3 {
            margin-bottom: 0.5rem;
            font-size: 1.25rem;
        }

        /* Architecture Diagram */
        .architecture {
            background: #1a202c;
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin: 2rem 0;
            overflow-x: auto;
        }

        .architecture pre {
            font-family: monospace;
            font-size: 0.8rem;
            white-space: pre;
        }

        /* Code Blocks */
        pre {
            background: #2d3748;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            font-size: 0.85rem;
            margin: 1rem 0;
        }

        code {
            font-family: 'Courier New', monospace;
            background: #edf2f7;
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
            font-size: 0.85rem;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            background: white;
            border-radius: 0.5rem;
            overflow: hidden;
        }

        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }

        th {
            background: #667eea;
            color: white;
        }

        /* Sections */
        .section {
            background: white;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .section h2 {
            color: #2d3748;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #667eea;
            display: inline-block;
        }

        /* Buttons */
        .btn {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: #48bb78;
            color: white;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }

        .btn:hover {
            background: #38a169;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            margin-top: 2rem;
            color: #718096;
            border-top: 1px solid #e2e8f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🤖 Groq RAG Chatbot</h1>
            <p>Smart Document Q&A with Retrieval-Augmented Generation</p>
        </div>

        <!-- Badges -->
        <div class="badges">
            <span class="badge badge-python">🐍 Python 3.8+</span>
            <span class="badge badge-groq">⚡ Groq API</span>
            <span class="badge badge-license">📄 MIT License</span>
            <span class="badge badge-rag">🧠 RAG Powered</span>
        </div>

        <!-- Demo Screenshot -->
        <div class="demo">
            <img src="screenshots/demo.png" alt="Chatbot Demo Screenshot" onerror="this.src='https://via.placeholder.com/800x400?text=Demo+Screenshot'; this.onerror=null;">
            <div class="demo-caption">
                📌 Successfully processing a 336-page syllabus (2.18 MB) into 516 searchable chunks
            </div>
        </div>

        <!-- Description -->
        <div class="section">
            <h2>✨ What is This?</h2>
            <p>Upload any PDF document <strong>(300+ pages)</strong>, ask questions in plain English, and get accurate answers using <strong>AI-powered semantic search</strong>. Perfect for:</p>
            <ul style="margin-left: 1.5rem; margin-top: 0.5rem;">
                <li>📚 <strong>Students</strong> - Ask questions about syllabi, textbooks, research papers</li>
                <li>👨‍💼 <strong>Professionals</strong> - Analyze contracts, reports, documentation</li>
                <li>🔬 <strong>Researchers</strong> - Query through academic papers</li>
                <li>📖 <strong>Teachers</strong> - Create interactive Q&A for course materials</li>
            </ul>
        </div>

        <!-- Features Grid -->
        <h2>⭐ Features</h2>
        <div class="features">
            <div class="feature-card">
                <h3>📚 Large PDF Support</h3>
                <p>Handles 300+ page documents. Tested with 336 pages, 618K characters, 516 chunks.</p>
            </div>
            <div class="feature-card">
                <h3>🔍 Semantic Search</h3>
                <p>Finds relevant information using AI embeddings, not just keywords.</p>
            </div>
            <div class="feature-card">
                <h3>🧠 RAG Architecture</h3>
                <p>Retrieves only relevant chunks, sends minimal context to LLM.</p>
            </div>
            <div class="feature-card">
                <h3>🚀 Groq's Speed</h3>
                <p>Ultra-fast inference (500+ tokens/sec).</p>
            </div>
            <div class="feature-card">
                <h3>💬 Beautiful UI</h3>
                <p>Modern, responsive chat interface with file preview.</p>
            </div>
            <div class="feature-card">
                <h3>🔒 Secure</h3>
                <p>Your API key stays local, never uploaded to GitHub.</p>
            </div>
        </div>

        <!-- Architecture -->
        <div class="section">
            <h2>🏗️ How It Works</h2>
            <div class="architecture">
                <pre style="color: #68d391; background: transparent; margin: 0; padding: 0;">
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Upload PDF │ -> │   Chunk     │ -> │  Embeddings │ -> │   FAISS     │
│  (336 pages)│    │ (516 chunks)│    │  (vectors)  │    │   Index     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────▼──────┐
│  Display    │ <- │   Groq LLM  │ <- │  Top-8 Most │ <- │   Query     │
│  Answer     │    │  (Llama 3)  │    │  Relevant   │    │  Embedding  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                </pre>
            </div>
        </div>

        <!-- Tech Stack -->
        <div class="section">
            <h2>🛠️ Tech Stack</h2>
            <table>
                <thead>
                    <tr><th>Technology</th><th>Purpose</th></tr>
                </thead>
                <tbody>
                    <tr><td><strong>Flask</strong></td><td>Backend web framework</td></tr>
                    <tr><td><strong>Groq API</strong></td><td>Ultra-fast LLM inference</td></tr>
                    <tr><td><strong>Sentence Transformers</strong></td><td>Text embeddings (all-MiniLM-L6-v2)</td></tr>
                    <tr><td><strong>FAISS</strong></td><td>Vector similarity search</td></tr>
                    <tr><td><strong>PyPDF2 / pdfplumber</strong></td><td>PDF text extraction</td></tr>
                </tbody>
            </table>
        </div>

        <!-- Prerequisites -->
        <div class="section">
            <h2>📋 Prerequisites</h2>
            <ul style="margin-left: 1.5rem;">
                <li>✅ <strong>Python 3.8 or higher</strong> - <a href="https://www.python.org/downloads/">Download</a></li>
                <li>✅ <strong>Git</strong> - <a href="https://git-scm.com/downloads">Download</a></li>
                <li>✅ <strong>Groq API Key</strong> - <a href="https://console.groq.com/keys">Get one for free</a></li>
                <li>✅ <strong>4GB RAM minimum</strong> (8GB recommended)</li>
            </ul>
        </div>

        <!-- Installation -->
        <div class="section">
            <h2>🚀 Step-by-Step Installation</h2>

            <h3>Step 1: Clone the Repository</h3>
            <pre><code>git clone https://github.com/ysujith728/groq-chatbot-rag.git
cd groq-chatbot-rag</code></pre>

            <h3>Step 2: Create Virtual Environment</h3>
            <p><strong>Windows:</strong></p>
            <pre><code>python -m venv venv
venv\Scripts\activate</code></pre>
            <p><strong>Mac/Linux:</strong></p>
            <pre><code>python3 -m venv venv
source venv/bin/activate</code></pre>

            <h3>Step 3: Install Dependencies</h3>
            <pre><code>pip install -r requirements.txt</code></pre>

            <h3>Step 4: Set Up API Key</h3>
            <p>Create a <code>.env</code> file (this will NOT be uploaded to GitHub):</p>
            <pre><code># Windows (PowerShell)
echo "GROQ_API_KEY=gsk_your_actual_api_key_here" > .env

# Mac/Linux
echo "GROQ_API_KEY=gsk_your_actual_api_key_here" >> .env</code></pre>
            <p>⚠️ <strong>Important:</strong> Replace <code>gsk_your_actual_api_key_here</code> with your real Groq API key from <a href="https://console.groq.com/keys">console.groq.com</a></p>

            <h3>Step 5: Run the Application</h3>
            <pre><code>python app.py</code></pre>
            <p>You should see:</p>
            <pre><code>✅ Groq client initialized successfully
✅ RAG (semantic search) initialized successfully
🚀 GROQ CHATBOT WITH RAG (Document Q&A)
📍 Server: http://localhost:5000</code></pre>

            <h3>Step 6: Open Browser</h3>
            <p>Navigate to: <strong><a href="http://localhost:5000">http://localhost:5000</a></strong></p>
        </div>

        <!-- Example Questions -->
        <div class="section">
            <h2>💬 Example Questions</h2>
            <p>Once you upload a document (like a syllabus), try asking:</p>
            <table>
                <thead><tr><th>Question</th><th>What it finds</th></tr></thead>
                <tbody>
                    <tr><td>"What are the course outcomes for Calculus?"</td><td>Specific course objectives</td></tr>
                    <tr><td>"List all programming languages taught"</td><td>Programming courses and languages</td></tr>
                    <tr><td>"What is the credit distribution for Semester 1?"</td><td>Course credits and structure</td></tr>
                    <tr><td>"Summarize the program educational objectives"</td><td>PEOs from the syllabus</td></tr>
                    <tr><td>"What electives are available in AI?"</td><td>AI specialization courses</td></tr>
                </tbody>
            </table>
        </div>

        <!-- Performance Metrics -->
        <div class="section">
            <h2>📊 Performance Metrics</h2>
            <table>
                <thead><tr><th>Metric</th><th>Value</th></tr></thead>
                <tbody>
                    <tr><td>Max PDF Size</td><td>100MB</td></tr>
                    <tr><td>Max Pages</td><td>~500 pages</td></tr>
                    <tr><td>Chunk Size</td><td>1500 characters</td></tr>
                    <tr><td>Overlap</td><td>300 characters</td></tr>
                    <tr><td>Context Window</td><td>128K tokens</td></tr>
                    <tr><td>Response Time</td><td>2-5 seconds</td></tr>
                    <tr><td>Embedding Model</td><td>all-MiniLM-L6-v2 (384 dimensions)</td></tr>
                </tbody>
            </table>
        </div>

        <!-- Project Structure -->
        <div class="section">
            <h2>📁 Project Structure</h2>
            <pre><code>groq-chatbot-rag/
│
├── app.py                 # Main Flask application (RAG implementation)
├── requirements.txt       # Python dependencies
├── .env.example          # Template for API key
├── .gitignore            # Git ignore rules
├── README.md             # Documentation
├── LICENSE               # MIT License
│
├── templates/
│   └── index.html        # Frontend UI
│
├── uploads/              # Temporary uploads (gitignored)
├── chunks/               # Vector store (gitignored)
│
└── screenshots/
    └── demo.png          # Demo screenshot</code></pre>
        </div>

        <!-- Troubleshooting -->
        <div class="section">
            <h2>🐛 Troubleshooting</h2>
            
            <h3>"RAG not available" Error</h3>
            <pre><code>pip install sentence-transformers faiss-cpu numpy</code></pre>

            <h3>"Model decommissioned" Error</h3>
            <p>Update model names in <code>templates/index.html</code> to:</p>
            <ul>
                <li><code>llama-3.3-70b-versatile</code></li>
                <li><code>llama-3.1-8b-instant</code></li>
                <li><code>mixtral-8x7b-32768</code></li>
            </ul>

            <h3>"GROQ_API_KEY not found"</h3>
            <p>Make sure <code>.env</code> file exists in the project root with your actual API key.</p>

            <h3>PDF Text Extraction Failed</h3>
            <p>Ensure the PDF contains <strong>selectable text</strong> (not scanned images). For scanned PDFs, you'll need to add OCR support.</p>
        </div>

        <!-- Extensions to Install -->
        <div class="section">
            <h2>📦 VS Code Extensions (Recommended)</h2>
            <table>
                <thead><tr><th>Extension</th><th>Purpose</th></tr></thead>
                <tbody>
                    <tr><td><strong>Python</strong> (ms-python.python)</td><td>Python language support</td></tr>
                    <tr><td><strong>Pylance</strong> (ms-python.vscode-pylance)</td><td>Python type checking</td></tr>
                    <tr><td><strong>Python Indent</strong> (KevinRose.vsc-python-indent)</td><td>Better indentation</td></tr>
                    <tr><td><strong>GitLens</strong> (eamodio.gitlens)</td><td>Git integration</td></tr>
                    <tr><td><strong>Thunder Client</strong> (rangav.vscode-thunder-client)</td><td>API testing</td></tr>
                </tbody>
            </table>
        </div>

        <!-- Contributing -->
        <div class="section">
            <h2>🤝 Contributing</h2>
            <p>Contributions are welcome!</p>
            <ol style="margin-left: 1.5rem;">
                <li>Fork the repository</li>
                <li>Create a feature branch: <code>git checkout -b feature/amazing</code></li>
                <li>Commit changes: <code>git commit -m 'Add amazing feature'</code></li>
                <li>Push: <code>git push origin feature/amazing</code></li>
                <li>Open a Pull Request</li>
            </ol>
            <p><strong>Ideas for contributions:</strong></p>
            <ul>
                <li>Add support for DOCX, PPTX files</li>
                <li>Implement streaming responses</li>
                <li>Add conversation memory</li>
                <li>Deploy to cloud (Railway, Render)</li>
                <li>Add dark mode toggle</li>
            </ul>
        </div>

        <!-- License -->
        <div class="section">
            <h2>📄 License</h2>
            <p>MIT License - See <a href="LICENSE">LICENSE</a> file for details.</p>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Built with ❤️ using Groq's lightning-fast inference engine</p>
            <p>
                <a href="https://github.com/ysujith728/groq-chatbot-rag" style="color: #667eea;">GitHub Repository</a> |
                <a href="#" style="color: #667eea;">Report Issue</a> |
                <a href="#" style="color: #667eea;">Star on GitHub</a>
            </p>
            <p style="font-size: 0.8rem;">"Education is the manifestation of perfection already in man." - Swami Vivekananda</p>
        </div>
    </div>
</body>
</html>
