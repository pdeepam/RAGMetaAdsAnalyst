"""
Data loading utilities for Meta Ads RAG Demo
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import os

class CampaignDataLoader:
    """Load and process campaign data for RAG system"""
    
    def __init__(self, data_source: str = "auto", data_path: str = None):
        """
        Initialize data loader with data source selection
        
        Args:
            data_source: "demo", "real", or "auto" (checks environment)
            data_path: Custom path to data file (overrides data_source)
        """
        if data_path:
            self.data_path = data_path
        else:
            self.data_path = self._get_data_path(data_source)
        
        self.data_source = data_source
        self.campaigns_data = None
        self.load_data()
    
    def _get_data_path(self, data_source: str) -> str:
        """Determine data path based on source"""
        if data_source == "auto":
            # Check environment variable, default to demo
            data_source = os.getenv("DATA_SOURCE", "demo")
        
        if data_source == "real":
            return "data/real/campaigns.json"
        else:  # demo or fallback
            return "data/demo/campaigns.json"
    
    def load_data(self):
        """Load campaign data from JSON file"""
        try:
            with open(self.data_path, 'r') as f:
                self.campaigns_data = json.load(f)
            print(f"✅ Loaded {len(self.campaigns_data['campaigns'])} campaigns")
        except FileNotFoundError:
            print(f"❌ Data file not found: {self.data_path}")
            self.campaigns_data = {"campaigns": [], "global_insights": {}}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in data file: {e}")
            self.campaigns_data = {"campaigns": [], "global_insights": {}}
    
    def get_all_campaigns(self) -> List[Dict]:
        """Get all campaign data"""
        return self.campaigns_data.get("campaigns", [])
    
    def get_campaign_by_id(self, campaign_id: str) -> Dict:
        """Get specific campaign by ID"""
        campaigns = self.get_all_campaigns()
        for campaign in campaigns:
            if campaign["id"] == campaign_id:
                return campaign
        return {}
    
    def get_campaigns_by_industry(self, industry: str) -> List[Dict]:
        """Get campaigns filtered by industry"""
        campaigns = self.get_all_campaigns()
        return [c for c in campaigns if c.get("industry", "").lower() == industry.lower()]
    
    def get_campaigns_by_audience(self, audience_type: str) -> List[Dict]:
        """Get campaigns filtered by audience type"""
        campaigns = self.get_all_campaigns()
        return [c for c in campaigns if audience_type.lower() in c.get("audience", "").lower()]
    
    def get_performance_summary(self) -> Dict:
        """Get overall performance summary"""
        campaigns = self.get_all_campaigns()
        
        total_spend = 0
        total_conversions = 0
        total_impressions = 0
        active_campaigns = 0
        
        for campaign in campaigns:
            if campaign.get("status") == "ACTIVE":
                active_campaigns += 1
            
            # Sum up latest performance metrics
            daily_perf = campaign.get("daily_performance", {})
            if daily_perf:
                latest_date = max(daily_perf.keys())
                latest_perf = daily_perf[latest_date]
                
                total_spend += latest_perf.get("spend", 0)
                total_conversions += latest_perf.get("conversions", 0) 
                total_impressions += latest_perf.get("impressions", 0)
        
        return {
            "total_campaigns": len(campaigns),
            "active_campaigns": active_campaigns,
            "total_spend": total_spend,
            "total_conversions": total_conversions,
            "total_impressions": total_impressions,
            "average_roas": total_conversions * 50 / total_spend if total_spend > 0 else 0  # Assuming $50 avg order value
        }
    
    def get_campaign_performance_df(self, campaign_id: str) -> pd.DataFrame:
        """Get campaign performance as pandas DataFrame"""
        campaign = self.get_campaign_by_id(campaign_id)
        if not campaign:
            return pd.DataFrame()
        
        daily_perf = campaign.get("daily_performance", {})
        if not daily_perf:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df_data = []
        for date, metrics in daily_perf.items():
            row = {"date": date, "campaign_name": campaign["name"]}
            row.update(metrics)
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        return df
    
    def get_all_performance_df(self) -> pd.DataFrame:
        """Get all campaigns performance as single DataFrame"""
        all_data = []
        
        for campaign in self.get_all_campaigns():
            daily_perf = campaign.get("daily_performance", {})
            for date, metrics in daily_perf.items():
                row = {
                    "date": date,
                    "campaign_id": campaign["id"],
                    "campaign_name": campaign["name"],
                    "industry": campaign.get("industry"),
                    "audience": campaign.get("audience"),
                    "status": campaign.get("status")
                }
                row.update(metrics)
                all_data.append(row)
        
        if not all_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['campaign_id', 'date'])
        
        return df
    
    def get_global_insights(self) -> Dict:
        """Get global insights and market trends"""
        return self.campaigns_data.get("global_insights", {})
    
    def search_campaigns(self, query: str) -> List[Dict]:
        """Simple text search across campaigns"""
        query = query.lower()
        results = []
        
        for campaign in self.get_all_campaigns():
            # Search in campaign name, industry, audience
            searchable_text = " ".join([
                campaign.get("name", ""),
                campaign.get("industry", ""),
                campaign.get("audience", ""),
                str(campaign.get("targeting", {}))
            ]).lower()
            
            if query in searchable_text:
                results.append(campaign)
        
        return results

# Utility functions for common queries
def format_currency(amount: float) -> str:
    """Format number as currency"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format as percentage"""
    return f"{value:.1f}%"

def format_number(value: float) -> str:
    """Format large numbers with commas"""
    return f"{value:,.0f}"

# Test the data loader
if __name__ == "__main__":
    loader = CampaignDataLoader()
    
    print("\n📊 Campaign Summary:")
    summary = loader.get_performance_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n🎯 Sample Campaigns:")
    campaigns = loader.get_all_campaigns()[:3]  # First 3
    for campaign in campaigns:
        print(f"  - {campaign['name']} ({campaign['status']})")
    
    print(f"\n✅ Data loader working properly!")