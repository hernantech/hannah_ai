#!/usr/bin/env python3
"""
Helper script to print the DATABASE_URL
Deploy this temporarily to get your production database URL
"""
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')
if db_url:
    print("DATABASE_URL found:")
    print(db_url)
else:
    print("DATABASE_URL not set")
