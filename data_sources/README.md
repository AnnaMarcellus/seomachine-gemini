# Data Sources Setup

Python-based data integrations and analysis modules for SEO Machine.

## Installation

```bash
cd data_sources
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `config/.env`
2. Fill in your API credentials
3. Place service account JSON files in `credentials/` directory

## Modules Overview

### Analysis Modules

#### keyword_analyzer.py
Analyzes keyword density, distribution, and semantic clustering.

**Usage**:
```python
from modules.keyword_analyzer import KeywordAnalyzer
analyzer = KeywordAnalyzer()
result = analyzer.analyze(
    content=article_text,
    primary_keyword="target keyword",
    secondary_keywords=["keyword 2", "keyword 3"],
    target_density=1.5
)
```

#### seo_quality_rater.py
Rates content against SEO best practices (0-100 score).

**Usage**:
```python
from modules.seo_quality_rater import SEOQualityRater
rater = SEOQualityRater()
score = rater.rate(
    content=article_text,
    meta_title="Title",
    meta_description="Description",
    primary_keyword="target keyword"
)
```

#### readability_scorer.py
Calculates readability scores and grade levels.

**Usage**:
```python
from modules.readability_scorer import ReadabilityScorer
scorer = ReadabilityScorer()
scores = scorer.score(content=article_text)
```

#### content_length_comparator.py
Compares word count against SERP competitors.

**Usage**:
```python
from modules.content_length_comparator import ContentLengthComparator
comparator = ContentLengthComparator()
comparison = comparator.compare(
    keyword="target keyword",
    your_word_count=2500
)
```

#### search_intent_analyzer.py
Classifies search intent for keywords.

**Usage**:
```python
from modules.search_intent_analyzer import SearchIntentAnalyzer
analyzer = SearchIntentAnalyzer()
intent = analyzer.analyze(keyword="target keyword")
```

### Data Integration Modules

#### google_analytics.py
Fetches data from Google Analytics 4.

**Requirements**:
- GA4_PROPERTY_ID in .env
- GA4 service account credentials

#### google_search_console.py
Fetches data from Google Search Console.

**Requirements**:
- GSC_SITE_URL in .env
- GSC service account credentials

#### dataforseo.py
SERP data and keyword metrics via DataForSEO API.

**Requirements**:
- DATAFORSEO_LOGIN and PASSWORD in .env

#### wordpress_publisher.py
Publishes content to WordPress via REST API.

**Requirements**:
- WordPress credentials in .env

### Utility Modules

#### data_aggregator.py
Combines data from multiple sources into unified analytics.

#### opportunity_scorer.py
Scores content opportunities using 8 weighted factors.

## Running Analysis Scripts

### Individual Module Tests
```bash
python3 -m modules.keyword_analyzer
python3 -m modules.seo_quality_rater
python3 -m modules.readability_scorer
```

### Full Content Analysis
```bash
python3 analyze_content.py --file drafts/article.md
```

### Research Scripts
```bash
python3 research_quick_wins.py
python3 research_competitor_gaps.py
python3 research_topic_clusters.py
```

## API Setup Guides

### Google Analytics 4

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable Google Analytics Data API
4. Create service account (IAM & Admin > Service Accounts)
5. Download JSON key
6. Add service account email to GA4 property (Viewer role)
7. Place JSON in `credentials/ga4-credentials.json`

### Google Search Console

1. Use same service account as GA4, or create new one
2. Enable Google Search Console API
3. Add service account email as user in Search Console
4. Place credentials in `credentials/gsc-credentials.json`

### DataForSEO

1. Sign up at [dataforseo.com](https://dataforseo.com)
2. Get API credentials from dashboard
3. Add to `.env` file

### WordPress

1. Install Application Passwords plugin or use built-in (WP 5.6+)
2. Generate application password
3. Add to `.env` file

## Cache System

All API responses are cached to reduce costs and improve speed.

**Cache Location**: `cache/` directory
**Default TTL**: 1 hour for SERP data, 24 hours for analytics

To clear cache:
```bash
rm -rf cache/*
```

## Error Handling

All modules include error handling and graceful degradation:
- API failures return partial results
- Missing data is noted in output
- Rate limiting is automatically handled

## Adding New Modules

1. Create new file in `modules/`
2. Follow existing module structure
3. Add error handling
4. Include docstrings
5. Add to this README

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Authentication failed"
- Check .env file credentials
- Verify service account permissions
- Check JSON credential file path

### "Rate limit exceeded"
- Wait and retry
- Check cache is working
- Reduce request frequency

## Performance Tips

- Use caching aggressively
- Batch API requests when possible
- Process large content in chunks
- Use async for multiple API calls

## Support

For issues with:
- **DataForSEO**: Contact their support
- **Google APIs**: Check Cloud Console
- **Custom modules**: File issue in repo
