
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# Project paths and database settings
PROJECT_DIR = Path(__file__).resolve().parent
DATABASE_DIR = PROJECT_DIR / "chroma_db"
COLLECTION_NAME = "researchpilot_documents"


def load_vector_database():
    """Load the existing local ChromaDB database."""

    if not DATABASE_DIR.exists():
        raise FileNotFoundError(
            "ChromaDB folder not found. "
            "Run create_vector_db.py first."
        )

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

    if vector_store._collection.count() == 0:
        raise ValueError(
            "The vector database is empty. "
            "Run create_vector_db.py first."
        )

    return vector_store


def search_pdf(vector_store, question, number_of_results=3):
    """Find PDF chunks relevant to the user's question."""

    results = vector_store.similarity_search(
        question,
        k=number_of_results
    )

    print("\n" + "=" * 55)
    print("SEARCH RESULTS")
    print("=" * 55)

    if not results:
        print("No matching text was found.")
        return

    for index, document in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("-" * 40)

        print("Source:", document.metadata.get("source", "Unknown"))
        print("Page:", document.metadata.get("page", "Unknown"))

        print("\nRelevant text:")
        print(document.page_content)

    print("\n" + "=" * 55)


def main():
    print("ResearchPilotAI - PDF Search")
    print("Loading local vector database...")

    try:
        vector_store = load_vector_database()
        print("Database loaded successfully!")

        while True:
            question = input(
                "\nEnter your question (or type 'exit' to quit): "
            ).strip()

            if question.lower() in {"exit", "quit"}:
                print("Exiting PDF search. Goodbye!")
                break

            if not question:
                print("Please enter a question.")
                continue

            search_pdf(
                vector_store=vector_store,
                question=question,
                number_of_results=3
            )

    except Exception as error:
        print(f"\nERROR: {error}")


if __name__ == "__main__":
    main()
