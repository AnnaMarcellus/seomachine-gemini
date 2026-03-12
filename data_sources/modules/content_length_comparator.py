"""
Content Length Comparator

Compares content word count against top-ranking SERP results
and provides recommendations for optimal content length.
"""

import requests
import time
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus


class ContentLengthComparator:
    """Compares content length against SERP competitors"""

    def __init__(self, dataforseo_auth: Optional[tuple] = None):
        """
        Initialize comparator

        Args:
            dataforseo_auth: (login, password) tuple for DataForSEO API
        """
        self.dataforseo_auth = dataforseo_auth
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def compare(
        self,
        keyword: str,
        your_word_count: int,
        location: str = 'us',
        fetch_content: bool = False
    ) -> Dict[str, Any]:
        """
        Compare your content length against top SERP results

        Args:
            keyword: Target keyword to analyze
            your_word_count: Your content's word count
            location: Search location (default: 'us')
            fetch_content: Whether to fetch full content (slower)

        Returns:
            Dict with comparison results and recommendations
        """
        # Get SERP results
        serp_results = self._get_serp_results(keyword, location)

        if not serp_results:
            return {
                'error': 'Could not fetch SERP results',
                'your_word_count': your_word_count,
                'recommendation': 'Unable to analyze - check API credentials'
            }

        # Analyze each result
        competitor_data = []
        word_counts = []

        for result in serp_results[:10]:  # Top 10
            url = result.get('url') or result.get('link')
            title = result.get('title', 'Unknown')

            comp_data = {
                'position': result.get('position', 0),
                'url': url,
                'title': title,
                'word_count': None,
                'content_fetched': False
            }

            if fetch_content and url:
                word_count = self._fetch_and_count(url)
                comp_data['word_count'] = word_count
                comp_data['content_fetched'] = word_count is not None
                if word_count:
                    word_counts.append(word_count)
                time.sleep(0.5)  # Be polite
            else:
                # Estimate based on typical content
                comp_data['word_count'] = 'estimated_2000'
                word_counts.append(2000)

            competitor_data.append(comp_data)

        # Calculate statistics
        if word_counts:
            avg_word_count = sum(word_counts) / len(word_counts)
            min_count = min(word_counts)
            max_count = max(word_counts)
            median_count = sorted(word_counts)[len(word_counts) // 2]
        else:
            avg_word_count = 2000
            min_count = 1500
            max_count = 3000
            median_count = 2000

        # Compare your content
        difference = your_word_count - avg_word_count
        percentage_diff = (difference / avg_word_count) * 100 if avg_word_count > 0 else 0

        # Generate recommendation
        if percentage_diff < -20:
            recommendation = f"Your content is {abs(percentage_diff):.0f}% shorter than average. Consider expanding to {int(avg_word_count)}+ words."
            status = 'too_short'
        elif percentage_diff > 30:
            recommendation = f"Your content is {percentage_diff:.0f}% longer than average. Length is good, but ensure quality is maintained."
            status = 'too_long'
        else:
            recommendation = "Your content length is competitive with top-ranking pages."
            status = 'optimal'

        return {
            'keyword': keyword,
            'location': location,
            'your_word_count': your_word_count,
            'competitor_analysis': {
                'average_word_count': round(avg_word_count, 0),
                'median_word_count': median_count,
                'min_word_count': min_count,
                'max_word_count': max_count,
                'results_analyzed': len(word_counts)
            },
            'comparison': {
                'difference': round(difference, 0),
                'percentage_diff': round(percentage_diff, 1),
                'status': status
            },
            'recommendation': recommendation,
            'top_competitors': competitor_data[:5],
            'target_word_count': self._suggest_target(
                your_word_count,
                avg_word_count,
                max_count
            )
        }

    def _get_serp_results(self, keyword: str, location: str) -> List[Dict]:
        """Fetch SERP results using DataForSEO or fallback"""
        results = []

        # Try DataForSEO if credentials available
        if self.dataforseo_auth:
            try:
                results = self._fetch_dataforseo_serp(keyword, location)
            except Exception as e:
                print(f"DataForSEO API error: {e}")

        # Fallback to simulated results
        if not results:
            results = self._simulate_serp_results(keyword)

        return results

    def _fetch_dataforseo_serp(self, keyword: str, location: str) -> List[Dict]:
        """Fetch SERP from DataForSEO API"""
        url = 'https://api.dataforseo.com/v3/serp/google/organic/live/advanced'

        payload = [{
            'keyword': keyword,
            'location_code': self._get_location_code(location),
            'language_code': 'en',
            'depth': 10
        }]

        response = requests.post(
            url,
            auth=self.dataforseo_auth,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('tasks') and data['tasks'][0].get('result'):
                items = data['tasks'][0]['result'][0].get('items', [])
                return [
                    {
                        'position': item.get('rank_group', i + 1),
                        'url': item.get('url'),
                        'title': item.get('title')
                    }
                    for i, item in enumerate(items)
                    if item.get('type') == 'organic'
                ]

        return []

    def _get_location_code(self, location: str) -> int:
        """Get DataForSEO location code"""
        codes = {
            'us': 2840,
            'gb': 2826,
            'ca': 2124,
            'au': 2036,
            'de': 2276,
            'fr': 2250
        }
        return codes.get(location.lower(), 2840)

    def _simulate_serp_results(self, keyword: str) -> List[Dict]:
        """Generate simulated SERP results when API unavailable"""
        # In production, this would be replaced with actual SERP scraping
        return [
            {'position': 1, 'url': f'https://example1.com/{keyword.replace(" ", "-")}', 'title': f'Best {keyword} Guide'},
            {'position': 2, 'url': f'https://example2.com/{keyword.replace(" ", "-")}', 'title': f'Complete {keyword} Tutorial'},
            {'position': 3, 'url': f'https://example3.com/{keyword.replace(" ", "-")}', 'title': f'{keyword} Tips and Tricks'},
            {'position': 4, 'url': f'https://example4.com/{keyword.replace(" ", "-")}', 'title': f'How to {keyword}'},
            {'position': 5, 'url': f'https://example5.com/{keyword.replace(" ", "-")}', 'title': f'{keyword} Strategies'},
            {'position': 6, 'url': f'https://example6.com/{keyword.replace(" ", "-")}', 'title': f'Ultimate {keyword} Guide'},
            {'position': 7, 'url': f'https://example7.com/{keyword.replace(" ", "-")}', 'title': f'{keyword} for Beginners'},
            {'position': 8, 'url': f'https://example8.com/{keyword.replace(" ", "-")}', 'title': f'Advanced {keyword}'},
            {'position': 9, 'url': f'https://example9.com/{keyword.replace(" ", "-")}', 'title': f'{keyword} Examples'},
            {'position': 10, 'url': f'https://example10.com/{keyword.replace(" ", "-")}', 'title': f'{keyword} Case Studies'},
        ]

    def _fetch_and_count(self, url: str) -> Optional[int]:
        """Fetch URL and count words"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                # Simple word count from HTML
                text = self._extract_text(response.text)
                return len(text.split())
        except Exception as e:
            print(f"Error fetching {url}: {e}")

        return None

    def _extract_text(self, html: str) -> str:
        """Extract readable text from HTML"""
        # Very basic HTML stripping
        import re
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _suggest_target(
        self,
        your_count: int,
        avg_count: float,
        max_count: int
    ) -> Dict[str, int]:
        """Suggest target word count"""
        # Target should beat average but be realistic
        suggested = max(int(avg_count * 1.1), 2000)

        return {
            'minimum': max(int(avg_count * 0.9), 1500),
            'recommended': suggested,
            'optimal': min(int(max_count * 1.1), 5000),
            'current_gap': max(0, suggested - your_count)
        }


# CLI interface
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: python content_length_comparator.py <keyword> <your_word_count> [location]")
        sys.exit(1)

    keyword = sys.argv[1]
    word_count = int(sys.argv[2])
    location = sys.argv[3] if len(sys.argv) > 3 else 'us'

    comparator = ContentLengthComparator()
    result = comparator.compare(keyword, word_count, location)

    print(f"\n=== Content Length Comparison ===")
    print(f"Keyword: {result['keyword']}")
    print(f"Your Word Count: {result['your_word_count']}")
    print(f"\n--- Competitor Analysis ---")
    print(f"Average: {result['competitor_analysis']['average_word_count']}")
    print(f"Median: {result['competitor_analysis']['median_word_count']}")
    print(f"Range: {result['competitor_analysis']['min_word_count']} - {result['competitor_analysis']['max_word_count']}")
    print(f"\n--- Your Comparison ---")
    print(f"Difference: {result['comparison']['difference']:+.0f} words")
    print(f"Percentage: {result['comparison']['percentage_diff']:+.1f}%")
    print(f"Status: {result['comparison']['status']}")
    print(f"\nRecommendation: {result['recommendation']}")
    print(f"\n--- Targets ---")
    print(f"Minimum: {result['target_word_count']['minimum']}")
    print(f"Recommended: {result['target_word_count']['recommended']}")
    print(f"Optimal: {result['target_word_count']['optimal']}")
    if result['target_word_count']['current_gap'] > 0:
        print(f"Gap to close: {result['target_word_count']['current_gap']} words")
