"""Data transformation and validation module."""
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transforms and validates incoming data."""
    
    def __init__(self, config):
        """Initialize transformer with configuration."""
        self.config = config
    
    def transform_market_data(self, raw_data: Dict) -> Dict:
        """
        Transform raw CoinGecko API data into standardized format.
        
        Args:
            raw_data: Raw data from CoinGecko API
            
        Returns:
            Transformed data in standard format
        """
        if not raw_data or '_metadata' not in raw_data:
            logger.warning("Invalid or missing raw data")
            return self._empty_result()
        
        try:
            transformed = {
                'timestamp': raw_data['_metadata']['timestamp'],
                'source': raw_data['_metadata']['source'],
                'cryptos': [],
                'summary': {
                    'total_count': 0,
                    'valid_count': 0,
                    'null_count': 0,
                    'errors': []
                }
            }
            
            # Process each cryptocurrency
            for crypto_id, crypto_data in raw_data.items():
                if crypto_id == '_metadata':
                    continue
                
                cell = self._transform_crypto(crypto_id, crypto_data)
                if cell:
                    transformed['cryptos'].append(cell)
                    transformed['summary']['valid_count'] += 1
                else:
                    transformed['summary']['null_count'] += 1
                
                transformed['summary']['total_count'] += 1
            
            # Calculate quality metrics
            transformed['summary']['data_quality_score'] = self._calculate_quality_score(transformed['summary'])
            
            return transformed
            
        except Exception as e:
            logger.error(f"Error transforming data: {str(e)}")
            return self._empty_result()
    
    def _transform_crypto(self, crypto_id: str, crypto_data: Dict) -> Optional[Dict]:
        """Transform individual cryptocurrency data."""
        try:
            # Handle USDdata
            if 'usd' not in crypto_data:
                return None
            
            usd_data = crypto_data['usd']
            
            # Required fields
            if not isinstance(usd_data, (int, float)):
                return None
            
            transformed = {
                'id': crypto_id.lower(),
                'name': crypto_id.replace('_', ' ').title(),
                'price_usd': round(float(usd_data), 2),
                'market_cap_usd': crypto_data.get('usd_market_cap'),
                'volume_24h_usd': crypto_data.get('usd_24h_vol'),
                'change_24h_percent': crypto_data.get('usd_24h_change'),
                'transformed_at': datetime.utcnow().isoformat()
            }
            
            return transformed
            
        except Exception as e:
            logger.warning(f"Failed to transform crypto {crypto_id}: {str(e)}")
            return None
    
    def _calculate_quality_score(self, summary: Dict) -> float:
        """Calculate data quality score (0-100)."""
        if summary['total_count'] == 0:
            return 0.0
        
        valid_percentage = (summary['valid_count'] / summary['total_count']) * 100
        return round(valid_percentage, 2)
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'CoinGecko',
            'cryptos': [],
            'summary': {
                'total_count': 0,
                'valid_count': 0,
                'null_count': 0,
                'errors': [],
                'data_quality_score': 0.0
            }
        }
    
    @staticmethod
    def validate_transformed_data(data: Dict) -> bool:
        """
        Validate transformed data structure.
        
        Args:
            data: Transformed data dictionary
            
        Returns:
            True if data is valid, False otherwise
        """
        required_keys = ['timestamp', 'cryptos', 'summary']
        return all(key in data for key in required_keys)
