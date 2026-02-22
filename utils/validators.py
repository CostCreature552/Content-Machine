"""
SEO and readability validation utilities.
Provides scoring for keyword density, readability, and heading structure.
"""

import re
from typing import Dict, List, Optional

try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False


class SEOValidator:
    """Validates and scores blog content for SEO and readability."""

    def __init__(self, content: str, keywords: Optional[List[str]] = None):
        """
        Initialize the validator with content and optional keywords.

        Args:
            content: The blog article content in Markdown format.
            keywords: List of target keywords to check density for.
        """
        self.content = content
        self.keywords = keywords or []
        self.plain_text = self._strip_markdown(content)
        self.word_count = len(self.plain_text.split())

    def _strip_markdown(self, text: str) -> str:
        """Remove Markdown formatting to get plain text."""
        # Remove headers
        text = re.sub(r"#{1,6}\s*", "", text)
        # Remove bold/italic
        text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
        text = re.sub(r"_{1,3}(.*?)_{1,3}", r"\1", text)
        # Remove links
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        # Remove images
        text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"\1", text)
        # Remove code blocks
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # Remove horizontal rules
        text = re.sub(r"---+", "", text)
        # Remove extra whitespace
        text = re.sub(r"\n+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def get_word_count(self) -> int:
        """Return the word count of the content."""
        return self.word_count

    def get_keyword_density(self) -> Dict[str, float]:
        """
        Calculate keyword density for each target keyword.

        Returns:
            Dict mapping keyword to its density percentage.
        """
        densities = {}
        lower_text = self.plain_text.lower()

        for keyword in self.keywords:
            keyword_lower = keyword.lower()
            count = lower_text.count(keyword_lower)
            density = (count / self.word_count * 100) if self.word_count > 0 else 0
            densities[keyword] = round(density, 2)

        return densities

    def check_heading_structure(self) -> Dict[str, any]:
        """
        Validate the heading structure of the content.

        Returns:
            Dict with heading counts and validation status.
        """
        h1_matches = re.findall(r"^# [^\n]+", self.content, re.MULTILINE)
        h2_matches = re.findall(r"^## [^\n]+", self.content, re.MULTILINE)
        h3_matches = re.findall(r"^### [^\n]+", self.content, re.MULTILINE)

        h1_count = len(h1_matches)
        h2_count = len(h2_matches)
        h3_count = len(h3_matches)

        issues = []
        if h1_count == 0:
            issues.append("Missing H1 heading (title)")
        elif h1_count > 1:
            issues.append(f"Multiple H1 headings found ({h1_count}). Should have exactly 1.")
        if h2_count < 3:
            issues.append(f"Only {h2_count} H2 headings. Recommend 3-5 for good structure.")
        elif h2_count > 6:
            issues.append(f"Too many H2 headings ({h2_count}). Consider consolidating.")

        return {
            "h1_count": h1_count,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "h1_headings": h1_matches,
            "h2_headings": h2_matches,
            "is_valid": h1_count == 1 and 3 <= h2_count <= 6,
            "issues": issues,
        }

    def get_readability_score(self) -> Dict[str, any]:
        """
        Calculate readability metrics for the content.

        Returns:
            Dict with Flesch Reading Ease score and interpretation.
        """
        if not TEXTSTAT_AVAILABLE:
            return {
                "flesch_reading_ease": None,
                "grade_level": None,
                "interpretation": "textstat library not available",
                "is_target_range": None,
            }

        flesch_score = textstat.flesch_reading_ease(self.plain_text)
        grade_level = textstat.flesch_kincaid_grade(self.plain_text)

        # Interpret the score
        if flesch_score >= 90:
            interpretation = "Very Easy — 5th grade level"
        elif flesch_score >= 80:
            interpretation = "Easy — 6th grade level"
        elif flesch_score >= 70:
            interpretation = "Fairly Easy — 7th grade level"
        elif flesch_score >= 60:
            interpretation = "Standard — 8th-9th grade level (Target ✓)"
        elif flesch_score >= 50:
            interpretation = "Fairly Difficult — 10th-12th grade level"
        elif flesch_score >= 30:
            interpretation = "Difficult — College level"
        else:
            interpretation = "Very Difficult — College graduate level"

        return {
            "flesch_reading_ease": round(flesch_score, 1),
            "grade_level": round(grade_level, 1),
            "interpretation": interpretation,
            "is_target_range": 60 <= flesch_score <= 70,
        }

    def get_avg_sentence_length(self) -> float:
        """Calculate average sentence length in words."""
        sentences = re.split(r"[.!?]+", self.plain_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return 0
        total_words = sum(len(s.split()) for s in sentences)
        return round(total_words / len(sentences), 1)

    def get_full_report(self) -> Dict[str, any]:
        """
        Generate a comprehensive SEO and readability report.

        Returns:
            Dict with all validation metrics.
        """
        keyword_density = self.get_keyword_density()
        heading_structure = self.check_heading_structure()
        readability = self.get_readability_score()
        avg_sentence_length = self.get_avg_sentence_length()

        # Overall SEO score (0-100)
        score = 100
        issues = []

        # Word count scoring
        if self.word_count < 700:
            score -= 15
            issues.append(f"Word count ({self.word_count}) is below 700 minimum")
        elif self.word_count > 1000:
            score -= 5
            issues.append(f"Word count ({self.word_count}) exceeds 1000 target")

        # Keyword density scoring
        for kw, density in keyword_density.items():
            if density < 0.5:
                score -= 10
                issues.append(f"Keyword '{kw}' density too low ({density}%)")
            elif density > 3.0:
                score -= 10
                issues.append(f"Keyword '{kw}' density too high ({density}%) — keyword stuffing risk")

        # Heading structure scoring
        if not heading_structure["is_valid"]:
            score -= 15
            issues.extend(heading_structure["issues"])

        # Readability scoring
        if readability["flesch_reading_ease"] is not None:
            if readability["flesch_reading_ease"] < 50:
                score -= 15
                issues.append("Content is too difficult to read")
            elif readability["flesch_reading_ease"] > 80:
                score -= 5
                issues.append("Content may be too simplistic")

        # Sentence length scoring
        if avg_sentence_length > 25:
            score -= 10
            issues.append(f"Average sentence length ({avg_sentence_length} words) is too long")

        score = max(0, score)

        return {
            "overall_score": score,
            "word_count": self.word_count,
            "keyword_density": keyword_density,
            "heading_structure": heading_structure,
            "readability": readability,
            "avg_sentence_length": avg_sentence_length,
            "issues": issues,
            "estimated_reading_time": f"{max(1, round(self.word_count / 200))} min read",
        }
