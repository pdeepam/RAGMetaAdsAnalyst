"""
Meta Ads RAG Demo
A Streamlit application for natural language queries over Meta Ads campaign data.
"""

import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append('src')

from data_loader import CampaignDataLoader
from data_chunker import CampaignDataChunker
from rag_pipeline import MetaAdsRAGPipeline

# Load environment variables
load_dotenv()

@st.cache_data
def load_campaign_data():
    """Load and cache campaign data"""
    loader = CampaignDataLoader()
    return loader

@st.cache_data
def create_data_chunks():
    """Create and cache data chunks"""
    loader = load_campaign_data()
    chunker = CampaignDataChunker(loader.campaigns_data)
    return chunker.create_all_chunks()

@st.cache_resource
def initialize_rag_pipeline():
    """Initialize and cache the RAG pipeline"""
    try:
        pipeline = MetaAdsRAGPipeline()
        return pipeline
    except Exception as e:
        st.error(f"Failed to initialize RAG pipeline: {e}")
        return None

def display_campaign_overview():
    """Display campaign overview dashboard"""
    st.markdown("### 📊 Campaign Portfolio Overview")
    
    loader = load_campaign_data()
    summary = loader.get_performance_summary()
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Campaigns", summary["total_campaigns"])
    with col2:
        st.metric("Active Campaigns", summary["active_campaigns"])
    with col3:
        st.metric("Total Spend", f"${summary['total_spend']:,.2f}")
    with col4:
        st.metric("Average ROAS", f"{summary['average_roas']:.1f}x")
    
    # Campaign performance chart
    df = loader.get_all_performance_df()
    if not df.empty:
        fig = px.line(
            df, 
            x='date', 
            y='roas', 
            color='campaign_name',
            title="Campaign ROAS Over Time"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    return df

def display_campaign_details():
    """Display detailed campaign information"""
    st.markdown("### 🎯 Campaign Details")
    
    loader = load_campaign_data()
    campaigns = loader.get_all_campaigns()
    
    # Campaign selector
    campaign_names = [f"{c['name']} ({c['status']})" for c in campaigns]
    selected_idx = st.selectbox("Select Campaign:", range(len(campaign_names)), format_func=lambda x: campaign_names[x])
    
    if selected_idx is not None:
        campaign = campaigns[selected_idx]
        
        # Campaign info
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Industry:** {campaign.get('industry')}")
            st.markdown(f"**Audience:** {campaign.get('audience')}")
            st.markdown(f"**Objective:** {campaign.get('objective')}")
            st.markdown(f"**Status:** {campaign.get('status')}")
        
        with col2:
            budget = campaign.get('budget', {})
            st.markdown(f"**Daily Budget:** ${budget.get('daily_budget', 0):,}")
            st.markdown(f"**Total Budget:** ${budget.get('total_budget', 0):,}")
            targeting = campaign.get('targeting', {})
            if targeting.get('age_min'):
                st.markdown(f"**Age Range:** {targeting['age_min']}-{targeting['age_max']}")
        
        # Performance data
        df = loader.get_campaign_performance_df(campaign['id'])
        if not df.empty:
            st.markdown("#### Performance Metrics")
            
            # Metrics over time
            metric_cols = ['spend', 'conversions', 'ctr', 'cpm', 'roas']
            selected_metrics = st.multiselect("Select Metrics:", metric_cols, default=['roas', 'cpm'])
            
            if selected_metrics:
                fig = go.Figure()
                for metric in selected_metrics:
                    fig.add_trace(go.Scatter(
                        x=df['date'],
                        y=df[metric],
                        name=metric.upper(),
                        mode='lines+markers'
                    ))
                fig.update_layout(title=f"Performance Trends - {campaign['name']}", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Performance table
            st.markdown("#### Daily Performance Data")
            display_df = df[['date', 'spend', 'impressions', 'clicks', 'conversions', 'ctr', 'cpm', 'cpc', 'roas']].copy()
            display_df['spend'] = display_df['spend'].apply(lambda x: f"${x:.2f}")
            display_df['impressions'] = display_df['impressions'].apply(lambda x: f"{x:,}")
            display_df['clicks'] = display_df['clicks'].apply(lambda x: f"{x:,}")
            display_df['ctr'] = display_df['ctr'].apply(lambda x: f"{x:.1f}%")
            display_df['cpm'] = display_df['cpm'].apply(lambda x: f"${x:.2f}")
            display_df['cpc'] = display_df['cpc'].apply(lambda x: f"${x:.2f}")
            display_df['roas'] = display_df['roas'].apply(lambda x: f"{x:.1f}x")
            
            st.dataframe(display_df, use_container_width=True)
        
        # Campaign insights
        insights = campaign.get('insights', {})
        if insights:
            st.markdown("#### 💡 Campaign Insights")
            for key, value in insights.items():
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

def handle_chat_interface():
    """Handle the chat interface for RAG queries"""
    st.markdown("### 💬 Ask Questions About Your Campaigns")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your campaigns..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response using RAG pipeline
        with st.chat_message("assistant"):
            with st.spinner("Analyzing campaigns..."):
                response = generate_rag_response(prompt)
                st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

def generate_rag_response(query: str) -> str:
    """Generate response using the RAG pipeline"""
    try:
        # Get the RAG pipeline instance
        pipeline = initialize_rag_pipeline()
        
        if pipeline is None:
            return "❌ RAG pipeline is not available. Please check the system configuration."
        
        # Process the query through the RAG pipeline
        result = pipeline.query(query, include_sources=True)
        
        if not result["success"]:
            return f"❌ I encountered an error processing your query: {result.get('error', 'Unknown error')}"
        
        # Format the response with sources
        response = result["answer"]
        
        # Add query intent information
        if result.get("query_intent"):
            intent = result["query_intent"]
            if hasattr(intent, 'intent_type') and intent.intent_type != "general_inquiry":
                response += f"\n\n🧠 **Query Type**: {intent.intent_type.replace('_', ' ').title()}"
        
        # Add sources if available
        if result.get("sources"):
            response += "\n\n📚 **Sources from your campaign data:**"
            for i, source in enumerate(result["sources"][:3], 1):
                chunk_type = source["metadata"].get("chunk_type", "campaign data")
                response += f"\n{i}. {chunk_type.replace('_', ' ').title()}: {source['content'][:100]}..."
        
        return response
        
    except Exception as e:
        return f"❌ I encountered an error processing your query: {str(e)}\n\nPlease try rephrasing your question or check the system configuration."

def generate_mock_response(query: str) -> str:
    """Generate intelligent mock responses based on query patterns"""
    query_lower = query.lower()
    
    # Pattern matching for different query types
    if "cpm spike" in query_lower or "cpm increase" in query_lower:
        return """Based on your campaign data, I can see a CPM spike in your Holiday Fashion Retargeting campaign after November 20th. Here's what happened:

🔍 **Root Cause Analysis:**
- CPM increased by 25% (from $10.50 to $11.25+)
- Audience frequency reached 3.2x, indicating saturation
- This matches the pattern we see when audiences become fatigued

📈 **Performance Impact:**
- CTR dropped from 3.0% to 2.5% 
- CPC increased from $0.35 to $0.45
- ROAS declined from 3.2x to 2.1x

🎯 **Recommendations:**
1. **Expand your audience** - Add similar interest groups or increase lookalike percentage
2. **Refresh creative assets** - Audience fatigue often indicates creative staleness  
3. **Implement frequency capping** - Set max frequency to 3.0 to prevent future saturation

This is a common pattern in retargeting campaigns during high-competition periods like Black Friday season."""

    elif "compare" in query_lower and ("retargeting" in query_lower or "lookalike" in query_lower):
        return """Here's a comprehensive comparison of your retargeting vs lookalike campaigns:

📊 **Performance Comparison:**

**🎯 Retargeting Campaigns:**
- Holiday Fashion Retargeting: 3.8x → 2.1x ROAS (declining due to saturation)
- Black Friday Electronics: 4.2x → 6.1x ROAS (excellent performance)
- Average CPC: $0.30-0.45

**👥 Lookalike Campaigns:**  
- Premium Products (1% Lookalike): 2.8x → 3.4x ROAS (steady growth)
- Average CPC: $0.50-0.60

**🏆 Key Insights:**
- **Retargeting wins on ROAS** when not saturated (4.2x vs 3.4x average)
- **Lookalikes cost more** but offer better scaling potential
- **Retargeting shows faster fatigue** - needs more frequent creative refresh
- **Lookalikes provide steadier growth** - more predictable performance

**💡 Strategic Recommendation:**
Use retargeting for quick wins and high ROAS, but invest in lookalikes for sustainable growth and scale."""

    elif "best" in query_lower and "audience" in query_lower:
        return """Based on your campaign performance data, here's your audience performance ranking:

🥇 **Top Performing Audiences:**

1. **Website Retargeting (Electronics)** - 6.1x ROAS
   - Black Friday Electronics campaign
   - High intent audience with excellent conversion rates
   - Best for: Immediate conversions, high-value products

2. **Website Visitors - 30 Days (Fashion)** - 3.8x ROAS (when not saturated)
   - Holiday Fashion Retargeting
   - Strong performance until frequency hits 3.0+
   - Best for: Fashion/lifestyle products, seasonal campaigns

3. **Lookalike 1% - High Value Customers** - 3.4x ROAS
   - Premium Products campaign  
   - Consistent growth, higher CPC but scalable
   - Best for: Expansion, premium products

🔍 **Audience Insights:**
- **Retargeting audiences** convert 40% better on average
- **Mobile-first audiences** show higher engagement
- **Age range 25-45** performs best across all verticals
- **Interest + behavior targeting** outperforms interest-only by 25%

**🎯 Scaling Strategy:**
Start with your website retargeting, then layer in lookalikes at 1-3% similarity for growth."""

    elif "predict" in query_lower or "next week" in query_lower:
        return """Based on historical patterns and current trends, here's my performance prediction:

📈 **Next Week Forecast (Jan 8-14, 2025):**

**🎯 Fitness Campaign (January Challenge):**
- **Expected Performance:** 📈 STRONG
- Predicted CTR: 4.2-4.5% (New Year momentum continues)
- Expected CPC: $0.12-0.15 (low competition in fitness)
- Conversion forecast: 95-110 leads/day
- **Confidence:** 85% - Strong seasonal pattern match

**⚠️ Fashion Campaigns:**
- **Expected Performance:** 📉 DECLINING  
- Post-holiday fatigue setting in
- Predicted 15-20% CTR decline from holiday peaks
- Recommend creative refresh or pause until Valentine's season

**🔥 Electronics (Black Friday campaign):**
- **Expected Performance:** ⏸️ MAINTAIN PAUSE
- Post-holiday market cooling
- Competition remains high, CPMs elevated
- Recommend resume in late January for best ROI

**💡 Strategic Actions:**
1. **Double down on Fitness** - increase budget 50% while performance is peak
2. **Pause Fashion** temporarily to avoid wasted spend  
3. **Prepare Valentine's creative** for mid-January launch

This prediction is based on 2+ years of seasonal pattern analysis."""

    elif "conversion" in query_lower and ("drop" in query_lower or "declining" in query_lower):
        return """I've identified the conversion decline in your campaigns. Here's the detailed analysis:

🔍 **Conversion Performance Analysis:**

**📉 Declining Campaigns:**
1. **Holiday Fashion Retargeting:** 18 → 8 conversions (-56%)
   - **Root Cause:** Audience saturation (frequency 3.2x)
   - **Timeline:** Started declining after Nov 20th
   - **Impact:** ROAS dropped from 3.2x to 2.1x

**📈 Strong Performers:**
2. **Black Friday Electronics:** 18 → 95 conversions (+428%)
   - **Success Factor:** High-intent audience + seasonal demand
   - **Timeline:** Peak performance during Black Friday week

**🎯 Root Cause Analysis:**
- **Audience Fatigue:** Primary factor in fashion campaign decline
- **Creative Staleness:** Same ads running 30+ days
- **Increased Competition:** Holiday season bid pressure
- **Post-Holiday Cooldown:** Natural decline after shopping peaks

**🚀 Recovery Strategy:**
1. **Immediate Actions:**
   - Pause saturated fashion audience (frequency >3.0)
   - Launch new creative variations
   - Expand targeting to fresh audiences

2. **Medium-term Fixes:**
   - Implement automated frequency capping at 3.0
   - Set up creative rotation every 2 weeks
   - Build separate audiences for different buying stages

**Expected Recovery:** 2-3 weeks with proper implementation."""

    else:
        # Generic helpful response
        loader = load_campaign_data()
        chunks = create_data_chunks()
        return f"""I understand you're asking: "{query}"

📊 **Based on your campaign data:**
- {len(loader.get_all_campaigns())} total campaigns analyzed
- {len([c for c in loader.get_all_campaigns() if c['status'] == 'ACTIVE'])} currently active
- {len(chunks)} data points available for analysis

🎯 **I can help you with questions like:**
- "Why did my CPM spike last week?"
- "Compare my retargeting vs lookalike performance"  
- "Which audience segment performs best?"
- "Predict next week's campaign performance"
- "What's causing conversion drops?"

💡 **Try asking about specific campaigns, metrics, or time periods for more detailed insights!**"""

def main():
    st.set_page_config(
        page_title="Meta Ads RAG Demo",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Meta Ads AI Assistant")
    st.markdown("**Natural language queries over Meta Ads campaign data powered by AI**")
    
    # Load data (this will show any loading errors)
    try:
        loader = load_campaign_data()
        chunks = create_data_chunks()
        st.success(f"✅ Loaded {len(loader.get_all_campaigns())} campaigns with {len(chunks)} data chunks")
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return
    
    # Sidebar with sample queries and navigation
    with st.sidebar:
        st.markdown("### 🔥 Try These Queries")
        sample_queries = [
            "Why did my CPM spike last week?",
            "Compare my retargeting vs lookalike campaigns", 
            "Which audience performs best?",
            "Predict next week's performance",
            "Why are conversions dropping?"
        ]
        
        for query in sample_queries:
            if st.button(query, key=f"sample_{hash(query)}", use_container_width=True):
                # Trigger the query in chat
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                st.session_state.messages.append({"role": "user", "content": query})
                response = generate_rag_response(query)
                st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.markdown("---")
        st.markdown("### 📊 Navigation")
        view_mode = st.radio("View Mode:", ["Chat Interface", "Campaign Overview", "Campaign Details"])
    
    # Main content based on selected view
    if view_mode == "Chat Interface":
        handle_chat_interface()
    elif view_mode == "Campaign Overview":
        display_campaign_overview()
    elif view_mode == "Campaign Details":
        display_campaign_details()

if __name__ == "__main__":
    main()