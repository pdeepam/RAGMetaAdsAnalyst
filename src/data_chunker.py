"""
Data chunking utilities for RAG system
Converts campaign data into meaningful text chunks for vector embeddings
"""

from typing import List, Dict, Any
from datetime import datetime
import json

class CampaignDataChunker:
    """Convert campaign data into text chunks for RAG system"""
    
    def __init__(self, campaigns_data: Dict):
        self.campaigns_data = campaigns_data
        self.chunks = []
    
    def create_all_chunks(self) -> List[Dict[str, Any]]:
        """Create all types of chunks from campaign data"""
        self.chunks = []
        
        # Create different types of chunks
        self.create_campaign_overview_chunks()
        self.create_daily_performance_chunks()
        self.create_insights_chunks()
        self.create_comparison_chunks()
        self.create_global_insights_chunks()
        
        print(f"✅ Created {len(self.chunks)} text chunks for RAG")
        return self.chunks
    
    def create_campaign_overview_chunks(self):
        """Create overview chunks for each campaign"""
        campaigns = self.campaigns_data.get("campaigns", [])
        
        for campaign in campaigns:
            # Basic campaign info chunk
            overview_text = self._format_campaign_overview(campaign)
            
            chunk = {
                "id": f"overview_{campaign['id']}",
                "content": overview_text,
                "metadata": {
                    "campaign_id": campaign["id"],
                    "campaign_name": campaign["name"],
                    "chunk_type": "campaign_overview",
                    "industry": campaign.get("industry"),
                    "audience": campaign.get("audience"),
                    "status": campaign.get("status"),
                    "objective": campaign.get("objective")
                }
            }
            self.chunks.append(chunk)
    
    def create_daily_performance_chunks(self):
        """Create performance chunks for each day"""
        campaigns = self.campaigns_data.get("campaigns", [])
        
        for campaign in campaigns:
            daily_perf = campaign.get("daily_performance", {})
            
            for date, metrics in daily_perf.items():
                perf_text = self._format_daily_performance(campaign, date, metrics)
                
                chunk = {
                    "id": f"daily_{campaign['id']}_{date}",
                    "content": perf_text,
                    "metadata": {
                        "campaign_id": campaign["id"],
                        "campaign_name": campaign["name"],
                        "chunk_type": "daily_performance",
                        "date": date,
                        "industry": campaign.get("industry"),
                        "audience": campaign.get("audience"),
                        "metrics": list(metrics.keys()),
                        "spend": metrics.get("spend"),
                        "roas": metrics.get("roas"),
                        "cpm": metrics.get("cpm"),
                        "ctr": metrics.get("ctr")
                    }
                }
                self.chunks.append(chunk)
    
    def create_insights_chunks(self):
        """Create chunks for campaign insights and recommendations"""
        campaigns = self.campaigns_data.get("campaigns", [])
        
        for campaign in campaigns:
            insights = campaign.get("insights", {})
            if not insights:
                continue
            
            insights_text = self._format_campaign_insights(campaign, insights)
            
            chunk = {
                "id": f"insights_{campaign['id']}",
                "content": insights_text,
                "metadata": {
                    "campaign_id": campaign["id"],
                    "campaign_name": campaign["name"],
                    "chunk_type": "campaign_insights",
                    "industry": campaign.get("industry"),
                    "audience": campaign.get("audience"),
                    "insights_keys": list(insights.keys())
                }
            }
            self.chunks.append(chunk)
    
    def create_comparison_chunks(self):
        """Create chunks that compare campaigns"""
        campaigns = self.campaigns_data.get("campaigns", [])
        
        # Group campaigns by industry for comparison
        by_industry = {}
        for campaign in campaigns:
            industry = campaign.get("industry", "Unknown")
            if industry not in by_industry:
                by_industry[industry] = []
            by_industry[industry].append(campaign)
        
        # Create comparison chunks for each industry
        for industry, industry_campaigns in by_industry.items():
            if len(industry_campaigns) > 1:
                comparison_text = self._format_industry_comparison(industry, industry_campaigns)
                
                chunk = {
                    "id": f"comparison_{industry.lower().replace(' ', '_')}",
                    "content": comparison_text,
                    "metadata": {
                        "chunk_type": "industry_comparison",
                        "industry": industry,
                        "campaign_count": len(industry_campaigns),
                        "campaign_ids": [c["id"] for c in industry_campaigns],
                        "campaign_names": [c["name"] for c in industry_campaigns]
                    }
                }
                self.chunks.append(chunk)
    
    def create_global_insights_chunks(self):
        """Create chunks for global market insights"""
        global_insights = self.campaigns_data.get("global_insights", {})
        
        if not global_insights:
            return
        
        # Market trends chunk
        if "market_trends" in global_insights:
            trends_text = self._format_market_trends(global_insights["market_trends"])
            chunk = {
                "id": "global_market_trends",
                "content": trends_text,
                "metadata": {
                    "chunk_type": "market_trends",
                    "data_type": "global_insights"
                }
            }
            self.chunks.append(chunk)
        
        # Best practices chunk
        if "best_practices" in global_insights:
            practices_text = self._format_best_practices(global_insights["best_practices"])
            chunk = {
                "id": "global_best_practices", 
                "content": practices_text,
                "metadata": {
                    "chunk_type": "best_practices",
                    "data_type": "global_insights"
                }
            }
            self.chunks.append(chunk)
        
        # Anomalies chunk
        if "anomalies_detected" in global_insights:
            anomalies_text = self._format_anomalies(global_insights["anomalies_detected"])
            chunk = {
                "id": "global_anomalies",
                "content": anomalies_text,
                "metadata": {
                    "chunk_type": "anomalies",
                    "data_type": "global_insights"
                }
            }
            self.chunks.append(chunk)
    
    # Formatting methods
    def _format_campaign_overview(self, campaign: Dict) -> str:
        """Format campaign overview as natural text"""
        name = campaign["name"]
        objective = campaign["objective"]
        status = campaign["status"]
        industry = campaign.get("industry", "Unknown")
        audience = campaign.get("audience", "Unknown")
        budget = campaign.get("budget", {})
        targeting = campaign.get("targeting", {})
        
        text = f"Campaign '{name}' is a {objective} campaign in the {industry} industry targeting {audience}. "
        text += f"Current status: {status}. "
        
        if budget:
            daily_budget = budget.get("daily_budget", 0)
            total_budget = budget.get("total_budget", 0)
            text += f"Daily budget: ${daily_budget}, Total budget: ${total_budget}. "
        
        if targeting:
            age_min = targeting.get("age_min")
            age_max = targeting.get("age_max")
            if age_min and age_max:
                text += f"Targeting ages {age_min}-{age_max}. "
            
            interests = targeting.get("interests", [])
            if interests:
                text += f"Interest targeting: {', '.join(interests)}. "
            
            placements = targeting.get("placements", [])
            if placements:
                text += f"Ad placements: {', '.join(placements)}."
        
        return text
    
    def _format_daily_performance(self, campaign: Dict, date: str, metrics: Dict) -> str:
        """Format daily performance as natural text"""
        name = campaign["name"]
        
        text = f"On {date}, campaign '{name}' generated {metrics.get('impressions', 0):,} impressions "
        text += f"and {metrics.get('clicks', 0):,} clicks, spending ${metrics.get('spend', 0):.2f}. "
        text += f"This resulted in {metrics.get('conversions', 0)} conversions. "
        text += f"Key metrics: CTR {metrics.get('ctr', 0):.1f}%, "
        text += f"CPM ${metrics.get('cpm', 0):.2f}, CPC ${metrics.get('cpc', 0):.2f}, "
        text += f"ROAS {metrics.get('roas', 0):.1f}x, Frequency {metrics.get('frequency', 0):.1f}."
        
        return text
    
    def _format_campaign_insights(self, campaign: Dict, insights: Dict) -> str:
        """Format campaign insights as natural text"""
        name = campaign["name"]
        text = f"Insights for campaign '{name}': "
        
        for key, value in insights.items():
            if isinstance(value, str):
                text += f"{key.replace('_', ' ').title()}: {value}. "
            elif isinstance(value, list):
                text += f"{key.replace('_', ' ').title()}: {', '.join(value)}. "
        
        return text
    
    def _format_industry_comparison(self, industry: str, campaigns: List[Dict]) -> str:
        """Format industry comparison as natural text"""
        text = f"Industry comparison for {industry} campaigns: "
        
        for campaign in campaigns:
            name = campaign["name"]
            status = campaign["status"]
            
            # Get latest performance
            daily_perf = campaign.get("daily_performance", {})
            if daily_perf:
                latest_date = max(daily_perf.keys())
                latest_perf = daily_perf[latest_date]
                roas = latest_perf.get("roas", 0)
                cpm = latest_perf.get("cpm", 0)
                
                text += f"'{name}' ({status}) shows ROAS of {roas:.1f}x with CPM of ${cpm:.2f}. "
        
        return text
    
    def _format_market_trends(self, trends: Dict) -> str:
        """Format market trends as natural text"""
        text = "Market trends and analysis: "
        
        for key, value in trends.items():
            formatted_key = key.replace('_', ' ').title()
            text += f"{formatted_key}: {value}. "
        
        return text
    
    def _format_best_practices(self, practices: Dict) -> str:
        """Format best practices as natural text"""
        text = "Best practices and recommendations: "
        
        for key, value in practices.items():
            formatted_key = key.replace('_', ' ').title()
            text += f"{formatted_key}: {value}. "
        
        return text
    
    def _format_anomalies(self, anomalies: Dict) -> str:
        """Format detected anomalies as natural text"""
        text = "Detected anomalies and issues: "
        
        for anomaly_name, details in anomalies.items():
            if isinstance(details, dict):
                date = details.get("date", "Unknown date")
                campaign = details.get("campaign", "Unknown campaign")
                issue = details.get("issue", "Unknown issue")
                resolution = details.get("resolution", "No resolution provided")
                
                text += f"{anomaly_name.replace('_', ' ').title()} on {date} in '{campaign}': {issue}. Resolution: {resolution}. "
        
        return text
    
    def get_chunks_by_type(self, chunk_type: str) -> List[Dict]:
        """Get chunks filtered by type"""
        return [chunk for chunk in self.chunks if chunk["metadata"]["chunk_type"] == chunk_type]
    
    def get_chunks_by_campaign(self, campaign_id: str) -> List[Dict]:
        """Get chunks for specific campaign"""
        return [chunk for chunk in self.chunks if chunk["metadata"].get("campaign_id") == campaign_id]

# Test the chunker
if __name__ == "__main__":
    from data_loader import CampaignDataLoader
    
    # Load data and create chunks
    loader = CampaignDataLoader()
    chunker = CampaignDataChunker(loader.campaigns_data)
    chunks = chunker.create_all_chunks()
    
    print(f"\n📝 Chunk Types:")
    chunk_types = {}
    for chunk in chunks:
        chunk_type = chunk["metadata"]["chunk_type"]
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
    
    for chunk_type, count in chunk_types.items():
        print(f"  {chunk_type}: {count}")
    
    print(f"\n📄 Sample Chunk:")
    sample_chunk = chunks[0]
    print(f"ID: {sample_chunk['id']}")
    print(f"Type: {sample_chunk['metadata']['chunk_type']}")
    print(f"Content: {sample_chunk['content'][:200]}...")
    
    print(f"\n✅ Data chunker working properly!")