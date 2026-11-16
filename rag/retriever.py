from typing import List, Dict, Any, Optional
from rag.embeddings import EmbeddingManager
from rag.vector_store import VectorStore
import config


class Retriever:
    def __init__(self, vector_store: Optional[VectorStore] = None, embedding_manager: Optional[EmbeddingManager] = None):
        self.vector_store = vector_store or VectorStore()
        self.embedding_manager = embedding_manager or EmbeddingManager()

    def retrieve(self, query: str, top_k: int = config.DEFAULT_TOP_K) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        is_broad_query = any(w in query.lower() for w in ["topic", "summary", "summarize", "overview", "table of contents", "chapters", "outline", "about this pdf", "current pdf"])
        effective_k = min(top_k + 2 if is_broad_query else top_k, 8)

        query_vector = self.embedding_manager.embed_query(query)
        raw_results = self.vector_store.query(query_vector, top_k=effective_k)

        formatted_results: List[Dict[str, Any]] = []
        for item in raw_results:
            meta = item.get("metadata", {})
            formatted_results.append({
                "chunk_id": item.get("chunk_id", ""),
                "text": item.get("text", ""),
                "source": meta.get("source", "Unknown Document"),
                "page": meta.get("page", 1),
                "char_count": meta.get("char_count", len(item.get("text", ""))),
                "similarity_score": item.get("similarity_score", 0.0),
                "distance": item.get("distance", 1.0)
            })

        return formatted_results

    def format_context_for_prompt(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        if not retrieved_chunks:
            return "No document context retrieved."

        context_blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("source", "Unknown")
            page = chunk.get("page", 1)
            score = chunk.get("similarity_score", 0.0)
            text = chunk.get("text", "").strip()

            block = (
                f"--- [Document Chunk {i}] ---\n"
                f"Source: {source} (Page {page}) | Relevance Score: {score:.2f}\n"
                f"Content:\n{text}\n"
            )
            context_blocks.append(block)

        return "\n".join(context_blocks)
