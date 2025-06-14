#!/usr/bin/env python3
"""
Japanese Music Trends Analysis Pipeline - Standalone Summarization Module

Standalone version of the summarization module for easy testing and execution.
Generates natural language insights and summaries from trend detection results.

"""

import json
import csv
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests
import time
import argparse
from dataclasses import dataclass, field
import sys

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Ensure logger level is set
if not logger.hasHandlers(): # Add handler only if none exist
    handler = logging.StreamHandler(sys.stdout) # Explicitly output to stdout
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
else: # If handlers exist, ensure at least one is for stdout at the correct level
    has_stdout_handler = False
    for h in logger.handlers:
        if hasattr(h, 'stream') and h.stream == sys.stdout:
            has_stdout_handler = True
            h.setLevel(logging.INFO) # Ensure existing stdout handler is at INFO
            if not h.formatter: # Add formatter if missing
                 formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                 h.setFormatter(formatter)
            break
    if not has_stdout_handler: # If no stdout handler, add one
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

@dataclass
class SummaryConfig:
    """Configuration for the summarization process."""
    ollama_host: str = field(default_factory=lambda: os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
    ollama_model: str = field(default_factory=lambda: os.getenv('OLLAMA_MODEL', 'llama3:8b'))
    ollama_timeout: int = 60
    max_retries: int = 3
    temperature: float = 0.7  # Added temperature
    max_tokens: int = 1024    # Added max_tokens
@dataclass
class TrendSummary:
    """Comprehensive trend summary data structure"""
    executive_summary: str
    key_findings: List[str]
    artist_insights: List[str]
    genre_insights: List[str]
    temporal_insights: List[str] # Added for temporal insights
    sentiment_analysis: str
    platform_analysis: str
    recommendations: List[str]
    market_implications: List[str]
    timestamp: str
    data_period: str
    confidence_score: float
class TrendSummarizer:
    """
    Standalone Trend Summarizer - Generates natural language summaries and insights
    """

    def __init__(self, config: Optional[SummaryConfig] = None, ollama_host_override: Optional[str] = None): # Renamed ollama_host to ollama_host_override for clarity
        self.config = config or SummaryConfig()
        if ollama_host_override: # Check for the override
            self.config.ollama_host = ollama_host_override # Corrected attribute name
        self.ollama_available = self._check_ollama_availability()

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.config.ollama_host}/api/tags", timeout=5) # Corrected attribute: ollama_host
            if response.status_code == 200:
                models = [model['name'] for model in response.json().get('models', [])]
                if self.config.ollama_model in models: # Corrected attribute: ollama_model
                    logger.info(f"✅ Ollama service available with {self.config.ollama_model} at {self.config.ollama_host}") # Corrected attributes
                    return True
                else:
                    logger.warning(f"⚠️ Model {self.config.ollama_model} not found in Ollama at {self.config.ollama_host}") # Corrected attributes
                    return False
            logger.warning(f"⚠️ Ollama service at {self.config.ollama_host} responded with status {response.status_code}") # Corrected attribute
            return False
        except Exception as e:
            logger.warning(f"⚠️ Ollama service not available at {self.config.ollama_host}: {e}") # Corrected attribute
            return False

    def load_trend_data(self, trend_summary_path: Path, artist_trends_path: Path, genre_trends_path: Path, temporal_trends_path: Path) -> Dict[str, Any]:
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

            # Load genre trends
            genre_trends = []
            with open(genre_trends_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    genre_trends.append(row)

            # Load temporal trends
            temporal_trends = []
            with open(temporal_trends_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    temporal_trends.append(row)

            logger.info(f"📊 Loaded trend data: {len(artist_trends)} artists, {len(genre_trends)} genres, {len(temporal_trends)} temporal points, summary from {trend_summary.get('analysis_timestamp', 'unknown')}")

            return {
                'summary': trend_summary,
                'artist_trends': artist_trends,
                'genre_trends': genre_trends,
                'temporal_trends': temporal_trends,
                'loaded_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error loading trend data: {e}")
            raise

    def _query_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and get response"""
        if not self.ollama_available:
            return self._generate_fallback_summary(prompt)

        try:
            payload = {
                "model": self.config.ollama_model, # Corrected attribute: ollama_model
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }

            logger.debug(f"🤖 Querying Ollama ({self.config.ollama_host}) with {len(prompt)} character prompt...") # Corrected attribute: ollama_host
            response = requests.post(
                f"{self.config.ollama_host}/api/generate", # Corrected attribute: ollama_host
                json=payload,
                timeout=self.config.ollama_timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"❌ Ollama API error ({self.config.ollama_host}): {response.status_code} - {response.text}")
                return self._generate_fallback_summary(prompt) # Changed to _generate_fallback_summary

        except Exception as e:
            logger.error(f"❌ Error querying Ollama ({self.config.ollama_host}): {e}")
            return self._generate_fallback_summary(prompt) # Changed to _generate_fallback_summary

    def _generate_fallback_summary(self, prompt: str) -> str: # Renamed and simplified
        """Generate basic summary when Ollama is not available"""
        # Rate-limit warnings to avoid spam - only warn every 50 calls
        if not hasattr(self, '_fallback_warning_count'):
            self._fallback_warning_count = 0

        self._fallback_warning_count += 1
        if self._fallback_warning_count == 1:
            logger.warning(f"⚠️ Ollama service unavailable - switching to fallback mode for all summaries")
        elif self._fallback_warning_count % 100 == 0:
            logger.info(f"📊 Fallback mode: {self._fallback_warning_count} summaries generated without LLM")

        return "Trend analysis summary (fallback mode): Basic trend detection completed. For detailed AI-generated insights, ensure Ollama service is running and configured correctly."

    def generate_executive_summary(self, trend_data: Dict[str, Any]) -> str:
        """Generate executive summary of trends"""
        summary = trend_data['summary']

        prompt = f"""You are an expert music industry analyst specializing in Japanese music trends. Generate a concise executive summary based on this social media trend analysis:

DATA OVERVIEW:
- Total Artists Analyzed: {summary['overview']['total_artists_analyzed']}
- Total Genres Analyzed: {summary['overview']['total_genres_analyzed']}
- Top Artists: {summary.get('top_artists', [])}
- Sentiment Distribution: {summary.get('sentiment_patterns', {})}

TASK: Write a professional 2-3 paragraph executive summary that highlights:
1. Overall Japanese music social media trend landscape
2. Key insights about fan engagement and artist popularity
3. Notable patterns or findings that matter for the music industry

Keep it data-driven, professional, and focused on actionable insights for music industry stakeholders."""

        return self._query_ollama(prompt)

    def generate_artist_insights(self, trend_data: Dict[str, Any]) -> List[str]:
        """Generate insights about individual artists"""
        artist_trends = trend_data['artist_trends']
        insights = []

        for artist in artist_trends:
            prompt = f"""Analyze this Japanese music artist\\'s social media trend data and provide professional insights:

ARTIST DATA:
- Name: {artist['entity_name']}
- Mentions: {artist['mention_count']}
- Sentiment Score: {artist['sentiment_score']}
- Trend Strength: {artist['trend_strength']}
- Platforms: {artist['platforms']}
- Engagement Level: {artist['engagement_level']}

Generate a concise 2-sentence professional insight about:
1. This artist\\'s current trending status and momentum
2. What this data indicates about their popularity in the Japanese music landscape

Focus on concrete observations and industry implications."""

            insight = self._query_ollama(prompt)
            if insight and len(insight) > 20:  # Basic validation
                insights.append(f"**{artist['entity_name']}**: {insight}")

        return insights

    def generate_genre_insights(self, trend_data: Dict[str, Any]) -> List[str]:
        """Generate insights about individual genres"""
        genre_trends = trend_data.get('genre_trends', [])
        insights = []

        if not genre_trends:
            logger.info("No genre trend data found to generate insights.")
            return insights

        for genre_data in genre_trends:
            # Adjust keys based on actual structure of genre_trends CSV
            # Check for various possible field names for genre
            genre_name = genre_data.get('genre') or genre_data.get('genre_name') or genre_data.get('entity_name')
            if not genre_name:
                logger.warning(f"Skipping genre insight generation for entry with missing name: {genre_data}")
                continue

            prompt = f"""Analyze this Japanese music genre\\'s social media trend data and provide professional insights:

GENRE DATA:
- Name: {genre_name}
- Popularity Score: {genre_data.get('popularity_score', 'N/A')}
- Sentiment Trend: {genre_data.get('sentiment_trend', 'N/A')}
- Artist Diversity: {genre_data.get('artist_diversity', 'N/A')}
- Cross Platform Presence: {genre_data.get('cross_platform_presence', 'N/A')}
- Emotional Associations: {genre_data.get('emotional_associations', 'N/A')}
- Trend Momentum: {genre_data.get('trend_momentum', 'N/A')}

Generate a concise 2-sentence professional insight about:
1. This genre\\'s current trending status and momentum within the Japanese music scene.
2. What this data indicates about its popularity and evolution.

Focus on concrete observations and industry implications for this genre."""

            insight = self._query_ollama(prompt)
            if insight and len(insight) > 20:  # Basic validation
                insights.append(f"**{genre_name}**: {insight}")
            elif not self.ollama_available: # If fallback, still add a basic entry
                insights.append(f"**{genre_name}**: Basic trend data processed (LLM fallback).")


        return insights

    def generate_temporal_insights(self, trend_data: Dict[str, Any]) -> List[str]:
        """Generate insights about temporal trends"""
        temporal_trends = trend_data.get('temporal_trends', [])
        insights = []

        if not temporal_trends:
            logger.info("No temporal trend data found to generate insights.")
            return insights

        # Consolidate temporal data for a summary prompt if too many data points
        # For now, let's assume we can process a few key points or a summary of them
        # This might involve selecting peak periods, significant changes, or overall trend direction.

        # Example: Create a summarized view of temporal data for the prompt
        # This is a placeholder. Actual summarization logic might be more complex.
        simplified_temporal_data = []
        if len(temporal_trends) > 5: # If more than 5 data points, summarize
            # This is a very basic summarization.
            # A more sophisticated approach might identify key periods (start, peak, end)
            # or calculate overall trend slopes.
            first_point = temporal_trends[0]
            last_point = temporal_trends[-1]
            peak_point = max(temporal_trends, key=lambda x: float(x.get('value', 0) or 0)) # Ensure value is float
            simplified_temporal_data.append(f"Start: Period {first_point.get('period', 'N/A')} - Value {first_point.get('value', 'N/A')}")
            simplified_temporal_data.append(f"Peak: Period {peak_point.get('period', 'N/A')} - Value {peak_point.get('value', 'N/A')}")
            simplified_temporal_data.append(f"End: Period {last_point.get('period', 'N/A')} - Value {last_point.get('value', 'N/A')}")
            num_periods = len(temporal_trends)
            overall_change = float(last_point.get('value', 0) or 0) - float(first_point.get('value', 0) or 0)
            simplified_temporal_data.append(f"Overall trend across {num_periods} periods: Change of {overall_change:.2f}")
        else:
            for point in temporal_trends:
                simplified_temporal_data.append(f"Period: {point.get('period', 'N/A')}, Value: {point.get('value', 'N/A')}, Change: {point.get('change', 'N/A')}")

        temporal_data_str = "\\n".join(simplified_temporal_data)

        prompt = f"""Analyze the temporal trends in Japanese music social media activity based on the following data points:

TEMPORAL DATA:
{temporal_data_str}

Generate a concise 2-3 sentence professional insight about:
1. The overall evolution of social media activity over the observed periods.
2. Any significant peaks, troughs, or patterns of change.
3. What this temporal data suggests about fan engagement dynamics or market shifts over time.

Focus on concrete observations and their implications for understanding music trends in Japan."""

        insight = self._query_ollama(prompt)
        if insight and len(insight) > 20:
            insights.append(insight)
        elif not self.ollama_available:
            insights.append("Temporal trend data processed (LLM fallback).")

        return insights

    def generate_sentiment_analysis(self, trend_data: Dict[str, Any]) -> str:
        """Analyze sentiment patterns across trends"""
        sentiment_patterns = trend_data['summary'].get('sentiment_patterns', {})

        prompt = f"""Analyze the sentiment patterns in Japanese music social media trends:

SENTIMENT DATA:
- Positive Trends: {sentiment_patterns.get('positive_trends', 0)}
- Negative Trends: {sentiment_patterns.get('negative_trends', 0)}
- Neutral Trends: {sentiment_patterns.get('neutral_trends', 0)}

Provide a professional 2-3 sentence analysis explaining:
1. What these sentiment patterns reveal about the current Japanese music landscape
2. What this means for fan engagement and artist-audience relationships
3. Any notable implications for the music industry

Focus on actionable insights and industry context."""

        return self._query_ollama(prompt)

    def generate_platform_analysis(self, trend_data: Dict[str, Any]) -> str:
        """Analyze platform-specific trends"""
        platforms = set()
        for artist in trend_data['artist_trends']:
            platform_list = artist.get('platforms', '[]')
            if isinstance(platform_list, str):
                try:
                    if platform_list.startswith('[') and platform_list.endswith(']'):
                        platform_list = eval(platform_list)
                    else:
                        platform_list = [platform_list] if platform_list else []
                except:
                    platform_list = [platform_list] if platform_list else []
            platforms.update(platform_list)

        prompt = f"""Analyze the platform distribution for Japanese music social media trends:

PLATFORM DATA:
- Active Platforms: {list(platforms)}
- Number of Platforms: {len(platforms)}

Provide a professional 2-3 sentence analysis covering:
1. What this platform distribution tells us about Japanese music fan behavior
2. Strategic implications for artists and labels in terms of platform presence
3. How this reflects broader trends in Japanese music social media engagement

Focus on strategic insights for music industry professionals."""

        return self._query_ollama(prompt)

    def generate_recommendations(self, trend_data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on trends"""
        summary = trend_data['summary']

        prompt = f"""Based on this Japanese music trend analysis, provide specific, actionable recommendations:

ANALYSIS DATA:
- Artists Analyzed: {summary['overview']['total_artists_analyzed']}
- Top Trending Artists: {summary.get('top_artists', [])}
- Sentiment Patterns: {summary.get('sentiment_patterns', {})}

Generate 4-5 specific recommendations for:
1. Music artists and their management teams
2. Record labels and music industry professionals
3. Social media and marketing strategies
4. Industry monitoring and trend tracking

Format as numbered list items with brief explanations. Focus on actionable, practical advice."""

        response = self._query_ollama(prompt)
        recommendations = []
        if response:
            lines = response.split('\\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                    recommendations.append(line)
        return recommendations

    def generate_market_implications(self, trend_data: Dict[str, Any]) -> List[str]:
        """Generate market implications and industry insights"""
        summary = trend_data['summary']

        prompt = f"""Based on this Japanese music trend analysis, identify key market implications:

TREND DATA:
- Total Artists: {summary['overview']['total_artists_analyzed']}
- Sentiment Distribution: {summary.get('sentiment_patterns', {})}
- Top Artists: {summary.get('top_artists', [])}

Identify 3-4 key market implications for the Japanese music industry focusing on:
1. Fan engagement patterns and behavior shifts
2. Platform preferences and digital strategy implications
3. Artist popularity dynamics and market opportunities
4. Industry-wide trends and strategic considerations

Format as bullet points with clear implications for industry stakeholders."""

        response = self._query_ollama(prompt)
        implications = []
        if response:
            lines = response.split('\\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('*') or line.startswith('•') or line[0].isdigit()):
                    implications.append(line)
        return implications

    def calculate_confidence_score(self, trend_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        summary = trend_data['summary']
        artist_trends = trend_data.get('artist_trends', [])
        genre_trends = trend_data.get('genre_trends', [])
        temporal_trends = trend_data.get('temporal_trends', [])

        total_artists = len(artist_trends)
        total_genres = len(genre_trends)
        total_temporal_points = len(temporal_trends)
        total_data_points = total_artists + total_genres + total_temporal_points
        sentiment_data_points = sum(summary.get('sentiment_patterns', {}).values())
        platforms = set()
        for artist in trend_data.get('artist_trends', []):
            platform_list = artist.get('platforms', '[]')
            if isinstance(platform_list, str):
                try:
                    if platform_list.startswith('[') and platform_list.endswith(']'):
                        platform_list = eval(platform_list)
                    else:
                        platform_list = [platform_list] if platform_list else []
                except:
                    platform_list = []
            elif isinstance(platform_list, list):
                pass
            else:
                platform_list = []
            platforms.update(platform_list)

        data_volume_score = min(0.5, (total_artists * 0.05) + (total_genres * 0.05) + (total_temporal_points * 0.02))
        sentiment_score = min(0.2, sentiment_data_points * 0.05)
        platform_score = min(0.2, len(platforms) * 0.05)
        llm_factor = 0.1 if self.ollama_available else 0.0
        total_confidence = data_volume_score + sentiment_score + platform_score + llm_factor
        return min(1.0, max(0.1, total_confidence))

    def generate_complete_summary(self, input_dir_str: str, date_tag: str, source_tag: str) -> TrendSummary:
        """Generate comprehensive trend summary and return a TrendSummary object"""
        input_dir = Path(input_dir_str)
        trend_summary_filename = f"trend_summary_{date_tag}_{source_tag}.json"
        artist_trends_filename = f"artist_trends_{date_tag}_{source_tag}.csv"
        genre_trends_filename = f"genre_trends_{date_tag}_{source_tag}.csv"
        temporal_trends_filename = f"temporal_trends_{date_tag}_{source_tag}.csv"

        trend_summary_path = input_dir / trend_summary_filename
        artist_trends_path = input_dir / artist_trends_filename
        genre_trends_path = input_dir / genre_trends_filename
        temporal_trends_path = input_dir / temporal_trends_filename

        logger.info("📥 Loading trend detection results...")
        trend_data = self.load_trend_data(
            trend_summary_path,
            artist_trends_path,
            genre_trends_path,
            temporal_trends_path
        )

        logger.info("📝 Generating executive summary...")
        executive_summary = self.generate_executive_summary(trend_data)

        logger.info("🎵 Generating artist insights...")
        artist_insights = self.generate_artist_insights(trend_data)

        # Placeholder for genre insights - to be implemented next
        # genre_insights = [] # self.generate_genre_insights(trend_data)
        logger.info("🎶 Generating genre insights...")
        genre_insights = self.generate_genre_insights(trend_data)

        logger.info("⏳ Generating temporal insights...") # Added log for temporal insights
        temporal_insights = self.generate_temporal_insights(trend_data) # Call new method

        logger.info("😊 Analyzing sentiment patterns...")
        sentiment_analysis = self.generate_sentiment_analysis(trend_data)

        logger.info("📱 Analyzing platform trends...")
        platform_analysis = self.generate_platform_analysis(trend_data)

        logger.info("💡 Generating recommendations...")
        recommendations = self.generate_recommendations(trend_data)

        logger.info("📈 Generating market implications...")
        market_implications = self.generate_market_implications(trend_data)

        confidence_score = self.calculate_confidence_score(trend_data)

        key_findings = []
        summary_data = trend_data['summary'] # Using a shorter alias

        if summary_data['overview']['total_artists_analyzed'] > 0:
            key_findings.append(f"Analyzed {summary_data['overview']['total_artists_analyzed']} trending Japanese music artists")

        if summary_data['overview'].get('total_genres_analyzed', 0) > 0: # Check for genres
             key_findings.append(f"Analyzed {summary_data['overview']['total_genres_analyzed']} trending Japanese music genres")

        if summary_data.get('top_artists'):
            top_artist = summary_data['top_artists'][0]
            key_findings.append(f"Top trending artist: {top_artist['name']} (trend strength: {top_artist['trend_strength']:.2f})")

        # Placeholder for top genre - adapt if top_genres is added to summary_data
        # if summary_data.get('top_genres'):
        #     top_genre = summary_data['top_genres'][0]
        #     key_findings.append(f"Top trending genre: {top_genre['name']} (trend strength: {top_genre['trend_strength']:.2f})")

        sentiment_patterns = summary_data.get('sentiment_patterns', {})
        total_sentiment = sum(sentiment_patterns.values())
        if total_sentiment > 0:
            dominant_sentiment = max(sentiment_patterns.items(), key=lambda x: x[1])
            key_findings.append(f"Dominant sentiment pattern: {dominant_sentiment[0]} ({dominant_sentiment[1]} trends)")

        platforms = set()
        for artist in trend_data.get('artist_trends', []):
            platform_list = artist.get('platforms', '[]')
            if isinstance(platform_list, str):
                try:
                    if platform_list.startswith('[') and platform_list.endswith(']'):
                        platform_list = eval(platform_list)
                    else:
                        platform_list = [platform_list] if platform_list else []
                except:
                    platform_list = []
            elif isinstance(platform_list, list):
                pass
            else:
                platform_list = []
            platforms.update(platform_list)

        if platforms:
            key_findings.append(f"Active platforms: {', '.join(platforms)}")

        return TrendSummary(
            executive_summary=executive_summary,
            key_findings=key_findings,
            artist_insights=artist_insights,
            genre_insights=genre_insights,
            temporal_insights=temporal_insights, # Add temporal insights to TrendSummary
            sentiment_analysis=sentiment_analysis,
            platform_analysis=platform_analysis,
            recommendations=recommendations,
            market_implications=market_implications,
            timestamp=datetime.now().isoformat(),
            data_period=trend_data['summary'].get('analysis_timestamp', 'Unknown'),
            confidence_score=confidence_score
        )

    def export_summary(self, summary: TrendSummary, output_dir_str: str, date_tag: str, source_tag: str) -> Dict[str, str]:
        """Export summary in multiple formats, using TrendSummary object and adding date/source tags to filenames"""
        output_path = Path(output_dir_str)
        output_path.mkdir(parents=True, exist_ok=True)

        outputs = {}
        base_filename = f"trend_insights_{date_tag}_{source_tag}"

        # JSON Export
        json_path = output_path / f"{base_filename}.json"
        summary_dict = {
            'timestamp': summary.timestamp,
            'data_period': summary.data_period,
            'confidence_score': summary.confidence_score,
            'executive_summary': summary.executive_summary,
            'key_findings': summary.key_findings,
            'artist_insights': summary.artist_insights,
            'genre_insights': summary.genre_insights,
            'temporal_insights': summary.temporal_insights, # Added temporal insights
            'sentiment_analysis': summary.sentiment_analysis,
            'platform_analysis': summary.platform_analysis,
            'recommendations': summary.recommendations,
            'market_implications': summary.market_implications
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary_dict, f, indent=4, ensure_ascii=False)
        outputs['json'] = str(json_path)
        logger.info(f"📄 JSON summary exported to {json_path}")

        # Markdown Report
        md_path = output_path / f"{base_filename}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(summary))
        outputs['markdown'] = str(md_path)
        logger.info(f"📝 Markdown report exported to {md_path}")

        # CSV Summary of Key Metrics
        csv_path = output_path / f"{base_filename}_metrics.csv"
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['metric', 'value'])
            writer.writerow(['timestamp', summary.timestamp])
            writer.writerow(['data_period', summary.data_period])
            writer.writerow(['confidence_score', f"{summary.confidence_score:.2f}"])
            writer.writerow(['key_findings_count', len(summary.key_findings)])
            writer.writerow(['artist_insights_count', len(summary.artist_insights)])
            writer.writerow(['genre_insights_count', len(summary.genre_insights)])
            writer.writerow(['temporal_insights_count', len(summary.temporal_insights)]) # Added temporal insights count
            writer.writerow(['recommendations_count', len(summary.recommendations)])
            writer.writerow(['market_implications_count', len(summary.market_implications)])
        outputs['csv'] = str(csv_path)
        logger.info(f"📊 CSV metrics exported to {csv_path}")

        return outputs

    def _generate_markdown_report(self, summary: TrendSummary) -> str:
        """Generate a markdown report from the TrendSummary object"""
        report = f"# Japanese Music Social Media Trend Analysis\\n\\n"
        report += f"**Report Generated:** {summary.timestamp}\\n"
        report += f"**Data Period:** {summary.data_period}\\n"
        report += f"**Confidence Score:** {summary.confidence_score:.2f}\\n\\n"

        report += "## 🌟 Executive Summary\\n\\n"
        report += f"{summary.executive_summary}\\n"

        report += "\\n---\\n\\n## 🔑 Key Findings\\n\\n"
        for i, finding in enumerate(summary.key_findings, 1):
            report += f"{i}. {finding}\\n"

        if summary.artist_insights:
            report += "\\n---\\n\\n## 🎤 Artist Insights\\n\\n"
            for insight in summary.artist_insights:
                report += f"- {insight}\\n"

        if summary.genre_insights:
            report += "\\n---\\n\\n## 🎶 Genre Insights\\n\\n"
            for insight in summary.genre_insights:
                report += f"- {insight}\\n"

        if summary.temporal_insights: # Added section for temporal insights
            report += "\\n---\\n\\n## ⏳ Temporal Insights\\n\\n"
            for insight in summary.temporal_insights:
                report += f"- {insight}\\n"

        report += "\\n---\\n\\n## 😊 Sentiment Analysis\\n\\n"
        report += f"{summary.sentiment_analysis}\\n"

        report += "\\n---\\n\\n## 📱 Platform Analysis\\n\\n"
        report += f"{summary.platform_analysis}\\n"

        if summary.recommendations:
            report += "\\n---\\n\\n## 💡 Recommendations\\n\\n"
            for rec in summary.recommendations:
                report += f"- {rec}\\n"

        if summary.market_implications:
            report += "\\n---\\n\\n## 📈 Market Implications\\n\\n"
            for imp in summary.market_implications:
                report += f"- {imp}\\n"

        return report

def main():
    logger.info("Main function logger active.")
    try:
        parser = argparse.ArgumentParser(description="Trend Summarization Standalone Script")
        parser.add_argument("--input-dir", type=str, default="data/intermediate/", help="Directory containing the input trend files.")
        parser.add_argument("--output-dir", type=str, default="data/summaries/", help="Directory to save the generated summaries.")
        parser.add_argument("--date-tag", type=str, required=True, help="Date tag for input/output files (e.g., YYYYMMDD).")
        parser.add_argument("--source-tag", type=str, required=True, help="Source tag for input/output files (e.g., combined, reddit, youtube).")
        parser.add_argument("--ollama-host", type=str, help="Optional: Ollama host URL (e.g., http://localhost:11434)")
        parser.add_argument("--ollama-model", type=str, help="Ollama model name (e.g., llama3:8b)")
        parser.add_argument("--temperature", type=float, help="Temperature for Ollama model.")
        parser.add_argument("--max_tokens", type=int, help="Max tokens for Ollama model response.")
        parser.add_argument("--log_level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level.")
        args = parser.parse_args()

        # Configure logging level based on command-line argument
        log_level_cli = args.log_level.upper()
        numeric_log_level = getattr(logging, log_level_cli, logging.INFO) # Default to INFO if invalid

        # Set the level for the module's logger instance and its handlers
        logger.setLevel(numeric_log_level)
        for handler_obj in logger.handlers:
            handler_obj.setLevel(numeric_log_level)

        logger.info(f"Logging level set to {log_level_cli} based on command-line argument.")
        # Example debug message to test if DEBUG level is working
        logger.debug("This is a debug message from main() after setting log level.")

        config_kwargs = {}
        if args.ollama_host:
            config_kwargs['ollama_host'] = args.ollama_host
        if args.ollama_model:
            config_kwargs['ollama_model'] = args.ollama_model
        if args.temperature is not None:
            config_kwargs['temperature'] = args.temperature
        if args.max_tokens is not None:
            config_kwargs['max_tokens'] = args.max_tokens

        summary_config = SummaryConfig(**config_kwargs)
        summarizer = TrendSummarizer(config=summary_config)

        logger.info(f"🚀 Starting summarization for {args.date_tag} from {args.source_tag}...")
        logger.info(f"Input directory: {Path(args.input_dir).resolve()}")
        logger.info(f"Output directory: {Path(args.output_dir).resolve()}")

        full_summary = summarizer.generate_complete_summary(args.input_dir, args.date_tag, args.source_tag)

        summarizer.export_summary(full_summary, args.output_dir, args.date_tag, args.source_tag)

        logger.info("✅ Summarization process completed successfully!")
        logger.info(f"Confidence Score: {full_summary.confidence_score:.2f}")
        logger.info(f"- Executive Summary: {'Generated' if full_summary.executive_summary and not 'fallback mode' in full_summary.executive_summary else 'Fallback or Empty'}")
        logger.info(f"- Key Findings: {len(full_summary.key_findings)} generated")
        logger.info(f"- Artist Insights: {len(full_summary.artist_insights)} generated")
        if full_summary.genre_insights:
            logger.info(f"- Genre Insights: {len(full_summary.genre_insights)} generated")
        if full_summary.temporal_insights: # Added for temporal insights
            logger.info(f"- Temporal Insights: {len(full_summary.temporal_insights)} generated") # Added for temporal insights
        logger.info(f"- Recommendations: {len(full_summary.recommendations)} generated")
        logger.info(f"Outputs saved in: {Path(args.output_dir).resolve()}")

    except Exception as e: # Add except block
        logger.error(f"An error occurred during script execution: {e}") # Log the exception
        import traceback # Import traceback
        logger.error(traceback.format_exc()) # Log the full traceback

if __name__ == "__main__":
    main()
