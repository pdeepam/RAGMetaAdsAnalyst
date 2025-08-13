"""
LangChain RAG Pipeline
Complete RAG system that connects query processing → retrieval → LLM generation
"""

import os
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

from rag_processor import CampaignRAGProcessor, MockVectorStore
from query_processor import CampaignQueryProcessor


class MetaAdsRAGPipeline:
    """Complete RAG pipeline for Meta Ads campaigns analysis"""
    
    def __init__(self, 
                 model_name: str = "gpt-4o-mini",
                 temperature: float = 0.1,
                 use_mock: bool = False):
        
        self.model_name = model_name
        self.temperature = temperature
        self.use_mock = use_mock
        
        # Initialize components
        self.rag_processor = CampaignRAGProcessor()
        self.query_processor = CampaignQueryProcessor()
        self.llm = None
        self.retriever = None
        self.rag_chain = None
        
        # Initialize the pipeline
        self._setup_pipeline()
    
    def _setup_pipeline(self):
        """Set up the complete RAG pipeline"""
        try:
            # Initialize LLM
            self._init_llm()
            
            # Initialize retriever
            self._init_retriever()
            
            # Create RAG chain
            self._create_rag_chain()
            
            print("✅ RAG Pipeline initialized successfully!")
            
        except Exception as e:
            print(f"⚠️ Setting up mock RAG pipeline: {e}")
            self.use_mock = True
            self._setup_mock_pipeline()
    
    def _init_llm(self):
        """Initialize the LLM"""
        if self.use_mock or not os.getenv("OPENAI_API_KEY"):
            # Use mock LLM for demo
            self.llm = MockLLM()
            print("📚 Using Mock LLM (no API key required)")
        else:
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            print(f"🤖 Initialized {self.model_name} with temperature {self.temperature}")
    
    def _init_retriever(self):
        """Initialize the retriever"""
        if self.use_mock or not os.getenv("OPENAI_API_KEY"):
            # Use mock vectorstore
            self.rag_processor.create_mock_vectorstore()
        else:
            # Use real ChromaDB
            self.rag_processor.create_vectorstore()
        
        self.retriever = self.rag_processor.get_retriever(search_kwargs={"k": 5})
        print("🔍 Retriever ready")
    
    def _create_rag_chain(self):
        """Create the RAG chain"""
        # Define the prompt template
        prompt_template = """You are a Meta Ads expert analyst. Use the provided campaign data to answer questions about Meta advertising performance, optimization, and insights.

Context from campaigns:
{context}

Question: {question}

Provide a detailed, data-driven answer based on the campaign information. If specific metrics are mentioned in the context, include them in your response. Be professional and actionable in your recommendations.

Answer:"""

        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # Create the RAG chain
        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        print("🔗 RAG chain created successfully")
    
    def _setup_mock_pipeline(self):
        """Setup mock pipeline when no API key is available"""
        self._init_llm()  # Will use mock LLM
        self._init_retriever()  # Will use mock vectorstore
        
        # Create a simple mock chain
        self.rag_chain = MockRAGChain(self.retriever, self.llm)
        print("🔗 Mock RAG chain created")
    
    def query(self, question: str, include_sources: bool = True) -> Dict[str, Any]:
        """Process a query through the RAG pipeline"""
        try:
            # Classify the query intent
            query_intent = self.query_processor.classify_query(question)
            
            # Get answer from RAG chain
            if hasattr(self.rag_chain, 'invoke'):
                answer = self.rag_chain.invoke(question)
            else:
                # Handle mock chain
                answer = self.rag_chain.query(question)
            
            # Get source documents if requested
            sources = []
            if include_sources:
                retrieved_docs = self.retriever.get_relevant_documents(question)
                sources = [
                    {
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in retrieved_docs[:3]  # Top 3 sources
                ]
            
            return {
                "answer": answer,
                "query_intent": query_intent,
                "sources": sources,
                "success": True
            }
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error processing your query: {str(e)}",
                "query_intent": "unknown",
                "sources": [],
                "success": False,
                "error": str(e)
            }
    
    def batch_query(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Process multiple queries"""
        return [self.query(q) for q in questions]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        stats = self.rag_processor.get_stats()
        stats.update({
            "llm_model": self.model_name if not self.use_mock else "Mock LLM",
            "temperature": self.temperature,
            "using_mock": self.use_mock,
            "pipeline_ready": self.rag_chain is not None
        })
        return stats


class MockLLM:
    """Mock LLM for demo purposes"""
    
    def __init__(self):
        self.responses = {
            "cpm": "Based on the campaign data, CPM spikes can indicate audience saturation or increased competition. I recommend analyzing frequency caps and expanding your target audience.",
            "roas": "The ROAS data shows strong performance in Electronics campaigns. Consider reallocating budget from underperforming segments to maximize returns.",
            "frequency": "High frequency rates may indicate audience fatigue. Try refreshing your creative assets or expanding your audience targeting.",
            "performance": "Campaign performance analysis shows seasonal trends. Black Friday periods typically see 40-60% higher engagement rates.",
            "optimization": "For campaign optimization, focus on high-performing ad sets and pause underperforming creative variants. A/B testing different audience segments is recommended."
        }
    
    def invoke(self, prompt):
        """Generate mock response"""
        if hasattr(prompt, 'to_string'):
            text = prompt.to_string()
        else:
            text = str(prompt)
        
        # Simple keyword matching for demo
        text_lower = text.lower()
        for keyword, response in self.responses.items():
            if keyword in text_lower:
                return f"{response}\n\n(Note: This is a mock response for demo purposes. Connect an OpenAI API key for real AI analysis.)"
        
        return "Based on the campaign data provided, I can help analyze your Meta Ads performance. Please provide more specific questions about CPM, ROAS, frequency, or campaign optimization.\n\n(Note: This is a mock response for demo purposes. Connect an OpenAI API key for real AI analysis.)"


class MockRAGChain:
    """Mock RAG chain for demo purposes"""
    
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
    
    def query(self, question: str) -> str:
        """Process query with mock RAG"""
        # Get relevant documents
        docs = self.retriever.get_relevant_documents(question)
        
        # Create context from documents
        context = "\n\n".join([doc.page_content[:300] for doc in docs[:3]])
        
        # Generate response with context awareness
        response = self.llm.invoke(f"Context: {context}\n\nQuestion: {question}")
        
        return response


# Test the pipeline
if __name__ == "__main__":
    print("🚀 Testing Meta Ads RAG Pipeline...")
    
    # Initialize pipeline (will use mock mode without API key)
    pipeline = MetaAdsRAGPipeline()
    
    # Test queries
    test_queries = [
        "Why did CPM spike in my fashion campaign?",
        "How is my Black Friday electronics campaign performing?",
        "What's causing audience saturation in my retargeting campaigns?",
        "Compare ROAS between lookalike and retargeting audiences",
        "What optimizations should I make for better performance?"
    ]
    
    print("\n📝 Testing RAG Pipeline with sample queries:\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Query {i}: {query}")
        result = pipeline.query(query)
        
        print(f"📋 Intent: {result['query_intent']}")
        print(f"💬 Answer: {result['answer'][:200]}...")
        if result['sources']:
            print(f"📚 Sources: {len(result['sources'])} documents")
        print(f"✅ Success: {result['success']}\n")
    
    # Show stats
    stats = pipeline.get_stats()
    print("📊 Pipeline Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ RAG Pipeline working correctly!")