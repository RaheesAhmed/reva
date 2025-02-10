from typing import List, Tuple, Optional, Dict, Union
import logging
from langchain_community.vectorstores import SupabaseVectorStore # type: ignore
from langchain_openai import OpenAIEmbeddings # type: ignore
from langchain_core.documents import Document # type: ignore
from supabase.client import Client, create_client # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter # type: ignore
from tenacity import retry, stop_after_attempt, wait_exponential # type: ignore
from datetime import datetime
from config.settings import settings
from logger import setup_logger
import asyncio

logger = setup_logger(__name__)

class VectorStoreManager:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        )
        self._vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
        )

    @property
    def vector_store(self) -> SupabaseVectorStore:
        if self._vector_store is None:
            self._vector_store = SupabaseVectorStore(
                embedding=self.embeddings,
                client=self.supabase,
                table_name="documents",
                query_name="match_documents"
            )
        return self._vector_store

    async def list_documents(self) -> List[Dict]:
        """List all uploaded documents with metadata."""
        try:
            # Use regular similarity search since we don't need scores for listing
            response = self.vector_store.similarity_search(
                query="",
                k=100  # Adjust this number based on how many documents you want to list
            )
            return [{"id": doc.metadata.get("id"), "metadata": doc.metadata} for doc in response]
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise

    async def get_document(self, document_id: str) -> Dict:
        """Get a specific document's metadata."""
        try:
            response = self.vector_store.similarity_search(
                query="",
                k=1,
                filter={"id": document_id}
            )
            if response:
                doc = response[0]
                return {"id": doc.metadata.get("id"), "metadata": doc.metadata}
            return {}
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {str(e)}")
            raise

    async def delete_document(self, document_id: str) -> None:
        """Delete a document and its vectors."""
        try:
            # SupabaseVectorStore handles deletion of vectors
            await self.vector_store.delete({"id": document_id})
            logger.info(f"Successfully deleted document {document_id}")
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_from_file(
        self,
        documents: List[Document],
        metadata: Dict,
    ) -> str:
        """Create vector store from documents with metadata."""
        try:
            # Split documents into chunks
            docs = self.text_splitter.split_documents(documents)
            
            # Add metadata to each document chunk
            for doc in docs:
                doc.metadata.update(metadata)
            
            # Create vector store directly using LangChain's SupabaseVectorStore
            vector_store = await self.create_from_documents(docs)
            
            # Return the first document's ID as the main document ID
            return docs[0].metadata.get("id") if docs else None
                
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_from_documents(
        self,
        documents: List[Document],
        chunk_size: int = 500
    ) -> SupabaseVectorStore:
        """Create vector store from documents with retry logic."""
        try:
            logger.info(f"Creating vector store from {len(documents)} documents")
            vector_store = SupabaseVectorStore.from_documents(
                documents,
                self.embeddings,
                client=self.supabase,
                table_name="documents",
                query_name="match_documents",
                chunk_size=chunk_size
            )
            logger.info("Successfully created vector store")
            return vector_store
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise

    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """
        Perform a similarity search and return documents.
        
        Args:
            query (str): The query text to search for
            k (int): Number of results to return. Defaults to 4.
            filter (Optional[Dict]): Metadata filter. Defaults to None.
            
        Returns:
            List[Document]: List of documents most similar to the query
        """
        try:
            results = self.vector_store.similarity_search(
                query,
                k=k,
                filter=filter
            )
            logger.info(f"Similarity search returned {len(results)} documents")
            return results
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise

    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict] = None,
        threshold: float = 0.5
    ) -> List[Tuple[Document, float]]:
        """
        Perform a similarity search and return documents with their scores.
        
        Args:
            query (str): The query text to search for
            k (int): Number of results to return. Defaults to 4.
            filter (Optional[Dict]): Metadata filter. Defaults to None.
            threshold (float): Minimum similarity score threshold. Defaults to 0.5.
            
        Returns:
            List[Tuple[Document, float]]: List of tuples of document and its similarity score
        """
        try:
            results = self.vector_store.similarity_search_with_relevance_scores(
                query,
                k=k,
                filter=filter
            )
            
            # Filter results by threshold
            filtered_results = [
                (doc, score) for doc, score in results
                if score >= threshold
            ]
            
            logger.info(f"Similarity search returned {len(filtered_results)} documents above threshold")
            return filtered_results
        except Exception as e:
            logger.error(f"Error in similarity search with scores: {str(e)}")
            raise

    async def query(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.5,
        return_scores: bool = False,
        filter: Optional[Dict] = None
    ) -> Union[List[Document], List[Tuple[Document, float]]]:
        """
        Query the vector store with options for different search types.
        
        Args:
            query (str): The query text to search for
            k (int): Number of results to return. Defaults to 5.
            threshold (float): Minimum similarity score threshold. Defaults to 0.5.
            return_scores (bool): Whether to return similarity scores. Defaults to False.
            filter (Optional[Dict]): Metadata filter. Defaults to None.
            
        Returns:
            Union[List[Document], List[Tuple[Document, float]]]: List of documents or tuples of document and score
        """
        if return_scores:
            return await self.similarity_search_with_score(query, k, filter, threshold)
        return await self.similarity_search(query, k, filter)