import os
from dotenv import load_dotenv

def load_config():
    """
    Load configuration from environment variables
    """
    load_dotenv()

    config = {
        'API_ID': os.getenv('API_ID'),
        'API_HASH': os.getenv('API_HASH'),
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'MONGODB_URI': os.getenv('MONGODB_URI'),
        'MONGODB_URI_BACKUP': os.getenv('MONGODB_URI_BACKUP'),
        'KAGGLE_USERNAME': os.getenv('KAGGLE_USERNAME'),
        'KAGGLE_KEY': os.getenv('KAGGLE_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'ADMIN_USERS': [int(id) for id in os.getenv('ADMIN_USERS', '').split(',') if id],
    }

    # Validate required configuration
    required_keys = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'MONGODB_URI']
    missing_keys = [key for key in required_keys if not config.get(key)]

    if missing_keys:
        raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")

    return config
