#!/usr/bin/env python3
"""
Japanese Music Trends Analysis Pipeline - Standalone Summarization Module

Standalone version of the summarization module for easy testing and execution.
Generates natural language insights and summaries from trend detection results.

Author: GitHub Copilot
Date: January 2025
"""

import json
import csv
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests
import time
import argparse  # Added argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendSummarizer:
    """
    Standalone Trend Summarizer - Generates natural language summaries and insights
    """

    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "llama3.1:8b"):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.max_tokens = 1000
        self.temperature = 0.7
        self.timeout = 60
        self.ollama_available = self._check_ollama_availability()

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [model['name'] for model in response.json().get('models', [])]
                if self.model_name in models:
                    logger.info(f"✅ Ollama service available with {self.model_name}")
                    return True
                else:
                    logger.warning(f"⚠️ Model {self.model_name} not found in Ollama")
                    return False
            return False
        except Exception as e:
            logger.warning(f"⚠️ Ollama service not available: {e}")
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

            logger.info(f"📊 Loaded trend data: {len(artist_trends)} artists, summary from {trend_summary.get('analysis_timestamp', 'unknown')}")

            return {
                'summary': trend_summary,
                'artist_trends': artist_trends,
                'loaded_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error loading trend data: {e}")
            raise

    def _query_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and get response"""
        if not self.ollama_available:
            return self._generate_fallback_response(prompt)

        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }

            logger.debug(f"🤖 Querying Ollama with {len(prompt)} character prompt...")
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"❌ Ollama API error: {response.status_code}")
                return self._generate_fallback_response(prompt)

        except Exception as e:
            logger.error(f"❌ Error querying Ollama: {e}")
            return self._generate_fallback_response(prompt)

    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate basic response when Ollama is not available"""
        if "executive summary" in prompt.lower():
            return "The analysis shows emerging trends in Japanese music social media engagement. Current data indicates moderate artist activity with neutral sentiment patterns. Further analysis with larger datasets would provide more comprehensive insights."
        elif "artist" in prompt.lower() and "insight" in prompt.lower():
            return "Shows moderate social media presence with neutral fan engagement. The trend data suggests stable but not explosive growth in online mentions and discussions."
        elif "sentiment" in prompt.lower():
            return "The sentiment patterns indicate a balanced engagement landscape with neutral emotional responses dominating the conversation around Japanese music trends."
        elif "platform" in prompt.lower():
            return "Platform analysis shows concentration on specific social media channels, indicating focused fan engagement patterns typical of Japanese music fandoms."
        elif "recommendation" in prompt.lower():
            return "1. Monitor emerging trends more closely\n2. Engage with fan communities on active platforms\n3. Track sentiment shifts over time\n4. Expand social media presence strategically"
        elif "market" in prompt.lower():
            return "- Social media engagement patterns suggest evolving fan behavior\n- Platform preferences indicate changing consumption habits\n- Sentiment neutrality may indicate opportunity for increased engagement"
        else:
            return "Analysis indicates moderate trends with opportunities for enhanced engagement and monitoring."

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
            prompt = f"""Analyze this Japanese music artist's social media trend data and provide professional insights:

ARTIST DATA:
- Name: {artist['entity_name']}
- Mentions: {artist['mention_count']}
- Sentiment Score: {artist['sentiment_score']}
- Trend Strength: {artist['trend_strength']}
- Platforms: {artist['platforms']}
- Engagement Level: {artist['engagement_level']}

Generate a concise 2-sentence professional insight about:
1. This artist's current trending status and momentum
2. What this data indicates about their popularity in the Japanese music landscape

Focus on concrete observations and industry implications."""

            insight = self._query_ollama(prompt)
            if insight and len(insight) > 20:  # Basic validation
                insights.append(f"**{artist['entity_name']}**: {insight}")

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
        # Extract platform information from artist trends
        platforms = set()
        for artist in trend_data['artist_trends']:
            platform_list = artist.get('platforms', '[]')
            if isinstance(platform_list, str):
                try:
                    # Handle string representation of list
                    if platform_list.startswith('[') and platform_list.endswith(']'):
                        platform_list = eval(platform_list)
                    else:
                        platform_list = [platform_list]
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

        # Parse implications into list
        implications = []
        if response:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('*') or line.startswith('•') or line[0].isdigit()):
                    implications.append(line)

        return implications

    def calculate_confidence_score(self, trend_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        summary = trend_data['summary']

        # Factors affecting confidence
        total_data_points = summary['overview']['total_artists_analyzed']
        sentiment_data_points = sum(summary.get('sentiment_patterns', {}).values())

        # Extract platform diversity
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
                    platform_list = []
            platforms.update(platform_list)

        # Confidence calculation
        data_volume_score = min(0.6, total_data_points * 0.15)  # Max 0.6 for data volume
        sentiment_score = min(0.2, sentiment_data_points * 0.1)  # Max 0.2 for sentiment data
        platform_score = min(0.2, len(platforms) * 0.1)  # Max 0.2 for platform diversity

        total_confidence = data_volume_score + sentiment_score + platform_score
        return min(1.0, max(0.1, total_confidence))  # Ensure between 0.1 and 1.0

    def generate_complete_summary(self, trend_summary_path: str, artist_trends_path: str) -> Dict[str, Any]:
        """Generate comprehensive trend summary"""
        logger.info("📥 Loading trend detection results...")
        trend_data = self.load_trend_data(trend_summary_path, artist_trends_path)

        logger.info("📝 Generating executive summary...")
        executive_summary = self.generate_executive_summary(trend_data)

        logger.info("🎵 Generating artist insights...")
        artist_insights = self.generate_artist_insights(trend_data)

        logger.info("😊 Analyzing sentiment patterns...")
        sentiment_analysis = self.generate_sentiment_analysis(trend_data)

        logger.info("📱 Analyzing platform trends...")
        platform_analysis = self.generate_platform_analysis(trend_data)

        logger.info("💡 Generating recommendations...")
        recommendations = self.generate_recommendations(trend_data)

        logger.info("📈 Generating market implications...")
        market_implications = self.generate_market_implications(trend_data)

        # Calculate confidence score
        confidence_score = self.calculate_confidence_score(trend_data)

        # Extract key findings from data
        key_findings = []
        summary = trend_data['summary']

        if summary['overview']['total_artists_analyzed'] > 0:
            key_findings.append(f"Analyzed {summary['overview']['total_artists_analyzed']} trending Japanese music artists")

        if summary.get('top_artists'):
            top_artist = summary['top_artists'][0]
            key_findings.append(f"Top trending artist: {top_artist['name']} (trend strength: {top_artist['trend_strength']:.2f})")

        sentiment_patterns = summary.get('sentiment_patterns', {})
        total_sentiment = sum(sentiment_patterns.values())
        if total_sentiment > 0:
            dominant_sentiment = max(sentiment_patterns.items(), key=lambda x: x[1])
            key_findings.append(f"Dominant sentiment pattern: {dominant_sentiment[0]} ({dominant_sentiment[1]} trends)")

        # Extract platform info
        platforms = set()
        for artist in trend_data['artist_trends']:
            platform_list = artist.get('platforms', '[]')
            if isinstance(platform_list, str) and platform_list.startswith('['):
                try:
                    platform_list = eval(platform_list)
                    platforms.update(platform_list)
                except:
                    pass

        if platforms:
            key_findings.append(f"Active platforms: {', '.join(platforms)}")

        return {
            'executive_summary': executive_summary,
            'key_findings': key_findings,
            'artist_insights': artist_insights,
            'genre_insights': [],  # No genre data in current dataset
            'sentiment_analysis': sentiment_analysis,
            'platform_analysis': platform_analysis,
            'recommendations': recommendations,
            'market_implications': market_implications,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'data_period': trend_data['summary'].get('analysis_timestamp', 'Unknown'),
                'confidence_score': confidence_score,
                'llm_available': self.ollama_available
            }
        }

    def export_summary(self, summary: Dict[str, Any], output_dir: str) -> Dict[str, str]:
        """Export summary in multiple formats"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        outputs = {}

        # Export as JSON
        json_path = output_path / "trend_insights_summary.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        outputs['json'] = str(json_path)

        # Export as Markdown report
        markdown_path = output_path / "trend_insights_report.md"
        markdown_content = self._generate_markdown_report(summary)
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        outputs['markdown'] = str(markdown_path)

        # Export key metrics as CSV
        csv_path = output_path / "trend_insights_metrics.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['metric', 'value'])
            writer.writerow(['analysis_timestamp', summary['metadata']['timestamp']])
            writer.writerow(['data_period', summary['metadata']['data_period']])
            writer.writerow(['confidence_score', summary['metadata']['confidence_score']])
            writer.writerow(['key_findings_count', len(summary['key_findings'])])
            writer.writerow(['artist_insights_count', len(summary['artist_insights'])])
            writer.writerow(['recommendations_count', len(summary['recommendations'])])
            writer.writerow(['market_implications_count', len(summary['market_implications'])])
            writer.writerow(['llm_available', summary['metadata']['llm_available']])
        outputs['csv'] = str(csv_path)

        logger.info(f"📁 Summary exported to: {list(outputs.keys())}")
        return outputs

    def _generate_markdown_report(self, summary: Dict[str, Any]) -> str:
        """Generate formatted Markdown report"""
        metadata = summary['metadata']

        report = f"""# 🎵 Japanese Music Trends Analysis Report

**Generated:** {metadata['timestamp']}
**Data Period:** {metadata['data_period']}
**Confidence Score:** {metadata['confidence_score']:.2f}/1.0
**LLM Status:** {'✅ Available' if metadata['llm_available'] else '⚠️ Fallback Mode'} (Host: {self.ollama_url})

---

## 📋 Executive Summary

{summary['executive_summary']}

---

## 🔍 Key Findings

"""

        for i, finding in enumerate(summary['key_findings'], 1):
            report += f"{i}. {finding}\\n"

        if summary['artist_insights']:
            report += "\\n---\\n\\n## 🎤 Artist Insights\\n\\n"
            for insight in summary['artist_insights']:
                report += f"{insight}\\n\\n"

        if summary['sentiment_analysis']:
            report += f"---\\n\\n## 😊 Sentiment Analysis\\n\\n{summary['sentiment_analysis']}\\n\\n"

        if summary['platform_analysis']:
            report += f"---\\n\\n## 📱 Platform Analysis\\n\\n{summary['platform_analysis']}\\n\\n"

        if summary['recommendations']:
            report += "---\\n\\n## 💡 Recommendations\\n\\n"
            for rec in summary['recommendations']:
                report += f"- {rec}\\n"

        if summary['market_implications']:
            report += "\\n---\\n\\n## 📈 Market Implications\\n\\n"
            for impl in summary['market_implications']:
                report += f"- {impl}\\n"

        report += f"\\n---\\n\\n*Report generated by Japanese Music Trends Analysis Pipeline*  \\n*Confidence Score: {metadata['confidence_score']:.2f} | LLM: {'Ollama' if metadata['llm_available'] else 'Fallback'} (Host: {self.ollama_url})*"

        return report

def main():
    """Main function for standalone execution"""
    parser = argparse.ArgumentParser(description="Standalone Summarization Module for Japanese Music Trends.")
    parser.add_argument("--trend-summary-file", type=str, required=True,
                        help="Path to the input trend summary JSON file.")
    parser.add_argument("--artist-trends-file", type=str, required=True,
                        help="Path to the input artist trends CSV file.")
    parser.add_argument("--output-dir", type=str, required=True,
                        help="Directory to save the output summary files.")
    parser.add_argument("--ollama-host", type=str, default="http://localhost:11434",
                        help="Ollama host URL (e.g., http://localhost:11434).")

    args = parser.parse_args()

    try:
        # Initialize summarizer
        logger.info(f"🚀 Initializing Japanese Music Trends Summarizer with Ollama host: {args.ollama_host}...")
        summarizer = TrendSummarizer(ollama_url=args.ollama_host)

        # File paths from arguments
        trend_summary_path = Path(args.trend_summary_file)
        artist_trends_path = Path(args.artist_trends_file)
        output_dir = Path(args.output_dir)

        # Verify input files exist
        if not trend_summary_path.exists():
            logger.error(f"❌ Trend summary file not found: {trend_summary_path}")
            return

        if not artist_trends_path.exists():
            logger.error(f"❌ Artist trends file not found: {artist_trends_path}")
            return

        # Generate complete summary
        logger.info("📊 Generating comprehensive trend summary...")
        summary = summarizer.generate_complete_summary(
            str(trend_summary_path),
            str(artist_trends_path)
        )

        # Export results
        logger.info(f"💾 Exporting summary reports to {output_dir}...")
        outputs = summarizer.export_summary(summary, str(output_dir))

        # Display results
        print("\\n" + "="*70)
        print("🎵 JAPANESE MUSIC TRENDS SUMMARIZATION COMPLETE")
        print("="*70)
        print(f"🗣️ Ollama Host Used: {args.ollama_host}")
        print(f"📝 Executive Summary: {summary['executive_summary'][:100]}...")
        print(f"🔍 Key Findings: {len(summary['key_findings'])} identified")
        print(f"🎤 Artist Insights: {len(summary['artist_insights'])} generated")
        print(f"💡 Recommendations: {len(summary['recommendations'])} provided")
        print(f"📈 Market Implications: {len(summary['market_implications'])} identified")
        print(f"🎯 Confidence Score: {summary['metadata']['confidence_score']:.2f}/1.0")
        print(f"🤖 LLM Status: {'Available' if summary['metadata']['llm_available'] else 'Fallback Mode'}")
        print(f"📁 Output Files: {', '.join(outputs.keys())}")
        print("="*70)

        # Print quick preview of insights
        if summary['key_findings']:
            print("\\n🔍 Key Findings Preview:")
            for finding in summary['key_findings'][:3]:
                print(f"   • {finding}")

        if summary['artist_insights']:
            print("\\n🎤 Artist Insights Preview:")
            for insight in summary['artist_insights'][:2]:
                print(f"   • {insight[:100]}...")

        print(f"\\n📁 Full report available at: {outputs['markdown']}")

    except Exception as e:
        logger.error(f"❌ Summarization failed: {e}")
        # raise # Optionally re-raise for debugging, or handle gracefully
        print(f"❌ An error occurred during summarization: {e}")


if __name__ == "__main__":
    main()
