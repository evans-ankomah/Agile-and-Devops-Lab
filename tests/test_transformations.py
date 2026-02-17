"""Tests for transformations module."""
import pytest
from datetime import datetime
from backend.transformations import DataTransformer
from backend.config import DevelopmentConfig


class TestDataTransformer:
    """Test cases for DataTransformer."""
    
    @pytest.fixture
    def transformer(self):
        """Create transformer instance for testing."""
        return DataTransformer(DevelopmentConfig)
    
    def test_transform_market_data_valid(self, transformer):
        """Test transformation of valid data."""
        raw_data = {
            'bitcoin': {
                'usd': 45000,
                'usd_market_cap': 880000000000,
                'usd_24h_vol': 25000000000,
                'usd_24h_change': 2.5
            },
            'ethereum': {
                'usd': 2500,
                'usd_market_cap': 300000000000,
                'usd_24h_vol': 15000000000,
                'usd_24h_change': 1.2
            },
            '_metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'CoinGecko',
                'status': 'success'
            }
        }
        
        result = transformer.transform_market_data(raw_data)
        
        assert result is not None
        assert 'cryptos' in result
        assert len(result['cryptos']) == 2
        assert result['summary']['valid_count'] == 2
        assert result['summary']['data_quality_score'] == 100.0
        
        # Check transformed crypto data
        bitcoin = next((c for c in result['cryptos'] if c['id'] == 'bitcoin'), None)
        assert bitcoin is not None
        assert bitcoin['price_usd'] == 45000
        assert bitcoin['market_cap_usd'] == 880000000000
    
    def test_transform_market_data_invalid(self, transformer):
        """Test transformation with invalid data."""
        raw_data = {
            'bitcoin': {
                # Invalid: usd not present
                'usd_market_cap': 880000000000
            },
            '_metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'CoinGecko',
                'status': 'success'
            }
        }
        
        result = transformer.transform_market_data(raw_data)
        
        assert result is not None
        assert result['summary']['valid_count'] == 0
        assert result['summary']['data_quality_score'] == 0.0
    
    def test_transform_market_data_mixed(self, transformer):
        """Test transformation with mix of valid and invalid data."""
        raw_data = {
            'bitcoin': {
                'usd': 45000,
                'usd_market_cap': 880000000000,
                'usd_24h_vol': 25000000000,
                'usd_24h_change': 2.5
            },
            'ethereum': {
                # Missing usd value
                'usd_market_cap': 300000000000
            },
            '_metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'CoinGecko',
                'status': 'success'
            }
        }
        
        result = transformer.transform_market_data(raw_data)
        
        assert result is not None
        assert result['summary']['valid_count'] == 1
        assert result['summary']['null_count'] == 1
        assert result['summary']['data_quality_score'] == 50.0
    
    def test_transform_market_data_empty(self, transformer):
        """Test transformation with None data."""
        result = transformer.transform_market_data(None)
        
        assert result is not None
        assert result['summary']['valid_count'] == 0
        assert result['summary']['total_count'] == 0
    
    def test_validate_transformed_data(self, transformer):
        """Test validation of transformed data."""
        valid_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'cryptos': [],
            'summary': {}
        }
        
        assert DataTransformer.validate_transformed_data(valid_data) is True
        
        invalid_data = {
            'timestamp': datetime.utcnow().isoformat()
            # Missing required fields
        }
        
        assert DataTransformer.validate_transformed_data(invalid_data) is False
    
    def test_quality_score_calculation(self, transformer):
        """Test data quality score calculation."""
        raw_data = {
            'bitcoin': {'usd': 45000},
            'ethereum': {'usd': 2500},
            'cardano': {'usd': 0.5},
            'polkadot': {'usd_market_cap': 10000000000},  # Invalid
            'solana': {'usd': 150},
            '_metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'CoinGecko',
                'status': 'success'
            }
        }
        
        result = transformer.transform_market_data(raw_data)
        
        # 4 valid out of 5 = 80%
        assert result['summary']['data_quality_score'] == 80.0
