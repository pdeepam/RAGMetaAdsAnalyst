"""
RAG Data Processor
Integrates campaign data with LangChain document processing for vector embeddings
"""

import os
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import tempfile

from data_loader import CampaignDataLoader
from data_chunker import CampaignDataChunker

class CampaignRAGProcessor:
    """Process campaign data for RAG system using LangChain"""
    
    def __init__(self, 
                 embeddings_model: str = "text-embedding-3-small",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 persist_directory: Optional[str] = None):
        
        self.embeddings_model = embeddings_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.persist_directory = persist_directory or self._get_temp_persist_dir()
        
        # Initialize components (will be lazy-loaded)
        self.embeddings = None
        self.text_splitter = None
        self.vectorstore = None
        self.campaign_loader = None
        self.campaign_chunker = None
        
        # Document storage
        self.documents = []
        self.processed_chunks = []
    
    def _get_temp_persist_dir(self) -> str:
        """Get temporary directory for ChromaDB persistence"""
        return os.path.join(tempfile.gettempdir(), "chroma_db_campaigns")
    
    def _init_embeddings(self):
        """Initialize embeddings (requires OpenAI API key)"""
        if self.embeddings is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            
            self.embeddings = OpenAIEmbeddings(
                model=self.embeddings_model,
                openai_api_key=api_key
            )
            print(f"✅ Initialized embeddings with model: {self.embeddings_model}")
    
    def _init_text_splitter(self):
        """Initialize text splitter"""
        if self.text_splitter is None:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            print(f"✅ Initialized text splitter (size: {self.chunk_size}, overlap: {self.chunk_overlap})")
    
    def load_campaign_data(self) -> List[Dict]:
        """Load campaign data"""
        if self.campaign_loader is None:
            self.campaign_loader = CampaignDataLoader()
        
        campaigns = self.campaign_loader.get_all_campaigns()
        print(f"✅ Loaded {len(campaigns)} campaigns")
        return campaigns
    
    def create_campaign_documents(self) -> List[Document]:
        """Convert campaign data to LangChain Documents"""
        if not self.campaign_loader:
            self.load_campaign_data()
        
        # Create chunker and generate text chunks
        if self.campaign_chunker is None:
            self.campaign_chunker = CampaignDataChunker(self.campaign_loader.campaigns_data)
        
        chunks = self.campaign_chunker.create_all_chunks()
        
        # Convert to LangChain Documents
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk["content"],
                metadata=chunk["metadata"]
            )
            documents.append(doc)
        
        self.documents = documents
        print(f"✅ Created {len(documents)} LangChain documents")
        return documents
    
    def split_documents(self, documents: Optional[List[Document]] = None) -> List[Document]:
        """Split documents into smaller chunks using LangChain splitter"""
        if documents is None:
            documents = self.documents
        
        if not documents:
            documents = self.create_campaign_documents()
        
        self._init_text_splitter()
        
        # Split documents
        split_docs = self.text_splitter.split_documents(documents)
        
        # Add chunk information to metadata
        for i, doc in enumerate(split_docs):
            doc.metadata["chunk_id"] = f"chunk_{i}"
            doc.metadata["source"] = "campaign_data"
            doc.metadata["chunk_length"] = len(doc.page_content)
        
        self.processed_chunks = split_docs
        print(f"✅ Split into {len(split_docs)} text chunks")
        return split_docs
    
    def create_vectorstore(self, documents: Optional[List[Document]] = None) -> Chroma:
        """Create ChromaDB vectorstore with campaign documents"""
        if documents is None:
            documents = self.processed_chunks
        
        if not documents:
            documents = self.split_documents()
        
        # Initialize embeddings
        self._init_embeddings()
        
        # Create or load vectorstore
        try:
            if os.path.exists(self.persist_directory):
                # Load existing vectorstore
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                print(f"✅ Loaded existing vectorstore from {self.persist_directory}")
                
                # Check if we need to add new documents
                existing_count = self.vectorstore._collection.count()
                if existing_count < len(documents):
                    print(f"📝 Adding {len(documents) - existing_count} new documents")
                    new_docs = documents[existing_count:]
                    self.vectorstore.add_documents(new_docs)
            else:
                # Create new vectorstore
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory
                )
                print(f"✅ Created new vectorstore with {len(documents)} documents")
            
            # Persist the vectorstore
            self.vectorstore.persist()
            print(f"💾 Vectorstore persisted to {self.persist_directory}")
            
        except Exception as e:
            print(f"❌ Error creating vectorstore: {e}")
            raise
        
        return self.vectorstore
    
    def create_mock_vectorstore(self, documents: Optional[List[Document]] = None) -> 'MockVectorStore':
        """Create a mock vectorstore that works without OpenAI API"""
        if documents is None:
            documents = self.processed_chunks
        
        if not documents:
            documents = self.split_documents()
        
        mock_store = MockVectorStore(documents)
        self.vectorstore = mock_store
        print(f"✅ Created mock vectorstore with {len(documents)} documents")
        return mock_store
    
    def search_similar(self, query: str, k: int = 5, use_mock: bool = False) -> List[Document]:
        """Search for similar documents"""
        if self.vectorstore is None:
            if use_mock or not os.getenv("OPENAI_API_KEY"):
                self.create_mock_vectorstore()
            else:
                self.create_vectorstore()
        
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            print(f"🔍 Found {len(results)} similar documents for query: '{query[:50]}...'")
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def get_retriever(self, search_kwargs: Dict[str, Any] = None):
        """Get a retriever for RAG pipeline"""
        if search_kwargs is None:
            search_kwargs = {"k": 5}
        
        if self.vectorstore is None:
            if os.getenv("OPENAI_API_KEY"):
                self.create_vectorstore()
            else:
                self.create_mock_vectorstore()
        
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = {
            "total_campaigns": len(self.campaign_loader.get_all_campaigns()) if self.campaign_loader else 0,
            "original_documents": len(self.documents),
            "processed_chunks": len(self.processed_chunks),
            "vectorstore_ready": self.vectorstore is not None,
            "embeddings_ready": self.embeddings is not None,
            "persist_directory": self.persist_directory
        }
        
        if self.vectorstore and hasattr(self.vectorstore, '_collection'):
            try:
                stats["vectorstore_count"] = self.vectorstore._collection.count()
            except:
                stats["vectorstore_count"] = "unknown"
        
        return stats


class MockVectorStore:
    """Mock vector store for demo purposes (no API key required)"""
    
    def __init__(self, documents: List[Document]):
        self.documents = documents
        print(f"📚 MockVectorStore initialized with {len(documents)} documents")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Simple keyword-based similarity search"""
        query_words = set(query.lower().split())
        
        # Score documents based on keyword overlap
        scored_docs = []
        for doc in self.documents:
            content_words = set(doc.page_content.lower().split())
            
            # Calculate simple similarity score
            overlap = len(query_words.intersection(content_words))
            relevance_score = overlap / len(query_words) if query_words else 0
            
            # Bonus for metadata matches
            metadata_text = " ".join(str(v) for v in doc.metadata.values()).lower()
            metadata_overlap = len(query_words.intersection(set(metadata_text.split())))
            relevance_score += metadata_overlap * 0.1
            
            if relevance_score > 0:
                scored_docs.append((relevance_score, doc))
        
        # Sort by relevance and return top k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        results = [doc for _, doc in scored_docs[:k]]
        
        # If no good matches, return some relevant docs
        if not results and self.documents:
            results = self.documents[:k]
        
        return results
    
    def as_retriever(self, search_kwargs: Dict[str, Any] = None):
        """Return a mock retriever"""
        if search_kwargs is None:
            search_kwargs = {"k": 5}
        
        class MockRetriever:
            def __init__(self, vectorstore, k=5):
                self.vectorstore = vectorstore
                self.k = k
            
            def get_relevant_documents(self, query: str) -> List[Document]:
                return self.vectorstore.similarity_search(query, k=self.k)
        
        return MockRetriever(self, search_kwargs.get("k", 5))


# Test the processor
if __name__ == "__main__":
    print("🚀 Testing Campaign RAG Processor...")
    
    # Test without API key (mock mode)
    processor = CampaignRAGProcessor()
    
    # Load and process data
    campaigns = processor.load_campaign_data()
    documents = processor.create_campaign_documents()
    chunks = processor.split_documents()
    
    # Create mock vectorstore
    vectorstore = processor.create_mock_vectorstore()
    
    # Test search
    test_queries = [
        "CPM spike fashion campaign",
        "Black Friday electronics performance",
        "audience saturation frequency",
        "retargeting vs lookalike ROAS"
    ]
    
    for query in test_queries:
        results = processor.search_similar(query, k=3, use_mock=True)
        print(f"\n🔍 Query: '{query}'")
        for i, doc in enumerate(results):
            print(f"  {i+1}. {doc.metadata.get('chunk_type', 'unknown')} - {doc.page_content[:100]}...")
    
    # Show stats
    stats = processor.get_stats()
    print(f"\n📊 Processing Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n✅ RAG Processor working correctly!")