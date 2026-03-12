"""
Search Intent Analyzer

Classifies search intent for keywords into categories:
- Informational: Seeking information
- Navigational: Looking for a specific site/page
- Commercial: Researching before purchase
- Transactional: Ready to buy/act
"""

from typing import Dict, List, Any
from enum import Enum


class SearchIntent(Enum):
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"


class SearchIntentAnalyzer:
    """Analyzes search intent for keywords"""

    def __init__(self):
        # Intent-indicating keywords
        self.intent_keywords = {
            'informational': [
                'what', 'how', 'why', 'when', 'where', 'who',
                'guide', 'tutorial', 'learn', 'understand',
                'explained', 'meaning', 'definition', 'examples',
                'tips', 'ideas', 'ways to', 'best practices',
                'vs', 'versus', 'difference between', 'comparison'
            ],
            'navigational': [
                'login', 'sign in', 'sign up', 'register',
                'website', 'homepage', 'official',
                'app', 'download', 'portal',
                'contact', 'support', 'help center',
                'facebook', 'twitter', 'instagram', 'linkedin'
            ],
            'commercial': [
                'best', 'top', 'review', 'reviews',
                'compare', 'comparison', 'vs', 'versus',
                'alternative', 'alternatives',
                'cheap', 'affordable', 'premium',
                'features', 'pricing', 'plans',
                'which', 'should i', 'worth it'
            ],
            'transactional': [
                'buy', 'purchase', 'order', 'shop',
                'discount', 'deal', 'coupon', 'sale',
                'free shipping', 'price', 'cost',
                'download', 'get', 'install',
                'trial', 'demo', 'free', 'subscription'
            ]
        }

    def analyze(self, keyword: str) -> Dict[str, Any]:
        """
        Analyze search intent for a keyword

        Args:
            keyword: Search query/keyword to analyze

        Returns:
            Dict with intent classification and confidence scores
        """
        keyword_lower = keyword.lower()
        scores = self._calculate_intent_scores(keyword_lower)

        # Determine primary and secondary intents
        primary_intent = max(scores, key=scores.get)
        secondary_intent = max(
            {k: v for k, v in scores.items() if k != primary_intent},
            key=scores.get
        )

        # Calculate confidence
        total_score = sum(scores.values())
        primary_confidence = scores[primary_intent] / total_score if total_score > 0 else 0

        # Content recommendations based on intent
        recommendations = self._get_content_recommendations(
            SearchIntent(primary_intent),
            scores
        )

        return {
            'keyword': keyword,
            'primary_intent': {
                'type': primary_intent,
                'confidence': round(primary_confidence * 100, 1),
                'score': scores[primary_intent]
            },
            'secondary_intent': {
                'type': secondary_intent,
                'score': scores[secondary_intent]
            },
            'all_scores': scores,
            'content_recommendations': recommendations,
            'serp_features_to_target': self._get_serp_features(SearchIntent(primary_intent)),
            'content_type_suggestions': self._get_content_types(SearchIntent(primary_intent))
        }

    def _calculate_intent_scores(self, keyword: str) -> Dict[str, int]:
        """Calculate intent scores based on keyword matching"""
        scores = {
            'informational': 0,
            'navigational': 0,
            'commercial': 0,
            'transactional': 0
        }

        # Check for intent keywords
        for intent_type, keywords in self.intent_keywords.items():
            for intent_keyword in keywords:
                if intent_keyword in keyword:
                    scores[intent_type] += 2  # Strong match
                elif any(word in keyword for word in intent_keyword.split()):
                    scores[intent_type] += 1  # Partial match

        # Question words strongly indicate informational
        question_starters = ['what', 'how', 'why', 'when', 'where', 'who', 'is', 'are', 'can', 'does']
        if any(keyword.startswith(q) for q in question_starters):
            scores['informational'] += 3

        # Brand/domain patterns indicate navigational
        if any(ext in keyword for ext in ['.com', '.org', '.net', 'website', 'official']):
            scores['navigational'] += 3

        # Price/buy patterns indicate transactional
        if any(word in keyword for word in ['price', 'cost', 'buy', 'order', 'purchase']):
            scores['transactional'] += 3

        # Comparison patterns indicate commercial
        if any(word in keyword for word in ['vs', 'versus', 'compare', 'best', 'top', 'review']):
            scores['commercial'] += 3

        # Ensure minimum scores for balance
        for key in scores:
            if scores[key] == 0:
                scores[key] = 1

        return scores

    def _get_content_recommendations(
        self,
        intent: SearchIntent,
        scores: Dict[str, int]
    ) -> List[str]:
        """Get content recommendations based on intent"""
        recommendations = []

        if intent == SearchIntent.INFORMATIONAL:
            recommendations = [
                "Focus on educating and explaining",
                "Include definitions and examples",
                "Use step-by-step instructions",
                "Add FAQ section for related questions",
                "Include statistics and research data"
            ]
        elif intent == SearchIntent.NAVIGATIONAL:
            recommendations = [
                "Ensure clear branding",
                "Optimize for branded keywords",
                "Include direct links to key pages",
                "Make navigation prominent",
                "Focus on user experience"
            ]
        elif intent == SearchIntent.COMMERCIAL:
            recommendations = [
                "Include comparison tables",
                "Add feature breakdowns",
                "Include pros and cons",
                "Add customer reviews/testimonials",
                "Create buyer's guide format"
            ]
        elif intent == SearchIntent.TRANSACTIONAL:
            recommendations = [
                "Include clear CTAs",
                "Add pricing information",
                "Include trust signals",
                "Offer guarantees/risk reversal",
                "Make purchase process clear"
            ]

        # Add secondary intent suggestions
        secondary = max(
            {k: v for k, v in scores.items() if k != intent.value},
            key=scores.get
        )

        if scores[secondary] > scores[intent.value] * 0.7:
            recommendations.append(
                f"Also address {secondary} intent as secondary focus"
            )

        return recommendations

    def _get_serp_features(self, intent: SearchIntent) -> List[str]:
        """Get SERP features to target based on intent"""
        features = {
            SearchIntent.INFORMATIONAL: [
                'Featured Snippet',
                'People Also Ask',
                'Knowledge Panel',
                'Video Carousel',
                'Images'
            ],
            SearchIntent.NAVIGATIONAL: [
                'Site Links',
                'Knowledge Panel',
                'Local Pack (if applicable)'
            ],
            SearchIntent.COMMERCIAL: [
                'Featured Snippet',
                'People Also Ask',
                'Shopping Results',
                'Rich Results'
            ],
            SearchIntent.TRANSACTIONAL: [
                'Shopping Ads',
                'Local Pack',
                'Featured Snippet',
                'Rich Results'
            ]
        }

        return features.get(intent, [])

    def _get_content_types(self, intent: SearchIntent) -> List[str]:
        """Get suggested content types based on intent"""
        types = {
            SearchIntent.INFORMATIONAL: [
                'How-to Guide',
                'Tutorial',
                'Explainer Article',
                'FAQ Page',
                'Definition/Guide'
            ],
            SearchIntent.NAVIGATIONAL: [
                'Homepage',
                'Landing Page',
                'Brand Page',
                'Contact Page'
            ],
            SearchIntent.COMMERCIAL: [
                'Product Comparison',
                'Buyer\'s Guide',
                'Review Roundup',
                'Feature Analysis'
            ],
            SearchIntent.TRANSACTIONAL: [
                'Product Page',
                'Checkout Page',
                'Pricing Page',
                'Free Trial Page'
            ]
        }

        return types.get(intent, [])

    def analyze_compound_intent(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze intent for multiple keywords (topic cluster)"""
        results = [self.analyze(kw) for kw in keywords]

        # Aggregate intent distribution
        intent_counts = {
            'informational': 0,
            'navigational': 0,
            'commercial': 0,
            'transactional': 0
        }

        for result in results:
            intent_counts[result['primary_intent']['type']] += 1

        total = len(keywords)
        distribution = {
            k: round(v / total * 100, 1) for k, v in intent_counts.items()
        }

        # Determine cluster strategy
        dominant_intent = max(intent_counts, key=intent_counts.get)

        return {
            'keywords_analyzed': total,
            'intent_distribution': distribution,
            'dominant_intent': dominant_intent,
            'cluster_strategy': self._get_cluster_strategy(dominant_intent),
            'individual_results': results
        }

    def _get_cluster_strategy(self, dominant_intent: str) -> str:
        """Get content strategy for intent cluster"""
        strategies = {
            'informational': 'Create comprehensive educational content hub with pillar page and supporting articles',
            'navigational': 'Optimize branded search presence and improve site structure',
            'commercial': 'Build comparison content and buyer-focused resources',
            'transactional': 'Optimize product pages and conversion funnels'
        }
        return strategies.get(dominant_intent, 'Create mixed content strategy')


# CLI interface
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python search_intent_analyzer.py <keyword>")
        print("       python search_intent_analyzer.py --batch <keyword1> <keyword2> ...")
        sys.exit(1)

    analyzer = SearchIntentAnalyzer()

    if sys.argv[1] == '--batch':
        keywords = sys.argv[2:]
        result = analyzer.analyze_compound_intent(keywords)

        print(f"\n=== Compound Intent Analysis ===")
        print(f"Keywords Analyzed: {result['keywords_analyzed']}")
        print(f"\nIntent Distribution:")
        for intent, pct in result['intent_distribution'].items():
            print(f"  {intent.capitalize()}: {pct}%")
        print(f"\nDominant Intent: {result['dominant_intent']}")
        print(f"Strategy: {result['cluster_strategy']}")
    else:
        keyword = sys.argv[1]
        result = analyzer.analyze(keyword)

        print(f"\n=== Search Intent Analysis ===")
        print(f"Keyword: {result['keyword']}")
        print(f"\nPrimary Intent: {result['primary_intent']['type'].upper()}")
        print(f"Confidence: {result['primary_intent']['confidence']}%")
        print(f"\nSecondary Intent: {result['secondary_intent']['type']}")
        print(f"\nAll Scores:")
        for intent, score in result['all_scores'].items():
            print(f"  {intent.capitalize()}: {score}")
        print(f"\nContent Recommendations:")
        for rec in result['content_recommendations']:
            print(f"  • {rec}")
        print(f"\nTarget SERP Features:")
        for feature in result['serp_features_to_target']:
            print(f"  • {feature}")
        print(f"\nSuggested Content Types:")
        for ctype in result['content_type_suggestions']:
            print(f"  • {ctype}")
