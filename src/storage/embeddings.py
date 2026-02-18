from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger("rog.storage.embedding")

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
    def embed_text(self, text: str):
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: list):
        return self.model.encode(texts).tolist()

# Singleton instance
_embedding_service = None

def get_embedding_service():
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
