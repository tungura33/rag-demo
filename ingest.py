from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

import faiss
import numpy as np
import pickle


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PDF_PATH = "data/employee.pdf"

INDEX_PATH = "vector.index"
CHUNKS_PATH = "chunks.pkl"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHUNK_SIZE = 100
CHUNK_OVERLAP = 20


# ---------------------------------------------------------
# Step 1: Read PDF
# ---------------------------------------------------------

def read_pdf(pdf_path):

    print(f"Reading PDF: {pdf_path}")

    reader = PdfReader(pdf_path)

    text = ""

    for page_number, page in enumerate(reader.pages, start=1):

        page_text = page.extract_text()

        if page_text:

            text += page_text + "\n"

        print(f"Processed page {page_number}")

    return text


# ---------------------------------------------------------
# Step 2: Split text into chunks
# ---------------------------------------------------------

def create_chunks(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ---------------------------------------------------------
# Step 3: Create embeddings
# ---------------------------------------------------------

def create_embeddings(chunks):

    print()
    print("Loading embedding model...")

    model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    print("Creating embeddings...")

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    return embeddings


# ---------------------------------------------------------
# Step 4: Create FAISS index
# ---------------------------------------------------------

def create_faiss_index(embeddings):

    print()
    print("Creating FAISS vector index...")

    # Number of dimensions in each embedding
    dimension = embeddings.shape[1]

    # L2 distance based FAISS index
    index = faiss.IndexFlatL2(dimension)

    # FAISS expects float32
    embeddings = np.array(
        embeddings
    ).astype("float32")

    # Add embeddings to the index
    index.add(embeddings)

    print(
        f"Added {index.ntotal} vectors to FAISS."
    )

    return index


# ---------------------------------------------------------
# Step 5: Save FAISS index
# ---------------------------------------------------------

def save_index(index):

    print()
    print(f"Saving FAISS index to: {INDEX_PATH}")

    faiss.write_index(
        index,
        INDEX_PATH
    )

    print("FAISS index saved successfully.")


# ---------------------------------------------------------
# Step 6: Save chunks
# ---------------------------------------------------------

def save_chunks(chunks):

    print(
        f"Saving chunks to: {CHUNKS_PATH}"
    )

    with open(
        CHUNKS_PATH,
        "wb"
    ) as file:

        pickle.dump(
            chunks,
            file
        )

    print("Chunks saved successfully.")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("        COMPANY POLICY RAG - INGESTION")
    print("=" * 60)

    # 1. Read PDF
    text = read_pdf(
        PDF_PATH
    )

    if not text.strip():

        print()
        print("ERROR: No text was extracted from the PDF.")

        return

    print()
    print(
        f"Extracted {len(text)} characters from PDF."
    )

    # 2. Create chunks
    print()
    print("Creating text chunks...")

    chunks = create_chunks(
        text
    )

    print(
        f"Created {len(chunks)} chunks."
    )

    # Display sample chunks
    print()
    print("=" * 60)
    print("SAMPLE CHUNKS")
    print("=" * 60)

    for i, chunk in enumerate(
        chunks[:3]
    ):

        print()
        print(f"Chunk {i}")
        print("-" * 60)
        print(chunk)

    # 3. Create embeddings
    embeddings = create_embeddings(
        chunks
    )

    print()
    print(
        f"Embedding shape: {embeddings.shape}"
    )

    # 4. Create FAISS index
    index = create_faiss_index(
        embeddings
    )

    # 5. Save FAISS index
    save_index(
        index
    )

    # 6. Save chunks
    save_chunks(
        chunks
    )

    # Final message
    print()
    print("=" * 60)
    print("          INGESTION COMPLETED")
    print("=" * 60)

    print()
    print("Created files:")

    print(f"  - {INDEX_PATH}")
    print(f"  - {CHUNKS_PATH}")

    print()
    print("You can now run:")
    print("  python app.py")


# ---------------------------------------------------------
# Application entry point
# ---------------------------------------------------------

if __name__ == "__main__":

    main()
