#!/usr/bin/env python3
"""
Convert real Facebook Ads CSV data to RAG JSON format
Usage: python scripts/convert_real_data.py
"""

import json
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

def convert_real_csv_to_rag_format(input_csv: str, output_json: str):
    """Convert real Facebook Ads CSV to RAG JSON format"""
    
    print(f"🔄 Converting real Facebook Ads data: {input_csv}")
    
    try:
        # Read CSV
        df = pd.read_csv(input_csv)
        print(f"✅ Loaded {len(df)} ad records from real Facebook data")
        
        # Group by campaign_id to create campaigns
        campaigns = []
        campaign_groups = df.groupby('campaign_id')
        
        for campaign_id, campaign_data in campaign_groups:
            
            # Get campaign basics from first row
            first_row = campaign_data.iloc[0]
            
            # Calculate campaign totals
            total_impressions = campaign_data['impressions'].sum()
            total_clicks = campaign_data['clicks'].sum()
            total_spend = campaign_data['spent'].sum()
            total_conversions = campaign_data['total_conversion'].sum()
            approved_conversions = campaign_data['approved_conversion'].sum()
            
            # Calculate derived metrics
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
            cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            
            # Get unique targeting data
            ages = campaign_data['age'].unique()
            genders = campaign_data['gender'].unique()
            interests = set()
            for _, row in campaign_data.iterrows():
                if pd.notna(row['interest1']): interests.add(str(int(row['interest1'])))
                if pd.notna(row['interest2']): interests.add(str(int(row['interest2'])))
                if pd.notna(row['interest3']): interests.add(str(int(row['interest3'])))
            
            # Create campaign structure
            campaign = {
                "id": f"real_camp_{campaign_id}",
                "name": f"Real Facebook Campaign {campaign_id}",
                "objective": "CONVERSIONS",
                "status": "ACTIVE",
                "industry": "Mixed",
                "audience": "Interest-based targeting",
                "created_date": "2017-08-17",
                "budget": {
                    "daily_budget": round(total_spend / len(campaign_data) * 10, 2),  # Estimate
                    "total_budget": round(total_spend * 30, 2)  # Estimate monthly
                },
                "targeting": {
                    "age_ranges": ages.tolist(),
                    "genders": genders.tolist(), 
                    "interests": list(interests)[:10],  # Limit to top 10
                    "placements": ["feed", "stories"],
                    "devices": ["mobile", "desktop"]
                }
            }
            
            # Create daily performance data grouped by date
            daily_performance = {}
            date_groups = campaign_data.groupby(['reporting_start', 'reporting_end'])
            
            for (start_date, end_date), daily_data in date_groups:
                # Convert date format from DD/MM/YYYY to YYYY-MM-DD
                try:
                    date_obj = datetime.strptime(start_date, '%d/%m/%Y')
                    date_key = date_obj.strftime('%Y-%m-%d')
                except:
                    date_key = "2017-08-17"  # Fallback
                
                day_impressions = daily_data['impressions'].sum()
                day_clicks = daily_data['clicks'].sum()
                day_spend = daily_data['spent'].sum()
                day_conversions = daily_data['total_conversion'].sum()
                
                # Calculate daily metrics
                day_ctr = (day_clicks / day_impressions * 100) if day_impressions > 0 else 0
                day_cpm = (day_spend / day_impressions * 1000) if day_impressions > 0 else 0
                day_cpc = (day_spend / day_clicks) if day_clicks > 0 else 0
                day_roas = (day_conversions * 50 / day_spend) if day_spend > 0 else 0  # Assume $50 per conversion
                
                daily_performance[date_key] = {
                    "impressions": int(day_impressions),
                    "clicks": int(day_clicks), 
                    "spend": round(day_spend, 2),
                    "conversions": int(day_conversions),
                    "ctr": round(day_ctr, 2),
                    "cpm": round(day_cpm, 2),
                    "cpc": round(day_cpc, 2),
                    "roas": round(day_roas, 2),
                    "frequency": round(day_impressions / (day_impressions * 0.7), 2),  # Estimate
                    "reach": int(day_impressions * 0.7)  # Estimate reach
                }
            
            campaign["daily_performance"] = daily_performance
            
            # Add insights based on real data patterns
            insights = []
            if ctr < 1.0:
                insights.append("Low CTR indicates potential audience or creative issues")
            if conversion_rate > 5.0:
                insights.append(f"High conversion rate of {conversion_rate:.1f}% shows strong audience targeting")
            if cpm > 10:
                insights.append("High CPM suggests competitive audience or premium placements")
            
            campaign["insights"] = {
                "performance_summary": f"Campaign generated {total_conversions} conversions from {total_impressions:,} impressions",
                "key_metrics": {
                    "ctr": round(ctr, 2),
                    "cpm": round(cpm, 2), 
                    "conversion_rate": round(conversion_rate, 2)
                },
                "recommendations": insights
            }
            
            campaigns.append(campaign)
        
        # Create global insights from all data
        global_insights = {
            "data_source": "real_facebook_ads",
            "original_dataset": "Facebook Ad Campaign Analysis - GitHub",
            "processed_date": datetime.now().isoformat(),
            "total_campaigns": len(campaigns),
            "total_ad_records": len(df),
            "date_range": "2017-08-17 to 2017-08-30",
            "data_summary": {
                "total_impressions": int(df['impressions'].sum()),
                "total_clicks": int(df['clicks'].sum()),
                "total_spend": round(df['spent'].sum(), 2),
                "total_conversions": int(df['total_conversion'].sum()),
                "overall_ctr": round(df['clicks'].sum() / df['impressions'].sum() * 100, 2),
                "overall_cpm": round(df['spent'].sum() / df['impressions'].sum() * 1000, 2)
            }
        }
        
        # Create final RAG structure
        rag_data = {
            "campaigns": campaigns,
            "global_insights": global_insights
        }
        
        # Save to JSON
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, 'w') as f:
            json.dump(rag_data, f, indent=2)
        
        print(f"✅ Converted {len(campaigns)} real campaigns to {output_json}")
        print(f"📊 Total records: {len(df)} ads across {len(campaigns)} campaigns")
        print(f"💰 Total spend: ${df['spent'].sum():.2f}")
        print(f"👀 Total impressions: {df['impressions'].sum():,}")
        print(f"🎯 Total conversions: {df['total_conversion'].sum()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting real data: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Convert real Facebook Ads data"""
    input_csv = "data/real/data.csv"
    output_json = "data/real/campaigns.json"
    
    if not os.path.exists(input_csv):
        print(f"❌ Real data file not found: {input_csv}")
        return
    
    success = convert_real_csv_to_rag_format(input_csv, output_json)
    
    if success:
        print("\n🎉 Real data conversion complete!")
        print(f"📁 Real campaigns available at: {output_json}")
        print("🔧 Set DATA_SOURCE=real to use this authentic Facebook Ads data")
        print("🚀 Your RAG system now has real-world Facebook campaign insights!")
    else:
        print("❌ Conversion failed")

if __name__ == "__main__":
    main()