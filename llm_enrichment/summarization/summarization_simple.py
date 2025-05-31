#!/usr/bin/env python3
"""
Japanese Music Trends Analysis Pipeline - Simple Summarization Module

Simplified version that focuses on generating basic insights and summaries.
"""

import json
import csv
import logging
from datetime import datetime
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ollama_availability():
    """Check if Ollama service is available"""
    try:
        response = requests.get("https://7f15e672cfd91e69daf5f01491eeca50.serveo.net/api/tags", timeout=5)
        if response.status_code == 200:
            models = [model['name'] for model in response.json().get('models', [])]
            if "llama3.1:8b" in models:
                logger.info("✅ Ollama service available with llama3.1:8b")
                return True
        return False
    except Exception as e:
        logger.warning(f"⚠️ Ollama service not available: {e}")
        return False

def load_trend_data(trend_summary_path, artist_trends_path):
    """Load trend detection results"""
    # Load trend summary
    with open(trend_summary_path, 'r', encoding='utf-8') as f:
        trend_summary = json.load(f)

    # Load artist trends
    artist_trends = []
    with open(artist_trends_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            artist_trends.append(row)

    logger.info(f"📊 Loaded {len(artist_trends)} artist trends")
    return {'summary': trend_summary, 'artist_trends': artist_trends}

def query_ollama(prompt):
    """Query Ollama for insights"""
    if not check_ollama_availability():
        return generate_fallback_response(prompt)

    try:
        payload = {
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 500}
        }
        headers = {
            "ngrok-skip-browser-warning": "true"
        }

        response = requests.post(
            "https://7f15e672cfd91e69daf5f01491eeca50.serveo.net/api/generate",
            json=payload,
            timeout=60,
            headers=headers
        )

        if response.status_code == 200:
            return response.json().get('response', '').strip()
        else:
            return generate_fallback_response(prompt)

    except Exception as e:
        logger.error(f"❌ Ollama query failed: {e}")
        return generate_fallback_response(prompt)

def generate_fallback_response(prompt):
    """Generate fallback response when Ollama is unavailable"""
    if "executive summary" in prompt.lower():
        return "The analysis reveals emerging trends in Japanese music social media engagement with moderate artist activity and neutral sentiment patterns."
    elif "artist" in prompt.lower():
        return "Shows stable social media presence with neutral fan engagement patterns."
    elif "sentiment" in prompt.lower():
        return "Sentiment patterns indicate balanced engagement with neutral responses dominating Japanese music discussions."
    elif "platform" in prompt.lower():
        return "Platform analysis shows focused engagement on specific social media channels."
    elif "recommendation" in prompt.lower():
        return "1. Monitor emerging trends closely\\n2. Engage with active fan communities\\n3. Track sentiment changes\\n4. Expand strategic social media presence"
    else:
        return "Analysis indicates moderate trends with opportunities for enhanced engagement."

def generate_executive_summary(trend_data):
    """Generate executive summary"""
    summary = trend_data['summary']

    prompt = f"""Generate a professional executive summary for Japanese music trends analysis:

Data: {summary['overview']['total_artists_analyzed']} artists analyzed, top artists: {summary.get('top_artists', [])}, sentiment: {summary.get('sentiment_patterns', {})}

Write 2-3 paragraphs highlighting key insights for music industry stakeholders."""

    return query_ollama(prompt)

def generate_artist_insights(trend_data):
    """Generate insights for each artist"""
    insights = []
    for artist in trend_data['artist_trends']:
        prompt = f"""Analyze Japanese music artist trend data:
Artist: {artist['entity_name']}, Mentions: {artist['mention_count']}, Sentiment: {artist['sentiment_score']}, Trend Strength: {artist['trend_strength']}

Provide 2-sentence professional insight about their trending status."""

        insight = query_ollama(prompt)
        if insight and len(insight) > 20:
            insights.append(f"**{artist['entity_name']}**: {insight}")

    return insights

def generate_recommendations(trend_data):
    """Generate actionable recommendations"""
    summary = trend_data['summary']

    prompt = f"""Based on Japanese music trend analysis with {summary['overview']['total_artists_analyzed']} artists, provide 4 specific recommendations for:
1. Artists and management
2. Record labels
3. Social media strategy
4. Industry monitoring

Format as numbered list."""

    response = query_ollama(prompt)
    recommendations = []
    if response:
        for line in response.split('\\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                recommendations.append(line)

    return recommendations

def calculate_confidence_score(trend_data):
    """Calculate analysis confidence score"""
    summary = trend_data['summary']
    total_artists = summary['overview']['total_artists_analyzed']
    sentiment_points = sum(summary.get('sentiment_patterns', {}).values())

    # Base confidence from data volume
    base_confidence = min(0.6, total_artists * 0.15)
    sentiment_bonus = min(0.2, sentiment_points * 0.1)

    return min(1.0, max(0.1, base_confidence + sentiment_bonus))

def generate_complete_summary(trend_summary_path, artist_trends_path):
    """Generate comprehensive trend summary"""
    logger.info("📥 Loading trend data...")
    trend_data = load_trend_data(trend_summary_path, artist_trends_path)

    logger.info("📝 Generating executive summary...")
    executive_summary = generate_executive_summary(trend_data)

    logger.info("🎵 Generating artist insights...")
    artist_insights = generate_artist_insights(trend_data)

    logger.info("💡 Generating recommendations...")
    recommendations = generate_recommendations(trend_data)

    # Calculate confidence
    confidence_score = calculate_confidence_score(trend_data)

    # Generate key findings
    summary = trend_data['summary']
    key_findings = []

    if summary['overview']['total_artists_analyzed'] > 0:
        key_findings.append(f"Analyzed {summary['overview']['total_artists_analyzed']} trending Japanese music artists")

    if summary.get('top_artists'):
        top_artist = summary['top_artists'][0]
        key_findings.append(f"Top trending artist: {top_artist['name']} (strength: {top_artist['trend_strength']:.2f})")

    sentiment_patterns = summary.get('sentiment_patterns', {})
    if sum(sentiment_patterns.values()) > 0:
        dominant = max(sentiment_patterns.items(), key=lambda x: x[1])
        key_findings.append(f"Dominant sentiment: {dominant[0]} ({dominant[1]} trends)")

    return {
        'executive_summary': executive_summary,
        'key_findings': key_findings,
        'artist_insights': artist_insights,
        'recommendations': recommendations,
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'confidence_score': confidence_score,
            'llm_available': check_ollama_availability()
        }
    }

def export_summary(summary, output_dir):
    """Export summary in multiple formats"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    outputs = {}

    # JSON export
    json_path = output_path / "trend_insights_summary.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    outputs['json'] = str(json_path)

    # Markdown report
    markdown_path = output_path / "trend_insights_report.md"
    markdown_content = generate_markdown_report(summary)
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    outputs['markdown'] = str(markdown_path)

    # CSV metrics
    csv_path = output_path / "trend_insights_metrics.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'value'])
        writer.writerow(['timestamp', summary['metadata']['timestamp']])
        writer.writerow(['confidence_score', summary['metadata']['confidence_score']])
        writer.writerow(['key_findings_count', len(summary['key_findings'])])
        writer.writerow(['artist_insights_count', len(summary['artist_insights'])])
        writer.writerow(['recommendations_count', len(summary['recommendations'])])
        writer.writerow(['llm_available', summary['metadata']['llm_available']])
    outputs['csv'] = str(csv_path)

    logger.info(f"📁 Exported to: {list(outputs.keys())}")
    return outputs

def generate_markdown_report(summary):
    """Generate Markdown report"""
    metadata = summary['metadata']

    report = f"""# 🎵 Japanese Music Trends Analysis Report

**Generated:** {metadata['timestamp']}
**Confidence Score:** {metadata['confidence_score']:.2f}/1.0
**LLM Status:** {'✅ Available' if metadata['llm_available'] else '⚠️ Fallback Mode'}

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

    if summary['recommendations']:
        report += "---\\n\\n## 💡 Recommendations\\n\\n"
        for rec in summary['recommendations']:
            report += f"- {rec}\\n"

    report += f"\\n---\\n\\n*Report generated by Japanese Music Trends Analysis Pipeline*  \\n*Confidence: {metadata['confidence_score']:.2f} | LLM: {'Ollama' if metadata['llm_available'] else 'Fallback'}*"

    return report

def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting Japanese Music Trends Summarization...")

        # File paths
        base_dir = Path(__file__).parent
        trend_summary_path = base_dir / "data" / "intermediate" / "trend_analysis" / "trend_summary.json"
        artist_trends_path = base_dir / "data" / "intermediate" / "trend_analysis" / "artist_trends.csv"
        output_dir = base_dir / "data" / "intermediate" / "summarization"

        # Check input files
        if not trend_summary_path.exists():
            logger.error(f"❌ Missing: {trend_summary_path}")
            return

        if not artist_trends_path.exists():
            logger.error(f"❌ Missing: {artist_trends_path}")
            return

        # Generate summary
        logger.info("📊 Generating comprehensive summary...")
        summary = generate_complete_summary(str(trend_summary_path), str(artist_trends_path))

        # Export results
        logger.info("💾 Exporting reports...")
        outputs = export_summary(summary, str(output_dir))

        # Display results
        print("\\n" + "="*70)
        print("🎵 JAPANESE MUSIC TRENDS SUMMARIZATION COMPLETE")
        print("="*70)
        print(f"📝 Executive Summary: {summary['executive_summary'][:100]}...")
        print(f"🔍 Key Findings: {len(summary['key_findings'])}")
        print(f"🎤 Artist Insights: {len(summary['artist_insights'])}")
        print(f"💡 Recommendations: {len(summary['recommendations'])}")
        print(f"🎯 Confidence Score: {summary['metadata']['confidence_score']:.2f}")
        print(f"🤖 LLM Status: {'Available' if summary['metadata']['llm_available'] else 'Fallback'}")
        print(f"📁 Output Files: {', '.join(outputs.keys())}")
        print("="*70)

        if summary['key_findings']:
            print("\\n🔍 Key Findings:")
            for finding in summary['key_findings']:
                print(f"   • {finding}")

        print(f"\\n📁 Full report: {outputs['markdown']}")

    except Exception as e:
        logger.error(f"❌ Summarization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
