# 📄 PDF Agent — Intelligent PDF Question Answering System

An AI-powered PDF Question Answering system that allows users to upload PDF documents and ask questions about their content. The system uses **text preprocessing, Retrieval-Augmented Generation (RAG), and conversation history memory** to provide context-aware answers.

The application is built with **FastAPI** for the backend and **Streamlit** for the frontend, and can be containerized using **Docker**.

---

## 🚀 Features

* 📤 **PDF Upload**

  * Upload PDF documents through the Streamlit interface.

* 🧹 **Text Preprocessing**

  * Extracts text from uploaded PDFs.
  * Cleans and preprocesses extracted text before indexing.
  * Splits large documents into manageable chunks for retrieval.

* 🔎 **Retrieval-Augmented Generation (RAG)**

  * Converts document chunks into vector embeddings.
  * Stores embeddings using **FAISS**.
  * Retrieves relevant document chunks based on the user's question.
  * Uses retrieved context to generate grounded answers.

* 🧠 **User History / Conversation Memory**

  * Maintains previous questions and answers during a session.
  * Uses conversation history to provide better context for follow-up questions.
  * Allows users to ask questions referring to previous interactions.

* 🤖 **LLM-Based Question Answering**

  * Uses Google's Gemini model for response generation.
  * Generates answers using the retrieved PDF context and conversation history.

* ⚡ **FastAPI Backend**

  * REST API architecture for PDF processing and question answering.
  * Separate endpoints for document processing and querying.

* 🖥️ **Streamlit Frontend**

  * Simple interactive interface for uploading PDFs and asking questions.

* 🐳 **Docker Support**

  * Backend and frontend can be containerized.
  * Supports running the complete application using Docker.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │   Streamlit UI      │
                    │     Frontend        │
                    └──────────┬──────────┘
                               │
                               │ HTTP Requests
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI         │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    PDF Processing   │
                    │ & Text Preprocessing│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Text Chunking       │
                    │ & Embeddings        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       FAISS         │
                    │   Vector Database   │
                    └──────────┬──────────┘
                               │
                    Relevant Chunks
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Conversation /      │
                    │ User History Memory │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Gemini LLM       │
                    │  Answer Generation  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Final Answer    │
                    └─────────────────────┘
```

---

## 🔄 How It Works

### 1. Upload PDF

The user uploads a PDF through the Streamlit frontend.

### 2. Extract and Preprocess Text

The backend extracts text from the PDF and performs preprocessing to make the document suitable for retrieval.

### 3. Create Document Chunks

The processed text is divided into smaller chunks using a text splitter.

### 4. Generate Embeddings

Each chunk is converted into a vector representation using an embedding model.

### 5. Store in FAISS

The generated embeddings are stored in a FAISS vector index.

### 6. Ask a Question

The user submits a question through the frontend.

### 7. Retrieve Relevant Information

The question is converted into an embedding and FAISS retrieves the most relevant document chunks.

### 8. Add Conversation History

Previous questions and answers from the user's session can be included as additional context, which helps the system handle follow-up questions.

For example:

```text
User: What is the main topic of the document?

AI: The document discusses ...

User: What are its main advantages?

AI: Based on the previous context, the main advantages are ...
```

### 9. Generate Answer

The retrieved document context and relevant conversation history are passed to the Gemini LLM to generate the final response.

---

## 🛠️ Tech Stack

| Technology                      | Purpose                   |
| ------------------------------- | ------------------------- |
| Python                          | Core programming language |
| FastAPI                         | Backend REST API          |
| Streamlit                       | Frontend UI               |
| LangChain                       | LLM and RAG orchestration |
| Google Gemini                   | LLM for answer generation |
| Google Generative AI Embeddings | Document embeddings       |
| FAISS                           | Vector similarity search  |
| PyPDF                           | PDF text extraction       |
| RecursiveCharacterTextSplitter  | Text chunking             |
| Docker                          | Containerization          |

---

## 📁 Project Structure

```text
PDF-Agent/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
│
└── README.md
```

> The exact structure may vary depending on your current project files.

---

## 🔌 API Endpoints

### Health Check

```http
GET /
```

Returns the status of the PDF QA backend.

### Health Endpoint

```http
GET /health
```

Used to verify that the backend is running correctly.

### Process PDF

```http
POST /text
```

Uploads and processes a PDF.

The endpoint:

1. Extracts PDF text
2. Preprocesses the text
3. Splits the text into chunks
4. Creates embeddings
5. Builds the FAISS retriever
6. Creates a session associated with the processed document

### Ask Question

```http
POST /ask
```

Accepts:

```text
session_id
question
```

The endpoint retrieves relevant document information and uses conversation history to generate an answer.

---

## 🐳 Running with Docker

### Build and Start

```bash
docker compose up --build
```

After the containers start:

```text
Frontend:
http://localhost:8501

Backend:
http://localhost:8000
```

To stop the containers:

```bash
docker compose down
```

---

## 💻 Running Locally

### Backend

Navigate to the backend directory:

```bash
cd backend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

### Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Streamlit:

```bash
streamlit run app.py
```

---

## 🔐 Environment Variables

Create a `.env` file in the backend:

```env
GOOGLE_API_KEY=your_api_key_here
```

Do not commit your `.env` file or API keys to GitHub.

Add it to `.gitignore`:

```text
.env
__pycache__/
*.pyc
```

---

## 🧠 Key AI/ML Concepts Used

This project demonstrates practical implementation of:

* Large Language Models (LLMs)
* Retrieval-Augmented Generation (RAG)
* Text preprocessing
* Text chunking
* Semantic embeddings
* Vector similarity search
* FAISS vector database
* Conversational memory
* Context-aware question answering
* Prompt engineering
* REST API development
* Containerization with Docker

---

## 🎯 Project Objective

The main objective of this project is to build a practical **document-based AI assistant** that can understand user-provided PDF documents, retrieve relevant information, maintain conversational context, and generate meaningful answers using an LLM.

The project combines **NLP, Generative AI, RAG, backend API development, and Docker deployment** into a single application.

---

## 🔮 Future Improvements

Possible future enhancements include:

* Support for multiple PDFs
* Persistent vector database storage
* User authentication
* Long-term conversation memory
* Streaming LLM responses
* Citation and source tracking
* Improved document preprocessing
* OCR support for scanned PDFs
* Hybrid search using keyword + semantic retrieval
* Reranking retrieved documents
* Cloud deployment
* Background document processing

---

## 👨‍💻 Author

**Parth Tarsariya**

AI/ML Engineer | Generative AI | RAG | NLP | FastAPI | Docker
