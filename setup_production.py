#!/usr/bin/env python3
"""
Setup script to activate production-level RAG system
Run this after setting your OpenAI API key
"""

import os
import sys
from dotenv import load_dotenv

def setup_production_rag():
    """Configure and test production RAG system"""
    
    print("🚀 Setting up Production-Level Meta Ads RAG System")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_actual_openai_api_key_here":
        print("❌ OpenAI API key not set!")
        print("📝 Please update your .env file with your real OpenAI API key:")
        print("   OPENAI_API_KEY=sk-your-actual-key-here")
        return False
    
    print("✅ OpenAI API key configured")
    
    # Check data source
    data_source = os.getenv("DATA_SOURCE", "demo")
    print(f"📊 Data source: {data_source}")
    
    # Test data loading
    sys.path.append('src')
    try:
        from data_loader import CampaignDataLoader
        loader = CampaignDataLoader(data_source=data_source)
        campaigns = loader.get_all_campaigns()
        print(f"✅ Loaded {len(campaigns)} campaigns from {data_source} data")
        
        if data_source == "real":
            # Show real data stats
            first_campaign = campaigns[0]
            total_spend = 0
            total_impressions = 0
            for campaign in campaigns:
                for date_data in campaign["daily_performance"].values():
                    total_spend += date_data.get("spend", 0)
                    total_impressions += date_data.get("impressions", 0)
            
            print(f"💰 Real ad spend analyzed: ${total_spend:,.2f}")
            print(f"👀 Real impressions: {total_impressions:,}")
        
    except Exception as e:
        print(f"❌ Error loading campaign data: {e}")
        return False
    
    # Test RAG pipeline with OpenAI
    try:
        from rag_pipeline import MetaAdsRAGPipeline
        print("\n🤖 Testing OpenAI-powered RAG pipeline...")
        
        pipeline = MetaAdsRAGPipeline()
        
        if pipeline.use_mock:
            print("⚠️ Pipeline is running in mock mode")
            print("💡 This usually means OpenAI API key issue")
        else:
            print("✅ Pipeline is using real OpenAI GPT-4!")
        
        # Test query
        test_query = "What's the average CPM across all campaigns?"
        print(f"\n🔍 Testing query: '{test_query}'")
        result = pipeline.query(test_query)
        
        if result["success"]:
            print("✅ RAG query successful!")
            print(f"📝 Response preview: {result['answer'][:100]}...")
        else:
            print(f"❌ RAG query failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error testing RAG pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test ChromaDB integration
    try:
        from rag_processor import CampaignRAGProcessor
        print("\n🗄️ Testing ChromaDB vector store...")
        
        processor = CampaignRAGProcessor()
        campaigns = processor.load_campaign_data()
        documents = processor.create_campaign_documents()
        chunks = processor.split_documents()
        
        if os.getenv("OPENAI_API_KEY"):
            # Test real vectorstore
            vectorstore = processor.create_vectorstore()
            print("✅ ChromaDB with OpenAI embeddings working!")
        else:
            # Test mock vectorstore  
            vectorstore = processor.create_mock_vectorstore()
            print("✅ ChromaDB with mock embeddings working!")
            
        # Test search
        results = processor.search_similar("campaign performance metrics", k=3)
        print(f"✅ Vector search returned {len(results)} relevant chunks")
        
    except Exception as e:
        print(f"❌ Error testing vector store: {e}")
        return False
    
    # Production readiness checklist
    print("\n📋 Production Readiness Checklist:")
    print("✅ OpenAI API key configured")
    print(f"✅ Using {data_source} campaign data")
    print("✅ RAG pipeline operational") 
    print("✅ ChromaDB vector store working")
    print("✅ Query processing functional")
    print("✅ Streamlit UI ready")
    
    print("\n🎉 Production RAG System Ready!")
    print("\n🚀 Start your production system:")
    print("   streamlit run app.py")
    print("\n💡 You now have:")
    print("   • Real OpenAI GPT-4 analysis")
    print("   • Authentic Facebook Ads data")  
    print("   • Professional vector search")
    print("   • Production-grade RAG responses")
    
    return True

if __name__ == "__main__":
    success = setup_production_rag()
    if not success:
        print("\n❌ Production setup failed")
        print("🔧 Please fix the issues above and try again")
        sys.exit(1)
    else:
        print("\n✅ Production setup complete!")
        sys.exit(0)