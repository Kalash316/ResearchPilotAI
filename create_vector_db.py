
from pathlib import Path

from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# Project folders
PROJECT_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = PROJECT_DIR / "backend" / "documents"
DATABASE_DIR = PROJECT_DIR / "chroma_db"

COLLECTION_NAME = "researchpilot_documents"


def create_vector_database():
    print("Step 1: Searching for PDF files...")

    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        print("ERROR: No PDF found in backend/documents!")
        return

    # Read each PDF page and preserve its metadata
    documents = []

    for pdf_path in pdf_files:
        print(f"Reading: {pdf_path.name}")

        reader = PdfReader(str(pdf_path))

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""

            if page_text.strip():
                documents.append(
                    Document(
                        page_content=page_text,
                        metadata={
                            "source": pdf_path.name,
                            "page": page_number
                        }
                    )
                )

    if not documents:
        print("ERROR: No readable text found in the PDFs.")
        return

    print(f"Pages with readable text: {len(documents)}")

    # Split text into manageable chunks
    print("\nStep 2: Splitting PDF text into chunks...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        print("ERROR: No text chunks were created.")
        return

    print(f"Total chunks: {len(chunks)}")

    # Load the local embedding model
    print("\nStep 3: Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # Create stable IDs to avoid re-adding the same chunks
    chunk_ids = [
        f"chunk-{index}"
        for index in range(len(chunks))
    ]

    # Save vectors and text to the persistent ChromaDB
    print("\nStep 4: Saving chunks to ChromaDB...")

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(DATABASE_DIR)
    )

    vector_store.add_documents(
        documents=chunks,
        ids=chunk_ids
    )

    print("\nStep 5: Verifying the database...")

    print(f"Database folder: {DATABASE_DIR}")
    print(f"Chunks in this run: {len(chunks)}")
    print(f"Total chunks in database: {vector_store._collection.count()}")

    # Test a similarity search
    test_question = chunks[0].page_content[:150]

    results = vector_store.similarity_search(
        test_question,
        k=1
    )

    print("\nSearch test:")
    if results:
        print("Source:", results[0].metadata.get("source"))
        print("Page:", results[0].metadata.get("page"))
        print("Matching text:")
        print(results[0].page_content[:300])

    print("\nSUCCESS: ChromaDB vector database is ready!")


if __name__ == "__main__":
    create_vector_database()
