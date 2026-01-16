#!/usr/bin/env python3
"""
Database migration script to add the SmartphoneScore table.
This script adds the new table while preserving existing data.
"""

import os
from dotenv import load_dotenv
from flask import Flask
from models import db, User, SearchHistory, SmartphoneScore

def create_app():
    """Create and configure the Flask app for database migration."""
    load_dotenv()
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///sentiment_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    
    return app

def migrate_database():
    """Add the SmartphoneScore table to the existing database."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the new table
            print("Creating SmartphoneScore table...")
            db.create_all()
            print("✅ SmartphoneScore table created successfully!")
            
            # Check if table exists and is accessible
            existing_scores = SmartphoneScore.query.count()
            print(f"📊 Current smartphone scores in database: {existing_scores}")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            raise

if __name__ == '__main__':
    print("🚀 Starting database migration...")
    migrate_database()
    print("✅ Migration completed successfully!")
