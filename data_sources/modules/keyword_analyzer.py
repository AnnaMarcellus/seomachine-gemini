"""
Keyword Analyzer

Calculates keyword density, analyzes distribution, and performs semantic clustering
to identify keyword usage patterns and topic clusters within content.
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter


class KeywordAnalyzer:
    """Analyzes keyword density, distribution, and clustering in content"""

    def __init__(self):
        self.stop_words = set([
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'you', 'your', 'this', 'their', 'but',
            'or', 'not', 'can', 'have', 'all', 'when', 'there', 'been', 'if',
            'more', 'so', 'about', 'what', 'which', 'who', 'would', 'could'
        ])

    def analyze(
        self,
        content: str,
        primary_keyword: str,
        secondary_keywords: Optional[List[str]] = None,
        target_density: float = 1.5
    ) -> Dict[str, Any]:
        """
        Comprehensive keyword analysis

        Args:
            content: Article content to analyze
            primary_keyword: Main target keyword
            secondary_keywords: List of secondary keywords
            target_density: Target keyword density percentage (default 1.5%)

        Returns:
            Dict with density metrics, distribution map, and recommendations
        """
        secondary_keywords = secondary_keywords or []

        # Clean and prepare content
        word_count = len(content.split())
        sections = self._extract_sections(content)

        # Analyze primary keyword
        primary_analysis = self._analyze_keyword(
            content,
            primary_keyword,
            word_count,
            sections,
            target_density
        )

        # Analyze secondary keywords
        secondary_analysis = []
        for keyword in secondary_keywords:
            analysis = self._analyze_keyword(
                content,
                keyword,
                word_count,
                sections,
                target_density * 0.5  # Lower target for secondary
            )
            secondary_analysis.append(analysis)

        # Detect keyword stuffing
        stuffing_risk = self._detect_keyword_stuffing(
            content,
            primary_keyword,
            primary_analysis['density']
        )

        # LSI/semantic keyword suggestions
        lsi_keywords = self._find_lsi_keywords(content, primary_keyword)

        return {
            'word_count': word_count,
            'primary_keyword': {
                'keyword': primary_keyword,
                **primary_analysis
            },
            'secondary_keywords': secondary_analysis,
            'keyword_stuffing': stuffing_risk,
            'lsi_keywords': lsi_keywords,
            'recommendations': self._generate_recommendations(
                primary_analysis,
                secondary_analysis,
                stuffing_risk,
                target_density
            )
        }

    def _analyze_keyword(
        self,
        content: str,
        keyword: str,
        word_count: int,
        sections: List[Dict],
        target_density: float
    ) -> Dict[str, Any]:
        """Analyze a single keyword"""
        content_lower = content.lower()
        keyword_lower = keyword.lower()

        # Count exact matches
        exact_count = content_lower.count(keyword_lower)

        # Calculate density
        density = (exact_count / word_count * 100) if word_count > 0 else 0

        # Check critical placements
        h1_count = self._count_in_headings(content, keyword, 'h1')
        h2_count = self._count_in_headings(content, keyword, 'h2')
        h3_count = self._count_in_headings(content, keyword, 'h3')
        first_100 = self._in_first_100_words(content, keyword)
        in_conclusion = self._in_conclusion(content, keyword)

        # Distribution across sections
        section_distribution = []
        for i, section in enumerate(sections):
            count = section['content'].lower().count(keyword_lower)
            section_distribution.append({
                'section': i + 1,
                'heading': section['heading'][:50] + '...' if len(section['heading']) > 50 else section['heading'],
                'count': count
            })

        # Determine status
        if density < target_density * 0.5:
            status = 'too_low'
        elif density > target_density * 2:
            status = 'too_high'
        else:
            status = 'optimal'

        return {
            'count': exact_count,
            'density': round(density, 2),
            'target_density': target_density,
            'status': status,
            'placements': {
                'h1': h1_count > 0,
                'h2': h2_count,
                'h3': h3_count,
                'first_100_words': first_100,
                'conclusion': in_conclusion
            },
            'section_distribution': section_distribution
        }

    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract sections based on H2 headings"""
        sections = []
        lines = content.split('\n')
        current_section = {'heading': 'Introduction', 'content': ''}

        for line in lines:
            if line.startswith('## '):
                if current_section['content']:
                    sections.append(current_section)
                current_section = {'heading': line.replace('## ', '').strip(), 'content': ''}
            else:
                current_section['content'] += line + '\n'

        if current_section['content']:
            sections.append(current_section)

        return sections

    def _count_in_headings(self, content: str, keyword: str, level: str) -> int:
        """Count keyword occurrences in headings of specific level"""
        pattern = rf'^{"#" * int(level[1:])} .*$'
        headings = re.findall(pattern, content, re.MULTILINE)
        return sum(1 for h in headings if keyword.lower() in h.lower())

    def _in_first_100_words(self, content: str, keyword: str) -> bool:
        """Check if keyword appears in first 100 words"""
        words = content.split()[:100]
        first_100 = ' '.join(words).lower()
        return keyword.lower() in first_100

    def _in_conclusion(self, content: str, keyword: str) -> bool:
        """Check if keyword appears in conclusion (last 10% of content)"""
        words = content.split()
        conclusion_start = int(len(words) * 0.9)
        conclusion = ' '.join(words[conclusion_start:]).lower()
        return keyword.lower() in conclusion

    def _detect_keyword_stuffing(
        self,
        content: str,
        keyword: str,
        density: float
    ) -> Dict[str, Any]:
        """Detect potential keyword stuffing"""
        risk_level = 'none'
        warnings = []

        # Check density
        if density > 4.0:
            risk_level = 'high'
            warnings.append(f"Density {density}% is very high (target: 1-2%)")
        elif density > 3.0:
            risk_level = 'medium'
            warnings.append(f"Density {density}% is higher than recommended")

        # Check proximity (same paragraph multiple times)
        paragraphs = content.split('\n\n')
        for i, para in enumerate(paragraphs):
            count = para.lower().count(keyword.lower())
            if count > 3:
                risk_level = max(risk_level, 'medium')
                warnings.append(f"Keyword appears {count} times in paragraph {i+1}")

        return {
            'risk_level': risk_level,
            'warnings': warnings
        }

    def _find_lsi_keywords(self, content: str, primary_keyword: str) -> List[str]:
        """Find potential LSI/semantic keywords"""
        # Simple implementation - in production, use NLP libraries
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = Counter(words)

        # Filter out stop words and primary keyword
        filtered = {
            word: count for word, count in word_freq.items()
            if word not in self.stop_words and word not in primary_keyword.lower()
        }

        # Return top 10 most frequent
        return [word for word, _ in Counter(filtered).most_common(10)]

    def _generate_recommendations(
        self,
        primary_analysis: Dict,
        secondary_analysis: List[Dict],
        stuffing_risk: Dict,
        target_density: float
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Primary keyword recommendations
        if primary_analysis['status'] == 'too_low':
            recommendations.append(
                f"Increase primary keyword usage (currently {primary_analysis['count']} times, "
                f"target ~{int(target_density * primary_analysis.get('word_count', 2000) / 100)} times)"
            )
        elif primary_analysis['status'] == 'too_high':
            recommendations.append(
                f"Reduce primary keyword usage to avoid stuffing (currently {primary_analysis['density']:.1f}%)"
            )

        if not primary_analysis['placements']['h1']:
            recommendations.append("Add primary keyword to H1 heading")

        if not primary_analysis['placements']['first_100_words']:
            recommendations.append("Include primary keyword in first 100 words")

        if primary_analysis['placements']['h2'] < 2:
            recommendations.append(f"Add primary keyword to more H2 headings (currently in {primary_analysis['placements']['h2']})")

        if not primary_analysis['placements']['conclusion']:
            recommendations.append("Include primary keyword in conclusion")

        # Keyword stuffing warnings
        if stuffing_risk['risk_level'] in ['medium', 'high']:
            recommendations.extend(stuffing_risk['warnings'])

        return recommendations


# CLI interface
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: python keyword_analyzer.py <content_file> <primary_keyword> [secondary_keywords...]")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        content = f.read()

    primary = sys.argv[2]
    secondary = sys.argv[3:] if len(sys.argv) > 3 else []

    analyzer = KeywordAnalyzer()
    result = analyzer.analyze(content, primary, secondary)

    print(f"\n=== Keyword Analysis ===")
    print(f"Primary Keyword: {result['primary_keyword']['keyword']}")
    print(f"Word Count: {result['word_count']}")
    print(f"Density: {result['primary_keyword']['density']}%")
    print(f"Status: {result['primary_keyword']['status']}")
    print(f"\nPlacements:")
    print(f"  H1: {'✓' if result['primary_keyword']['placements']['h1'] else '✗'}")
    print(f"  First 100 words: {'✓' if result['primary_keyword']['placements']['first_100_words'] else '✗'}")
    print(f"  H2 headings: {result['primary_keyword']['placements']['h2']}")
    print(f"  Conclusion: {'✓' if result['primary_keyword']['placements']['conclusion'] else '✗'}")
    print(f"\nStuffing Risk: {result['keyword_stuffing']['risk_level']}")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")
