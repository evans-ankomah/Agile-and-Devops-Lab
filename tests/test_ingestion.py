"""Tests for data_ingestion module."""
import pytest
from unittest.mock import patch, Mock
from backend.data_ingestion import CoinGeckoIngester


class TestCoinGeckoIngester:
    """Test cases for CoinGeckoIngester."""
    
    @pytest.fixture
    def ingester(self):
        """Create ingester instance for testing."""
        return CoinGeckoIngester(
            api_url="https://api.coingecko.com/api/v3",
            cryptos=['bitcoin', 'ethereum', 'cardano']
        )
    
    @patch('backend.data_ingestion.requests.get')
    def test_fetch_market_data_success(self, mock_get, ingester):
        """Test successful data fetch."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'bitcoin': {'usd': 45000, 'usd_market_cap': 880000000000},
            'ethereum': {'usd': 2500, 'usd_market_cap': 300000000000},
            'cardano': {'usd': 0.5, 'usd_market_cap': 17500000000}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = ingester.fetch_market_data()
        
        assert result is not None
        assert '_metadata' in result
        assert result['bitcoin']['usd'] == 45000
        assert ingester.error_count == 0
    
    @patch('backend.data_ingestion.requests.get')
    def test_fetch_market_data_failure(self, mock_get, ingester):
        """Test data fetch failure."""
        mock_get.side_effect = Exception("Network error")
        
        result = ingester.fetch_market_data()
        
        assert result is None
        assert ingester.error_count > 0
    
    def test_get_status(self, ingester):
        """Test ingester status method."""
        status = ingester.get_status()
        
        assert 'last_fetch_time' in status
        assert 'error_count' in status
        assert 'monitored_cryptos' in status
        assert 'status' in status
        assert status['monitored_cryptos'] == 3
    
    @patch('backend.data_ingestion.requests.get')
    def test_error_recovery(self, mock_get, ingester):
        """Test that error count resets on successful fetch."""
        # First, simulate a failure
        mock_get.side_effect = Exception("Network error")
        ingester.fetch_market_data()
        assert ingester.error_count == 1
        
        # Then, simulate success
        mock_response = Mock()
        mock_response.json.return_value = {'bitcoin': {'usd': 45000}}
        mock_response.raise_for_status = Mock()
        mock_get.side_effect = None
        mock_get.return_value = mock_response
        
        result = ingester.fetch_market_data()
        assert result is not None
        assert ingester.error_count == 0
