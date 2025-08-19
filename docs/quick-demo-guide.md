# Meta Ads RAG - Quick Demo Guide (3 Days)

> **Goal**: Prove RAG concept with minimal setup. Production-ready architecture is in [implementation-guide.md](./implementation-guide.md)

## Tech Stack (Demo-Optimized)

### Single-File Dependencies
```txt
# requirements.txt
streamlit==1.28.0
langchain==0.1.0
langchain-openai==0.0.2
langchain-community==0.0.13
chromadb==0.4.18
openai==1.6.0
pandas==2.1.0
plotly==5.17.0
python-dotenv==1.0.0
```

### Why These Choices?
- **ChromaDB**: No external service, runs locally
- **Streamlit**: Instant UI with zero frontend code
- **Single file**: app.py contains everything
- **No FastAPI**: Direct integration, no API layer

---

## Project Structure (Minimal)
```
meta-ads-rag-demo/
├── app.py                 # Complete Streamlit app (200 lines)
├── requirements.txt       # Dependencies
├── .env                   # API keys
├── data/
│   └── campaigns.json     # Mock campaign data
└── README.md             # Quick setup instructions
```

---

## 3-Day Sprint Tasks

### **Day 1: Foundation** (4 hours)
**Morning** (2 hours):
- [ ] Set up Python environment and install dependencies
- [ ] Create realistic mock campaign data (10 campaigns, 90 days)
- [ ] Basic Streamlit app with data loading

**Afternoon** (2 hours):
- [ ] Implement data chunking for campaign insights
- [ ] Set up ChromaDB vector store locally
- [ ] Test embedding generation and storage

### **Day 2: RAG Integration** (4 hours)
**Morning** (2 hours):
- [ ] Integrate LangChain RetrievalQA chain
- [ ] Connect OpenAI embeddings and GPT-4
- [ ] Basic query processing and response generation

**Afternoon** (2 hours):
- [ ] Add query intent classification (simple keyword matching)
- [ ] Create specialized prompts for different query types
- [ ] Test with core demo queries

### **Day 3: Demo Polish** (4 hours)
**Morning** (2 hours):
- [ ] Add Plotly charts for campaign performance
- [ ] Create sidebar with sample queries
- [ ] Improve UI with loading states and error handling

**Afternoon** (2 hours):
- [ ] Perfect 5 demo scenarios
- [ ] Add prediction insights (simple pattern matching)
- [ ] Final testing and demo script preparation

---

## Core Code Structure

### app.py (Main Components)
```python
import streamlit as st
import pandas as pd
import json
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import plotly.express as px

# 1. Data Loading
@st.cache_data
def load_campaign_data():
    with open('data/campaigns.json', 'r') as f:
        return json.load(f)

# 2. RAG Setup  
@st.cache_resource
def setup_rag_chain():
    # Load and chunk data
    chunks = create_campaign_chunks(load_campaign_data())
    
    # Create vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_texts(chunks, embeddings)
    
    # Create QA chain
    llm = OpenAI(temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
    )
    return qa_chain

# 3. Streamlit UI
def main():
    st.title("🎯 Meta Ads AI Assistant")
    
    # Sidebar with sample queries
    st.sidebar.markdown("### Try These Queries:")
    sample_queries = [
        "Why did my CPM spike last week?",
        "Compare my retargeting campaigns",
        "Which audience performs best?",
        "Predict next week's performance",
        "Why are my conversions dropping?"
    ]
    
    # Chat interface
    if query := st.chat_input("Ask about your campaigns..."):
        with st.spinner("Analyzing campaigns..."):
            response = qa_chain.run(query)
            st.write(response)
            
            # Add visualization if relevant
            if "performance" in query.lower():
                show_performance_chart()

if __name__ == "__main__":
    main()
```

---

## Mock Data Structure

### campaigns.json (Sample)
```json
{
  "campaigns": [
    {
      "id": "camp_001",
      "name": "Black Friday Electronics Sale",
      "objective": "CONVERSIONS",
      "status": "ACTIVE",
      "industry": "Electronics",
      "audience": "Retargeting",
      "daily_performance": {
        "2024-11-01": {
          "impressions": 15000,
          "clicks": 450,
          "spend": 125.50,
          "conversions": 18,
          "ctr": 3.0,
          "cpm": 8.37,
          "cpc": 0.28,
          "roas": 4.2
        },
        "2024-11-02": {
          "impressions": 18000,
          "clicks": 520,
          "spend": 145.25,
          "conversions": 22,
          "ctr": 2.9,
          "cpm": 8.07,
          "cpc": 0.28,
          "roas": 4.5
        }
      }
    }
  ]
}
```

---

## Quick Setup Commands

### Environment Setup
```bash
# Create project
mkdir meta-ads-rag-demo && cd meta-ads-rag-demo

# Python environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Environment variables
echo "OPENAI_API_KEY=your_key_here" > .env
```

### Run Demo
```bash
# Single command to start
streamlit run app.py

# Opens browser to http://localhost:8501
# Ready to demo immediately!
```

---

## Demo Script (5 Minutes)

### Setup (30 seconds)
"Traditional Meta Ads analysis requires exporting CSVs, manual Excel work, and takes hours. Let me show you a better way..."

### Query 1: Anomaly Detection (60 seconds)
**Input**: "Why did my Black Friday campaign CPM spike 40% last week?"  
**Expected Output**: "Your CPM increased due to holiday competition in electronics category. Similar spike occurred November 2022 (+45%). Competitor analysis shows 12 new advertisers targeting identical audiences..."

### Query 2: Campaign Comparison (60 seconds)  
**Input**: "Compare my retargeting vs lookalike campaigns this month"  
**Expected Output**: "Retargeting campaigns: 4.2x ROAS, $0.28 CPC. Lookalike: 3.1x ROAS, $0.35 CPC. Retargeting wins by 35% due to higher intent audience..."

### Query 3: Optimization (60 seconds)
**Input**: "How can I improve my fashion campaign performance?"  
**Expected Output**: "Analysis shows audience fatigue (frequency 3.2x). Recommendations: 1) Refresh creative assets, 2) Expand age range 25-45, 3) Test Instagram Reels placement..."

### Query 4: Prediction (60 seconds)  
**Input**: "Predict my holiday campaign performance next week"  
**Expected Output**: "Based on 2022-2023 patterns, expect 25% impression increase, CPM spike to $12-15, maintain current ROAS. Recommend increasing budget by 20%..."

### Conclusion (30 seconds)
"What took 2+ hours in spreadsheets now takes 30 seconds. Questions?"

---

## Success Criteria (Demo Day)

### ✅ Must Work Perfectly
1. **Natural language queries** return relevant, specific answers
2. **Response time** under 3 seconds
3. **Historical context** included in explanations  
4. **Actionable recommendations** provided
5. **No crashes** during demo

### ✅ Nice to Have
1. Charts automatically generated for performance queries
2. Confidence scores for predictions
3. Multiple follow-up queries work smoothly

### ❌ Don't Worry About
- Perfect UI design (Streamlit default is fine)
- Mobile responsiveness  
- Production deployment
- Authentication or security
- Advanced error handling

---

## Post-Demo Evolution Path

### After Successful Demo
1. **Week 1**: Migrate to production architecture (FastAPI + React)
2. **Week 2**: Real Meta Ads API integration  
3. **Week 3**: Advanced predictive features
4. **Week 4**: Production deployment

### Or Keep It Simple
- Demo version might be sufficient for many use cases
- Can enhance Streamlit app with custom CSS
- Deploy to Streamlit Cloud for easy sharing

---

**🎯 Remember: Goal is proving RAG value, not building perfect software. Focus on making the AI responses incredibly smart and relevant!**