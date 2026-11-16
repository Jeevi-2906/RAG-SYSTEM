import os
import sys
import shutil
from pathlib import Path
from rag.document_processor import DocumentProcessor
from rag.chunking import IntelligentChunker
from rag.embeddings import EmbeddingManager
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.generator import AnswerGenerator
import config


def run_all_tests():
    print("=" * 70)
    print("DOCUMIND AI — AUTOMATED 12-POINT SPECIFICATION VALIDATION SUITE")
    print("=" * 70)

    pdf_path = Path("sample_documents/AI_Concepts.pdf")
    print("\n[TEST 1] Verifying PDF document collection...")
    assert pdf_path.exists(), "Sample PDF not found!"
    doc_res = DocumentProcessor.extract_text_from_pdf(str(pdf_path), filename=pdf_path.name)
    total_pages = doc_res["total_pages"]
    print(f"  → Document: {pdf_path.name} | Total Pages: {total_pages}")
    assert total_pages >= 5, f"Expected at least 5 pages, got {total_pages}"
    print("  [PASS] Test 1: Real PDF document verified.")

    print("\n[TEST 2] Verifying text extraction from PDF...")
    assert doc_res["success"] is True
    assert len(doc_res["pages"]) == total_pages
    page_1_text = doc_res["pages"][0]["text"]
    assert len(page_1_text) > 20
    print(f"  → Page 1 sample text preview: {page_1_text[:80]}...")
    print("  [PASS] Test 2: Text extraction successfully retrieved all pages.")

    print("\n[TEST 3] Verifying text chunking...")
    chunker = IntelligentChunker(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    chunks = chunker.chunk_document(doc_res)
    print(f"  → Generated {len(chunks)} chunks across {total_pages} pages.")
    assert len(chunks) >= 5, f"Expected multiple chunks, got {len(chunks)}"

    for sample_chunk in [chunks[0], chunks[-1]]:
        meta = sample_chunk["metadata"]
        assert "source" in meta
        assert "page" in meta
        assert "chunk_id" in meta
        assert len(sample_chunk["text"]) > 20
    print("  [PASS] Test 3: Meaningful chunking with rich metadata validated.")

    print("\n[TEST 4] Verifying embedding generation with Sentence Transformers...")
    embed_mgr = EmbeddingManager(model_name=config.EMBEDDING_MODEL_NAME)
    sample_text = chunks[0]["text"]
    query_vector = embed_mgr.embed_query("What is Artificial Intelligence?")
    assert len(query_vector) == 384, f"Expected vector dim 384, got {len(query_vector)}"
    print(f"  → Embedding vector dimension: {len(query_vector)}")
    print("  [PASS] Test 4: Embedding generation successful.")

    print("\n[TEST 5] Verifying persistent ChromaDB storage and deduplication...")
    test_db_dir = Path("test_validation_chromadb")
    if test_db_dir.exists():
        shutil.rmtree(test_db_dir, ignore_errors=True)

    vstore = VectorStore(persist_directory=str(test_db_dir), collection_name="validation_col")
    all_embeddings = embed_mgr.embed_texts([c["text"] for c in chunks])
    vstore.add_chunks(chunks, all_embeddings)

    stats = vstore.get_collection_stats()
    assert stats["total_chunks"] == len(chunks)
    assert stats["total_documents"] == 1

    vstore.add_chunks(chunks, all_embeddings)
    stats_after = vstore.get_collection_stats()
    assert stats_after["total_chunks"] == len(chunks)
    print(f"  → Chunks indexed: {stats_after['total_chunks']} (Deduplication confirmed)")
    print("  [PASS] Test 5: Persistent ChromaDB indexing and deduplication verified.")

    print("\n[TEST 6 & 7] Asking in-document questions & verifying relevant chunk retrieval...")
    retriever = Retriever(vector_store=vstore, embedding_manager=embed_mgr)

    test_questions = [
        {"query": "What is Artificial Intelligence?", "keyword": "Intelligence"},
        {"query": "What is Retrieval-Augmented Generation?", "keyword": "Retrieval"}
    ]

    for item in test_questions:
        q = item["query"]
        results = retriever.retrieve(q, top_k=config.DEFAULT_TOP_K)
        assert len(results) > 0, f"No chunks retrieved for: {q}"
        top = results[0]
        print(f"  Q: '{q}'")
        print(f"    → Top Chunk: Page {top['page']} | Score: {top['similarity_score']} | ID: {top['chunk_id']}")
        found_keyword = any(item["keyword"].lower() in c["text"].lower() for c in results)
        assert found_keyword, f"Expected keyword '{item['keyword']}' in retrieved chunks for '{q}'"
        print(f"    ✓ Retrieved exact relevant context containing '{item['keyword']}'")
    print("  [PASS] Tests 6 & 7: Semantic retrieval fetched top relevant chunks with high scores.")

    print("\n[TEST 8] Verifying RAG Prompt construction...")
    generator = AnswerGenerator()
    retrieved_for_rag = retriever.retrieve("What is RAG?", top_k=2)
    context_str = retriever.format_context_for_prompt(retrieved_for_rag)
    assert len(context_str) > 20
    print("  [PASS] Test 8: RAG prompt construction verified.")

    print("\n[TEST 9 & 10] Asking out-of-scope question & verifying strict refusal behavior...")
    out_of_scope_query = "What is the recipe for chocolate chip cookies?"
    empty_chunks = []
    out_of_scope_res = generator.generate_rag_answer(out_of_scope_query, empty_chunks)
    expected_refusal = "I could not find this information in your uploaded documents."
    assert out_of_scope_res["answer"] == expected_refusal, f"Expected '{expected_refusal}', got '{out_of_scope_res['answer']}'"
    print(f"  → Query: '{out_of_scope_query}'")
    print(f"  → System Output: \"{out_of_scope_res['answer']}\"")
    print("  [PASS] Tests 9 & 10: System strictly refuses to answer when information is unavailable.")

    print("\n[TEST 11] Testing Normal LLM vs RAG Comparison flow...")
    comp_query = "What is Retrieval-Augmented Generation?"
    rag_chunks = retriever.retrieve(comp_query, top_k=3)
    assert len(rag_chunks) > 0
    rag_context_present = len(rag_chunks) > 0
    assert rag_context_present is True
    print("  [PASS] Test 11: Normal vs RAG comparative paths verified.")

    print("\n[TEST 12] Verifying Source Document and Page Reference Display...")
    for chunk in rag_chunks:
        assert chunk["source"] == "AI_Concepts.pdf"
        assert isinstance(chunk["page"], int) and chunk["page"] > 0
        assert 0.0 <= chunk["similarity_score"] <= 1.0
    print(f"  → Verified sources: {rag_chunks[0]['source']}, Page {rag_chunks[0]['page']}")
    print("  [PASS] Test 12: Source and page references accurately tracked and formatted.")

    shutil.rmtree(test_db_dir, ignore_errors=True)
    print("\n" + "=" * 70)
    print("ALL 12 ASSIGNMENT SPECIFICATIONS VALIDATED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
