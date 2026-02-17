"""Flask application for real-time data streaming dashboard."""
import logging
import os
from flask import Flask, render_template, jsonify
from datetime import datetime
from backend.config import current_config
from backend.data_ingestion import CoinGeckoIngester
from backend.transformations import DataTransformer

# Setup logging
os.makedirs('./logs', exist_ok=True)
logging.basicConfig(
    level=current_config.LOG_LEVEL,
    format=current_config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(current_config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Determine the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_folder = os.path.join(project_root, 'frontend')
static_folder = os.path.join(project_root, 'frontend')

# Initialize Flask app with absolute paths
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.config.from_object(current_config)

# Initialize components
ingester = CoinGeckoIngester(current_config.COINGECKO_API_URL, current_config.CRYPTOS)
transformer = DataTransformer(current_config)

# In-memory cache for latest data
cache = {
    'latest_data': None,
    'last_update': None,
    'update_count': 0,
    'error_count': 0
}


@app.route('/')
def index():
    """Serve the dashboard homepage."""
    return render_template('index.html')


@app.route('/api/data')
def get_data():
    """API endpoint to get latest data."""
    return jsonify({
        'data': cache['latest_data'],
        'last_update': cache['last_update'],
        'stats': {
            'update_count': cache['update_count'],
            'error_count': cache['error_count']
        }
    })


@app.route('/api/refresh')
def refresh_data():
    """API endpoint to manually refresh data."""
    try:
        # Fetch raw data
        raw_data = ingester.fetch_market_data()
        
        if raw_data:
            # Transform data
            transformed_data = transformer.transform_market_data(raw_data)
            
            # Update cache
            cache['latest_data'] = transformed_data
            cache['last_update'] = datetime.utcnow().isoformat()
            cache['update_count'] += 1
            
            logger.info(f"Data refreshed successfully. Valid records: {transformed_data['summary']['valid_count']}")
            
            return jsonify({
                'status': 'success',
                'message': f"Fetched {transformed_data['summary']['valid_count']} cryptocurrencies",
                'data': transformed_data
            }), 200
        else:
            cache['error_count'] += 1
            logger.error("Failed to fetch market data")
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch market data from CoinGecko'
            }), 500
            
    except Exception as e:
        cache['error_count'] += 1
        logger.error(f"Error in refresh_data: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    ingester_status = ingester.get_status()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'ingester': ingester_status,
        'cache': {
            'has_data': cache['latest_data'] is not None,
            'last_update': cache['last_update'],
            'update_count': cache['update_count'],
            'error_count': cache['error_count']
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

