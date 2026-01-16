"""
REST API endpoints for the Sentiment Analysis application.
Provides JSON responses for the Angular frontend.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    create_refresh_token, get_jwt
)
from models import db, User, SearchHistory, SmartphoneScore
from app_backend.sentiment_logic import get_product_sentiment_analysis
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# ==================== Authentication Endpoints ====================

@api.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 409
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {user.username}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500


@api.route('/auth/login', methods=['POST'])
def login():
    """Login user and return JWT tokens"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'username': user.username, 'email': user.email}
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        
        logger.info(f"User logged in: {user.username}")
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500


@api.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = int(get_jwt_identity())
        new_access_token = create_access_token(identity=str(current_user_id))
        
        return jsonify({'access_token': new_access_token}), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({'error': 'Token refresh failed'}), 500


@api.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 200
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({'error': 'Failed to get user info'}), 500


# ==================== Sentiment Analysis Endpoints ====================

@api.route('/sentiment/analyze', methods=['GET'])
@jwt_required()
def analyze_sentiment():
    """Analyze sentiment for one or two products"""
    try:
        current_user_id = int(get_jwt_identity())
        product1 = request.args.get('product1')
        product2 = request.args.get('product2')
        
        if not product1:
            return jsonify({'error': 'product1 parameter is required'}), 400
        
        # Analyze first product
        logger.info(f"Analyzing sentiment for: {product1}")
        results1 = get_product_sentiment_analysis(product1)
        
        # Convert relative URLs to absolute URLs for Angular frontend
        if results1.get('word_cloud_url'):
            results1['word_cloud_url'] = request.host_url.rstrip('/') + results1['word_cloud_url']
        if results1.get('product_image_url') and results1['product_image_url'].startswith('/'):
            results1['product_image_url'] = request.host_url.rstrip('/') + results1['product_image_url']
        
        # Save to search history
        search_entry = SearchHistory(product_name=product1, user_id=current_user_id)
        db.session.add(search_entry)
        
        # Save/update smartphone score
        existing_score = SmartphoneScore.query.filter_by(product_name=product1).first()
        if existing_score:
            existing_score.update_score(results1)
        else:
            new_score = SmartphoneScore(
                product_name=product1,
                overall_score=results1['overall_score'],
                positive_count=results1['overall_sentiment']['positive'],
                negative_count=results1['overall_sentiment']['negative'],
                neutral_count=results1['overall_sentiment']['neutral'],
                tweets_count=results1['tweets_count']
            )
            db.session.add(new_score)
        
        response_data = {
            'product1': {
                'name': product1,
                'results': results1
            }
        }
        
        # Analyze second product if provided
        if product2 and product2.strip():
            logger.info(f"Analyzing sentiment for: {product2}")
            results2 = get_product_sentiment_analysis(product2)
            
            # Convert relative URLs to absolute URLs for Angular frontend
            if results2.get('word_cloud_url'):
                results2['word_cloud_url'] = request.host_url.rstrip('/') + results2['word_cloud_url']
            if results2.get('product_image_url') and results2['product_image_url'].startswith('/'):
                results2['product_image_url'] = request.host_url.rstrip('/') + results2['product_image_url']
            
            # Save to search history
            search_entry2 = SearchHistory(product_name=product2, user_id=current_user_id)
            db.session.add(search_entry2)
            
            # Save/update smartphone score
            existing_score2 = SmartphoneScore.query.filter_by(product_name=product2).first()
            if existing_score2:
                existing_score2.update_score(results2)
            else:
                new_score2 = SmartphoneScore(
                    product_name=product2,
                    overall_score=results2['overall_score'],
                    positive_count=results2['overall_sentiment']['positive'],
                    negative_count=results2['overall_sentiment']['negative'],
                    neutral_count=results2['overall_sentiment']['neutral'],
                    tweets_count=results2['tweets_count']
                )
                db.session.add(new_score2)
            
            response_data['product2'] = {
                'name': product2,
                'results': results2
            }
        
        db.session.commit()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Sentiment analysis failed'}), 500


# ==================== Smartphone Rankings Endpoints ====================

@api.route('/smartphones/top', methods=['GET'])
@jwt_required()
def get_top_smartphones():
    """Get top smartphones by sentiment score"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # Cap at 50
        
        top_smartphones = SmartphoneScore.get_top_smartphones(limit)
        
        return jsonify({
            'smartphones': [{
                'product_name': phone.product_name,
                'overall_score': phone.overall_score,
                'positive_count': phone.positive_count,
                'negative_count': phone.negative_count,
                'neutral_count': phone.neutral_count,
                'tweets_count': phone.tweets_count,
                'price_usd': phone.price_usd,
                'performance_score': phone.performance_score,
                'battery_score': phone.battery_score,
                'camera_score': phone.camera_score,
                'value_for_money': phone.value_for_money,
                'last_updated': phone.last_updated.isoformat() if phone.last_updated else None
            } for phone in top_smartphones]
        }), 200
        
    except Exception as e:
        logger.error(f"Get top smartphones error: {e}")
        return jsonify({'error': 'Failed to fetch top smartphones'}), 500


# ==================== Search History Endpoints ====================

@api.route('/history', methods=['GET'])
@jwt_required()
def get_search_history():
    """Get user's search history with pagination"""
    try:
        current_user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # Cap at 100
        
        history_pagination = SearchHistory.query.filter_by(user_id=current_user_id)\
            .order_by(SearchHistory.search_time.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'history': [{
                'id': item.id,
                'product_name': item.product_name,
                'search_time': item.search_time.isoformat()
            } for item in history_pagination.items],
            'total': history_pagination.total,
            'pages': history_pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': history_pagination.has_next,
            'has_prev': history_pagination.has_prev
        }), 200
        
    except Exception as e:
        logger.error(f"Get search history error: {e}")
        return jsonify({'error': 'Failed to fetch search history'}), 500


@api.route('/history/recent', methods=['GET'])
@jwt_required()
def get_recent_history():
    """Get recent unique searches for sidebar"""
    try:
        current_user_id = int(get_jwt_identity())
        limit = request.args.get('limit', 5, type=int)
        
        # Get distinct product names ordered by most recent search
        recent_searches = db.session.query(SearchHistory.product_name)\
            .filter_by(user_id=current_user_id)\
            .distinct()\
            .order_by(db.func.max(SearchHistory.search_time).desc())\
            .group_by(SearchHistory.product_name)\
            .limit(limit).all()
        
        return jsonify({
            'recent_searches': [item[0] for item in recent_searches]
        }), 200
        
    except Exception as e:
        logger.error(f"Get recent history error: {e}")
        return jsonify({'error': 'Failed to fetch recent history'}), 500


# ==================== Performance Rankings Endpoints ====================

@api.route('/performance/rankings', methods=['GET'])
@jwt_required()
def get_performance_rankings():
    """Get performance rankings by category"""
    try:
        category = request.args.get('category', 'overall')
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)
        
        if category == 'performance':
            smartphones = SmartphoneScore.get_top_performance_smartphones(limit)
        elif category == 'battery':
            smartphones = SmartphoneScore.get_top_battery_smartphones(limit)
        elif category == 'camera':
            smartphones = SmartphoneScore.get_top_camera_smartphones(limit)
        elif category == 'value':
            smartphones = SmartphoneScore.get_top_value_smartphones(limit)
        else:  # overall
            smartphones = SmartphoneScore.get_top_smartphones(limit)
        
        return jsonify({
            'category': category,
            'smartphones': [{
                'product_name': phone.product_name,
                'overall_score': phone.overall_score,
                'performance_score': phone.performance_score,
                'battery_score': phone.battery_score,
                'camera_score': phone.camera_score,
                'value_for_money': phone.value_for_money,
                'price_usd': phone.price_usd,
                'positive_count': phone.positive_count,
                'negative_count': phone.negative_count,
                'neutral_count': phone.neutral_count
            } for phone in smartphones]
        }), 200
        
    except Exception as e:
        logger.error(f"Get performance rankings error: {e}")
        return jsonify({'error': 'Failed to fetch performance rankings'}), 500


@api.route('/performance/all-categories', methods=['GET'])
@jwt_required()
def get_all_performance_categories():
    """Get top smartphones for all performance categories"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)
        
        return jsonify({
            'overall': [{
                'product_name': phone.product_name,
                'overall_score': phone.overall_score,
                'positive_count': phone.positive_count,
                'negative_count': phone.negative_count,
                'neutral_count': phone.neutral_count
            } for phone in SmartphoneScore.get_top_smartphones(limit)],
            'performance': [{
                'product_name': phone.product_name,
                'performance_score': phone.performance_score,
                'overall_score': phone.overall_score
            } for phone in SmartphoneScore.get_top_performance_smartphones(limit)],
            'battery': [{
                'product_name': phone.product_name,
                'battery_score': phone.battery_score,
                'overall_score': phone.overall_score
            } for phone in SmartphoneScore.get_top_battery_smartphones(limit)],
            'camera': [{
                'product_name': phone.product_name,
                'camera_score': phone.camera_score,
                'overall_score': phone.overall_score
            } for phone in SmartphoneScore.get_top_camera_smartphones(limit)],
            'value': [{
                'product_name': phone.product_name,
                'value_for_money': phone.value_for_money,
                'price_usd': phone.price_usd,
                'overall_score': phone.overall_score
            } for phone in SmartphoneScore.get_top_value_smartphones(limit)]
        }), 200
        
    except Exception as e:
        logger.error(f"Get all performance categories error: {e}")
        return jsonify({'error': 'Failed to fetch performance data'}), 500


# ==================== Health Check ====================

@api.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
