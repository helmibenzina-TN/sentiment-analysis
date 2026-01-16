#!/usr/bin/env python3
"""
Database initialization script for the sentiment analysis app.
This script creates the SQLite database and all necessary tables.
"""

import os
from dotenv import load_dotenv
from flask import Flask
from models import db, User, SearchHistory

def create_app():
    """Create and configure the Flask app for database initialization."""
    load_dotenv()
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///sentiment_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    
    return app

def init_database():
    """Initialize the database with all tables."""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables (if they exist) and recreate them
        db.drop_all()
        db.create_all()
        
        print("Database tables created successfully!")
        
        # Create a default admin user for testing
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("Default admin user created:")
        print("  Username: admin")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("\nDatabase initialization complete!")

if __name__ == '__main__':
    init_database()
