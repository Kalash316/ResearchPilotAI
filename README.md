#  ResearchPilotAI — AI-Powered Research Paper Assistant

ResearchPilotAI is an AI-powered research assistant that helps users explore research papers by uploading PDF documents and asking questions in natural language. It uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from documents and generate context-based answers with source references.

##  Features

- **PDF Upload:** Upload research papers in PDF format.
- **Question Answering:** Ask questions about the uploaded research papers in natural language.
- **Retrieval-Augmented Generation (RAG):** Retrieve relevant document content to provide context for answers.
- **Source References:** Display source information associated with retrieved document content.
- **Local LLM Integration:** Generate responses using Ollama and the `llama3.2:3b` model.
- **Semantic Search:** Use vector embeddings to find relevant document passages.
- **Interactive Web Interface:** Use a React-based frontend to interact with the research assistant.

##  Tech Stack

**Frontend**
- React.js
- Vite
- JavaScript
- CSS

**Backend**
- Python
- FastAPI
- LangChain

**AI and Retrieval**
- Ollama (`llama3.2:3b`)
- Hugging Face Sentence Transformers
- `sentence-transformers/all-MiniLM-L6-v2`
- ChromaDB
- Retrieval-Augmented Generation (RAG)

**PDF Processing**
- PyPDF
- Text splitting and document chunking

##  Project Structure

```text
ResearchPilotAI/
├── backend/
│   ├── documents/
│   │   └── ai_research.pdf
│   └── main.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── .gitignore
├── create_vector_db.py
├── chunk_pdf.py
├── read_pdf.py
├── search_pdf.py
└── README.md
```

## ⚙️ Prerequisites

Install the following before running the project:

- Python 3.10 or a compatible version for the installed dependencies
- Node.js and npm
- Git
- Ollama
- The Ollama `llama3.2:3b` model

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Kalash316/ResearchPilotAI.git
cd ResearchPilotAI
```

### 2. Set Up the Python Backend

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
pip install fastapi uvicorn langchain langchain-community langchain-chroma langchain-huggingface sentence-transformers chromadb pypdf
```

> If your project uses additional packages, install those listed in your project's dependency file or install them as required by your code.

### 3. Set Up Ollama

Install Ollama from [ollama.com](https://ollama.com/).

Download the model:

```bash
ollama pull llama3.2:3b
```

Ensure Ollama is running before starting the backend.

### 4. Start the Backend

Open a terminal in the project root, then run:

```powershell
cd backend
python -m uvicorn main:app --reload
```

The backend should be available at:

`http://127.0.0.1:8000`

FastAPI interactive API documentation:

`http://127.0.0.1:8000/docs`

### 5. Start the Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in your terminal, usually:

`http://localhost:5173`

##  How to Use

1. Start Ollama and the backend server.
2. Start the frontend development server.
3. Open the frontend in your browser.
4. Upload a research paper in PDF format.
5. Select the uploaded document if the interface provides document selection.
6. Ask questions about the paper.
7. Review the generated answer and its source references.

Example questions:

- What is the main objective of this research paper?
- Who are the authors?
- Summarize the abstract in simple English.
- What methodology does the paper use?
- What are the main findings?

##  How It Works

1. **Document Upload:** The backend receives the uploaded PDF.
2. **Text Extraction:** PDF text is extracted page by page.
3. **Text Chunking:** The extracted text is split into smaller passages.
4. **Embedding Generation:** The passages are converted into vector embeddings.
5. **Vector Storage:** Chunks and their metadata are stored in ChromaDB.
6. **Semantic Retrieval:** Relevant passages are retrieved for a user's question.
7. **Answer Generation:** The retrieved context is passed to the local LLM to generate a response.
8. **Source Display:** Relevant source metadata is returned to the frontend.

##  Future Improvements

- Add support for comparing multiple research papers.
- Improve answer evaluation and factual grounding.
- Add conversation history.
- Export summaries and research notes.
- Add automated tests and deployment support.
- Improve document management and retrieval performance.

##  Security Notes

- Do not commit API keys, passwords, access tokens, or `.env` files.
- Keep virtual environments, `node_modules`, and local database files out of version control when appropriate.
- Upload only PDF documents that you have permission to use or share.

##  Author

**Kalash Dwivedi**

- GitHub: [@Kalash316](https://github.com/Kalash316)

---

*ResearchPilotAI is a learning and development project exploring document question answering, semantic retrieval, and local LLM-based research assistance.*
