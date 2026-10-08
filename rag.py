import os
import pickle

import faiss
import numpy as np

from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

INDEX_PATH = "vector.index"
CHUNKS_PATH = "chunks.pkl"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

TOP_K = 3


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)


# ---------------------------------------------------------
# Validate API key
# ---------------------------------------------------------

if not OPENAI_API_KEY:

    raise ValueError(
        "OPENAI_API_KEY is not set. "
        "Please add it to your .env file."
    )


# ---------------------------------------------------------
# Create OpenAI client
# ---------------------------------------------------------

client = OpenAI(
    api_key=OPENAI_API_KEY
)


# ---------------------------------------------------------
# Load embedding model
# ---------------------------------------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


# ---------------------------------------------------------
# Load FAISS vector database
# ---------------------------------------------------------

print("Loading FAISS vector database...")

if not os.path.exists(INDEX_PATH):

    raise FileNotFoundError(
        f"{INDEX_PATH} not found. "
        "Please run 'python ingest.py' first."
    )


index = faiss.read_index(
    INDEX_PATH
)


# ---------------------------------------------------------
# Load text chunks
# ---------------------------------------------------------

print("Loading document chunks...")

if not os.path.exists(CHUNKS_PATH):

    raise FileNotFoundError(
        f"{CHUNKS_PATH} not found. "
        "Please run 'python ingest.py' first."
    )


with open(
    CHUNKS_PATH,
    "rb"
) as file:

    chunks = pickle.load(
        file
    )


print(
    f"Loaded {len(chunks)} chunks."
)


# ---------------------------------------------------------
# Retrieve relevant documents
# ---------------------------------------------------------

def retrieve_documents(
    question,
    top_k=TOP_K
):
    """
    Convert the user question into an embedding
    and search the FAISS vector database.
    """

    # Create embedding for the question
    question_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True
    )

    # Convert to float32
    question_embedding = np.array(
        question_embedding
    ).astype("float32")

    # Search FAISS
    distances, indexes = index.search(
        question_embedding,
        top_k
    )

    results = []

    for position, idx in enumerate(
        indexes[0]
    ):

        if idx < 0:
            continue

        if idx >= len(chunks):
            continue

        results.append(
            {
                "chunk": chunks[idx],
                "distance": float(
                    distances[0][position]
                ),
                "index": int(idx)
            }
        )

    return results


# ---------------------------------------------------------
# Build context
# ---------------------------------------------------------

def build_context(documents):

    context_parts = []

    for i, document in enumerate(
        documents,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {i}

{document["chunk"]}
"""
        )

    return "\n".join(
        context_parts
    )


# ---------------------------------------------------------
# Generate answer using OpenAI
# ---------------------------------------------------------

def generate_answer(question):

    # Retrieve relevant chunks
    documents = retrieve_documents(
        question
    )

    # If nothing was found
    if not documents:

        return (
            "I could not find this information "
            "in the company policy."
        )

    # Create context
    context = build_context(
        documents
    )

    # Prompt
    prompt = f"""
You are an assistant for a company employee
policy application.

Your job is to answer questions using ONLY
the company policy information provided below.

IMPORTANT RULES:

1. Do not make up information.
2. Do not use information that is not present
   in the provided context.
3. If the answer cannot be found in the context,
   say:

   "I could not find this information in the
   company policy."

4. Give a clear and concise answer.
5. When appropriate, mention the relevant
   policy section.

Company Policy Context
======================

{context}

======================

Employee Question:

{question}
"""

    # Call OpenAI
    response = client.responses.create(
        model="gpt-5.6",
        input=prompt
    )

    answer = response.output_text

    return answer


# ---------------------------------------------------------
# Optional: Display retrieved documents
# ---------------------------------------------------------

def show_retrieved_documents(
    question
):
    """
    Useful for debugging and understanding
    what the RAG system retrieved.
    """

    documents = retrieve_documents(
        question
    )

    print()
    print("=" * 60)
    print("RETRIEVED DOCUMENTS")
    print("=" * 60)

    if not documents:

        print("No documents found.")

        return

    for i, document in enumerate(
        documents,
        start=1
    ):

        print()
        print(
            f"Document {i}"
        )

        print("-" * 60)

        print(
            f"FAISS Distance: "
            f"{document['distance']:.4f}"
        )

        print()

        print(
            document["chunk"]
        )


# ---------------------------------------------------------
# Test the RAG system directly
# ---------------------------------------------------------

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("          COMPANY POLICY RAG TEST")
    print("=" * 60)

    question = input(
        "\nEnter your question: "
    )

    if not question.strip():

        print(
            "Please enter a question."
        )

    else:

        # Show what the retriever found
        show_retrieved_documents(
            question
        )

        # Generate final answer
        answer = generate_answer(
            question
        )

        print()
        print("=" * 60)
        print("ANSWER")
        print("=" * 60)

        print()
        print(answer)
