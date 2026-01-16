from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# --- NEW CLASS ADDED ---
class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    search_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign key to link to the User table
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship to easily access the User object from a SearchHistory instance
    user = db.relationship('User', backref=db.backref('search_history', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<SearchHistory {self.product_name} by User {self.user_id}>'

# --- NEW CLASS FOR SMARTPHONE SCORES ---
class SmartphoneScore(db.Model):
    __tablename__ = 'smartphone_scores'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False, unique=True)
    overall_score = db.Column(db.Float, nullable=False)
    positive_count = db.Column(db.Integer, default=0)
    negative_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    tweets_count = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    analysis_count = db.Column(db.Integer, default=1)  # How many times this phone was analyzed

    # NEW: Price and performance metrics
    price_usd = db.Column(db.Float, nullable=True)  # Price in USD
    price_currency = db.Column(db.String(3), default='USD')  # Currency code
    performance_score = db.Column(db.Float, nullable=True)  # Overall performance score (0-100)
    battery_score = db.Column(db.Float, nullable=True)  # Battery performance (0-100)
    camera_score = db.Column(db.Float, nullable=True)  # Camera quality (0-100)
    display_score = db.Column(db.Float, nullable=True)  # Display quality (0-100)
    build_quality_score = db.Column(db.Float, nullable=True)  # Build quality (0-100)
    value_for_money = db.Column(db.Float, nullable=True)  # Value for money ratio (sentiment_score/price)

    def __repr__(self):
        return f'<SmartphoneScore {self.product_name}: {self.overall_score}>'

    def update_score(self, new_results):
        """Update the score with new analysis results"""
        # Calculate weighted average based on analysis count
        total_weight = self.analysis_count + 1

        # Update overall score (weighted average)
        self.overall_score = round(
            (self.overall_score * self.analysis_count + new_results['overall_score']) / total_weight, 3
        )

        # Update sentiment counts (weighted average)
        new_positive = new_results['overall_sentiment']['positive']
        new_negative = new_results['overall_sentiment']['negative']
        new_neutral = new_results['overall_sentiment']['neutral']

        self.positive_count = round(
            (self.positive_count * self.analysis_count + new_positive) / total_weight
        )
        self.negative_count = round(
            (self.negative_count * self.analysis_count + new_negative) / total_weight
        )
        self.neutral_count = round(
            (self.neutral_count * self.analysis_count + new_neutral) / total_weight
        )
        self.tweets_count = round(
            (self.tweets_count * self.analysis_count + new_results['tweets_count']) / total_weight
        )

        self.analysis_count += 1
        self.last_updated = datetime.utcnow()

    @classmethod
    def get_top_smartphones(cls, limit=10):
        """Get top smartphones by overall sentiment score"""
        return cls.query.order_by(cls.overall_score.desc()).limit(limit).all()

    @classmethod
    def get_top_performance_smartphones(cls, limit=10):
        """Get top smartphones by performance score"""
        return cls.query.filter(cls.performance_score.isnot(None)).order_by(cls.performance_score.desc()).limit(limit).all()

    @classmethod
    def get_top_battery_smartphones(cls, limit=10):
        """Get top smartphones by battery score"""
        return cls.query.filter(cls.battery_score.isnot(None)).order_by(cls.battery_score.desc()).limit(limit).all()

    @classmethod
    def get_top_camera_smartphones(cls, limit=10):
        """Get top smartphones by camera score"""
        return cls.query.filter(cls.camera_score.isnot(None)).order_by(cls.camera_score.desc()).limit(limit).all()

    @classmethod
    def get_top_value_smartphones(cls, limit=10):
        """Get top smartphones by value for money"""
        return cls.query.filter(cls.value_for_money.isnot(None)).order_by(cls.value_for_money.desc()).limit(limit).all()