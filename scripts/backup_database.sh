#!/bin/bash

# Database Backup Script for Social Media Tracker
# Creates a compressed backup of the PostgreSQL database that can be used to initialize a new instance

set -e  # Exit on any error

# Environment variables should already be available in the shell session
# No need to source .env file manually

# Configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="social_media_tracker_backup_${TIMESTAMP}"
TEMP_DIR="/tmp/db_backup_${TIMESTAMP}"

# Database connection details (from environment or defaults)
# Detect execution environment for correct connection parameters
if [ -f /.dockerenv ] || [ -n "${DOCKER_CONTAINER_ENV}" ]; then
    # Running inside Docker container - use service name from env or default
    DB_HOST="${WAREHOUSE_HOST:-dbt}"
    DB_PORT="${WAREHOUSE_PORT:-5432}"
    EXECUTION_CONTEXT="container"
    echo "🐳 Running inside Docker container"
else
    # Running locally from VM - override environment settings for local access
    DB_HOST="localhost"
    DB_PORT="5434"
    EXECUTION_CONTEXT="local"
    echo "💻 Running locally from VM"
fi

DB_NAME=${WAREHOUSE_DB:-social_db}
DB_USER=${WAREHOUSE_USER:-dbt}
DB_PASSWORD=${WAREHOUSE_PASSWORD}

# Debug: Show what variables were actually read
echo "🔍 Debug - Environment variables:"
echo "   WAREHOUSE_DB='$WAREHOUSE_DB' -> DB_NAME='$DB_NAME'"
echo "   WAREHOUSE_USER='$WAREHOUSE_USER' -> DB_USER='$DB_USER'"
echo "   WAREHOUSE_PASSWORD='$WAREHOUSE_PASSWORD' -> DB_PASSWORD='$DB_PASSWORD'"

echo "🚀 Starting database backup process..."
echo "📅 Timestamp: $TIMESTAMP"
echo "🗄️  Database: $DB_NAME"
echo "🖥️  Host: $DB_HOST:$DB_PORT"
echo "👤 User: $DB_USER"
echo "🔑 Password set: $([ -n "$DB_PASSWORD" ] && echo 'Yes' || echo 'No')"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$TEMP_DIR"

# Function to cleanup temporary files
cleanup() {
    echo "🧹 Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Create database dump
echo "📤 Creating database dump..."
DUMP_FILE="$TEMP_DIR/${BACKUP_NAME}.sql"

if [ "$EXECUTION_CONTEXT" = "container" ]; then
    # Running inside container - use pg_dump directly with service name
    echo "🔧 Using direct pg_dump (inside container)"
    PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --verbose --clean --if-exists --create > "$DUMP_FILE"
else
    # Running locally from VM - connect to localhost:5434
    echo "💻 Using local connection to PostgreSQL"
    PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --verbose --clean --if-exists --create > "$DUMP_FILE"
fi

# Check if dump was successful
if [ ! -f "$DUMP_FILE" ] || [ ! -s "$DUMP_FILE" ]; then
    echo "❌ Error: Database dump failed or is empty"
    exit 1
fi

echo "✅ Database dump created successfully"
echo "📊 Dump size: $(du -h "$DUMP_FILE" | cut -f1)"

# Create additional metadata
echo "📝 Creating backup metadata..."
cat > "$TEMP_DIR/backup_info.txt" << EOF
Social Media Tracker Database Backup
====================================

Backup Date: $(date)
Database Name: $DB_NAME
Database Host: $DB_HOST:$DB_PORT
Database User: $DB_USER
Backup Script Version: 1.0
Project Repository: https://github.com/florent-bossart/social_media_tracker

Restore Instructions:
====================

1. Ensure PostgreSQL is running and accessible
2. Extract this backup: tar -xzf ${BACKUP_NAME}.tar.gz
3. Restore database: psql -h <host> -p <port> -U <user> -d postgres -f ${BACKUP_NAME}.sql
4. Update your .env file with appropriate database credentials
5. Run: docker-compose up to start the application

Note: This backup includes all schemas (raw, staging, analytics) and data.
The restore will drop and recreate the database if it exists.

Schemas included:
- raw: Raw data from APIs (YouTube, Reddit)
- staging: Cleaned and processed data
- analytics: Aggregated analytics and insights
- dbt models and transformations

For more information, see PROJECT_DOCUMENTATION.md in the repository.
EOF

# Create README for the backup
cat > "$TEMP_DIR/README_RESTORE.md" << EOF
# Database Backup Restore Guide

This backup contains a complete snapshot of the Social Media Tracker database.

## Quick Restore

\`\`\`bash
# Extract backup
tar -xzf ${BACKUP_NAME}.tar.gz

# Restore to PostgreSQL (adjust connection details as needed)
psql -h localhost -p 5432 -U postgres -d postgres -f ${BACKUP_NAME}.sql
\`\`\`

## Docker Restore

If using the provided Docker Compose setup:

\`\`\`bash
# Start PostgreSQL container
docker-compose up postgres -d

# Wait for PostgreSQL to be ready
sleep 10

# Restore database
docker exec -i social_media_tracker-postgres-1 psql -U postgres -d postgres < ${BACKUP_NAME}.sql
\`\`\`

## Environment Setup

After restoring the database, make sure to:

1. Copy \`env_file.example\` to \`.env\`
2. Update database credentials in \`.env\`
3. Install dependencies: \`poetry install\`
4. Start services: \`docker-compose up\`

## Schemas Included

- **raw**: Raw API data (YouTube comments, Reddit posts)
- **staging**: Cleaned and processed data
- **analytics**: Aggregated insights and trends

## Data Included

This backup contains sample data for Japanese music trend analysis including:
- YouTube comments and metadata
- Reddit posts and discussions
- Sentiment analysis results
- Entity extraction data
- Temporal trends and analytics

Perfect for getting started with the social media analytics pipeline!
EOF

# Compress the backup
echo "🗜️  Compressing backup..."
cd "$TEMP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" \
    "${BACKUP_NAME}.sql" \
    "backup_info.txt" \
    "README_RESTORE.md"

# Move the compressed backup to the backup directory
mv "${BACKUP_NAME}.tar.gz" "$BACKUP_DIR/"

cd - > /dev/null

# Verify compressed backup
if [ ! -f "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" ]; then
    echo "❌ Error: Compressed backup creation failed"
    exit 1
fi

# Get final backup size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)

echo "✅ Backup completed successfully!"
echo "📁 Backup location: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "📊 Compressed size: $BACKUP_SIZE"
echo "🔗 Backup name: ${BACKUP_NAME}.tar.gz"

# Create or update latest symlink
cd "$BACKUP_DIR"
ln -sf "${BACKUP_NAME}.tar.gz" "latest_backup.tar.gz"
echo "🔗 Latest backup symlink updated"

# Show backup contents
echo ""
echo "📋 Backup contents:"
tar -tzf "${BACKUP_NAME}.tar.gz"

echo ""
echo "🎉 Database backup process completed!"
echo "💡 To restore this backup on a new system:"
echo "   1. Extract: tar -xzf ${BACKUP_NAME}.tar.gz"
echo "   2. Read: README_RESTORE.md for detailed instructions"
echo "   3. Restore: psql -h <host> -U <user> -d postgres -f ${BACKUP_NAME}.sql"

# Optional: Clean up old backups (keep last 5)
echo ""
echo "🧹 Cleaning up old backups (keeping last 5)..."
cd "$BACKUP_DIR"
ls -t social_media_tracker_backup_*.tar.gz | tail -n +6 | xargs -r rm -f
echo "✅ Cleanup completed"

echo ""
echo "📈 Current backups in $BACKUP_DIR:"
ls -lah social_media_tracker_backup_*.tar.gz 2>/dev/null || echo "No previous backups found"
