
from langchain_ollama import ChatOllama

def main():
    print("Connecting to local Ollama model...")

    llm = ChatOllama(
        model="llama3.2:3b",
        temperature=0
    )

    response = llm.invoke(
        "Explain Artificial Intelligence in 3 simple sentences."
    )

    print("\nAI Response:")
    print(response.content)

if __name__ == "__main__":
    main()
