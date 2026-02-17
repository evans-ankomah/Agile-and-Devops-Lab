"""Configuration for the data streaming platform."""
import os
from datetime import datetime

class Config:
    """Base configuration."""
    
    # Flask settings
    DEBUG = os.getenv('FLASK_DEBUG', False)
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # CoinGecko API settings
    COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
    CRYPTOS = ['bitcoin', 'ethereum', 'cardano', 'polkadot', 'solana']
    INGESTION_INTERVAL = int(os.getenv('INGESTION_INTERVAL', 61))  # seconds (respect CoinGecko rate limits)
    
    # Data storage
    DATABASE_FILE = 'market_data.db'
    CACHE_DIR = './data'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = './logs/app.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Data quality thresholds
    MAX_NULL_PERCENTAGE = 10  # Alert if >10% of records have null values
    DUPLICATE_THRESHOLD = 5   # Alert if >5% duplicates detected
    MAX_PRICE_CHANGE_PERCENTAGE = 20  # Alert if price changes >20% in one interval


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    INGESTION_INTERVAL = 30  # More frequent for testing


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    INGESTION_INTERVAL = 60  # Standard interval


# Select config based on environment
ENV = os.getenv('FLASK_ENV', 'development')
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

current_config = config_dict.get(ENV, DevelopmentConfig)
