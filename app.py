from flask import Flask, render_template, jsonify
import os
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """
    Main page - shows bot status
    """
    return render_template('index.html', 
                          bot_name="IPL Telegram Bot",
                          current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/status')
def status():
    """
    API endpoint for bot status
    """
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
