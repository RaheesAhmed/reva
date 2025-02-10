from typing import List, Union
from pathlib import Path
import logging
from logger import setup_logger
from langchain_community.document_loaders import ( 
    UnstructuredExcelLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
) 
from langchain_core.documents import Document 

logger = setup_logger(__name__)

class DocumentLoader:
    """Handles loading of various document types with error handling and logging."""
    
    SUPPORTED_EXTENSIONS = {
        '.xlsx': UnstructuredExcelLoader,
        '.pdf': PyPDFLoader,
        '.docx': Docx2txtLoader,
        '.txt': TextLoader
    }
    
    @classmethod
    def load_file(cls, file_path: Union[str, Path]) -> List[Document]:
        """Load a single file with appropriate loader based on extension."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        extension = file_path.suffix.lower()
        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")
            
        try:
            loader = cls.SUPPORTED_EXTENSIONS[extension](str(file_path))
            logger.info(f"Loading file: {file_path}")
            documents = loader.load()
            logger.info(f"Successfully loaded {len(documents)} documents from {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            raise

    @classmethod
    def load_directory(cls, directory_path: Union[str, Path]) -> List[Document]:
        """Load all supported files from a directory."""
        directory = Path(directory_path)
        if not directory.exists():
            raise NotADirectoryError(f"Directory not found: {directory}")
            
        all_documents = []
        for file_path in directory.iterdir():
            if file_path.suffix.lower() in cls.SUPPORTED_EXTENSIONS:
                try:
                    documents = cls.load_file(file_path)
                    all_documents.extend(documents)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    continue
                    
        return all_documents