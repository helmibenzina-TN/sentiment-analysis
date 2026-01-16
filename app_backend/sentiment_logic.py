import os
import nltk
import json # For loading local tweet datasets
import time # For caching
# ---- BEGIN NLTK Path Configuration ----
project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
custom_nltk_data_path = os.path.join(project_root_dir, 'nltk_data')
if os.path.isdir(custom_nltk_data_path):
    if custom_nltk_data_path not in nltk.data.path:
        nltk.data.path.insert(0, custom_nltk_data_path)
else:
    print(f"WARNING (sentiment_logic): Custom NLTK data path does not exist: {custom_nltk_data_path}.")
# ---- END NLTK Path Configuration ----

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import random
from googleapiclient.discovery import build
import logging
import requests 

# --- NEW: Word Cloud Generation ---
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
# --- END NEW ---

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
else:
    logger.setLevel(logging.DEBUG)

try:
    sid = SentimentIntensityAnalyzer()
except LookupError: 
    logger.info("Downloading VADER lexicon for NLTK...")
    nltk.download('vader_lexicon', download_dir=custom_nltk_data_path if os.path.isdir(custom_nltk_data_path) else None, quiet=True)
    sid = SentimentIntensityAnalyzer()
try:
    nltk.data.find('tokenizers/punkt')
except LookupError: 
    logger.info("Downloading Punkt tokenizer for NLTK...")
    nltk.download('punkt', download_dir=custom_nltk_data_path if os.path.isdir(custom_nltk_data_path) else None, quiet=True)

ASPECTS_KEYWORDS = {
    "battery": ["battery", "power", "charge", "life", "charging", "mah", "backup", "lasts", "duration"],
    "camera": ["camera", "photo", "picture", "lens", "image", "video", "shot", "sensor", "zoom", "pixel", "focus", "megapixel", "mp", "photos", "videos", "photograph"],
    "screen": ["screen", "display", "resolution", "amoled", "lcd", "brightness", "hdr", "refresh rate", "size", "oled", "dynamic island", "proMotion"],
    "performance": ["performance", "speed", "fast", "slow", "lag", "chip", "processor", "ram", "gaming", "smooth", "a16", "a17", "benchmark"],
    "price": ["price", "cost", "value", "cheap", "expensive", "budget", "affordable", "money", "worth", "deal"],
    "design": ["design", "look", "feel", "build", "aesthetic", "style", "beautiful", "ugly", "premium", "color", "material", "titanium", "action button"],
    "software": ["software", "os", "ui", "update", "app", "bloatware", "interface", "ios", "ios 17", "siri"],
    "sound": ["sound", "audio", "speaker", "music", "volume", "microphone", "call quality", "spatial audio"],
    "durability": ["durability", "strong", "robust", "scratch", "waterproof", "resistant", "ip68", "ceramic shield"],
    "features": ["feature", "functionality", "fingerprint", "face id", "nfc", "5g", "wireless charging", "storage", "usb-c", "connectivity"],
    "heating": ["heat", "hot", "warm", "overheating", "cool"],
    "overall": ["love it", "hate it", "amazing", "disappointed", "best phone", "worst phone", "recommend", "impressed", "regret"]
}

CACHE_DIR = os.path.join(project_root_dir, "api_cache")
CACHE_EXPIRY_SECONDS = 3600 
if not os.path.exists(CACHE_DIR):
    try: os.makedirs(CACHE_DIR)
    except OSError as e: logger.error(f"Could not create cache directory {CACHE_DIR}: {e}")

# --- NEW: Word Cloud Directory ---
WORDCLOUD_DIR = os.path.join(project_root_dir, 'static', 'generated_images')
if not os.path.exists(WORDCLOUD_DIR):
    try: os.makedirs(WORDCLOUD_DIR)
    except OSError as e: logger.error(f"Could not create wordcloud directory {WORDCLOUD_DIR}: {e}")

def get_cached_data(cache_key):
    if not os.path.exists(CACHE_DIR): return None
    cache_file = os.path.join(CACHE_DIR, f"{cache_key.replace(' ', '_').replace('/', '_')[:50]}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f: data = json.load(f)
            if time.time() - data.get('timestamp', 0) < CACHE_EXPIRY_SECONDS:
                logger.debug(f"Serving cached data for key '{cache_key}'")
                return data.get('content')
            else: logger.debug(f"Cache expired for key '{cache_key}'")
        except Exception as e: logger.error(f"Error reading cache for {cache_key}: {e}")
    return None

def cache_data(cache_key, content):
    if not os.path.exists(CACHE_DIR):
        try: os.makedirs(CACHE_DIR)
        except OSError as e: logger.error(f"Could not create cache directory {CACHE_DIR} for writing: {e}"); return
    cache_file = os.path.join(CACHE_DIR, f"{cache_key.replace(' ', '_').replace('/', '_')[:50]}.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f: json.dump({'timestamp': time.time(), 'content': content}, f, ensure_ascii=False, indent=2)
        logger.debug(f"Cached data for key '{cache_key}'")
    except Exception as e: logger.error(f"Error writing cache for {cache_key}: {e}")

def test_google_search_api_access():
    api_key = os.getenv("GOOGLE_API_KEY"); cse_id = os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cse_id: return False, "Google API Key or CSE ID not set."
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q="test", cx=cse_id, num=1).execute()
        if 'items' in res: return True, "Google Custom Search API access successful."
        elif 'error' in res: return False, f"Google API Error: {res['error'].get('message', 'Unknown')}"
        else: return True, "Google API call made, no items (check CSE config)."
    except Exception as e: return False, f"Google API Error: {str(e)}"

def fetch_google_search_result(full_query, product_name_for_log, search_type=None):
    cache_key = f"google_{search_type or 'web'}_{full_query.replace(' ', '_')[:50]}"
    cached_content = get_cached_data(cache_key)
    if cached_content is not None: return cached_content
    api_key = os.getenv("GOOGLE_API_KEY"); cse_id = os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cse_id: logger.warning(f"Google API Key/CSE ID not set for '{full_query}' search."); return None
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        search_params = {'q': full_query, 'cx': cse_id, 'num': 5, 'safe': 'medium'} 
        if search_type == 'image': search_params['searchType'] = 'image'; search_params['imgSize'] = 'LARGE'
        logger.debug(f"Google Search for '{product_name_for_log}' query '{full_query}', params: {search_params}")
        res = service.cse().list(**search_params).execute()
        content_to_cache = None
        if 'items' in res and len(res['items']) > 0:
            if search_type == 'image':
                for i, item in enumerate(res['items']):
                    cse_image_src = item.get('pagemap', {}).get('cse_image', [{}])[0].get('src')
                    link = item.get('link') 
                    logger.debug(f"Img Item {i+1} - CSE: {cse_image_src}, Link: {link}, Mime: {item.get('mime')}")
                    if cse_image_src and cse_image_src.lower().startswith('http') and any(cse_image_src.lower().endswith(ext) for ext in ('.png','.jpg','.jpeg','.webp')): content_to_cache = cse_image_src; break
                    if link and link.lower().startswith('http') and any(link.lower().endswith(ext) for ext in ('.png','.jpg','.jpeg','.webp')): content_to_cache = link; break
                if not content_to_cache and res['items'][0].get('pagemap', {}).get('cse_image', [{}])[0].get('src'):
                    first_cse_img = res['items'][0]['pagemap']['cse_image'][0]['src']
                    if first_cse_img and first_cse_img.lower().startswith('http'): content_to_cache = first_cse_img
            else: 
                for item in res['items']:
                    snippet = item.get('snippet')
                    if snippet and len(snippet) > 70: content_to_cache = snippet; break
                if not content_to_cache: content_to_cache = res['items'][0].get('snippet') or res['items'][0].get('title')
        if content_to_cache: cache_data(cache_key, content_to_cache)
        return content_to_cache
    except Exception as e: logger.error(f"Error Google fetch '{full_query}': {e}", exc_info=False); return None

def fetch_product_image_url(product_name):
    logger.info(f"Fetching image for: {product_name}")
    queries = [f"{product_name} official product image png", f"{product_name} official product image white background", f"{product_name} product photo"]
    for q in queries:
        url = fetch_google_search_result(q, product_name, search_type='image')
        if url: return url
    return None

def fetch_product_specifications_snippet(product_name):
    logger.info(f"Fetching specs for: {product_name}")
    queries = [f"{product_name} key specifications list", f"{product_name} official tech specs", f"{product_name} gsmarena specifications"]
    best_snippet = "Detailed specifications snippet not found."
    max_score = 0
    for q in queries:
        snip = fetch_google_search_result(q, product_name)
        if snip:
            score = len(snip)
            if "gsmarena" in q.lower(): score += 100
            if score > max_score and len(snip) > 50: max_score = score; best_snippet = snip
            if "gsmarena" in q.lower() and len(snip) > 100: return snip 
    return best_snippet

LARGE_MOCK_DATASET_PATH = os.path.join(project_root_dir, "tweet_datasets", "various_smartphones_tweets.json")
ALL_MOCK_TWEETS = []
if os.path.exists(LARGE_MOCK_DATASET_PATH):
    try:
        with open(LARGE_MOCK_DATASET_PATH, 'r', encoding='utf-8') as f:
            ALL_MOCK_TWEETS = json.load(f)
        logger.info(f"Successfully loaded {len(ALL_MOCK_TWEETS)} tweets from the large mock dataset.")
    except Exception as e:
        logger.error(f"Error loading large mock dataset from {LARGE_MOCK_DATASET_PATH}: {e}")
else:
    logger.warning(f"Large mock dataset not found at {LARGE_MOCK_DATASET_PATH}. Generic mocks will be very simple if product-specific files also missing.")

def generate_fallback_mock_tweets(product_name, count=50):
    logger.info(f"Generating {count} FALLBACK mock tweets for {product_name}.")
    templates = [ f"Thinking about the {product_name}.", f"Is the {product_name} any good?", f"The {product_name} has a nice design.",
                  f"My {product_name} battery is okay.", f"Camera on {product_name} seems decent."]
    return [random.choice(templates) for _ in range(count)], None

def generate_mock_tweets_from_large_dataset(product_name, count=100):
    if not ALL_MOCK_TWEETS:
        logger.warning(f"Large mock dataset not loaded. Using fallback generic mock for {product_name}.")
        return generate_fallback_mock_tweets(product_name, count)

    product_keywords = product_name.lower().split()
    relevant_tweets = [t for t in ALL_MOCK_TWEETS if any(pk in t.lower() for pk in product_keywords)]
    other_tweets = [t for t in ALL_MOCK_TWEETS if not any(pk in t.lower() for pk in product_keywords)]
    
    final_selection = []
    random.shuffle(relevant_tweets)
    final_selection.extend(relevant_tweets)
    
    if len(final_selection) < count:
        random.shuffle(other_tweets)
        final_selection.extend(other_tweets)
        
    logger.info(f"Selected {min(count, len(final_selection))} mock tweets for '{product_name}' from large dataset.")
    return final_selection[:count], None

def fetch_real_tweets(product_name, count=100):
    product_file_key = product_name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
    dataset_file_path = os.path.join(project_root_dir, "tweet_datasets", f"{product_file_key}_tweets.json")

    if os.path.exists(dataset_file_path):
        try:
            with open(dataset_file_path, 'r', encoding='utf-8') as f:
                tweets_from_file = json.load(f)
            logger.info(f"Loaded {len(tweets_from_file)} tweets for '{product_name}' from specific local dataset: {dataset_file_path}")
            random.shuffle(tweets_from_file)
            return tweets_from_file[:count], None
        except Exception as e:
            logger.error(f"Error reading specific local dataset {dataset_file_path} for {product_name}: {e}")

    logger.info(f"No specific dataset for '{product_name}'. Attempting to use large mock dataset.")
    return generate_mock_tweets_from_large_dataset(product_name, count=count)

def analyze_sentiment_vader(text):
    if not sid: return 'neutral', {}
    scores = sid.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.05: return 'positive', scores
    elif compound <= -0.05: return 'negative', scores
    else: return 'neutral', scores

# --- NEW: Word Cloud Generation Function ---
def generate_word_cloud(text, product_name):
    """Generates a word cloud image from a block of text and saves it."""
    if not text.strip():
        logger.warning(f"No text provided for word cloud generation for {product_name}.")
        return None
        
    safe_filename = "".join(c for c in product_name if c.isalnum() or c in (' ', '_')).rstrip()
    safe_filename = safe_filename.replace(' ', '_').lower()
    
    output_filename = f"wc_{safe_filename}_{int(time.time())}.png"
    output_path = os.path.join(WORDCLOUD_DIR, output_filename)
    
    try:
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            colormap='viridis',
            max_words=100,
            collocations=False
        ).generate(text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(output_path)
        plt.close()

        logger.info(f"Word cloud saved for {product_name} at {output_path}")
        return f"/static/generated_images/{output_filename}"
    except Exception as e:
        logger.error(f"Could not generate word cloud for {product_name}: {e}")
        return None

def get_product_sentiment_analysis(product_name):
    logger.info(f"Starting analysis for: {product_name}")
    
    tweets, twitter_error_message = fetch_real_tweets(product_name, count=200)
    
    product_image = fetch_product_image_url(product_name)
    spec_snippet = fetch_product_specifications_snippet(product_name)

    results = {
        'product_image_url': product_image,
        'product_specifications_snippet': spec_snippet,
        'overall_sentiment': {'positive': 0, 'negative': 0, 'neutral': 0},
        'aspect_sentiments': {}, 'tweets_count': 0, 'sample_tweets': [],
        'error_message': twitter_error_message,
        'overall_score': 0.0, # NEW: Add numerical score
        'word_cloud_url': None # NEW: Add path for word cloud image
    }

    if not tweets:
        logger.warning(f"No tweets available (mocked or live) for '{product_name}'. Error: {twitter_error_message}")
        results['error_message'] = results.get('error_message') or "No tweets available for analysis."
        results['sample_tweets'] = [{"text": results['error_message'], "sentiment": "neutral"}]
        return results

    results['tweets_count'] = len(tweets)
    aspect_sentiments_data = {aspect: {'positive': 0, 'negative': 0, 'neutral': 0, 'mentions': 0} for aspect in ASPECTS_KEYWORDS}
    analyzed_tweets_details = []
    total_compound_score = 0.0

    for tweet_text in tweets:
        sentiment_label, scores = analyze_sentiment_vader(tweet_text)
        total_compound_score += scores.get('compound', 0.0)
        results['overall_sentiment'][sentiment_label] += 1
        analyzed_tweets_details.append({'text': tweet_text, 'sentiment': sentiment_label})
        try:
            sentences = sent_tokenize(tweet_text.lower())
        except Exception as e:
            logger.warning(f"Could not tokenize tweet: {tweet_text[:50]}... Error: {e}")
            sentences = [tweet_text.lower()] 

        tweet_aspects_found = set()
        for sentence in sentences:
            sentence_sentiment_label, _ = analyze_sentiment_vader(sentence)
            for aspect, keywords in ASPECTS_KEYWORDS.items():
                if any(keyword in sentence for keyword in keywords):
                    if aspect not in tweet_aspects_found:
                        aspect_sentiments_data[aspect]['mentions'] += 1
                        tweet_aspects_found.add(aspect)
                    aspect_sentiments_data[aspect][sentence_sentiment_label] += 1
    
    if results['tweets_count'] > 0:
        results['overall_score'] = round(total_compound_score / results['tweets_count'], 3)
        full_tweet_text = " ".join(tweets)
        results['word_cloud_url'] = generate_word_cloud(full_tweet_text, product_name)

    results['aspect_sentiments'] = { asp: data for asp, data in aspect_sentiments_data.items() if data['mentions'] >= 2 }
    results['sample_tweets'] = random.sample(analyzed_tweets_details, min(5, len(analyzed_tweets_details))) if analyzed_tweets_details else [{"text": "No tweets available for sampling.", "sentiment": "neutral"}]
    
    logger.info(f"Finished analysis for: {product_name}")
    return results