from typing import List, Dict, Any, Optional
from langchain.schema import Document #type: ignore
from langchain_community.vectorstores import SupabaseVectorStore #type: ignore
from langchain_openai import OpenAIEmbeddings #type: ignore
import os
from logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)

class DocumentProcessor:
    """Handles processing and vectorization of documents."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY
        )
        
    def process_documents(
        self,
        documents: List[Document],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Process documents and add metadata.
        
        Args:
            documents: List of documents to process
            metadata: Optional metadata to add to documents
            
        Returns:
            List[Document]: Processed documents
        """
        try:
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            logger.info(f"Processed {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            raise
    
    def vectorize_documents(
        self,
        documents: List[Document],
        vector_store: SupabaseVectorStore
    ) -> None:
        """
        Convert documents to vectors and store in vector database.
        
        Args:
            documents: List of documents to vectorize
            vector_store: Vector store instance
        """
        try:
            vector_store.add_documents(documents)
            logger.info(f"Vectorized and stored {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error vectorizing documents: {str(e)}")
            raise
            
    def search_similar(
        self,
        query: str,
        vector_store: SupabaseVectorStore,
        num_results: int = 5
    ) -> List[Document]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query
            vector_store: Vector store instance
            num_results: Number of results to return
            
        Returns:
            List[Document]: Similar documents
        """
        try:
            results = vector_store.similarity_search(
                query,
                k=num_results
            )
            logger.info(f"Found {len(results)} similar documents for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            raise 