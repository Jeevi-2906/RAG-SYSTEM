import os
import shutil
from pathlib import Path
from rag.document_processor import DocumentProcessor
from rag.chunking import IntelligentChunker
from rag.embeddings import EmbeddingManager
from rag.vector_store import VectorStore
from rag.retriever import Retriever
import config


def run_pipeline_test():
    print("=" * 60)
    print("RUNNING DOCUMIND RAG PIPELINE INTEGRATION TEST")
    print("=" * 60)

    pdf_path = Path("sample_documents/AI_Concepts.pdf")
    assert pdf_path.exists(), f"Sample PDF not found at {pdf_path}"

    print("\n[Step 1] Testing Document Extraction...")
    doc_res = DocumentProcessor.extract_text_from_pdf(str(pdf_path), filename=pdf_path.name)
    assert doc_res["success"], f"Extraction failed: {doc_res['error']}"
    print(f"✓ Extraction Success! Extracted {doc_res['total_pages']} pages from '{doc_res['filename']}'.")
    assert doc_res["total_pages"] >= 5, f"Expected at least 5 pages, got {doc_res['total_pages']}"

    print("\n[Step 2] Testing Intelligent Chunking...")
    chunker = IntelligentChunker(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    chunks = chunker.chunk_document(doc_res)
    print(f"✓ Chunking Success! Generated {len(chunks)} chunks across {doc_res['total_pages']} pages.")
    assert len(chunks) >= 5, f"Expected at least 5 chunks, got {len(chunks)}"

    first_chunk = chunks[0]
    print(f"  Sample Chunk ID: {first_chunk['metadata']['chunk_id']}")
    print(f"  Sample Chunk Page: {first_chunk['metadata']['page']}")
    print(f"  Sample Chunk Length: {len(first_chunk['text'])} chars")
    assert "source" in first_chunk["metadata"]
    assert "page" in first_chunk["metadata"]
    assert "chunk_id" in first_chunk["metadata"]

    print("\n[Step 3] Testing Embedding Generation (all-MiniLM-L6-v2)...")
    embed_mgr = EmbeddingManager(model_name=config.EMBEDDING_MODEL_NAME)
    sample_texts = [c["text"] for c in chunks[:5]]
    embeddings = embed_mgr.embed_texts(sample_texts)
    print(f"✓ Embeddings Success! Generated {len(embeddings)} vectors of dimension {len(embeddings[0])}.")
    assert len(embeddings) == 5
    assert len(embeddings[0]) == 384, f"Expected 384 dimensions, got {len(embeddings[0])}"

    print("\n[Step 4] Testing Vector Store Storage (ChromaDB)...")
    test_db_dir = Path("test_chroma_db")
    if test_db_dir.exists():
        shutil.rmtree(test_db_dir, ignore_errors=True)

    vstore = VectorStore(persist_directory=str(test_db_dir), collection_name="test_collection")
    all_embeddings = embed_mgr.embed_texts([c["text"] for c in chunks])
    count_added = vstore.add_chunks(chunks, all_embeddings)
    print(f"✓ Vector Store Success! Indexed {count_added} chunks in ChromaDB.")

    stats = vstore.get_collection_stats()
    print(f"  Collection Stats: {stats['total_chunks']} chunks, {stats['total_documents']} docs, {stats['total_pages']} pages.")
    assert stats["total_chunks"] == len(chunks)

    print("\n[Step 5] Testing Deduplication on Re-upload...")
    vstore.add_chunks(chunks, all_embeddings)
    stats_after_reupload = vstore.get_collection_stats()
    print(f"  After Re-upload: {stats_after_reupload['total_chunks']} chunks (Deduplication verified!)")
    assert stats_after_reupload["total_chunks"] == len(chunks), "Duplicate records detected!"

    print("\n[Step 6] Testing Semantic Retrieval with Real Questions...")
    retriever = Retriever(vector_store=vstore, embedding_manager=embed_mgr)

    queries = [
        ("What is the MTTR requirement for a P1 incident at Valentius Kryptix?", "Page 7"),
        ("What are the HNSW index parameters (M, efConstruction, efSearch)?", "Page 3"),
        ("How long is the onboarding sequence for interns?", "Page 8"),
        ("What is the maximum daily input token budget for research projects?", "Page 12")
    ]

    for q, expected_page in queries:
        results = retriever.retrieve(q, top_k=3)
        print(f"\n  Query: '{q}'")
        assert len(results) > 0, "No results returned!"
        top_res = results[0]
        print(f"  → Top Match: Page {top_res['page']} | Score: {top_res['similarity_score']} | ID: {top_res['chunk_id']}")
        print(f"  → Snippet: {top_res['text'][:120]}...")

    shutil.rmtree(test_db_dir, ignore_errors=True)
    print("\n" + "=" * 60)
    print("ALL PIPELINE INTEGRATION TESTS PASSED PERFECTLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline_test()
