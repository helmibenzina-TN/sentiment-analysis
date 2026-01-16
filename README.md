# Sentiment Analysis Web App for Smartphones

## Overview
This project is a comprehensive web application designed to analyze public sentiment regarding smartphones. By leveraging natural language processing (NLP) and external APIs (Twitter, Google), the application provides real-time insights into user opinions, helping to understand market trends and product reception.

## Features
- **Real-time Sentiment Analysis**: Analyzes tweets and user feedback using the VADER lexicon.
- **Aspect-Based Analysis**: Breaks down sentiment by specific features (Battery, Camera, Performance, Design, Price).
- **Comparative Analysis**: Allows side-by-side comparison of two different smartphone models.
- **Visualizations**: Interactive charts and word clouds to display sentiment distribution and key themes.
- **User Management**: Secure authentication system with search history tracking.

## Architecture
The application follows a modular MVC architecture using Flask:
- **Backend**: Flask (Python) with SQLAlchemy for ORM.
- **Frontend**: HTML/CSS/JS with Jinja2 templates.
- **Database**: SQLite (Development) / MySQL or PostgreSQL (Production).
- **External APIs**: Twitter API v2 (Tweets), Google Custom Search API (Images/Info).

## Installation

### Prerequisites
- Python 3.8+
- Twitter Developer Account (Bearer Token)
- Google Cloud Console Project (API Key & Custom Search Engine ID)

### Setup
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sentiment-analysis
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your_secret_key
   DATABASE_URI=sqlite:///sentiment_app.db
   TWITTER_BEARER_TOKEN=your_twitter_token
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_cse_id
   ```

5. **Initialize Database:**
   ```bash
   python init_db.py
   ```

6. **Run the Application:**
   ```bash
   python app.py
   ```
   Access the app at `http://localhost:5000`.

## Usage
1. Register/Login to access the dashboard.
2. Enter a smartphone name (e.g., "iPhone 15") in the search bar.
3. View the sentiment analysis results, including charts and word clouds.
4. Use the comparison feature to analyze two phones simultaneously.

## License
[License Name]
