import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import config


class VectorStore:
    def __init__(self, persist_directory: Optional[str] = None, collection_name: Optional[str] = None):
        self.persist_directory = persist_directory or config.CHROMA_PERSIST_DIR
        self.collection_name = collection_name or config.CHROMA_COLLECTION_NAME

        os.makedirs(self.persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
        if not chunks:
            return 0

        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch between number of chunks ({len(chunks)}) and embeddings ({len(embeddings)})")

        docs_to_update = set(chunk["metadata"]["source"] for chunk in chunks)
        for doc_name in docs_to_update:
            self.delete_document(doc_name)

        ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            self.collection.upsert(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )

        return len(chunks)

    def query(self, query_embedding: List[float], top_k: int = 4) -> List[Dict[str, Any]]:
        total_count = self.collection.count()
        if total_count == 0:
            return []

        k = min(top_k, total_count)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )

        retrieved: List[Dict[str, Any]] = []
        if not results or not results["ids"] or not results["ids"][0]:
            return []

        ids = results["ids"][0]
        docs = results["documents"][0] if results["documents"] else []
        metas = results["metadatas"][0] if results["metadatas"] else []
        dists = results["distances"][0] if results["distances"] else []

        for idx in range(len(ids)):
            distance = dists[idx] if idx < len(dists) else 1.0
            similarity = max(0.0, min(1.0, 1.0 - distance))

            retrieved.append({
                "chunk_id": ids[idx],
                "text": docs[idx] if idx < len(docs) else "",
                "metadata": metas[idx] if idx < len(metas) else {},
                "distance": distance,
                "similarity_score": round(similarity, 4)
            })

        return retrieved

    def delete_document(self, filename: str) -> None:
        try:
            self.collection.delete(where={"source": filename})
        except Exception:
            pass

    def clear_collection(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def get_collection_stats(self) -> Dict[str, Any]:
        total_chunks = self.collection.count()
        if total_chunks == 0:
            return {
                "total_chunks": 0,
                "total_documents": 0,
                "documents": []
            }

        all_data = self.collection.get(include=["metadatas"])
        doc_names = set()
        doc_pages: Dict[str, set] = {}
        doc_chunks: Dict[str, int] = {}

        for meta in all_data.get("metadatas", []):
            if meta and "source" in meta:
                source = meta["source"]
                doc_names.add(source)
                doc_chunks[source] = doc_chunks.get(source, 0) + 1
                if source not in doc_pages:
                    doc_pages[source] = set()
                if "page" in meta:
                    doc_pages[source].add(meta["page"])

        doc_summary = [
            {
                "filename": name,
                "pages_indexed": len(doc_pages.get(name, set())),
                "chunks_indexed": doc_chunks.get(name, 0)
            }
            for name in sorted(doc_names)
        ]

        total_pages = sum(item["pages_indexed"] for item in doc_summary)

        return {
            "total_chunks": total_chunks,
            "total_documents": len(doc_names),
            "total_pages": total_pages,
            "documents": doc_summary
        }
