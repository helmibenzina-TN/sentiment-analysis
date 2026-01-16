#!/usr/bin/env python3
"""
Database migration script to add price and performance fields to SmartphoneScore table.
"""

import os
from dotenv import load_dotenv
from flask import Flask
from models import db, SmartphoneScore
import random  # For generating test data

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
    """Add price and performance fields to SmartphoneScore table."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create or update the table with new columns
            print("Updating SmartphoneScore table with price and performance fields...")
            db.create_all()
            print("✅ SmartphoneScore table updated successfully!")
            
            # Check if table exists and is accessible
            existing_scores = SmartphoneScore.query.count()
            print(f"📊 Current smartphone scores in database: {existing_scores}")
            
            # Add sample price and performance data for testing
            if existing_scores > 0:
                print("Adding sample price and performance data...")
                
                # Sample price ranges for different smartphone tiers
                price_ranges = {
                    'iPhone 15 Pro': (999, 1099),
                    'iPhone 15 Pro Max': (1099, 1199),
                    'iPhone 15': (799, 899),
                    'iPhone 14 Pro': (899, 999),
                    'iPhone 14': (699, 799),
                    'iPhone 13': (599, 699),
                    'Samsung Galaxy S24 Ultra': (1199, 1299),
                    'Samsung Galaxy S24+': (999, 1099),
                    'Samsung Galaxy S24': (799, 899),
                    'Samsung Galaxy S23': (699, 799),
                    'Samsung Galaxy Z Fold 5': (1799, 1899),
                    'Samsung Galaxy Z Flip 5': (999, 1099),
                    'Google Pixel 8 Pro': (899, 999),
                    'Google Pixel 8': (699, 799),
                    'Google Pixel 7': (599, 699),
                    'OnePlus 12': (799, 899),
                    'OnePlus 11': (699, 799),
                    'Xiaomi 14': (799, 899),
                    'Xiaomi 13': (699, 799),
                    'Samsung Galaxy A54': (399, 499)
                }
                
                # Default price range for other smartphones
                default_price_range = (499, 899)
                
                # Update each smartphone with price and performance data
                smartphones = SmartphoneScore.query.all()
                for phone in smartphones:
                    # Set price based on model or random within default range
                    price_range = price_ranges.get(phone.product_name, default_price_range)
                    phone.price_usd = round(random.uniform(price_range[0], price_range[1]), 2)
                    
                    # Set performance metrics (random values for testing)
                    # Higher-end phones generally get better scores
                    is_premium = phone.price_usd > 800
                    is_mid_range = 500 <= phone.price_usd <= 800
                    
                    base_performance = 80 if is_premium else (70 if is_mid_range else 60)
                    base_camera = 85 if is_premium else (75 if is_mid_range else 65)
                    base_battery = 75 if is_premium else (80 if is_mid_range else 70)  # Mid-range often has better battery
                    base_display = 90 if is_premium else (80 if is_mid_range else 70)
                    base_build = 85 if is_premium else (75 if is_mid_range else 65)
                    
                    # Add some randomness
                    phone.performance_score = min(100, round(base_performance + random.uniform(-5, 10), 1))
                    phone.camera_score = min(100, round(base_camera + random.uniform(-8, 8), 1))
                    phone.battery_score = min(100, round(base_battery + random.uniform(-10, 15), 1))
                    phone.display_score = min(100, round(base_display + random.uniform(-5, 5), 1))
                    phone.build_quality_score = min(100, round(base_build + random.uniform(-5, 5), 1))
                    
                    # Calculate value for money (sentiment score / price * 1000)
                    # Higher is better - good sentiment at lower price
                    if phone.overall_score > 0:  # Only for positive sentiment
                        phone.value_for_money = round((phone.overall_score / phone.price_usd) * 1000, 2)
                    else:
                        phone.value_for_money = 0
                    
                    print(f"✅ Updated {phone.product_name}: ${phone.price_usd}, Performance: {phone.performance_score}")
                
                db.session.commit()
                print("✅ Sample data added successfully!")
                
                # Show top 3 by performance
                top_performance = SmartphoneScore.get_top_performance_smartphones(3)
                print("\n🏆 Top 3 by Performance:")
                for i, phone in enumerate(top_performance, 1):
                    print(f"   {i}. {phone.product_name}: {phone.performance_score}")
                
                # Show top 3 by value
                top_value = SmartphoneScore.get_top_value_smartphones(3)
                print("\n💰 Top 3 by Value for Money:")
                for i, phone in enumerate(top_value, 1):
                    print(f"   {i}. {phone.product_name}: {phone.value_for_money}")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("🚀 Starting database migration for price and performance fields...")
    migrate_database()
    print("✅ Migration completed successfully!")
