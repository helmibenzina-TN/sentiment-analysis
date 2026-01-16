// TypeScript interfaces for the application

export interface User {
    id: number;
    username: string;
    email: string;
}

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    user: User;
}

export interface SentimentScores {
    positive: number;
    negative: number;
    neutral: number;
    compound?: number;
}

export interface AspectSentiment {
    positive: number;
    negative: number;
    neutral: number;
    mentions: number;
}

export interface SampleTweet {
    text: string;
    sentiment: 'positive' | 'negative' | 'neutral';
}

export interface SentimentResult {
    product_image_url: string | null;
    product_specifications_snippet: string;
    overall_sentiment: {
        positive: number;
        negative: number;
        neutral: number;
    };
    aspect_sentiments: { [key: string]: AspectSentiment };
    tweets_count: number;
    sample_tweets: SampleTweet[];
    error_message: string | null;
    overall_score: number;
    word_cloud_url: string | null;
    price_usd?: number;
    performance_score?: number;
    battery_score?: number;
    camera_score?: number;
    value_for_money?: number;
}

export interface AnalysisResponse {
    product1: {
        name: string;
        results: SentimentResult;
    };
    product2?: {
        name: string;
        results: SentimentResult;
    };
}

export interface SmartphoneScore {
    product_name: string;
    overall_score: number;
    positive_count: number;
    negative_count: number;
    neutral_count: number;
    tweets_count: number;
    price_usd: number | null;
    performance_score: number | null;
    battery_score: number | null;
    camera_score: number | null;
    value_for_money: number | null;
    last_updated: string | null;
}

export interface SearchHistoryItem {
    id: number;
    product_name: string;
    search_time: string;
}

export interface HistoryResponse {
    history: SearchHistoryItem[];
    total: number;
    pages: number;
    current_page: number;
    per_page: number;
    has_next: boolean;
    has_prev: boolean;
}

export interface PerformanceRankingsResponse {
    category: string;
    smartphones: SmartphoneScore[];
}

export interface AllPerformanceCategoriesResponse {
    overall: SmartphoneScore[];
    performance: SmartphoneScore[];
    battery: SmartphoneScore[];
    camera: SmartphoneScore[];
    value: SmartphoneScore[];
}
