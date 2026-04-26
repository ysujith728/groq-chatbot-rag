# 🤖 Groq RAG Chatbot

### Smart Document Q&A with Retrieval-Augmented Generation (RAG)

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Groq](https://img.shields.io/badge/Groq-API-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![RAG](https://img.shields.io/badge/AI-RAG-brightgreen)

---

## 📌 Overview

This project allows you to **upload large PDF documents (300+ pages)** and ask questions in plain English.
It uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware answers.

### 🎯 Use Cases

* 📚 Students – Query textbooks, syllabi, research papers
* 👨‍💼 Professionals – Analyze contracts and reports
* 🔬 Researchers – Search academic documents
* 📖 Teachers – Build interactive Q&A systems

---

## ⭐ Features

* 📚 Supports large PDFs (300+ pages)
* 🔍 Semantic search using embeddings
* 🧠 Efficient RAG pipeline
* ⚡ Ultra-fast inference with Groq
* 💬 Clean and responsive UI
* 🔒 API key stays local (secure)

---

## 🏗️ Architecture

```
PDF → Chunking → Embeddings → FAISS Index
                             ↓
User Query → Embedding → Top-K Retrieval → Groq LLM → Answer
```

---

## 🛠️ Tech Stack

| Technology            | Purpose           |
| --------------------- | ----------------- |
| Flask                 | Backend framework |
| Groq API              | LLM inference     |
| Sentence Transformers | Text embeddings   |
| FAISS                 | Vector search     |
| PyPDF2 / pdfplumber   | PDF extraction    |

---

## 📋 Prerequisites

* Python 3.8+
* Git
* Groq API Key (free)

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/ysujith728/groq-chatbot-rag.git
cd groq-chatbot-rag
```

### 2. Create virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add API Key

Create `.env` file:

```bash
GROQ_API_KEY=your_api_key_here
```

### 5. Run the app

```bash
python app.py
```

Open 👉 http://localhost:5000

---

## 💬 Example Questions

* What are the course outcomes?
* List all programming languages taught
* What is the credit distribution?
* Summarize the objectives
* What AI electives are available?

---

## 📊 Performance

| Metric          | Value            |
| --------------- | ---------------- |
| Max PDF Size    | 100MB            |
| Pages           | ~500             |
| Chunk Size      | 1500 chars       |
| Response Time   | 2–5 sec          |
| Embedding Model | all-MiniLM-L6-v2 |

---

## 📁 Project Structure

```
groq-chatbot-rag/
│
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── LICENSE
│
├── templates/
│   └── index.html
│
├── uploads/        (ignored)
├── chunks/         (ignored)
└── screenshots/
```

---

## 🐛 Troubleshooting

### RAG not working

```bash
pip install sentence-transformers faiss-cpu numpy
```

### API Key issue

Ensure `.env` exists with:

```
GROQ_API_KEY=your_key
```

### PDF not working

Make sure the PDF has selectable text (not scanned images)

---

## 🤝 Contributing

1. Fork the repo
2. Create branch: `feature/your-feature`
3. Commit changes
4. Push and open PR

---

## 📄 License

MIT License

---

## ⭐ Support

If you like this project:

* Star ⭐ the repo
* Share it
* Contribute

---

## ❤️ Built With

Groq’s ultra-fast inference engine
