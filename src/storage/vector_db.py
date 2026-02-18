from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging
import uuid

logger = logging.getLogger("rog.storage.vector_db")

COLLECTION_NAME = "rog_documents"

class VectorDBStub:
    """
    Qdrant client using local disk storage for persistence.
    """
    def __init__(self):
        # Using local disk storage
        self.db_path = "data/qdrant_db"
        # Ensure path exists? Qdrant handles it usually, but let's be safe if needed or let library handle.
        # Actually Qdrant local mode creates it.
        self.client = QdrantClient(path=self.db_path) 
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )
            logger.info(f"Collection {COLLECTION_NAME} created.")
        except Exception:
            # Collection might already exist
            pass

    def upsert_chunks(self, chunks: list, embeddings: list, keys: list, metadata: dict, filename: str):
        """
        Upsert processed chunks into the DB.
        """
        points = []
        for i, (text, vector) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            payload = {
                "text": text,
                "keys": keys,
                "filename": filename,
                "chunk_index": i,
                **metadata
            }
            
            points.append(models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            ))
            
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        logger.info(f"Upserted {len(points)} chunks for {filename}")

    def search(self, query_vector: list, filter_keys: list = None, exclude_keys: list = None, top_k: int = 5):
        """
        Search for similar chunks.
        """
        # Build filters
        should_conditions = None
        if filter_keys:
            # Match ANY of the filter keys
            should_conditions = [
                models.FieldCondition(key="keys", match=models.MatchValue(value=k))
                for k in filter_keys
            ]

        must_not_conditions = None
        if exclude_keys:
             must_not_conditions = [
                models.FieldCondition(key="keys", match=models.MatchValue(value=k))
                for k in exclude_keys
            ]
            
        if should_conditions or must_not_conditions:
            query_filter = models.Filter(
                should=should_conditions,
                must_not=must_not_conditions
            )
            
        # For simplicity in this step, just basic search
        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k
        )
        return results

# Singleton
_vector_db = None

def get_vector_db():
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDBStub()
    return _vector_db
