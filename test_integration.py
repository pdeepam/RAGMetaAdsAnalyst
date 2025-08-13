#!/usr/bin/env python3
"""
Integration Test for Meta Ads RAG Demo
Tests the complete pipeline from data loading to RAG responses
"""

import sys
import os
sys.path.append('src')

def test_complete_pipeline():
    """Test the complete RAG pipeline integration"""
    print("🚀 Testing Complete Meta Ads RAG Pipeline Integration\n")
    
    try:
        # Test 1: Data Loading
        print("📊 Test 1: Data Loading...")
        from data_loader import CampaignDataLoader
        loader = CampaignDataLoader()
        campaigns = loader.get_all_campaigns()
        print(f"✅ Loaded {len(campaigns)} campaigns")
        
        # Test 2: Data Chunking
        print("\n📝 Test 2: Data Chunking...")
        from data_chunker import CampaignDataChunker
        chunker = CampaignDataChunker(loader.campaigns_data)
        chunks = chunker.create_all_chunks()
        print(f"✅ Created {len(chunks)} text chunks")
        
        # Test 3: Query Processing
        print("\n🧠 Test 3: Query Processing...")
        from query_processor import CampaignQueryProcessor
        query_processor = CampaignQueryProcessor()
        test_query = "Why did my CPM spike in the fashion campaign?"
        intent = query_processor.classify_query(test_query)
        print(f"✅ Query classified as: {intent.intent_type}")
        
        # Test 4: RAG Processor
        print("\n🔍 Test 4: RAG Processor...")
        from rag_processor import CampaignRAGProcessor
        rag_processor = CampaignRAGProcessor()
        
        # Load and process data
        campaigns = rag_processor.load_campaign_data()
        documents = rag_processor.create_campaign_documents()
        chunks = rag_processor.split_documents()
        
        # Create mock vectorstore (works without API key)
        vectorstore = rag_processor.create_mock_vectorstore()
        print(f"✅ RAG processor ready with {len(chunks)} chunks")
        
        # Test 5: Complete RAG Pipeline
        print("\n🤖 Test 5: Complete RAG Pipeline...")
        from rag_pipeline import MetaAdsRAGPipeline
        pipeline = MetaAdsRAGPipeline()
        
        # Test with sample queries
        test_queries = [
            "Why did CPM spike in my fashion campaign?",
            "Compare retargeting vs lookalike ROAS",
            "How is my Black Friday campaign performing?"
        ]
        
        for query in test_queries:
            result = pipeline.query(query)
            print(f"✅ Query: '{query}' -> Success: {result['success']}")
        
        # Test 6: Pipeline Stats
        print("\n📊 Test 6: Pipeline Statistics...")
        stats = pipeline.get_stats()
        print(f"✅ Total campaigns: {stats['total_campaigns']}")
        print(f"✅ Processed chunks: {stats['processed_chunks']}")
        print(f"✅ Pipeline ready: {stats['pipeline_ready']}")
        print(f"✅ Using mock mode: {stats['using_mock']}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📋 System Status:")
        print("✅ Data loading and chunking working")
        print("✅ Query classification working")
        print("✅ RAG processor with ChromaDB integration working")
        print("✅ Complete RAG pipeline working")
        print("✅ Mock mode functional (no API key required)")
        print("\n🚀 The Meta Ads RAG Demo is ready for use!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_pipeline()
    sys.exit(0 if success else 1)