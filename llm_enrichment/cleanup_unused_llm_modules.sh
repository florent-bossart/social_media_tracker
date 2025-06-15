#!/bin/bash

# LLM Enrichment Cleanup Script
# This script removes unused/orphaned modules from the llm_enrichment folder
# Based on usage analysis from codebase references and cmds.log

set -e  # Exit on any error

echo "🧹 LLM Enrichment Cleanup Script"
echo "=================================="
echo

# Define the base directory
LLM_DIR="/home/florent.bossart/code/florent-bossart/social_media_tracker/llm_enrichment"

# Check if we're in the right directory
if [[ ! -d "$LLM_DIR" ]]; then
    echo "❌ Error: LLM enrichment directory not found: $LLM_DIR"
    exit 1
fi

echo "📂 Working directory: $LLM_DIR"
echo

# Create backup directory with timestamp
BACKUP_DIR="$LLM_DIR/backup_unused_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "💾 Created backup directory: $BACKUP_DIR"
echo

# Function to backup and remove a file
backup_and_remove() {
    local file_path="$1"
    local relative_path="${file_path#$LLM_DIR/}"
    
    if [[ -f "$file_path" ]]; then
        echo "🗂️  Backing up and removing: $relative_path"
        
        # Create subdirectory structure in backup if needed
        local backup_subdir="$(dirname "$BACKUP_DIR/$relative_path")"
        mkdir -p "$backup_subdir"
        
        # Copy to backup and remove original
        cp "$file_path" "$BACKUP_DIR/$relative_path"
        rm "$file_path"
        echo "   ✅ Moved to backup: backup_unused_$(date +%Y%m%d_%H%M%S)/$relative_path"
    else
        echo "⚠️  File not found (may already be removed): $relative_path"
    fi
}

echo "🗑️  Removing unused LLM modules..."
echo

# Remove unused simple/basic variant modules
echo "📦 Removing simple/basic variant modules:"
backup_and_remove "$LLM_DIR/sentiment/simple_sentiment_analysis.py"
backup_and_remove "$LLM_DIR/summarization/summarization_simple.py"
backup_and_remove "$LLM_DIR/trend/trend_detection_config_simple.py"
backup_and_remove "$LLM_DIR/trend/trend_detection_config_basic.py"
echo

# Remove unused database SQL generator modules
echo "📦 Removing unused database SQL generator modules:"
backup_and_remove "$LLM_DIR/database/generate_insights_sql.py"
backup_and_remove "$LLM_DIR/database/generate_metrics_sql.py"
backup_and_remove "$LLM_DIR/database/generate_sentiment_sql.py"
backup_and_remove "$LLM_DIR/database/generate_trend_sql.py"
backup_and_remove "$LLM_DIR/database/generate_sql_imports.py"
echo

echo "🎯 Cleanup Summary:"
echo "=================="
echo "✅ Removed 9 unused Python modules"
echo "💾 All removed files backed up to: $BACKUP_DIR"
echo
echo "📋 Remaining active modules:"
echo "   • Entity extraction (core + config)"
echo "   • Sentiment analysis (core + config + mock for tests)"
echo "   • Trend detection (core + config + standalone scripts)"
echo "   • Summarization (core + standalone)"
echo "   • Database integration (core)"
echo
echo "🔍 To verify the cleanup, check the LLM_USAGE_ANALYSIS.md file"
echo
echo "✨ LLM enrichment cleanup completed successfully!"
