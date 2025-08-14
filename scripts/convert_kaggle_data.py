#!/usr/bin/env python3
"""
Convert Kaggle Facebook Ads dataset to RAG format
Usage: python scripts/convert_kaggle_data.py
"""

import json
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

def convert_kaggle_to_rag_format(input_csv: str, output_json: str):
    """Convert Kaggle dataset to our RAG JSON format"""
    
    print(f"🔄 Converting {input_csv} to RAG format...")
    
    try:
        # Read Kaggle CSV
        df = pd.read_csv(input_csv)
        print(f"✅ Loaded {len(df)} rows from Kaggle dataset")
        
        # Create campaigns structure
        campaigns = []
        
        # Process each row (assuming each row is a campaign or daily data)
        for idx, row in df.iterrows():
            campaign = {
                "id": f"kaggle_{idx}",
                "name": f"Campaign {idx + 1}",
                "objective": "CONVERSIONS",
                "status": "ACTIVE",
                "industry": "Mixed",
                "audience": "Unknown",
                "created_date": "2024-01-01",
                "budget": {
                    "daily_budget": 100,
                    "total_budget": 3000
                },
                "targeting": {
                    "age_min": 18,
                    "age_max": 65,
                    "interests": ["general"],
                    "placements": ["feed", "stories"],
                    "devices": ["mobile", "desktop"]
                }
            }
            
            # Map Kaggle columns to our format (adjust based on actual dataset)
            daily_performance = {}
            date_str = "2024-01-01"  # Default date
            
            # Try to map common column names
            performance_data = {
                "impressions": int(row.get('impressions', row.get('Impressions', 1000))),
                "clicks": int(row.get('clicks', row.get('Clicks', 30))),
                "spend": float(row.get('spend', row.get('Spend', 25.0))),
                "conversions": int(row.get('conversions', row.get('Conversions', 2))),
                "ctr": float(row.get('ctr', row.get('CTR', 3.0))),
                "cpm": float(row.get('cpm', row.get('CPM', 25.0))),
                "cpc": float(row.get('cpc', row.get('CPC', 0.83))),
                "roas": float(row.get('roas', row.get('ROAS', 3.0))),
                "frequency": float(row.get('frequency', row.get('Frequency', 1.5))),
                "reach": int(row.get('reach', row.get('Reach', 667)))
            }
            
            daily_performance[date_str] = performance_data
            campaign["daily_performance"] = daily_performance
            
            campaigns.append(campaign)
        
        # Create final structure
        rag_data = {
            "campaigns": campaigns,
            "global_insights": {
                "data_source": "kaggle",
                "processed_date": datetime.now().isoformat(),
                "total_campaigns": len(campaigns),
                "conversion_note": "Converted from Kaggle Facebook Ads dataset"
            }
        }
        
        # Save to JSON
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, 'w') as f:
            json.dump(rag_data, f, indent=2)
        
        print(f"✅ Converted {len(campaigns)} campaigns to {output_json}")
        return True
        
    except Exception as e:
        print(f"❌ Error converting data: {e}")
        return False

def main():
    """Main conversion function"""
    input_csv = "data/sources/kaggle_facebook_ads.csv"
    output_json = "data/real/campaigns.json"
    
    if not os.path.exists(input_csv):
        print(f"❌ Input file not found: {input_csv}")
        print("📥 Please download Kaggle dataset to data/sources/ first")
        return
    
    success = convert_kaggle_to_rag_format(input_csv, output_json)
    
    if success:
        print("🎉 Conversion complete!")
        print(f"📁 Real data available at: {output_json}")
        print("🔧 Update DATA_SOURCE=real to use this data")
    else:
        print("❌ Conversion failed")

if __name__ == "__main__":
    main()