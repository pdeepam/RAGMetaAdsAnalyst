# System Architecture Diagram

This document provides a visual representation of the Meta Ads RAG system's architecture. The diagram shows the flow of data from the initial data preparation to how a user's query is processed to generate an answer.

```mermaid
graph TD
    subgraph "Phase 1: Data Preparation (Offline Process)"
        direction LR
        A[Campaign Data <br> (JSON files in /data)] --> B(Data Loader <br> src/data_loader.py);
        B --> C(Data Chunker <br> src/data_chunker.py);
        C --> D{RAG Processor <br> src/rag_processor.py};
        D --> E[(ChromaDB <br> Vector Store)];
    end

    subgraph "Phase 2: Query Processing (Live Interaction)"
        direction TD
        F[User] -- "1. Asks question via UI" --> G(Streamlit UI <br> app.py);
        G -- "2. Sends query to pipeline" --> H{RAG Pipeline <br> src/rag_pipeline.py};
        H -- "3. Understands the query" --> I(Query Processor <br> src/query_processor.py);
        H -- "4. Searches for relevant data" --> J(RAG Processor <br> src/rag_processor.py);
        J -- "5. Retrieves data from" --> E;
        H -- "6. Sends query + data to LLM" --> K([OpenAI GPT-4o-mini]);
        K -- "7. Generates answer" --> H;
        H -- "8. Returns final answer to UI" --> G;
        G -- "9. Displays answer to user" --> F;
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style K fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#f8d,stroke:#333,stroke-width:2px
    style F fill:#9f9,stroke:#333,stroke-width:2px
```

## Explanation of the Flow

The architecture is divided into two main phases:

### Phase 1: Data Preparation

This is an "offline" process that happens when the application starts. It prepares the knowledge base for the AI.

1.  **Campaign Data**: The system starts with your raw campaign data, stored in JSON files.
2.  **Data Loader**: This module reads the JSON files.
3.  **Data Chunker**: This module breaks the raw data into smaller, meaningful text chunks that are easier for the AI to search through.
4.  **RAG Processor**: This component takes the text chunks and uses an AI model to convert them into numerical representations (embeddings).
5.  **ChromaDB Vector Store**: The numerical representations (embeddings) of the data chunks are stored in this specialized database, which acts as the AI's searchable library or knowledge base.

### Phase 2: Query Processing

This is the "live" process that happens whenever you ask a question.

1.  **User Interaction**: You ask a question in the Streamlit web interface.
2.  **Pipeline Entry**: The query is sent to the main RAG Pipeline, which orchestrates the entire process.
3.  **Query Understanding**: The `Query Processor` analyzes your question to determine your intent (e.g., are you comparing campaigns, asking for advice, etc.).
4.  **Data Retrieval**: The `RAG Processor` searches the `ChromaDB` vector store to find the most relevant data chunks that can help answer your question.
5.  **Context Building**: The retrieved data chunks are collected to form a "context".
6.  **LLM Generation**: The original question and the retrieved data context are sent to the OpenAI GPT-4o-mini model.
7.  **Answer Formulation**: The AI model, acting as an expert analyst, uses the provided context to formulate a detailed, data-driven answer.
8.  **Response Delivery**: The final answer is sent back through the pipeline to the user interface.
9.  **Display**: The answer is displayed to you in the chat window.
