from typing import List, Union
import numpy as np


class EmbeddingManager:
    _instance = None
    _model = None

    def __new__(cls, model_name: str = "all-MiniLM-L6-v2"):
        if cls._instance is None:
            cls._instance = super(EmbeddingManager, cls).__new__(cls)
            cls._instance.model_name = model_name
        return cls._instance

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load embedding model '{self.model_name}': {str(e)}. "
                    "Ensure 'sentence-transformers' and 'torch' are properly installed."
                )

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        if not texts:
            return []

        self._load_model()
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        if isinstance(embeddings, np.ndarray):
            return embeddings.tolist()
        return [e.tolist() if hasattr(e, "tolist") else list(e) for e in embeddings]

    def embed_query(self, query: str) -> List[float]:
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")

        self._load_model()
        embedding = self._model.encode(
            query.strip(),
            show_progress_bar=False,
            normalize_embeddings=True
        )

        if isinstance(embedding, np.ndarray):
            return embedding.tolist()
        return list(embedding)
