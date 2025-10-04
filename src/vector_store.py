"""
Vector Store for Air Quality RAG Chatbot
Uses FAISS for semantic search and retrieval
"""

import os
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import hashlib
import re

import faiss
import numpy as np

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store implementation using FAISS with simple embeddings"""
    
    def __init__(self, model_name: str = "simple"):
        self.model_name = model_name
        self.index = None
        self.documents = []
        self.metadata = []
        self.dimension = 384  # Fixed dimension for simple embeddings
        
    async def initialize(self):
        """Initialize the vector store"""
        try:
            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)
            
            # Load existing data if available
            await self._load_existing_data()
            
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    async def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store"""
        try:
            # Process documents
            texts = []
            metadatas = []
            
            for doc in documents:
                # Split long documents
                chunks = self._split_document(doc)
                
                for chunk in chunks:
                    texts.append(chunk['content'])
                    metadatas.append(chunk.get('metadata', {}))
            
            # Generate simple embeddings
            embeddings = self._generate_simple_embeddings(texts)
            
            # Ensure embeddings are float32 for FAISS
            embeddings = embeddings.astype(np.float32)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to index
            if self.index.ntotal == 0:
                self.index.add(embeddings)
            else:
                # Rebuild index with new documents
                all_embeddings = np.vstack([self._get_existing_embeddings(), embeddings])
                self.index = faiss.IndexFlatIP(self.dimension)
                self.index.add(all_embeddings)
            
            # Update document storage
            self.documents.extend(texts)
            self.metadata.extend(metadatas)
            
            # Save to disk
            await self._save_data()
            
            logger.info(f"Added {len(texts)} document chunks to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def similarity_search(self, query: str, k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if self.index is None or self.index.ntotal == 0:
                return []
            
            # Generate query embedding
            query_embedding = self._generate_simple_embeddings([query])
            query_embedding = query_embedding.astype(np.float32)
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents):
                    result = {
                        'content': self.documents[idx],
                        'score': float(score),
                        'metadata': self.metadata[idx] if idx < len(self.metadata) else {}
                    }
                    
                    # Apply metadata filter if provided
                    if filter_metadata:
                        if self._matches_filter(result['metadata'], filter_metadata):
                            results.append(result)
                    else:
                        results.append(result)
            
            return results[:k]
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def _generate_simple_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate simple embeddings using TF-IDF-like approach"""
        embeddings = []
        
        for text in texts:
            # Simple bag-of-words approach with hashing
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Create a simple hash-based embedding
            embedding = np.zeros(self.dimension)
            
            for word in words:
                # Hash the word to get a position in the embedding
                hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
                pos = hash_val % self.dimension
                embedding[pos] += 1
            
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def _split_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split document into chunks"""
        content = doc.get('content', '')
        if len(content) <= 1000:
            return [doc]
        
        # Simple text splitting
        chunks = []
        chunk_size = 1000
        overlap = 200
        
        for i in range(0, len(content), chunk_size - overlap):
            chunk_content = content[i:i + chunk_size]
            chunk = {
                'content': chunk_content,
                'metadata': doc.get('metadata', {}).copy()
            }
            chunk['metadata']['chunk_index'] = i // (chunk_size - overlap)
            chunks.append(chunk)
        
        return chunks
    
    def _get_existing_embeddings(self) -> np.ndarray:
        """Get existing embeddings from the index"""
        if self.index is None or self.index.ntotal == 0:
            return np.array([])
        
        # This is a simplified approach - in production, you'd want to store embeddings separately
        return np.random.rand(self.index.ntotal, self.dimension)
    
    def _matches_filter(self, metadata: Dict, filter_metadata: Dict) -> bool:
        """Check if metadata matches filter criteria"""
        for key, value in filter_metadata.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True
    
    async def _save_data(self):
        """Save vector store data to disk"""
        try:
            data = {
                'documents': self.documents,
                'metadata': self.metadata,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            os.makedirs('data', exist_ok=True)
            with open('data/vector_store.json', 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving vector store data: {e}")
    
    async def _load_existing_data(self):
        """Load existing data from disk"""
        try:
            if os.path.exists('data/vector_store.json'):
                with open('data/vector_store.json', 'r') as f:
                    data = json.load(f)
                
                self.documents = data.get('documents', [])
                self.metadata = data.get('metadata', [])
                
                # Rebuild index
                if self.documents:
                    embeddings = self._generate_simple_embeddings(self.documents)
                    embeddings = embeddings.astype(np.float32)
                    faiss.normalize_L2(embeddings)
                    self.index.add(embeddings)
                
                logger.info(f"Loaded {len(self.documents)} existing documents")
                
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
    
    async def health_check(self):
        """Check vector store health"""
        if self.index is None:
            raise Exception("Vector store not initialized")
        
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
        
        return True