"""Data ingestion module for fetching cryptocurrency data from CoinGecko API."""
import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class CoinGeckoIngester:
    """Fetches real-time cryptocurrency data from CoinGecko API."""
    
    def __init__(self, api_url: str, cryptos: List[str]):
        """
        Initialize the ingester.
        
        Args:
            api_url: Base URL for CoinGecko API
            cryptos: List of cryptocurrency IDs to track
        """
        self.api_url = api_url
        self.cryptos = cryptos
        self.last_fetch_time = None
        self.error_count = 0
    
    def fetch_market_data(self) -> Optional[Dict]:
        """
        Fetch market data for configured cryptocurrencies.
        
        Returns:
            Dictionary with market data or None if fetch fails
        """
        try:
            # CoinGecko endpoint for market data
            params = {
                'ids': ','.join(self.cryptos),
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true'
            }
            
            endpoint = f"{self.api_url}/simple/price"
            response = requests.get(endpoint, params=params, timeout=10)
            
            # Handle rate limiting gracefully
            if response.status_code == 429:
                logger.warning("CoinGecko API rate limit reached (429). Backing off...")
                self.error_count += 1
                return None
            
            response.raise_for_status()
            
            data = response.json()
            
            # Add metadata
            data['_metadata'] = {
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'CoinGecko',
                'status': 'success'
            }
            
            self.last_fetch_time = datetime.utcnow()
            self.error_count = 0
            
            logger.info(f"Successfully fetched data for {len(data)-1} cryptocurrencies")
            return data
            
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            logger.error(f"Failed to fetch data from CoinGecko API: {str(e)}")
            return None
        except Exception as e:
            self.error_count += 1
            logger.error(f"Unexpected error during data ingestion: {str(e)}")
            return None
    
    def get_status(self) -> Dict:
        """Get ingestion status and health metrics."""
        return {
            'last_fetch_time': self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            'error_count': self.error_count,
            'monitored_cryptos': len(self.cryptos),
            'status': 'healthy' if self.error_count < 3 else 'unhealthy'
        }
