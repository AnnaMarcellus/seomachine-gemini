"""
SEO Quality Rater

Rates content quality against SEO best practices and guidelines.
Provides scoring (0-100) and specific recommendations for improvement.
"""

import re
from typing import Dict, List, Optional, Any


class SEOQualityRater:
    """Rates content against SEO best practices"""

    def __init__(self, guidelines: Optional[Dict[str, Any]] = None):
        """
        Initialize SEO Quality Rater

        Args:
            guidelines: Custom SEO guidelines (defaults to standard best practices)
        """
        self.guidelines = guidelines or self._default_guidelines()

    def _default_guidelines(self) -> Dict[str, Any]:
        """Default SEO guidelines based on industry standards"""
        return {
            'min_word_count': 2000,
            'optimal_word_count': 2500,
            'max_word_count': 3000,
            'primary_keyword_density_min': 1.0,
            'primary_keyword_density_max': 2.0,
            'secondary_keyword_density': 0.5,
            'min_internal_links': 3,
            'optimal_internal_links': 5,
            'min_external_links': 2,
            'optimal_external_links': 3,
            'meta_title_length_min': 50,
            'meta_title_length_max': 60,
            'meta_description_length_min': 150,
            'meta_description_length_max': 160,
            'min_h2_sections': 4,
            'optimal_h2_sections': 6,
            'h2_with_keyword_ratio': 0.33,
            'max_sentence_length': 25,
            'target_reading_level_min': 8,
            'target_reading_level_max': 10,
        }

    def rate(
        self,
        content: str,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
        primary_keyword: Optional[str] = None,
        secondary_keywords: Optional[List[str]] = None,
        keyword_density: Optional[float] = None,
        internal_link_count: Optional[int] = None,
        external_link_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Rate content against SEO best practices

        Args:
            content: Article content
            meta_title: Meta title tag
            meta_description: Meta description tag
            primary_keyword: Target primary keyword
            secondary_keywords: Target secondary keywords
            keyword_density: Pre-calculated keyword density
            internal_link_count: Number of internal links
            external_link_count: Number of external links

        Returns:
            Dict with overall score, category scores, and recommendations
        """
        # Extract structure
        structure = self._analyze_structure(content, primary_keyword)

        # Score each category
        content_score = self._score_content(content, structure)
        keyword_score = self._score_keyword_optimization(
            content, structure, primary_keyword, secondary_keywords, keyword_density
        )
        meta_score = self._score_meta_elements(meta_title, meta_description, primary_keyword)
        structure_score = self._score_structure(structure)
        link_score = self._score_links(content, internal_link_count, external_link_count)
        readability_score = self._score_readability(content, structure)

        # Calculate overall score (weighted average)
        weights = {
            'content': 0.20,
            'keywords': 0.25,
            'meta': 0.15,
            'structure': 0.15,
            'links': 0.15,
            'readability': 0.10
        }

        overall_score = (
            content_score['score'] * weights['content'] +
            keyword_score['score'] * weights['keywords'] +
            meta_score['score'] * weights['meta'] +
            structure_score['score'] * weights['structure'] +
            link_score['score'] * weights['links'] +
            readability_score['score'] * weights['readability']
        )

        # Compile all issues
        critical_issues = []
        warnings = []
        suggestions = []

        for score_dict in [content_score, keyword_score, meta_score, structure_score, link_score, readability_score]:
            critical_issues.extend(score_dict.get('critical_issues', []))
            warnings.extend(score_dict.get('warnings', []))
            suggestions.extend(score_dict.get('suggestions', []))

        return {
            'overall_score': round(overall_score, 1),
            'category_scores': {
                'content': content_score['score'],
                'keywords': keyword_score['score'],
                'meta': meta_score['score'],
                'structure': structure_score['score'],
                'links': link_score['score'],
                'readability': readability_score['score']
            },
            'structure': structure,
            'critical_issues': critical_issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'publishing_ready': overall_score >= 75 and len(critical_issues) == 0
        }

    def _analyze_structure(self, content: str, primary_keyword: Optional[str]) -> Dict[str, Any]:
        """Analyze content structure"""
        # Extract headings
        h1_pattern = r'^#\s+(.+)$'
        h2_pattern = r'^##\s+(.+)$'
        h3_pattern = r'^###\s+(.+)$'

        h1_matches = re.findall(h1_pattern, content, re.MULTILINE)
        h2_matches = re.findall(h2_pattern, content, re.MULTILINE)
        h3_matches = re.findall(h3_pattern, content, re.MULTILINE)

        word_count = len(content.split())

        # Check keyword in headings
        keyword_in_h1 = False
        keyword_in_h2_count = 0

        if primary_keyword:
            keyword_lower = primary_keyword.lower()
            keyword_in_h1 = any(keyword_lower in h.lower() for h in h1_matches)
            keyword_in_h2_count = sum(1 for h in h2_matches if keyword_lower in h.lower())

        return {
            'word_count': word_count,
            'h1_count': len(h1_matches),
            'h2_count': len(h2_matches),
            'h3_count': len(h3_matches),
            'h1_text': h1_matches[0] if h1_matches else None,
            'keyword_in_h1': keyword_in_h1,
            'keyword_in_h2_count': keyword_in_h2_count,
            'has_introduction': word_count > 0,
            'has_conclusion': len(content.split('\n')[-10:]) > 50 if content else False
        }

    def _score_content(self, content: str, structure: Dict) -> Dict[str, Any]:
        """Score content quality"""
        score = 100
        critical_issues = []
        warnings = []
        suggestions = []

        word_count = structure['word_count']
        g = self.guidelines

        # Word count scoring
        if word_count < g['min_word_count']:
            score -= 25
            critical_issues.append(f"Word count ({word_count}) below minimum ({g['min_word_count']})")
        elif word_count < g['optimal_word_count']:
            score -= 10
            warnings.append(f"Word count ({word_count}) below optimal ({g['optimal_word_count']})")
        elif word_count > g['max_word_count']:
            score -= 5
            suggestions.append(f"Word count ({word_count}) exceeds recommended maximum")

        # Content structure
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) < 5:
            score -= 15
            warnings.append("Content has too few paragraphs")

        # Check for lists
        has_lists = bool(re.search(r'^[\*\-\+]\s', content, re.MULTILINE))
        if not has_lists:
            score -= 5
            suggestions.append("Add bulleted or numbered lists for better scannability")

        return {
            'score': max(0, score),
            'critical_issues': critical_issues,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _score_keyword_optimization(
        self,
        content: str,
        structure: Dict,
        primary_keyword: Optional[str],
        secondary_keywords: Optional[List[str]],
        keyword_density: Optional[float]
    ) -> Dict[str, Any]:
        """Score keyword optimization"""
        score = 100
        critical_issues = []
        warnings = []
        suggestions = []

        if not primary_keyword:
            return {'score': 50, 'critical_issues': ['No primary keyword specified'], 'warnings': [], 'suggestions': []}

        g = self.guidelines

        # Keyword density
        if keyword_density is not None:
            if keyword_density < g['primary_keyword_density_min']:
                score -= 15
                warnings.append(f"Keyword density ({keyword_density:.1f}%) below minimum ({g['primary_keyword_density_min']}%)")
            elif keyword_density > g['primary_keyword_density_max']:
                score -= 20
                critical_issues.append(f"Keyword density ({keyword_density:.1f}%) too high (max {g['primary_keyword_density_max']}%)")

        # Keyword in headings
        if not structure['keyword_in_h1']:
            score -= 15
            warnings.append("Primary keyword not in H1 heading")

        h2_keyword_ratio = structure['keyword_in_h2_count'] / max(structure['h2_count'], 1)
        if h2_keyword_ratio < g['h2_with_keyword_ratio']:
            score -= 10
            suggestions.append(f"Add keyword to more H2 headings (currently in {structure['keyword_in_h2_count']}/{structure['h2_count']})")

        # First 100 words
        first_100 = ' '.join(content.split()[:100]).lower()
        if primary_keyword.lower() not in first_100:
            score -= 10
            warnings.append("Primary keyword not in first 100 words")

        return {
            'score': max(0, score),
            'critical_issues': critical_issues,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _score_meta_elements(
        self,
        meta_title: Optional[str],
        meta_description: Optional[str],
        primary_keyword: Optional[str]
    ) -> Dict[str, Any]:
        """Score meta elements"""
        score = 100
        critical_issues = []
        warnings = []
        suggestions = []

        g = self.guidelines

        # Meta title
        if not meta_title:
            score -= 20
            critical_issues.append("Missing meta title")
        else:
            title_len = len(meta_title)
            if title_len < g['meta_title_length_min']:
                score -= 10
                warnings.append(f"Meta title ({title_len} chars) too short (min {g['meta_title_length_min']})")
            elif title_len > g['meta_title_length_max']:
                score -= 10
                warnings.append(f"Meta title ({title_len} chars) too long (max {g['meta_title_length_max']})")

            if primary_keyword and primary_keyword.lower() not in meta_title.lower():
                score -= 10
                warnings.append("Primary keyword not in meta title")

        # Meta description
        if not meta_description:
            score -= 15
            critical_issues.append("Missing meta description")
        else:
            desc_len = len(meta_description)
            if desc_len < g['meta_description_length_min']:
                score -= 8
                warnings.append(f"Meta description ({desc_len} chars) too short")
            elif desc_len > g['meta_description_length_max']:
                score -= 8
                warnings.append(f"Meta description ({desc_len} chars) too long")

            if primary_keyword and primary_keyword.lower() not in meta_description.lower():
                score -= 5
                suggestions.append("Consider adding primary keyword to meta description")

        return {
            'score': max(0, score),
            'critical_issues': critical_issues,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _score_structure(self, structure: Dict) -> Dict[str, Any]:
        """Score content structure"""
        score = 100
        critical_issues = []
        warnings = []
        suggestions = []

        g = self.guidelines

        # H1 check
        if structure['h1_count'] == 0:
            score -= 20
            critical_issues.append("Missing H1 heading")
        elif structure['h1_count'] > 1:
            score -= 15
            critical_issues.append(f"Multiple H1 headings ({structure['h1_count']})")

        # H2 sections
        if structure['h2_count'] < g['min_h2_sections']:
            score -= 15
            warnings.append(f"Too few H2 sections ({structure['h2_count']}, min {g['min_h2_sections']})")
        elif structure['h2_count'] < g['optimal_h2_sections']:
            score -= 5
            suggestions.append(f"Consider adding more H2 sections (currently {structure['h2_count']})")

        # H3 usage
        if structure['h3_count'] == 0:
            score -= 5
            suggestions.append("Consider using H3 subsections for better structure")

        return {
            'score': max(0, score),
            'critical_issues': critical_issues,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _score_links(
        self,
        content: str,
        internal_link_count: Optional[int],
        external_link_count: Optional[int]
    ) -> Dict[str, Any]:
        """Score link strategy"""
        score = 100
        critical_issues = []
        warnings = []
        suggestions = []

        g = self.guidelines

        # Count links if not provided
        if internal_link_count is None:
            internal_link_count = len(re.findall(r'\[.+?\]\((?!http).+?\)', content))
        if external_link_count is None:
            external_link_count = len(re.findall(r'\[.+?\]\(https?://', content))

        # Internal links
        if internal_link_count < g['min_internal_links']:
            score -= 15
            warnings.append(f"Too few internal links ({internal_link_count}, min {g['min_internal_links']})")
        elif internal_link_count < g['optimal_internal_links']:
            score -= 5
            suggestions.append(f"Consider adding more internal links (currently {internal_link_count})")

        # External links
        if external_link_count < g['min_external_links']:
            score -= 10
            warnings.append(f"Too few external links ({external_link_count}, min {g['min_external_links']})")

        return {
            'score': max(0, score),
            'critical_issues': critical_issues,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _score_readability(self, content: str, structure: Dict) -> Dict[str, Any]:
        """Score readability"""
        score = 100
        critical_issues = []
        warnings = []
        suggestions = []

        g = self.guidelines

        # Sentence length
        sentences = re.split(r'[.!?]+', content)
        long_sentences = [s for s in sentences if len(s.split()) > g['max_sentence_length']]
        if len(long_sentences) > len(sentences) * 0.2:
            score -= 10
            warnings.append(f"{len(long_sentences)} sentences exceed recommended length")

        # Paragraph length
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        long_paragraphs = [p for p in paragraphs if len(p.split()) > 100]
        if long_paragraphs:
            score -= 10
            warnings.append(f"{len(long_paragraphs)} paragraphs are too long (break them up)")

        return {
            'score': max(0, score),
            'critical_issues': critical_issues,
            'warnings': warnings,
            'suggestions': suggestions
        }


# CLI interface
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python seo_quality_rater.py <content_file> [meta_title] [meta_description] [primary_keyword]")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        content = f.read()

    meta_title = sys.argv[2] if len(sys.argv) > 2 else None
    meta_description = sys.argv[3] if len(sys.argv) > 3 else None
    primary_keyword = sys.argv[4] if len(sys.argv) > 4 else None

    rater = SEOQualityRater()
    result = rater.rate(content, meta_title, meta_description, primary_keyword)

    print(f"\n=== SEO Quality Rating ===")
    print(f"Overall Score: {result['overall_score']}/100")
    print(f"Publishing Ready: {'✓ Yes' if result['publishing_ready'] else '✗ No'}")
    print(f"\nCategory Scores:")
    for category, score in result['category_scores'].items():
        print(f"  {category.capitalize()}: {score}/100")

    if result['critical_issues']:
        print(f"\nCritical Issues:")
        for issue in result['critical_issues']:
            print(f"  ⚠️  {issue}")

    if result['warnings']:
        print(f"\nWarnings:")
        for warning in result['warnings']:
            print(f"  ⚡ {warning}")

    if result['suggestions']:
        print(f"\nSuggestions:")
        for suggestion in result['suggestions']:
            print(f"  💡 {suggestion}")
