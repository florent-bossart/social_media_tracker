#!/usr/bin/env python3
"""
Japanese Music Trends Analysis Pipeline - Summarization Module (Stage 4)

This module generates natural language insights and summaries from trend detection results.
Uses Llama 3.1-8B via Ollama to create comprehensive trend reports.

"""

import json
import csv
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SummaryConfig:
    """Configuration for trend summarization"""
    ollama_url: str = "http://localhost:11434"
    model_name: str = "llama3.1:8b"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 60
    include_recommendations: bool = True
    include_market_insights: bool = True
    language_style: str = "professional"  # professional, casual, academic
    output_format: str = "markdown"  # markdown, html, plain

@dataclass
class TrendSummary:
    """Comprehensive trend summary data structure"""
    executive_summary: str
    key_findings: List[str]
    artist_insights: List[str]
    genre_insights: List[str]
    sentiment_analysis: str
    platform_analysis: str
    recommendations: List[str]
    market_implications: List[str]
    timestamp: str
    data_period: str
    confidence_score: float

class TrendSummarizer:
    """
    Generates natural language summaries and insights from trend detection results
    """

    def __init__(self, config: Optional[SummaryConfig] = None, ollama_host: Optional[str] = None):
        self.config = config or SummaryConfig()
        if ollama_host:
            self.config.ollama_url = ollama_host # Override ollama_url from config if host is provided
        self.ollama_available = self._check_ollama_availability()

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama service is available"""
        try:
            # Use self.config.ollama_url which might have been overridden
            response = requests.get(f"{self.config.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [model['name'] for model in response.json().get('models', [])]
                if self.config.model_name in models:
                    logger.info(f"Ollama service available with {self.config.model_name}")
                    return True
                else:
                    logger.warning(f"Model {self.config.model_name} not found in Ollama")
                    return False
            return False
        except Exception as e:
            logger.warning(f"Ollama service not available: {e}")
            return False

    def load_trend_data(self, trend_summary_path: str, artist_trends_path: str) -> Dict[str, Any]:
        """Load trend detection results from JSON and CSV files"""
        try:
            # Load trend summary
            with open(trend_summary_path, 'r', encoding='utf-8') as f:
                trend_summary = json.load(f)

            # Load artist trends
            artist_trends = []
            with open(artist_trends_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    artist_trends.append(row)

            return {
                'summary': trend_summary,
                'artist_trends': artist_trends,
                'loaded_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error loading trend data: {e}")
            raise

    def _query_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and get response"""
        if not self.ollama_available:
            return self._generate_fallback_summary(prompt)

        try:
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }

            response = requests.post(
                f"{self.config.ollama_url}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._generate_fallback_summary(prompt)

        except Exception as e:
            logger.error(f"Error querying Ollama: {e}")
            return self._generate_fallback_summary(prompt)

    def _generate_fallback_summary(self, prompt: str) -> str:
        """Generate basic summary when Ollama is not available"""
        return "Trend analysis summary (fallback mode): Basic trend detection completed. For detailed AI-generated insights, ensure Ollama service is running."

    def generate_executive_summary(self, trend_data: Dict[str, Any]) -> str:
        """Generate executive summary of trends"""
        summary = trend_data['summary']

        prompt = f"""
        You are an expert music industry analyst. Generate a concise executive summary of Japanese music trends based on this data:

        Total Artists Analyzed: {summary['overview']['total_artists_analyzed']}
        Total Genres Analyzed: {summary['overview']['total_genres_analyzed']}

        Top Artists: {summary.get('top_artists', [])}
        Sentiment Patterns: {summary.get('sentiment_patterns', {})}

        Write a 2-3 paragraph executive summary highlighting:
        1. Overall trend landscape
        2. Key insights about Japanese music social media engagement
        3. Notable patterns or findings

        Keep it professional and data-driven.
        """

        return self._query_ollama(prompt)

    def generate_artist_insights(self, trend_data: Dict[str, Any]) -> List[str]:
        """Generate insights about individual artists"""
        artist_trends = trend_data['artist_trends']
        insights = []

        for artist in artist_trends:
            prompt = f"""
            Analyze this Japanese music artist's social media trend data:

            Artist: {artist['entity_name']}
            Mentions: {artist['mention_count']}
            Sentiment Score: {artist['sentiment_score']}
            Trend Strength: {artist['trend_strength']}
            Platforms: {artist['platforms']}
            Engagement Level: {artist['engagement_level']}

            Generate a 2-sentence insight about this artist's trending status and what it indicates about their current popularity or momentum in Japanese music.
            """

            insight = self._query_ollama(prompt)
            if insight and len(insight) > 20:  # Basic validation
                insights.append(f"**{artist['entity_name']}**: {insight}")

        return insights

    def generate_sentiment_analysis(self, trend_data: Dict[str, Any]) -> str:
        """Analyze sentiment patterns across trends"""
        sentiment_patterns = trend_data['summary'].get('sentiment_patterns', {})

        prompt = f"""
        Analyze the sentiment patterns in Japanese music social media trends:

        Positive Trends: {sentiment_patterns.get('positive_trends', 0)}
        Negative Trends: {sentiment_patterns.get('negative_trends', 0)}
        Neutral Trends: {sentiment_patterns.get('neutral_trends', 0)}

        Provide a 2-3 sentence analysis of what these sentiment patterns reveal about the current Japanese music landscape and fan engagement.
        """

        return self._query_ollama(prompt)

    def generate_platform_analysis(self, trend_data: Dict[str, Any]) -> str:
        """Analyze platform-specific trends"""
        # Extract platform information from artist trends
        platforms = set()
        for artist in trend_data['artist_trends']:
            platform_list = artist.get('platforms', '[]')
            if isinstance(platform_list, str):
                try:
                    platform_list = eval(platform_list)  # Convert string representation of list
                except:
                    platform_list = [platform_list]
            platforms.update(platform_list)

        prompt = f"""
        Analyze the platform distribution for Japanese music trends:

        Platforms with trending content: {list(platforms)}

        Provide a 2-3 sentence analysis of what this platform distribution tells us about where Japanese music conversations are happening and what it means for artist engagement strategies.
        """

        return self._query_ollama(prompt)

    def generate_recommendations(self, trend_data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on trends"""
        if not self.config.include_recommendations:
            return []

        summary = trend_data['summary']

        prompt = f"""
        Based on this Japanese music trend analysis, provide 3-5 specific, actionable recommendations for:
        1. Music artists and their teams
        2. Record labels and music industry professionals
        3. Marketing and social media strategies

        Data context:
        - Artists analyzed: {summary['overview']['total_artists_analyzed']}
        - Top trending artists: {summary.get('top_artists', [])}
        - Sentiment patterns: {summary.get('sentiment_patterns', {})}

        Format as a numbered list with brief explanations.
        """

        response = self._query_ollama(prompt)

        # Parse recommendations into list
        recommendations = []
        if response:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                    recommendations.append(line)

        return recommendations

    def generate_market_implications(self, trend_data: Dict[str, Any]) -> List[str]:
        """Generate market implications and industry insights"""
        if not self.config.include_market_insights:
            return []

        prompt = f"""
        Based on this Japanese music trend analysis, identify 3-4 key market implications for the Japanese music industry:

        Consider:
        - Fan engagement patterns
        - Artist popularity trends
        - Platform preferences
        - Sentiment distributions

        Focus on broader industry implications rather than specific artist advice.
        Format as bullet points.
        """

        response = self._query_ollama(prompt)

        # Parse implications into list
        implications = []
        if response:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('*') or line.startswith('•')):
                    implications.append(line)

        return implications

    def calculate_confidence_score(self, trend_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        summary = trend_data['summary']

        # Factors affecting confidence
        total_data_points = summary['overview']['total_artists_analyzed']
        has_sentiment_data = sum(summary.get('sentiment_patterns', {}).values()) > 0
        has_multiple_platforms = len(set().union(*[
            eval(artist.get('platforms', '[]')) if isinstance(artist.get('platforms'), str) else artist.get('platforms', [])
            for artist in trend_data['artist_trends']
        ])) > 1

        # Base confidence calculation
        base_confidence = min(0.8, total_data_points * 0.2)  # Max 0.8 for data volume
        sentiment_bonus = 0.1 if has_sentiment_data else 0
        platform_bonus = 0.1 if has_multiple_platforms else 0

        return min(1.0, base_confidence + sentiment_bonus + platform_bonus)

    def generate_complete_summary(self, trend_summary_path: str, artist_trends_path: str) -> TrendSummary:
        """Generate comprehensive trend summary"""
        logger.info("Loading trend detection results...")
        trend_data = self.load_trend_data(trend_summary_path, artist_trends_path)

        logger.info("Generating executive summary...")
        executive_summary = self.generate_executive_summary(trend_data)

        logger.info("Generating artist insights...")
        artist_insights = self.generate_artist_insights(trend_data)

        logger.info("Generating sentiment analysis...")
        sentiment_analysis = self.generate_sentiment_analysis(trend_data)

        logger.info("Generating platform analysis...")
        platform_analysis = self.generate_platform_analysis(trend_data)

        logger.info("Generating recommendations...")
        recommendations = self.generate_recommendations(trend_data)

        logger.info("Generating market implications...")
        market_implications = self.generate_market_implications(trend_data)

        # Calculate confidence score
        confidence_score = self.calculate_confidence_score(trend_data)

        # Extract key findings from artist data
        key_findings = []
        summary = trend_data['summary']

        if summary['overview']['total_artists_analyzed'] > 0:
            key_findings.append(f"Analyzed {summary['overview']['total_artists_analyzed']} trending Japanese music artists")

        if summary.get('top_artists'):
            top_artist = summary['top_artists'][0]
            key_findings.append(f"Top trending artist: {top_artist['name']} (strength: {top_artist['trend_strength']:.2f})")

        sentiment_patterns = summary.get('sentiment_patterns', {})
        total_sentiment = sum(sentiment_patterns.values())
        if total_sentiment > 0:
            dominant_sentiment = max(sentiment_patterns.items(), key=lambda x: x[1])
            key_findings.append(f"Dominant sentiment pattern: {dominant_sentiment[0]} ({dominant_sentiment[1]} trends)")

        return TrendSummary(
            executive_summary=executive_summary,
            key_findings=key_findings,
            artist_insights=artist_insights,
            genre_insights=[],  # No genre data in current dataset
            sentiment_analysis=sentiment_analysis,
            platform_analysis=platform_analysis,
            recommendations=recommendations,
            market_implications=market_implications,
            timestamp=datetime.now().isoformat(),
            data_period=trend_data['summary'].get('analysis_timestamp', 'Unknown'),
            confidence_score=confidence_score
        )

    def export_summary(self, summary: TrendSummary, output_dir: str) -> Dict[str, str]:
        """Export summary in multiple formats"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        outputs = {}

        # Export as JSON
        json_path = output_path / "trend_insights_summary.json"
        summary_dict = {
            'executive_summary': summary.executive_summary,
            'key_findings': summary.key_findings,
            'artist_insights': summary.artist_insights,
            'genre_insights': summary.genre_insights,
            'sentiment_analysis': summary.sentiment_analysis,
            'platform_analysis': summary.platform_analysis,
            'recommendations': summary.recommendations,
            'market_implications': summary.market_implications,
            'metadata': {
                'timestamp': summary.timestamp,
                'data_period': summary.data_period,
                'confidence_score': summary.confidence_score
            }
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary_dict, f, indent=2, ensure_ascii=False)
        outputs['json'] = str(json_path)

        # Export as Markdown
        markdown_path = output_path / "trend_insights_report.md"
        markdown_content = self._generate_markdown_report(summary)

        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        outputs['markdown'] = str(markdown_path)

        # Export key metrics as CSV
        csv_path = output_path / "trend_insights_summary.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['metric', 'value'])
            writer.writerow(['analysis_timestamp', summary.timestamp])
            writer.writerow(['data_period', summary.data_period])
            writer.writerow(['confidence_score', summary.confidence_score])
            writer.writerow(['key_findings_count', len(summary.key_findings)])
            writer.writerow(['artist_insights_count', len(summary.artist_insights)])
            writer.writerow(['recommendations_count', len(summary.recommendations)])
        outputs['csv'] = str(csv_path)

        logger.info(f"Summary exported to: {outputs}")
        return outputs

    def _generate_markdown_report(self, summary: TrendSummary) -> str:
        """Generate formatted Markdown report"""
        report = f"""# Japanese Music Trends Analysis Report

**Generated:** {summary.timestamp}
**Data Period:** {summary.data_period}
**Confidence Score:** {summary.confidence_score:.2f}

---

## Executive Summary

{summary.executive_summary}

---

## Key Findings

"""

        for finding in summary.key_findings:
            report += f"- {finding}\n"

        if summary.artist_insights:
            report += "\n---\n\n## Artist Insights\n\n"
            for insight in summary.artist_insights:
                report += f"{insight}\n\n"

        if summary.sentiment_analysis:
            report += f"---\n\n## Sentiment Analysis\n\n{summary.sentiment_analysis}\n\n"

        if summary.platform_analysis:
            report += f"---\n\n## Platform Analysis\n\n{summary.platform_analysis}\n\n"

        if summary.recommendations:
            report += "---\n\n## Recommendations\n\n"
            for rec in summary.recommendations:
                report += f"{rec}\n"

        if summary.market_implications:
            report += "\n---\n\n## Market Implications\n\n"
            for impl in summary.market_implications:
                report += f"{impl}\n"

        report += f"\n---\n\n*Analysis generated by Japanese Music Trends Pipeline*"

        return report

def main():
    """Main function for standalone execution"""
    # Configuration
    config = SummaryConfig(
        language_style="professional",
        include_recommendations=True,
        include_market_insights=True
    )

    # File paths
    base_dir = Path(__file__).parent.parent
    trend_summary_path = base_dir / "data" / "intermediate" / "trend_analysis" / "trend_summary.json"
    artist_trends_path = base_dir / "data" / "intermediate" / "trend_analysis" / "artist_trends.csv"
    output_dir = base_dir / "data" / "intermediate" / "summarization"

    try:
        # Initialize summarizer
        summarizer = TrendSummarizer(config)

        # Generate complete summary
        logger.info("Generating comprehensive trend summary...")
        summary = summarizer.generate_complete_summary(
            str(trend_summary_path),
            str(artist_trends_path)
        )

        # Export results
        outputs = summarizer.export_summary(summary, str(output_dir))

        print("\n" + "="*60)
        print("JAPANESE MUSIC TRENDS SUMMARIZATION COMPLETE")
        print("="*60)
        print(f"Executive Summary: {summary.executive_summary[:100]}...")
        print(f"Key Findings: {len(summary.key_findings)} identified")
        print(f"Artist Insights: {len(summary.artist_insights)} generated")
        print(f"Confidence Score: {summary.confidence_score:.2f}")
        print(f"Output Files: {list(outputs.keys())}")
        print("="*60)

    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise

if __name__ == "__main__":
    main()
