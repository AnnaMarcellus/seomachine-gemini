"""
Readability Scorer

Calculates readability metrics including Flesch Reading Ease, grade levels,
and provides recommendations for improving content accessibility.
"""

import re
import math
from typing import Dict, List, Any


class ReadabilityScorer:
    """Scores content readability using multiple metrics"""

    def __init__(self):
        self.syllable_cache = {}

    def score(self, content: str) -> Dict[str, Any]:
        """
        Calculate comprehensive readability scores

        Args:
            content: Article content to analyze

        Returns:
            Dict with readability metrics and recommendations
        """
        # Clean content
        clean_text = self._clean_text(content)

        # Basic counts
        sentences = self._split_sentences(clean_text)
        words = clean_text.split()
        syllables = sum(self._count_syllables(word) for word in words)

        sentence_count = len(sentences)
        word_count = len(words)

        if sentence_count == 0 or word_count == 0:
            return {
                'error': 'Insufficient content to analyze',
                'flesch_score': 0,
                'grade_level': 0,
                'reading_time_minutes': 0
            }

        # Calculate metrics
        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = syllables / word_count

        # Flesch Reading Ease
        flesch_score = self._flesch_reading_ease(
            avg_sentence_length,
            avg_syllables_per_word
        )

        # Flesch-Kincaid Grade Level
        fk_grade = self._flesch_kincaid_grade(
            avg_sentence_length,
            avg_syllables_per_word
        )

        # Additional metrics
        gunning_fog = self._gunning_fog_index(clean_text)
        smog = self._smog_index(sentences)
        coleman_liau = self._coleman_liau_index(clean_text, words)

        # Reading time (average 200 WPM)
        reading_time = math.ceil(word_count / 200)

        # Complexity analysis
        complex_words = [w for w in words if self._count_syllables(w) > 2]
        complex_word_pct = (len(complex_words) / word_count) * 100

        # Sentence variety
        sentence_lengths = [len(s.split()) for s in sentences]
        length_variance = self._calculate_variance(sentence_lengths)

        return {
            'flesch_score': round(flesch_score, 1),
            'flesch_interpretation': self._interpret_flesch(flesch_score),
            'grade_level': round(fk_grade, 1),
            'gunning_fog_index': round(gunning_fog, 1),
            'smog_index': round(smog, 1),
            'coleman_liau_index': round(coleman_liau, 1),
            'reading_time_minutes': reading_time,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'complex_word_percentage': round(complex_word_pct, 1),
            'sentence_length_variance': round(length_variance, 1),
            'recommendations': self._generate_recommendations(
                flesch_score,
                fk_grade,
                avg_sentence_length,
                complex_word_pct,
                length_variance
            )
        }

    def _clean_text(self, text: str) -> str:
        """Remove markdown and clean text for analysis"""
        # Remove markdown
        text = re.sub(r'[#*\[\]()|`]', '', text)
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 5]

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower().strip('.,!?;:"()[]')

        if word in self.syllable_cache:
            return self.syllable_cache[word]

        # Handle silent e
        if word.endswith('e'):
            word = word[:-1]

        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel

        # Ensure at least 1 syllable
        syllable_count = max(1, syllable_count)

        self.syllable_cache[word] = syllable_count
        return syllable_count

    def _flesch_reading_ease(self, avg_sentence_length: float, avg_syllables_per_word: float) -> float:
        """Calculate Flesch Reading Ease score"""
        # Formula: 206.835 - (1.015 × ASL) - (84.6 × ASW)
        return 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)

    def _flesch_kincaid_grade(self, avg_sentence_length: float, avg_syllables_per_word: float) -> float:
        """Calculate Flesch-Kincaid Grade Level"""
        # Formula: (0.39 × ASL) + (11.8 × ASW) - 15.59
        return (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59

    def _gunning_fog_index(self, text: str) -> float:
        """Calculate Gunning Fog Index"""
        words = text.split()
        sentences = self._split_sentences(text)

        if not sentences:
            return 0

        complex_words = [w for w in words if self._count_syllables(w) > 2]
        complex_word_pct = (len(complex_words) / len(words)) * 100

        avg_sentence_length = len(words) / len(sentences)

        # Formula: 0.4 × (ASL + percentage of complex words)
        return 0.4 * (avg_sentence_length + complex_word_pct)

    def _smog_index(self, sentences: List[str]) -> float:
        """Calculate SMOG Index"""
        if len(sentences) < 3:
            return 0

        # Use last 30 sentences or all if less
        sample_sentences = sentences[-30:] if len(sentences) >= 30 else sentences

        polysyllables = 0
        for sentence in sample_sentences:
            words = sentence.split()
            polysyllables += sum(1 for w in words if self._count_syllables(w) > 2)

        # Formula: 1.043 × √(polysyllables × 30 / sentences) + 3.1291
        import math
        return 1.043 * math.sqrt(polysyllables * 30 / len(sample_sentences)) + 3.1291

    def _coleman_liau_index(self, text: str, words: List[str]) -> float:
        """Calculate Coleman-Liau Index"""
        sentences = self._split_sentences(text)
        if not sentences:
            return 0

        # Count letters
        letters = sum(c.isalpha() for c in text)
        word_count = len(words)
        sentence_count = len(sentences)

        L = (letters / word_count) * 100 if word_count > 0 else 0
        S = (sentence_count / word_count) * 100 if word_count > 0 else 0

        # Formula: 0.0588L - 0.296S - 15.8
        return 0.0588 * L - 0.296 * S - 15.8

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance in a list of values"""
        if len(values) < 2:
            return 0

        mean = sum(values) / len(values)
        squared_diffs = [(x - mean) ** 2 for x in values]
        return sum(squared_diffs) / len(squared_diffs)

    def _interpret_flesch(self, score: float) -> str:
        """Interpret Flesch Reading Ease score"""
        if score >= 90:
            return "Very Easy (5th grade)"
        elif score >= 80:
            return "Easy (6th grade)"
        elif score >= 70:
            return "Fairly Easy (7th grade)"
        elif score >= 60:
            return "Standard (8th-9th grade)"
        elif score >= 50:
            return "Fairly Difficult (10th-12th grade)"
        elif score >= 30:
            return "Difficult (College level)"
        else:
            return "Very Difficult (College graduate)"

    def _generate_recommendations(
        self,
        flesch_score: float,
        grade_level: float,
        avg_sentence_length: float,
        complex_word_pct: float,
        sentence_variance: float
    ) -> List[str]:
        """Generate readability improvement recommendations"""
        recommendations = []

        # Flesch score recommendations
        if flesch_score < 50:
            recommendations.append(
                f"Flesch score ({flesch_score:.1f}) is quite difficult. "
                "Consider simplifying vocabulary and shortening sentences."
            )
        elif flesch_score > 80:
            recommendations.append(
                f"Flesch score ({flesch_score:.1f}) is very easy. "
                "Content may be too simple for professional audiences."
            )

        # Grade level
        if grade_level > 12:
            recommendations.append(
                f"Grade level ({grade_level:.1f}) is college-level. "
                "Consider simplifying for broader audience."
            )
        elif grade_level < 8:
            recommendations.append(
                f"Grade level ({grade_level:.1f}) is below 8th grade. "
                "May be too simple for B2B content."
            )

        # Sentence length
        if avg_sentence_length > 20:
            recommendations.append(
                f"Average sentence length ({avg_sentence_length:.1f} words) is high. "
                "Aim for 15-20 words per sentence."
            )

        # Complex words
        if complex_word_pct > 15:
            recommendations.append(
                f"Complex words ({complex_word_pct:.1f}%) are high. "
                "Consider using simpler alternatives."
            )

        # Sentence variety
        if sentence_variance < 10:
            recommendations.append(
                "Sentence lengths are too uniform. Vary sentence structure for better flow."
            )

        return recommendations


# CLI interface
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python readability_scorer.py <content_file>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        content = f.read()

    scorer = ReadabilityScorer()
    result = scorer.score(content)

    print(f"\n=== Readability Analysis ===")
    print(f"Word Count: {result['word_count']}")
    print(f"Sentence Count: {result['sentence_count']}")
    print(f"Reading Time: ~{result['reading_time_minutes']} minutes")
    print(f"\n--- Scores ---")
    print(f"Flesch Reading Ease: {result['flesch_score']} ({result['flesch_interpretation']})")
    print(f"Grade Level (FK): {result['grade_level']}")
    print(f"Gunning Fog Index: {result['gunning_fog_index']}")
    print(f"SMOG Index: {result['smog_index']}")
    print(f"Coleman-Liau Index: {result['coleman_liau_index']}")
    print(f"\n--- Details ---")
    print(f"Avg Sentence Length: {result['avg_sentence_length']} words")
    print(f"Avg Syllables/Word: {result['avg_syllables_per_word']}")
    print(f"Complex Words: {result['complex_word_percentage']}%")

    if result['recommendations']:
        print(f"\n--- Recommendations ---")
        for rec in result['recommendations']:
            print(f"  • {rec}")
