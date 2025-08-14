# Data Organization

This folder contains all campaign data for the Meta Ads RAG Demo, organized by data source and type.

## 📁 Folder Structure

```
data/
├── demo/                   # Demo data for presentations
│   └── campaigns.json      # Curated demo campaigns (6 campaigns)
├── real/                   # Real Meta Ads data
│   ├── campaigns.json      # Processed real campaign data
│   └── processed/          # Cleaned and formatted data
├── sources/                # Raw downloaded datasets
│   ├── kaggle_facebook_ads.csv
│   ├── meta_ad_library.json
│   └── other_datasets/
└── README.md               # This file
```

## 🎯 Data Sources

### Demo Data (`demo/`)
- **Purpose**: Polished, curated data for demonstrations
- **Size**: 6 campaigns, 33 text chunks
- **Features**: 
  - Realistic business scenarios
  - Seasonal patterns (Black Friday, New Year)
  - Multiple industries (Electronics, Fashion, Fitness)
  - Performance anomalies and insights

### Real Data (`real/`)
- **Purpose**: Authentic Meta Ads campaign data
- **Sources**: Kaggle datasets, Meta Ad Library
- **Format**: Same JSON structure as demo data
- **Use Cases**: 
  - Production RAG responses
  - Advanced analytics
  - Realistic business insights

### Raw Sources (`sources/`)
- **Purpose**: Original downloaded datasets
- **Formats**: CSV, JSON, Excel
- **Processing**: Use conversion scripts to transform into RAG format

## 🔧 Usage

### Environment Configuration
Set the data source in your environment:

```bash
# Use demo data (default)
export DATA_SOURCE=demo

# Use real data
export DATA_SOURCE=real
```

### Code Usage
```python
from data_loader import CampaignDataLoader

# Load demo data
loader = CampaignDataLoader(data_source="demo")

# Load real data  
loader = CampaignDataLoader(data_source="real")

# Auto-select based on environment
loader = CampaignDataLoader()  # Checks DATA_SOURCE env var
```

## 📊 Data Formats

All processed data follows this JSON structure:

```json
{
  "campaigns": [
    {
      "id": "camp_001",
      "name": "Campaign Name",
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
        }
      }
    }
  ]
}
```

## 🔄 Adding New Data

### From Kaggle
1. Download dataset to `sources/`
2. Run conversion script: `python scripts/convert_kaggle_data.py`
3. Processed data saved to `real/campaigns.json`

### From Meta Ad Library
1. Use scraping tools to download to `sources/`
2. Run Meta conversion script: `python scripts/convert_meta_data.py`
3. Merge with existing real data

## 🧪 Testing

Test data loading with:
```bash
python test_data_loading.py
```

## 📈 Data Quality

- **Demo Data**: Hand-crafted for optimal RAG demonstrations
- **Real Data**: Authentic campaign metrics with realistic patterns
- **Validation**: All data validated against schema before processing