"""
Query Processor for Meta Ads RAG System
Handles query classification, intent detection, and response routing
"""

import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class QueryIntent:
    """Represents a classified query intent"""
    intent_type: str
    confidence: float
    extracted_entities: Dict[str, Any]
    suggested_filters: Dict[str, Any]

class CampaignQueryProcessor:
    """Process and classify campaign-related queries"""
    
    def __init__(self):
        self.intent_patterns = self._build_intent_patterns()
        self.entity_patterns = self._build_entity_patterns()
        
    def _build_intent_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for intent classification"""
        return {
            "performance_anomaly": [
                r"\b(spike|jump|increase|rise|surge)\b.*\b(cpm|cpc|cost|spend)",
                r"\b(drop|decline|decrease|fall|crash)\b.*\b(roas|conversion|ctr|performance)",
                r"\bwhy\b.*\b(high|low|bad|poor|expensive)",
                r"\bwhat.*(happen|wrong|cause|problem)",
                r"\b(anomaly|unusual|strange|weird|unexpected)"
            ],
            "campaign_comparison": [
                r"\bcompare\b.*\b(campaign|audience|performance)",
                r"\b(vs|versus|against|compared to)\b",
                r"\bbetter\b.*\b(campaign|audience|performance)",
                r"\b(difference|different)\b.*\b(between|campaign)",
                r"\b(retargeting|lookalike|interest)\b.*\b(vs|versus|compared)"
            ],
            "performance_ranking": [
                r"\bbest\b.*\b(perform|campaign|audience|creative)",
                r"\btop\b.*\b(perform|campaign|audience)",
                r"\b(worst|lowest|highest|most|least)\b.*\b(perform|roas|cpm|cpc)",
                r"\brank.*\b(campaign|audience|performance)",
                r"\bwhich.*\b(best|better|perform)"
            ],
            "trend_analysis": [
                r"\btrend\b.*\b(over time|monthly|weekly|daily)",
                r"\b(pattern|seasonal|timeline|history)",
                r"\b(last|past|previous)\b.*\b(week|month|quarter|year)",
                r"\bover\b.*\b(time|period|duration)",
                r"\b(growth|decline|change)\b.*\b(time|period)"
            ],
            "prediction_forecast": [
                r"\bpredict\b.*\b(performance|next|future)",
                r"\bforecast\b.*\b(week|month|performance)",
                r"\bnext\b.*\b(week|month|quarter)",
                r"\bfuture\b.*\b(performance|trend|result)",
                r"\bwill\b.*\b(perform|cost|convert)",
                r"\bexpect\b.*\b(performance|result|roas)"
            ],
            "optimization_advice": [
                r"\bhow.*\b(improve|optimize|fix|increase|decrease)",
                r"\bwhat.*\b(should|recommend|suggest|advice)",
                r"\b(recommendation|advice|suggestion|tip)",
                r"\b(optimize|improve|fix|boost|enhance)",
                r"\bshould i\b.*\b(pause|stop|increase|decrease)"
            ],
            "budget_spend": [
                r"\bbudget\b.*\b(increase|decrease|optimize|allocate)",
                r"\bspend\b.*\b(too much|too little|optimize|control)",
                r"\bcost\b.*\b(per|efficiency|optimization)",
                r"\b(expensive|cheap|costly)\b.*\b(campaign|audience)",
                r"\bmoney\b.*\b(waste|save|optimize|efficient)"
            ],
            "audience_analysis": [
                r"\baudience\b.*\b(perform|target|segment|behavior)",
                r"\b(demographic|interest|behavior)\b.*\b(perform|target)",
                r"\b(age|gender|location|interest)\b.*\b(perform|convert)",
                r"\btarget\b.*\b(audience|demographic|interest)",
                r"\bsegment\b.*\b(perform|audience|target)"
            ],
            "creative_performance": [
                r"\bcreative\b.*\b(perform|fatigue|refresh|test)",
                r"\bad\b.*\b(creative|copy|image|video|perform)",
                r"\b(headline|copy|image|video)\b.*\b(perform|test)",
                r"\bcreative.*\b(rotation|refresh|update|change)",
                r"\b(fatigue|tired|stale)\b.*\b(creative|ad|audience)"
            ]
        }
    
    def _build_entity_patterns(self) -> Dict[str, str]:
        """Build patterns for entity extraction"""
        return {
            "campaign_names": r"\b(campaign|ad)\s+['\"]([^'\"]+)['\"]",
            "metrics": r"\b(roas|cpm|cpc|ctr|spend|cost|conversion|impression|click|reach|frequency)\b",
            "time_periods": r"\b(last|past|previous|next)\s+(week|month|quarter|year|day)",
            "specific_dates": r"\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})\b",
            "percentages": r"\b(\d+(?:\.\d+)?)\s*%",
            "currency": r"\$(\d+(?:,\d{3})*(?:\.\d{2})?)",
            "audience_types": r"\b(retargeting|lookalike|interest|broad|custom|website\s+visitor)\b",
            "industries": r"\b(fashion|electronics|fitness|travel|luxury|home|garden)\b",
            "placements": r"\b(feed|story|stories|reel|reels|messenger|audience\s+network)\b"
        }
    
    def classify_query(self, query: str) -> QueryIntent:
        """Classify query and extract intent"""
        query_lower = query.lower()
        
        # Score each intent type
        intent_scores = {}
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, query_lower, re.IGNORECASE)
                score += len(matches) * (1.0 / len(patterns))  # Normalize by pattern count
            intent_scores[intent_type] = score
        
        # Get best matching intent
        if not intent_scores or max(intent_scores.values()) == 0:
            best_intent = "general_inquiry"
            confidence = 0.3
        else:
            best_intent = max(intent_scores.keys(), key=lambda x: intent_scores[x])
            max_score = intent_scores[best_intent]
            confidence = min(max_score, 1.0)  # Cap at 1.0
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Generate suggested filters
        filters = self._suggest_filters(query, entities, best_intent)
        
        return QueryIntent(
            intent_type=best_intent,
            confidence=confidence,
            extracted_entities=entities,
            suggested_filters=filters
        )
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract relevant entities from query"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def _suggest_filters(self, query: str, entities: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """Suggest filters based on query and extracted entities"""
        filters = {}
        
        # Time-based filters
        if "time_periods" in entities:
            time_period = entities["time_periods"][0] if entities["time_periods"] else None
            if time_period:
                # Handle tuple from regex groups
                if isinstance(time_period, tuple):
                    time_period = " ".join(time_period)
                filters["time_filter"] = self._parse_time_period(time_period)
        
        # Campaign filters
        if "campaign_names" in entities:
            filters["campaign_filter"] = entities["campaign_names"]
        
        # Audience filters
        if "audience_types" in entities:
            filters["audience_filter"] = entities["audience_types"]
        
        # Industry filters
        if "industries" in entities:
            filters["industry_filter"] = entities["industries"]
        
        # Metric filters
        if "metrics" in entities:
            filters["metrics_focus"] = entities["metrics"]
        
        # Intent-specific filters
        if intent == "campaign_comparison":
            # Look for comparison keywords
            if any(word in query.lower() for word in ["retargeting", "lookalike"]):
                filters["comparison_type"] = "audience_type"
            elif any(word in query.lower() for word in ["campaign", "ad"]):
                filters["comparison_type"] = "campaign_level"
        
        elif intent == "performance_ranking":
            # Determine ranking criteria
            if any(word in query.lower() for word in ["roas", "return"]):
                filters["ranking_metric"] = "roas"
            elif any(word in query.lower() for word in ["cpm", "cost", "expensive"]):
                filters["ranking_metric"] = "cpm"
            elif any(word in query.lower() for word in ["ctr", "engagement"]):
                filters["ranking_metric"] = "ctr"
        
        return filters
    
    def _parse_time_period(self, time_period: str) -> Dict[str, str]:
        """Parse time period into start/end dates"""
        # This is a simplified implementation
        # In production, you'd want more robust date parsing
        period_lower = time_period.lower()
        
        if "last week" in period_lower or "past week" in period_lower:
            return {"period": "last_week", "days": 7}
        elif "last month" in period_lower or "past month" in period_lower:
            return {"period": "last_month", "days": 30}
        elif "last quarter" in period_lower:
            return {"period": "last_quarter", "days": 90}
        elif "next week" in period_lower:
            return {"period": "next_week", "days": 7}
        elif "next month" in period_lower:
            return {"period": "next_month", "days": 30}
        else:
            return {"period": "custom", "raw": time_period}
    
    def generate_context_prompt(self, query: str, query_intent: QueryIntent, retrieved_docs: List[Any]) -> str:
        """Generate context-aware prompt for LLM"""
        
        # Base prompt template
        base_prompt = f"""You are an expert Meta Ads analyst. Answer the user's question based on the provided campaign data.

User Question: {query}
Query Intent: {query_intent.intent_type}
Confidence: {query_intent.confidence:.2f}

Campaign Data:
"""
        
        # Add retrieved document content
        for i, doc in enumerate(retrieved_docs):
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            
            base_prompt += f"\nDocument {i+1} ({metadata.get('chunk_type', 'unknown')}):\n{content}\n"
        
        # Add intent-specific instructions
        intent_instructions = {
            "performance_anomaly": """
Focus on identifying root causes, timeline of changes, and actionable recommendations.
Include specific metrics and percentage changes where available.""",
            
            "campaign_comparison": """
Provide a clear side-by-side comparison with specific metrics.
Highlight the winner and explain why one performs better than the other.""",
            
            "performance_ranking": """
Rank the items clearly (1st, 2nd, 3rd, etc.) with supporting metrics.
Explain what makes the top performers successful.""",
            
            "prediction_forecast": """
Base predictions on historical patterns and seasonal trends.
Include confidence levels and key assumptions in your forecast.""",
            
            "optimization_advice": """
Provide specific, actionable recommendations with expected impact.
Prioritize suggestions by potential ROI and ease of implementation."""
        }
        
        if query_intent.intent_type in intent_instructions:
            base_prompt += f"\nSpecific Instructions: {intent_instructions[query_intent.intent_type]}"
        
        base_prompt += """

Requirements:
1. Be specific and data-driven
2. Include relevant metrics and comparisons  
3. Provide actionable insights
4. Use marketing terminology appropriately
5. Structure your response clearly with sections

Answer:"""
        
        return base_prompt
    
    def get_search_keywords(self, query: str, query_intent: QueryIntent) -> List[str]:
        """Generate optimal search keywords for vector retrieval"""
        keywords = []
        
        # Add original query words
        query_words = [word.lower() for word in re.findall(r'\b\w+\b', query)]
        keywords.extend(query_words)
        
        # Add entity-based keywords
        entities = query_intent.extracted_entities
        
        if "metrics" in entities:
            keywords.extend(entities["metrics"])
        
        if "audience_types" in entities:
            keywords.extend(entities["audience_types"])
        
        if "industries" in entities:
            keywords.extend(entities["industries"])
        
        # Add intent-based keywords
        intent_keywords = {
            "performance_anomaly": ["spike", "increase", "problem", "issue", "anomaly"],
            "campaign_comparison": ["compare", "versus", "performance", "better"],
            "performance_ranking": ["best", "top", "rank", "performance"],
            "trend_analysis": ["trend", "pattern", "over time", "change"],
            "prediction_forecast": ["predict", "forecast", "future", "next"],
            "optimization_advice": ["optimize", "improve", "recommendation", "advice"]
        }
        
        if query_intent.intent_type in intent_keywords:
            keywords.extend(intent_keywords[query_intent.intent_type])
        
        # Remove duplicates and return
        return list(set(keywords))


# Test the query processor
if __name__ == "__main__":
    print("🚀 Testing Query Processor...")
    
    processor = CampaignQueryProcessor()
    
    test_queries = [
        "Why did my CPM spike last week in the fashion campaign?",
        "Compare my retargeting vs lookalike campaigns performance",
        "Which audience segment performs best for conversions?",
        "Predict next week's performance for Black Friday campaign",
        "How can I optimize my ROAS for electronics campaigns?",
        "What's the trend in my campaign performance over the last month?",
        "Should I increase my budget for the fitness campaign?",
        "Why are my conversions dropping in the luxury goods campaign?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        intent = processor.classify_query(query)
        keywords = processor.get_search_keywords(query, intent)
        
        print(f"   Intent: {intent.intent_type} (confidence: {intent.confidence:.2f})")
        print(f"   Entities: {intent.extracted_entities}")
        print(f"   Filters: {intent.suggested_filters}")
        print(f"   Search Keywords: {keywords[:5]}")  # Show first 5 keywords
    
    print(f"\n✅ Query Processor working correctly!")