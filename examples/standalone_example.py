"""
Standalone example showing LogLens usage without web frameworks.
"""

import logging
from datetime import datetime
from loglensx import LogParser, LogAnalyzer
from loglensx.visualizers import ChartGenerator, TableGenerator
import os
import json

# Setup logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"log_file_{datetime.now().strftime('%Y-%m-%d')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Create various loggers for demonstration
app_logger = logging.getLogger("myapp")
db_logger = logging.getLogger("myapp.database")
api_logger = logging.getLogger("myapp.api")
cache_logger = logging.getLogger("myapp.cache")


def generate_sample_logs():
    """Generate some sample log entries for demonstration."""
    print("Generating sample logs...")
    
    app_logger.info("Application started")
    api_logger.info("API server listening on port 8000")
    db_logger.info("Connected to database")
    cache_logger.info("Cache initialized")
    
    # Simulate some errors and warnings
    for i in range(5):
        db_logger.warning(f"Database query slow: {i*100}ms")
        api_logger.info(f"Request #{i}: GET /users - 200 OK")
    
    api_logger.error("Failed to authenticate user: invalid token")
    cache_logger.warning("Cache hit rate below 50%")
    db_logger.error("Connection timeout after 30 seconds")
    
    app_logger.info("All sample logs generated")
    print("✓ Sample logs generated\n")


def display_summary(analyzer):
    """Display log summary."""
    print("="*60)
    print("LogLens Summary")
    print("="*60)
    
    summary = analyzer.get_log_summary()
    for key, value in summary.items():
        print(f"{key:20}: {value}")
    
    print("="*60 + "\n")


def display_level_statistics(analyzer):
    """Display logs by level."""
    print("Log Level Statistics:")
    print("-" * 40)
    
    stats = analyzer.get_level_statistics()
    for level, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * (count // 5) if count > 0 else ""
        print(f"{level:10} {count:5} {bar}")
    print()


def display_top_loggers(analyzer):
    """Display top loggers."""
    print("Top Loggers:")
    print("-" * 40)
    
    top_loggers = analyzer.get_top_loggers(limit=10)
    for i, (logger_name, count) in enumerate(top_loggers, 1):
        print(f"{i:2}. {logger_name:30} {count:5} logs")
    print()


def display_recent_errors(analyzer):
    """Display recent errors."""
    print("Recent Errors:")
    print("-" * 60)
    
    errors = analyzer.get_recent_errors(limit=10)
    for i, error in enumerate(errors, 1):
        print(f"{i}. [{error.get('timestamp', 'N/A')}] {error.get('message', 'N/A')[:50]}")
    print()


def generate_visualizations(analyzer):
    """Generate and save visualizations as JSON."""
    print("Generating Visualizations:")
    print("-" * 40)
    
    # Get data
    level_stats = analyzer.get_level_statistics()
    top_loggers = analyzer.get_top_loggers(limit=10)
    error_freq = analyzer.get_error_frequency(hours=24)
    
    # Generate charts
    level_chart = ChartGenerator.plotly_level_distribution(level_stats)
    error_timeline = ChartGenerator.plotly_error_timeline(error_freq)
    top_loggers_chart = ChartGenerator.plotly_top_loggers(top_loggers)
    
    # Save to files
    os.makedirs("visualizations", exist_ok=True)
    
    with open("visualizations/level_distribution.json", "w") as f:
        f.write(level_chart)
    print("✓ Saved: visualizations/level_distribution.json")
    
    with open("visualizations/error_timeline.json", "w") as f:
        f.write(error_timeline)
    print("✓ Saved: visualizations/error_timeline.json")
    
    with open("visualizations/top_loggers.json", "w") as f:
        f.write(top_loggers_chart)
    print("✓ Saved: visualizations/top_loggers.json")
    print()


def search_logs(parser):
    """Demonstrate log searching."""
    print("Searching Logs:")
    print("-" * 40)
    
    # Search for "error"
    results = parser.search_logs("error", limit=10)
    print(f"Found {len(results)} results for 'error':")
    for i, result in enumerate(results[:3], 1):
        print(f"{i}. {result.get('message', 'N/A')[:60]}")
    print()


def filter_logs(analyzer):
    """Demonstrate log filtering."""
    print("Filtering Logs:")
    print("-" * 40)
    
    # Filter by level
    errors = analyzer.filter_logs(level="ERROR", limit=10)
    print(f"ERROR logs: {len(errors)}")
    
    warnings = analyzer.filter_logs(level="WARNING", limit=10)
    print(f"WARNING logs: {len(warnings)}")
    
    # Filter by logger
    db_logs = analyzer.filter_logs(logger="database", limit=10)
    print(f"Database logs: {len(db_logs)}")
    print()


def main():
    """Main function."""
    print("\n" + "="*60)
    print("LogLens Standalone Example")
    print("="*60 + "\n")
    
    # Generate sample logs
    generate_sample_logs()
    
    # Create parser and analyzer
    parser = LogParser(log_dir="logs")
    analyzer = LogAnalyzer(parser)
    
    # Display summary and statistics
    display_summary(analyzer)
    display_level_statistics(analyzer)
    display_top_loggers(analyzer)
    display_recent_errors(analyzer)
    
    # Generate visualizations
    generate_visualizations(analyzer)
    
    # Search and filter
    search_logs(parser)
    filter_logs(analyzer)
    
    print("="*60)
    print("Example completed successfully!")
    print("Check 'visualizations/' directory for generated charts")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
