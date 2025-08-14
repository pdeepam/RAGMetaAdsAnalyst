# Data Sources

This folder contains raw datasets downloaded from various sources.

## 📥 How to Add Data Sources

### From Kaggle
1. **Install Kaggle CLI**:
   ```bash
   pip install kaggle
   ```

2. **Download Facebook Ads datasets**:
   ```bash
   # Main Facebook Ad Campaign dataset
   kaggle datasets download -d madislemsalu/facebook-ad-campaign
   unzip facebook-ad-campaign.zip
   mv *.csv kaggle_facebook_ads.csv
   
   # Marketing Campaign Performance dataset  
   kaggle datasets download -d manishabhatt22/marketing-campaign-performance-dataset
   
   # Facebook Campaign Analytics dataset
   kaggle datasets download -d emmanueldjegou/campaign-dataset
   ```

3. **Convert to RAG format**:
   ```bash
   python scripts/convert_kaggle_data.py
   ```

### From Meta Ad Library
1. **Use scraping tools** (Apify, Stevesie, etc.)
2. **Download as CSV/JSON** to this folder
3. **Run conversion script**:
   ```bash
   python scripts/convert_meta_library.py
   ```

## 📊 Expected File Structure

```
sources/
├── kaggle_facebook_ads.csv       # Main Kaggle dataset
├── marketing_campaigns.csv       # Additional campaign data  
├── meta_ad_library.json          # Meta Ad Library data
├── other_datasets/               # Additional sources
└── README.md                     # This file
```

## 🔄 Data Processing Pipeline

1. **Raw Data** (CSV, JSON) → `sources/`
2. **Conversion Scripts** → Transform to RAG format
3. **Processed Data** → Save to `data/real/campaigns.json`
4. **RAG System** → Load and chunk for vector storage

## 📋 Data Quality Checklist

When adding new datasets, ensure:
- [ ] Contains campaign performance metrics (impressions, clicks, spend)
- [ ] Has temporal data (dates, time periods) 
- [ ] Includes targeting information (audience, demographics)
- [ ] Campaign objectives are specified
- [ ] Data is recent (2022-2025 preferred)
- [ ] No personal identifiable information (PII)

## 🎯 Recommended Datasets

### High Priority
1. **Kaggle Facebook Ad Campaign** - Most popular, well-structured
2. **Marketing Campaign Performance** - Recent 2023 data
3. **Facebook Campaign Analytics** - Marketing-specific

### Medium Priority  
4. **Meta Ad Library** - Current running ads data
5. **Facebook Metrics Dataset** - Additional performance data
6. **Advertising Dataset** - General advertising metrics

Place downloaded files here and run the appropriate conversion script!