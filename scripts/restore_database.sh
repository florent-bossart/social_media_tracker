#!/bin/bash

# Database Restore Script for Social Media Tracker
# Restores a compressed database backup

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"
TEMP_DIR="/tmp/db_restore_$(date +%s)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to cleanup temporary files
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        print_status "Cleaning up temporary files..."
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

# Help function
show_help() {
    cat << EOF
Database Restore Script for Social Media Tracker

Usage: $0 [OPTIONS] [BACKUP_FILE]

OPTIONS:
    -h, --help          Show this help message
    -d, --docker        Use Docker PostgreSQL container (default: auto-detect)
    -l, --local         Use local PostgreSQL installation
    -f, --force         Skip confirmation prompts
    -v, --verbose       Enable verbose output
    --host HOST         Database host (default: localhost)
    --port PORT         Database port (default: 5432)
    --user USER         Database user (default: from .env or postgres)
    --db-name NAME      Database name to restore to (default: from .env)

EXAMPLES:
    $0                                  # Restore latest backup (auto-detect setup)
    $0 backup_20240622_120000.tar.gz   # Restore specific backup file
    $0 --docker --force                # Force restore using Docker, no prompts
    $0 --local --host localhost        # Restore to local PostgreSQL

If no backup file is specified, the script will use the latest available backup.
EOF
}

# Parse command line arguments
BACKUP_FILE=""
USE_DOCKER=""
FORCE=false
VERBOSE=false
DB_HOST=""
DB_PORT=""
DB_USER=""
DB_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--docker)
            USE_DOCKER=true
            shift
            ;;
        -l|--local)
            USE_DOCKER=false
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --host)
            DB_HOST="$2"
            shift 2
            ;;
        --port)
            DB_PORT="$2"
            shift 2
            ;;
        --user)
            DB_USER="$2"
            shift 2
            ;;
        --db-name)
            DB_NAME="$2"
            shift 2
            ;;
        -*)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            if [ -z "$BACKUP_FILE" ]; then
                BACKUP_FILE="$1"
            else
                print_error "Multiple backup files specified"
                exit 1
            fi
            shift
            ;;
    esac
done

print_status "🚀 Starting database restore process..."

# Load environment variables if available
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
    print_status "Loaded configuration from .env file"
else
    print_warning ".env file not found. Using defaults."
fi

# Set defaults from environment or fallback values
# Detect execution environment for correct port configuration
if [ -f /.dockerenv ] || [ -n "${DOCKER_CONTAINER_ENV}" ]; then
    # Running inside Docker container
    DB_HOST=${DB_HOST:-${WAREHOUSE_HOST:-postgres}}
    DB_PORT=${DB_PORT:-${WAREHOUSE_PORT:-5432}}
    EXECUTION_CONTEXT="container"
    print_status "🐳 Running inside Docker container"
else
    # Running locally
    DB_HOST=${DB_HOST:-${WAREHOUSE_HOST:-localhost}}
    DB_PORT=${DB_PORT:-${WAREHOUSE_PORT:-5434}}
    EXECUTION_CONTEXT="local"
    print_status "💻 Running locally"
fi

DB_USER=${DB_USER:-${WAREHOUSE_USER:-postgres}}
DB_NAME=${DB_NAME:-${WAREHOUSE_DB:-social_media_tracker}}

# Docker container name
DOCKER_CONTAINER="social_media_tracker-postgres-1"

# Determine backup file to use
if [ -z "$BACKUP_FILE" ]; then
    if [ -f "$BACKUP_DIR/latest_backup.tar.gz" ]; then
        BACKUP_FILE="$BACKUP_DIR/latest_backup.tar.gz"
        print_status "Using latest backup: $(readlink -f "$BACKUP_FILE")"
    else
        print_error "No backup file specified and no latest backup found"
        print_error "Available backups in $BACKUP_DIR:"
        ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null || echo "No backups found"
        exit 1
    fi
elif [ ! -f "$BACKUP_FILE" ]; then
    # Try to find the file in the backup directory
    if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
        BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
    else
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
fi

# Get absolute path
BACKUP_FILE=$(readlink -f "$BACKUP_FILE")
print_status "Using backup file: $BACKUP_FILE"

# Auto-detect Docker if not specified
if [ -z "$USE_DOCKER" ]; then
    if docker ps | grep -q "$DOCKER_CONTAINER"; then
        USE_DOCKER=true
        print_status "🐳 Auto-detected PostgreSQL running in Docker container"
    else
        USE_DOCKER=false
        print_status "💻 Auto-detected local PostgreSQL installation"
    fi
fi

# Verify PostgreSQL availability
if [ "$USE_DOCKER" = true ]; then
    if ! docker ps | grep -q "$DOCKER_CONTAINER"; then
        print_error "Docker container $DOCKER_CONTAINER is not running"
        print_status "Start it with: docker-compose up postgres -d"
        exit 1
    fi
else
    if ! command -v psql &> /dev/null; then
        print_error "psql command not found. Please install PostgreSQL client"
        exit 1
    fi
fi

# Show restore configuration
echo ""
print_status "📋 Restore Configuration:"
echo "   Database Host: $DB_HOST:$DB_PORT"
echo "   Database User: $DB_USER"
echo "   Database Name: $DB_NAME"
echo "   Backup File: $(basename "$BACKUP_FILE")"
echo "   Using Docker: $USE_DOCKER"
echo "   Backup Size: $(du -h "$BACKUP_FILE" | cut -f1)"

# Confirmation prompt
if [ "$FORCE" = false ]; then
    echo ""
    print_warning "⚠️  WARNING: This will DROP and RECREATE the database '$DB_NAME'"
    print_warning "All existing data will be LOST!"
    echo ""
    read -p "Are you sure you want to continue? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Restore cancelled by user"
        exit 0
    fi
fi

# Create temporary directory and extract backup
print_status "📤 Extracting backup archive..."
mkdir -p "$TEMP_DIR"
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Find the SQL dump file
SQL_FILE=$(find "$TEMP_DIR" -name "*.sql" | head -n 1)
if [ -z "$SQL_FILE" ]; then
    print_error "No SQL dump file found in backup archive"
    exit 1
fi

print_status "Found SQL dump: $(basename "$SQL_FILE")"

# Show backup info if available
INFO_FILE=$(find "$TEMP_DIR" -name "backup_info.txt" | head -n 1)
if [ -n "$INFO_FILE" ] && [ "$VERBOSE" = true ]; then
    echo ""
    print_status "📋 Backup Information:"
    cat "$INFO_FILE"
    echo ""
fi

# Perform the restore
print_status "🔄 Restoring database..."

if [ "$EXECUTION_CONTEXT" = "container" ]; then
    # Running inside container - use psql directly
    export PGPASSWORD="${WAREHOUSE_PASSWORD}"
    if [ "$VERBOSE" = true ]; then
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres < "$SQL_FILE"
    else
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres < "$SQL_FILE" > /dev/null 2>&1
    fi
elif [ "$USE_DOCKER" = true ]; then
    # Running locally but PostgreSQL is in Docker - use docker exec
    if [ "$VERBOSE" = true ]; then
        docker exec -i "$DOCKER_CONTAINER" psql -U "$DB_USER" -d postgres < "$SQL_FILE"
    else
        docker exec -i "$DOCKER_CONTAINER" psql -U "$DB_USER" -d postgres < "$SQL_FILE" > /dev/null 2>&1
    fi
else
    # Running locally with local PostgreSQL
    export PGPASSWORD="${WAREHOUSE_PASSWORD}"
    if [ "$VERBOSE" = true ]; then
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres < "$SQL_FILE"
    else
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres < "$SQL_FILE" > /dev/null 2>&1
    fi
fi

# Verify restore
print_status "✅ Verifying restore..."

if [ "$EXECUTION_CONTEXT" = "container" ]; then
    # Running inside container - use psql directly
    export PGPASSWORD="${WAREHOUSE_PASSWORD}"
    TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog');" | tr -d ' ')
elif [ "$USE_DOCKER" = true ]; then
    # Running locally but PostgreSQL is in Docker - use docker exec
    TABLE_COUNT=$(docker exec "$DOCKER_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog');" | tr -d ' ')
else
    # Running locally with local PostgreSQL
    export PGPASSWORD="${WAREHOUSE_PASSWORD}"
    TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog');" | tr -d ' ')
fi

if [ "$TABLE_COUNT" -gt 0 ]; then
    print_success "🎉 Database restored successfully!"
    print_success "📊 Restored $TABLE_COUNT tables"
else
    print_error "❌ Restore verification failed - no tables found"
    exit 1
fi

# Show next steps
echo ""
print_status "🎯 Next Steps:"
echo "   1. Verify your .env file has correct database credentials"
echo "   2. Start the application: docker-compose up"  
echo "   3. Access Airflow at: http://localhost:8080"
echo "   4. Access Dashboard at: http://localhost:8501"
echo ""

# Show README if available
README_FILE=$(find "$TEMP_DIR" -name "README_RESTORE.md" | head -n 1)
if [ -n "$README_FILE" ]; then
    print_status "📖 For detailed instructions, see: $(basename "$README_FILE")"
    if [ "$VERBOSE" = true ]; then
        echo ""
        cat "$README_FILE"
    fi
fi

print_success "✨ Database restore completed successfully!"
