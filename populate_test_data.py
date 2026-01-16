#!/usr/bin/env python3
"""
Script to populate test data for the top 10 smartphones feature.
This creates sample smartphone scores to demonstrate the functionality.
"""

import os
from dotenv import load_dotenv
from flask import Flask
from models import db, SmartphoneScore
from datetime import datetime

def create_app():
    """Create and configure the Flask app."""
    load_dotenv()
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///sentiment_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    db.init_app(app)
    return app

def populate_test_data():
    """Add sample smartphone scores for testing."""
    app = create_app()
    
    # Sample smartphone data with realistic scores
    test_smartphones = [
        {
            'product_name': 'iPhone 15 Pro',
            'overall_score': 0.245,
            'positive_count': 156,
            'negative_count': 34,
            'neutral_count': 89,
            'tweets_count': 279
        },
        {
            'product_name': 'Samsung Galaxy S24 Ultra',
            'overall_score': 0.198,
            'positive_count': 142,
            'negative_count': 45,
            'neutral_count': 98,
            'tweets_count': 285
        },
        {
            'product_name': 'Google Pixel 8 Pro',
            'overall_score': 0.167,
            'positive_count': 134,
            'negative_count': 52,
            'neutral_count': 94,
            'tweets_count': 280
        },
        {
            'product_name': 'iPhone 15',
            'overall_score': 0.156,
            'positive_count': 128,
            'negative_count': 48,
            'neutral_count': 102,
            'tweets_count': 278
        },
        {
            'product_name': 'OnePlus 12',
            'overall_score': 0.134,
            'positive_count': 119,
            'negative_count': 56,
            'neutral_count': 105,
            'tweets_count': 280
        },
        {
            'product_name': 'Samsung Galaxy S24',
            'overall_score': 0.123,
            'positive_count': 115,
            'negative_count': 59,
            'neutral_count': 108,
            'tweets_count': 282
        },
        {
            'product_name': 'Xiaomi 14',
            'overall_score': 0.089,
            'positive_count': 98,
            'negative_count': 67,
            'neutral_count': 115,
            'tweets_count': 280
        },
        {
            'product_name': 'iPhone 14 Pro',
            'overall_score': 0.078,
            'positive_count': 95,
            'negative_count': 72,
            'neutral_count': 113,
            'tweets_count': 280
        },
        {
            'product_name': 'Google Pixel 8',
            'overall_score': 0.067,
            'positive_count': 89,
            'negative_count': 75,
            'neutral_count': 116,
            'tweets_count': 280
        },
        {
            'product_name': 'Samsung Galaxy Z Fold 5',
            'overall_score': 0.045,
            'positive_count': 82,
            'negative_count': 78,
            'neutral_count': 120,
            'tweets_count': 280
        },
        {
            'product_name': 'iPhone 13',
            'overall_score': 0.023,
            'positive_count': 76,
            'negative_count': 84,
            'neutral_count': 120,
            'tweets_count': 280
        },
        {
            'product_name': 'Samsung Galaxy A54',
            'overall_score': -0.012,
            'positive_count': 68,
            'negative_count': 92,
            'neutral_count': 120,
            'tweets_count': 280
        }
    ]
    
    with app.app_context():
        try:
            print("🚀 Adding test smartphone data...")
            
            # Clear existing test data
            existing_count = SmartphoneScore.query.count()
            if existing_count > 0:
                print(f"📊 Found {existing_count} existing records")
                choice = input("Do you want to clear existing data? (y/N): ")
                if choice.lower() == 'y':
                    SmartphoneScore.query.delete()
                    db.session.commit()
                    print("🗑️ Cleared existing data")
            
            # Add test data
            for smartphone_data in test_smartphones:
                existing = SmartphoneScore.query.filter_by(product_name=smartphone_data['product_name']).first()
                if not existing:
                    smartphone = SmartphoneScore(
                        product_name=smartphone_data['product_name'],
                        overall_score=smartphone_data['overall_score'],
                        positive_count=smartphone_data['positive_count'],
                        negative_count=smartphone_data['negative_count'],
                        neutral_count=smartphone_data['neutral_count'],
                        tweets_count=smartphone_data['tweets_count'],
                        last_updated=datetime.utcnow(),
                        analysis_count=1
                    )
                    db.session.add(smartphone)
                    print(f"✅ Added: {smartphone_data['product_name']} (Score: {smartphone_data['overall_score']})")
                else:
                    print(f"⚠️ Skipped: {smartphone_data['product_name']} (already exists)")
            
            db.session.commit()
            
            # Verify data
            total_count = SmartphoneScore.query.count()
            top_3 = SmartphoneScore.query.order_by(SmartphoneScore.overall_score.desc()).limit(3).all()
            
            print(f"\n📊 Database now contains {total_count} smartphone records")
            print("🏆 Top 3 smartphones:")
            for i, phone in enumerate(top_3, 1):
                print(f"   {i}. {phone.product_name}: {phone.overall_score}")
            
            print("\n✅ Test data populated successfully!")
            
        except Exception as e:
            print(f"❌ Error populating test data: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    populate_test_data()
