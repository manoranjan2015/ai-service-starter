from ai_service.rag.document_loader import load_documents
from ai_service.rag.embedding_service import create_embeddings
from ai_service.rag.vector_store import add_documents, has_documents


DOCUMENTS_DIR = "documents"


def index_documents() -> None:
    if has_documents():
        return
    
    chunks = load_documents(DOCUMENTS_DIR)

    if not chunks:
        print("No document chunks found.")
        return

    embeddings = create_embeddings(chunks)
    add_documents(chunks, embeddings)

    print(f"Indexed {len(chunks)} chunks.")


if __name__ == "__main__":
    index_documents()
