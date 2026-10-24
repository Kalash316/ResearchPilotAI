
from langchain_huggingface import HuggingFaceEmbeddings


def main():
    print("Loading local embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    text = "Artificial Intelligence helps computers perform tasks."
    vector = embeddings.embed_query(text)

    print("\nEmbedding model loaded successfully!")
    print("Input text:", text)
    print("Vector dimensions:", len(vector))
    print("First 5 numbers:", vector[:5])


if __name__ == "__main__":
    main()
