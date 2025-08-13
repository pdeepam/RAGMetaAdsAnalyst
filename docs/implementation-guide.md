# Meta Ads RAG - Implementation Guide

## Tech Stack (Specific Tools)

### Core Components
```bash
# Backend & API
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"

# RAG Framework
langchain = "^0.1.0"
langchain-community = "^0.0.13"
langchain-openai = "^0.0.2"

# Vector Database
pinecone-client = "^2.2.4"  # or chromadb = "^0.4.18"
openai = "^1.6.0"  # embeddings

# LLM
openai = "^1.6.0"  # GPT-4

# Data Processing
pandas = "^2.1.0"
numpy = "^1.25.0"
python-dotenv = "^1.0.0"

# Frontend (Demo)
streamlit = "^1.28.0"
plotly = "^5.17.0"  # for charts
```

### Development Tools
```bash
# Code Quality
black = "^23.0.0"
isort = "^5.12.0" 
pytest = "^7.4.0"

# Environment
poetry  # dependency management
```

---

## Project Structure
```
meta-ads-rag/
├── src/
│   ├── api/                    # FastAPI endpoints
│   ├── data/                   # Mock data & ingestion
│   ├── rag/                    # RAG pipeline
│   ├── models/                 # Data models
│   └── ui/                     # Streamlit interface
├── data/                       # Mock campaign data
├── tests/                      # Unit tests
├── docs/                       # Documentation
└── config/                     # Environment configs
```

---

## Implementation Tasks (3 Phases)

### **Phase 1: Foundation** (Week 1-2)

#### Task 1.1: Project Setup (Day 1)
- [ ] Initialize Python project with Poetry
- [ ] Set up project structure and git repo
- [ ] Configure environment variables (.env)
- [ ] Install core dependencies

#### Task 1.2: Mock Data Creation (Day 2-3)
- [ ] Create realistic Meta Ads campaign data (JSON)
- [ ] Include: campaigns, ad sets, daily metrics, metadata
- [ ] Generate 3 months of historical data for 10 campaigns
- [ ] Add seasonal patterns and anomalies

```python
# Example data structure
{
    "campaign_001": {
        "name": "Holiday Electronics Sale",
        "objective": "CONVERSIONS", 
        "daily_metrics": {
            "2024-01-01": {"impressions": 15000, "clicks": 450, "spend": 125.50, ...},
            "2024-01-02": {"impressions": 14800, "clicks": 425, "spend": 118.75, ...}
        },
        "metadata": {"industry": "Electronics", "audience": "retargeting", ...}
    }
}
```

#### Task 1.3: Basic RAG Pipeline (Day 4-6)
- [ ] Implement data chunking strategy (temporal + hierarchical)
- [ ] Set up OpenAI embeddings generation
- [ ] Configure Pinecone vector database
- [ ] Create basic retrieval function

#### Task 1.4: Simple Query Interface (Day 7)
- [ ] Build basic Streamlit UI with text input
- [ ] Test with simple queries: "Show campaign performance"
- [ ] Verify end-to-end data flow

---

### **Phase 2: Intelligence Layer** (Week 3-4)

#### Task 2.1: Query Understanding (Day 8-9)
- [ ] Implement query intent classification
- [ ] Handle patterns: comparison, trends, anomalies, optimization
- [ ] Add query preprocessing (extract dates, campaign names)

```python
# Query patterns to handle
patterns = {
    "comparison": "Compare campaigns X and Y",
    "trends": "Show trends for last month", 
    "anomaly": "Why did CPM spike?",
    "optimization": "How to improve ROAS?"
}
```

#### Task 2.2: Advanced Retrieval (Day 10-11)
- [ ] Implement hybrid search (semantic + metadata filtering)
- [ ] Add reranking based on business logic
- [ ] Optimize retrieval for different query types

#### Task 2.3: Response Generation (Day 12-13)
- [ ] Create specialized prompt templates for each query type
- [ ] Implement LLM response generation with context
- [ ] Add response formatting and visualization

#### Task 2.4: Predictive Insights Engine (Day 14)
- [ ] Pattern matching against historical data
- [ ] Simple trend forecasting (7-day predictions)
- [ ] Risk factor identification (audience saturation, etc.)

---

### **Phase 3: Demo Polish** (Week 5-6)

#### Task 3.1: UI Enhancement (Day 15-17)
- [ ] Improve Streamlit interface with chat-like experience
- [ ] Add sample queries and use cases
- [ ] Include charts and visualizations with Plotly
- [ ] Add loading states and error handling

#### Task 3.2: Demo Scenarios (Day 18-19)
- [ ] Prepare 5 compelling demo queries
- [ ] Create realistic campaign narratives
- [ ] Test all user journeys

```python
# Demo queries to perfect
demo_queries = [
    "Why did my Black Friday campaign CPM jump 40% last week?",
    "Compare performance of my retargeting vs lookalike campaigns",
    "Which audience segment is performing best this month?",
    "Predict performance for my holiday campaign next week",
    "What's causing the drop in my fashion campaign conversions?"
]
```

#### Task 3.3: Performance & Error Handling (Day 20-21)
- [ ] Optimize query response time (<3 seconds)
- [ ] Add comprehensive error handling
- [ ] Implement caching for common queries
- [ ] Add logging and basic monitoring

---

## Key Implementation Details

### 1. Data Chunking Strategy
```python
def chunk_campaign_data(campaign_data):
    chunks = []
    
    # Daily performance chunks
    for date, metrics in campaign_data["daily_metrics"].items():
        chunk = f"Campaign '{campaign_data['name']}' on {date}: {format_metrics(metrics)}"
        chunks.append({
            "content": chunk,
            "metadata": {
                "campaign_id": campaign_data["id"],
                "date": date,
                "chunk_type": "daily_performance",
                "metrics": list(metrics.keys())
            }
        })
    
    return chunks
```

### 2. Query Classification
```python
def classify_query_intent(query):
    patterns = {
        "comparison": ["compare", "vs", "versus", "difference"],
        "trend": ["trend", "over time", "last week", "monthly"],
        "anomaly": ["spike", "drop", "why", "sudden", "change"],
        "optimization": ["improve", "optimize", "increase", "reduce"]
    }
    
    for intent, keywords in patterns.items():
        if any(keyword in query.lower() for keyword in keywords):
            return intent
    return "general"
```

### 3. Response Templates
```python
PROMPT_TEMPLATES = {
    "anomaly": """
    You're a Meta Ads expert analyzing a performance anomaly.
    
    Campaign Data: {context}
    User Question: {query}
    
    Provide: 
    1. What changed (specific metrics)
    2. Most likely causes
    3. Historical context if similar patterns occurred
    4. Recommended actions
    
    Be specific and actionable.
    """,
    
    "comparison": """
    You're comparing Meta Ads campaign performance.
    
    Campaign Data: {context}
    User Question: {query}
    
    Provide:
    1. Key performance differences
    2. Winner and by how much
    3. Insights into why differences exist
    4. Optimization recommendations
    """
}
```

---

## Development Commands

### Setup
```bash
# Project initialization
poetry init && poetry install
poetry shell

# Environment setup
cp .env.example .env
# Add your API keys: OPENAI_API_KEY, PINECONE_API_KEY
```

### Development
```bash
# Run tests
pytest tests/

# Start API server
uvicorn src.api.main:app --reload --port 8000

# Start Streamlit UI
streamlit run src/ui/main.py --server.port 8501

# Code formatting
black src/ && isort src/
```

### Testing Queries
```bash
# Test via API
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Why did my CPM spike last week?"}'

# Test via UI
# Open http://localhost:8501
```

---

## Success Milestones

### Week 1 Checkpoint
✅ Mock data generating realistic campaign insights  
✅ Basic RAG retrieval working  
✅ Simple UI accepting natural language queries

### Week 2 Checkpoint  
✅ Query intent classification working  
✅ Advanced retrieval with metadata filtering  
✅ LLM generating relevant marketing insights

### Week 3 Checkpoint
✅ Predictive insights engine functional  
✅ Polished UI with visualizations  
✅ 5 demo scenarios working flawlessly

**Final Goal**: 30-second conversational insights that would take 30+ minutes in traditional spreadsheet analysis.