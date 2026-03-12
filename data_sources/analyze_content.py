#!/usr/bin/env python3
"""
Master Content Analysis Script

Runs all SEO analysis modules on a given content file and generates
a comprehensive report.

Usage:
    python3 analyze_content.py <content_file> [primary_keyword]

Output:
    Saves report to audits/<filename>-analysis.md
"""

import sys
import os
from datetime import datetime

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from keyword_analyzer import KeywordAnalyzer
from seo_quality_rater import SEOQualityRater
from readability_scorer import ReadabilityScorer
from content_length_comparator import ContentLengthComparator
from search_intent_analyzer import SearchIntentAnalyzer


def extract_meta_data(content: str) -> dict:
    """Extract meta data from markdown frontmatter or content"""
    meta = {
        'title': None,
        'description': None,
        'keywords': [],
        'slug': None
    }

    # Try to extract from YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            # Simple parsing
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    if key in meta:
                        if key == 'keywords':
                            meta[key] = [k.strip() for k in value.split(',')]
                        else:
                            meta[key] = value

    # Extract from H1 if no title
    if not meta['title']:
        import re
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            meta['title'] = h1_match.group(1)

    return meta


def count_links(content: str) -> tuple:
    """Count internal and external links"""
    import re

    # Internal links (no http)
    internal = len(re.findall(r'\[.+?\]\((?!https?://)[^)]+\)', content))

    # External links (with http)
    external = len(re.findall(r'\[.+?\]\(https?://[^)]+\)', content))

    return internal, external


def generate_report(
    content_file: str,
    content: str,
    keyword: str,
    keyword_result: dict,
    seo_result: dict,
    readability_result: dict,
    intent_result: dict
) -> str:
    """Generate comprehensive markdown report"""

    meta = extract_meta_data(content)
    internal_links, external_links = count_links(content)

    report = f"""# Content Analysis Report

**File**: `{content_file}`  
**Analyzed**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Primary Keyword**: {keyword or 'Not specified'}

---

## Executive Summary

**Overall SEO Score**: {seo_result.get('overall_score', 'N/A')}/100  
**Publishing Ready**: {'✓ Yes' if seo_result.get('publishing_ready') else '✗ No'}

| Category | Score |
|----------|-------|
| Content | {seo_result.get('category_scores', {}).get('content', 'N/A')}/100 |
| Keywords | {seo_result.get('category_scores', {}).get('keywords', 'N/A')}/100 |
| Meta | {seo_result.get('category_scores', {}).get('meta', 'N/A')}/100 |
| Structure | {seo_result.get('category_scores', {}).get('structure', 'N/A')}/100 |
| Links | {seo_result.get('category_scores', {}).get('links', 'N/A')}/100 |
| Readability | {seo_result.get('category_scores', {}).get('readability', 'N/A')}/100 |

---

## Content Statistics

- **Word Count**: {readability_result.get('word_count', 'N/A')}
- **Sentence Count**: {readability_result.get('sentence_count', 'N/A')}
- **Reading Time**: ~{readability_result.get('reading_time_minutes', 'N/A')} minutes
- **Internal Links**: {internal_links}
- **External Links**: {external_links}

---

## Keyword Analysis

### Primary Keyword: "{keyword or 'Not specified'}"

**Density**: {keyword_result.get('primary_keyword', {}).get('density', 'N/A')}%  
**Occurrences**: {keyword_result.get('primary_keyword', {}).get('count', 'N/A')}  
**Status**: {keyword_result.get('primary_keyword', {}).get('status', 'N/A')}

**Placements**:
- H1 Heading: {'✓' if keyword_result.get('primary_keyword', {}).get('placements', {}).get('h1') else '✗'}
- First 100 Words: {'✓' if keyword_result.get('primary_keyword', {}).get('placements', {}).get('first_100_words') else '✗'}
- H2 Headings: {keyword_result.get('primary_keyword', {}).get('placements', {}).get('h2', 0)}
- Conclusion: {'✓' if keyword_result.get('primary_keyword', {}).get('placements', {}).get('conclusion') else '✗'}

**Keyword Stuffing Risk**: {keyword_result.get('keyword_stuffing', {}).get('risk_level', 'N/A')}

---

## Readability Analysis

**Flesch Reading Ease**: {readability_result.get('flesch_score', 'N/A')}  
*({readability_result.get('flesch_interpretation', 'N/A')})*

**Grade Level**: {readability_result.get('grade_level', 'N/A')}

| Metric | Score |
|--------|-------|
| Flesch-Kincaid Grade | {readability_result.get('grade_level', 'N/A')} |
| Gunning Fog Index | {readability_result.get('gunning_fog_index', 'N/A')} |
| SMOG Index | {readability_result.get('smog_index', 'N/A')} |
| Coleman-Liau Index | {readability_result.get('coleman_liau_index', 'N/A')} |

**Details**:
- Average Sentence Length: {readability_result.get('avg_sentence_length', 'N/A')} words
- Average Syllables/Word: {readability_result.get('avg_syllables_per_word', 'N/A')}
- Complex Words: {readability_result.get('complex_word_percentage', 'N/A')}%

---

## Search Intent

**Primary Intent**: {intent_result.get('primary_intent', {}).get('type', 'N/A').upper()}  
**Confidence**: {intent_result.get('primary_intent', {}).get('confidence', 'N/A')}%

**Secondary Intent**: {intent_result.get('secondary_intent', {}).get('type', 'N/A')}

**Target SERP Features**:
"""

    for feature in intent_result.get('serp_features_to_target', []):
        report += f"- {feature}\n"

    report += f"""
**Suggested Content Types**:
"""
    for ctype in intent_result.get('content_type_suggestions', []):
        report += f"- {ctype}\n"

    # Issues and recommendations
    report += """
---

## Issues & Recommendations

"""

    if seo_result.get('critical_issues'):
        report += "### Critical Issues\n\n"
        for issue in seo_result['critical_issues']:
            report += f"- ⚠️ {issue}\n"
        report += "\n"

    if seo_result.get('warnings'):
        report += "### Warnings\n\n"
        for warning in seo_result['warnings']:
            report += f"- ⚡ {warning}\n"
        report += "\n"

    if seo_result.get('suggestions'):
        report += "### Suggestions\n\n"
        for suggestion in seo_result['suggestions']:
            report += f"- 💡 {suggestion}\n"
        report += "\n"

    if keyword_result.get('recommendations'):
        report += "### Keyword Recommendations\n\n"
        for rec in keyword_result['recommendations'][:5]:
            report += f"- {rec}\n"
        report += "\n"

    if readability_result.get('recommendations'):
        report += "### Readability Recommendations\n\n"
        for rec in readability_result['recommendations'][:3]:
            report += f"- {rec}\n"

    report += """
---

## Action Items

1. [ ] Review critical issues
2. [ ] Address high-priority warnings
3. [ ] Implement keyword recommendations
4. [ ] Improve readability where needed
5. [ ] Final review before publishing

---

*Report generated by SEO Machine Gemini Edition*
"""

    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_content.py <content_file> [primary_keyword]")
        sys.exit(1)

    content_file = sys.argv[1]
    primary_keyword = sys.argv[2] if len(sys.argv) > 2 else None

    # Read content
    try:
        with open(content_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{content_file}' not found")
        sys.exit(1)

    print(f"Analyzing: {content_file}")
    print(f"Word count: {len(content.split())}")

    # Try to extract keyword if not provided
    if not primary_keyword:
        meta = extract_meta_data(content)
        if meta['keywords']:
            primary_keyword = meta['keywords'][0]
            print(f"Using keyword from meta: {primary_keyword}")

    # Run analyses
    print("\nRunning analyses...")

    # Keyword analysis
    print("- Keyword analysis...")
    keyword_analyzer = KeywordAnalyzer()
    keyword_result = keyword_analyzer.analyze(
        content,
        primary_keyword or 'placeholder',
        target_density=1.5
    ) if primary_keyword else {'error': 'No keyword specified'}

    # SEO quality rating
    print("- SEO quality rating...")
    internal_links, external_links = count_links(content)
    seo_rater = SEOQualityRater()
    seo_result = seo_rater.rate(
        content,
        meta_title=extract_meta_data(content).get('title'),
        meta_description=extract_meta_data(content).get('description'),
        primary_keyword=primary_keyword,
        internal_link_count=internal_links,
        external_link_count=external_links
    )

    # Readability scoring
    print("- Readability scoring...")
    readability_scorer = ReadabilityScorer()
    readability_result = readability_scorer.score(content)

    # Search intent analysis
    print("- Search intent analysis...")
    intent_analyzer = SearchIntentAnalyzer()
    intent_result = intent_analyzer.analyze(primary_keyword or 'unknown')

    # Generate report
    print("\nGenerating report...")
    report = generate_report(
        content_file,
        content,
        primary_keyword or 'Not specified',
        keyword_result,
        seo_result,
        readability_result,
        intent_result
    )

    # Save report
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'workspace', 'audits')
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(content_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}-analysis.md")

    with open(output_file, 'w') as f:
        f.write(report)

    print(f"\n✓ Report saved to: {output_file}")
    print(f"\nOverall SEO Score: {seo_result.get('overall_score', 'N/A')}/100")
    print(f"Publishing Ready: {'Yes' if seo_result.get('publishing_ready') else 'No'}")


if __name__ == '__main__':
    main()
