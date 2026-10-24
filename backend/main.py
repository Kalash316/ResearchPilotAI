
from pathlib import Path
from io import BytesIO
from uuid import uuid4
from typing import Annotated

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, WithJsonSchema

from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_DIR / "chroma_db"
COLLECTION_NAME = "researchpilot_documents"

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB per PDF


PDFUploadFile = Annotated[
    UploadFile,
    WithJsonSchema({
        "type": "string",
        "format": "binary"
    })
]


app = FastAPI(
    title="ResearchPilotAI",
    description="Local AI research assistant with PDF-based RAG",
    version="2.2.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ResearchRequest(BaseModel):
    question: str
    source: str | None = None


# ============================================================
# EMBEDDING MODEL AND VECTOR DATABASE
# ============================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)


vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=str(DATABASE_DIR)
)


# ============================================================
# LOCAL LANGUAGE MODEL
# ============================================================

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_selected_pdf_chunks(filename: str):
    """Return all indexed chunks belonging to one PDF."""

    result = vector_store.get(
        where={"source": filename},
        include=["documents", "metadatas"]
    )

    documents = []

    contents = result.get("documents") or []
    metadatas = result.get("metadatas") or []

    for content, metadata in zip(contents, metadatas):
        if content and content.strip():
            documents.append(
                Document(
                    page_content=content,
                    metadata=metadata or {}
                )
            )

    # Keep the PDF's original page order.
    documents.sort(
        key=lambda doc: (
            doc.metadata.get("page", 0),
            doc.metadata.get("chunk", 0)
        )
    )

    return documents


def is_metadata_question(question: str) -> bool:
    """Identify questions that usually need the first page."""

    q = question.lower()

    keywords = [
        "title",
        "author",
        "authors",
        "abstract",
        "first page",
        "page 1",
        "main topic",
        "paper about",
        "research objective",
        "research objectives"
    ]

    return any(keyword in q for keyword in keywords)


def build_context(documents):
    """Prepare the retrieved PDF text and its source references."""

    context_parts = []
    sources = []

    for document in documents:
        filename = document.metadata.get("source", "Unknown")
        page = document.metadata.get("page", "Unknown")

        context_parts.append(
            f"Source: {filename}, Page: {page}\n"
            f"Text:\n{document.page_content}"
        )

        reference = {
            "source": filename,
            "page": page
        }

        if reference not in sources:
            sources.append(reference)

    return "\n\n---\n\n".join(context_parts), sources


# ============================================================
# HOME ENDPOINT
# ============================================================

@app.get("/")
def home():
    return {
        "message": "ResearchPilotAI RAG API is running!"
    }


# ============================================================
# ASK QUESTIONS ABOUT A PDF
# ============================================================

@app.post("/ask")
def ask_question(request: ResearchRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    source = (
        Path(request.source).name
        if request.source and request.source.strip()
        else None
    )

    try:
        if vector_store._collection.count() == 0:
            raise HTTPException(
                status_code=503,
                detail="Vector database is empty. Upload a PDF first."
            )

        # ----------------------------------------------------
        # STEP 1: Get chunks for the selected PDF
        # ----------------------------------------------------

        if source:
            all_pdf_documents = get_selected_pdf_chunks(source)

            if not all_pdf_documents:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"{source} is not indexed. "
                        "Please upload this PDF again."
                    )
                )
        else:
            # If no PDF is selected, search across all indexed PDFs.
            all_pdf_documents = []

        # ----------------------------------------------------
        # STEP 2: Select relevant text
        # ----------------------------------------------------

        if source and is_metadata_question(question):
            # For title, authors and abstract, use actual first-page
            # text rather than relying only on semantic similarity.
            documents = [
                doc for doc in all_pdf_documents
                if doc.metadata.get("page") == 1
            ]

            # If the first page is not indexed, fall back to search.
            if not documents:
                documents = vector_store.similarity_search(
                    question,
                    k=8,
                    filter={"source": source}
                )

        elif source:
            documents = vector_store.similarity_search(
                question,
                k=8,
                filter={"source": source}
            )

        else:
            documents = vector_store.similarity_search(
                question,
                k=8
            )

        if not documents:
            return {
                "question": question,
                "answer": "No relevant text was found in the indexed PDF.",
                "sources": []
            }

        # ----------------------------------------------------
        # STEP 3: Print retrieved text for debugging
        # ----------------------------------------------------

        print("\n" + "=" * 65)
        print("RESEARCHPILOTAI - RETRIEVED PDF TEXT")
        print(f"Question: {question}")
        print(f"Selected PDF: {source or 'All indexed PDFs'}")
        print("=" * 65)

        for document in documents:
            print(
                f"\nFile: {document.metadata.get('source', 'Unknown')}"
                f" | Page: {document.metadata.get('page', 'Unknown')}"
            )
            print(document.page_content[:2000])
            print("-" * 65)

        # ----------------------------------------------------
        # STEP 4: Build context and source references
        # ----------------------------------------------------

        context, sources = build_context(documents)

        # ----------------------------------------------------
        # STEP 5: Build the prompt
        # ----------------------------------------------------

        prompt = f"""
You are ResearchPilotAI, a research assistant that answers
questions using uploaded PDF documents.

Use ONLY the PDF excerpts supplied below as evidence.

Rules:
1. Answer the user's exact question.
2. For a title question, identify the paper title from the
   title or heading on the first page.
3. For an author question, identify the authors listed below
   the paper title. Do not confuse cited authors with paper authors.
4. For an abstract question, summarize the ABSTRACT section
   if it appears in the provided text.
5. For a main-topic question, explain the paper's purpose,
   research problem, method, and findings when available.
6. For a page-specific question, discuss only the requested page
   if that page's text is provided.
7. Do not claim that information is missing when it is clearly
   present in the excerpts.
8. Do not invent names, titles, findings, or other facts.
9. If the provided text truly lacks the requested information,
   state that clearly.
10. Use simple, clear English.
11. Include page numbers when useful.

SELECTED PDF:
{source or "No specific PDF selected"}

PDF EXCERPTS:
{context}

USER QUESTION:
{question}

ANSWER:
"""

        # ----------------------------------------------------
        # STEP 6: Generate the answer
        # ----------------------------------------------------

        response = llm.invoke(prompt)
        answer = str(response.content).strip()

        if not answer:
            answer = (
                "The local AI model returned an empty answer. "
                "Please try again."
            )

        return {
            "question": question,
            "selected_file": source,
            "answer": answer,
            "sources": sources
        }

    except HTTPException:
        raise

    except Exception as error:
        print(f"ERROR in /ask: {error}")

        raise HTTPException(
            status_code=500,
            detail=f"Could not generate an answer: {str(error)}"
        )


# ============================================================
# UPLOAD AND INDEX PDF FILES
# ============================================================

@app.post("/upload-pdfs")
async def upload_pdfs(
    files: Annotated[
        list[PDFUploadFile],
        File(description="Select one or more PDF files")
    ]
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please select at least one PDF file."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=True
    )

    uploaded_files = []
    seen_filenames = set()
    all_chunks = []
    filenames_to_replace = []

    try:
        # ----------------------------------------------------
        # STEP 1: Validate and extract all uploaded PDFs
        # ----------------------------------------------------

        for file in files:
            filename = Path(file.filename or "").name

            if not filename or filename in {".", ".."}:
                raise HTTPException(
                    status_code=400,
                    detail="A file has an invalid filename."
                )

            if not filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400,
                    detail=f"{filename} is not a PDF file."
                )

            if filename in seen_filenames:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Duplicate filename in this upload: {filename}. "
                        "Rename one file and try again."
                    )
                )

            seen_filenames.add(filename)

            content = await file.read()

            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"{filename} exceeds the 20 MB limit."
                )

            if not content.startswith(b"%PDF-"):
                raise HTTPException(
                    status_code=400,
                    detail=f"{filename} is not a valid PDF file."
                )

            try:
                reader = PdfReader(BytesIO(content))

                if reader.is_encrypted:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"{filename} is password-protected. "
                            "Upload an unlocked PDF."
                        )
                    )

                page_documents = []

                for page_number, page in enumerate(
                    reader.pages,
                    start=1
                ):
                    page_text = page.extract_text() or ""

                    if page_text.strip():
                        page_documents.append(
                            Document(
                                page_content=page_text,
                                metadata={
                                    "source": filename,
                                    "page": page_number
                                }
                            )
                        )

                if not page_documents:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"No extractable text found in {filename}. "
                            "Scanned PDFs may require OCR."
                        )
                    )

                chunks = splitter.split_documents(page_documents)

                # Add a stable chunk position for sorting/debugging.
                for chunk_number, chunk in enumerate(chunks):
                    chunk.metadata["chunk"] = chunk_number

                chunk_ids = [str(uuid4()) for _ in chunks]

                all_chunks.extend(zip(chunks, chunk_ids))
                filenames_to_replace.append(filename)

                uploaded_files.append({
                    "filename": filename,
                    "pages": len(reader.pages),
                    "text_pages": len(page_documents),
                    "chunks": len(chunks)
                })

            except HTTPException:
                raise

            except Exception as error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not read {filename}: {str(error)}"
                )

        # ----------------------------------------------------
        # STEP 2: Replace previous chunks for the same filenames
        # ----------------------------------------------------

        for filename in filenames_to_replace:
            vector_store._collection.delete(
                where={"source": filename}
            )

        # ----------------------------------------------------
        # STEP 3: Store the new chunks
        # ----------------------------------------------------

        if all_chunks:
            documents_to_store = [
                item[0] for item in all_chunks
            ]

            ids_to_store = [
                item[1] for item in all_chunks
            ]

            vector_store.add_documents(
                documents=documents_to_store,
                ids=ids_to_store
            )

        total_chunks = len(all_chunks)

        print("\nPDF upload completed.")
        for uploaded_file in uploaded_files:
            print(
                f"{uploaded_file['filename']}: "
                f"{uploaded_file['chunks']} chunks"
            )

        return {
            "message": "PDF files processed successfully!",
            "files": uploaded_files,
            "total_files": len(uploaded_files),
            "total_chunks": total_chunks
        }

    except HTTPException:
        raise

    except Exception as error:
        print(f"ERROR in /upload-pdfs: {error}")

        raise HTTPException(
            status_code=500,
            detail=f"Could not process uploaded PDFs: {str(error)}"
        )

    finally:
        for file in files:
            await file.close()
