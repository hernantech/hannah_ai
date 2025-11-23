#!/usr/bin/env python3
"""
Database initialization script
Run this to create the necessary tables in your PostgreSQL database
"""

from db import init_db
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        logger.info("Starting database initialization...")
        init_db()
        logger.info("✓ Database initialized successfully!")
        logger.info("Tables created:")
        logger.info("  - pinterest_users")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        exit(1)
