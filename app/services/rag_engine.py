"""
RAG (Retrieval-Augmented Generation) Engine
Handles document indexing and retrieval using embeddings and FAISS
"""
import numpy as np
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import faiss
from app.core.config import settings
from app.core.logger import logger


class RAGEngine:
    """RAG engine for document retrieval"""
    
    def __init__(self):
        self.model = None
        self.index = None
        self.documents = []
        self.embeddings = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
    
    def index_documents(self, documents: List[str]):
        """Index documents for retrieval"""
        try:
            if not self.model:
                raise Exception("Embedding model not initialized")
            
            if not documents:
                logger.warning("No documents to index")
                return
            
            # Store documents
            self.documents = documents
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(documents)} documents...")
            self.embeddings = self.model.encode(documents, show_progress_bar=True)
            
            # Create FAISS index
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            
            # Add embeddings to index
            self.index.add(np.array(self.embeddings).astype('float32'))
            
            logger.info(f"Indexed {len(documents)} documents successfully")
            
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")
            raise
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> List[Tuple[str, float]]:
        """Retrieve most relevant documents for a query"""
        try:
            if not self.model or not self.index:
                raise Exception("RAG engine not initialized")
            
            if not self.documents:
                logger.warning("No documents indexed")
                return []
            
            k = top_k or settings.TOP_K_RESULTS
            k = min(k, len(self.documents))  # Don't retrieve more than available
            
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            
            # Search in FAISS index
            distances, indices = self.index.search(
                np.array([query_embedding]).astype('float32'),
                k
            )
            
            # Prepare results
            results = []
            for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
                if idx < len(self.documents):
                    # Convert distance to similarity score (inverse)
                    score = 1 / (1 + distance)
                    results.append((self.documents[idx], float(score)))
            
            logger.info(f"Retrieved {len(results)} documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    def add_documents(self, new_documents: List[str]):
        """Add new documents to existing index"""
        try:
            if not new_documents:
                return
            
            # If no existing index, create new one
            if not self.index:
                self.index_documents(new_documents)
                return
            
            # Add to existing documents
            self.documents.extend(new_documents)
            
            # Generate embeddings for new documents
            new_embeddings = self.model.encode(new_documents)
            
            # Add to index
            self.index.add(np.array(new_embeddings).astype('float32'))
            
            # Update embeddings array
            if self.embeddings is not None:
                self.embeddings = np.vstack([self.embeddings, new_embeddings])
            else:
                self.embeddings = new_embeddings
            
            logger.info(f"Added {len(new_documents)} new documents to index")
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def clear_index(self):
        """Clear the current index"""
        self.index = None
        self.documents = []
        self.embeddings = None
        logger.info("Index cleared")


# Create global instance
rag_engine = RAGEngine()

