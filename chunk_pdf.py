
from pathlib import Path
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_pdf():
    # Locate the PDF folder
    documents_folder = (
        Path(__file__).resolve().parent
        / "backend"
        / "documents"
    )

    # Find PDF files
    pdf_files = sorted(documents_folder.glob("*.pdf"))

    if not pdf_files:
        print("ERROR: No PDF found in backend/documents!")
        return

    pdf_path = pdf_files[0]
    print(f"Reading PDF: {pdf_path.name}")

    # Extract text page by page
    reader = PdfReader(str(pdf_path))
    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": pdf_path.name,
                        "page": page_number
                    }
                )
            )

    if not documents:
        print("ERROR: No readable text found in this PDF.")
        return

    print(f"Pages containing text: {len(documents)}")

    # Configure the text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )

    # Split the PDF text into chunks
    chunks = splitter.split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    # Display the first three chunks
    for index, chunk in enumerate(chunks[:3], start=1):
        print(f"\n{'=' * 20} CHUNK {index} {'=' * 20}")
        print(f"Source: {chunk.metadata['source']}")
        print(f"Page: {chunk.metadata['page']}")
        print(f"Characters: {len(chunk.page_content)}")
        print(chunk.page_content[:500])

    print("\nPDF chunking completed successfully!")


if __name__ == "__main__":
    chunk_pdf()
