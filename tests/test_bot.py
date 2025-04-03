import unittest
import sys
import os
import logging
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import load_config
from database.mongo_client import MongoDBClient
from ml.nlp_processor import process_text, is_telugu_text
from ml.conversation_model import get_response
from ml.ipl_stats import search_ipl_data

# Disable logging for tests
logging.disable(logging.CRITICAL)

class TestBotFunctionality(unittest.TestCase):
    """Test basic bot functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'API_ID': '12345',
            'API_HASH': 'abcdef1234567890',
            'BOT_TOKEN': '123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'MONGODB_URI': 'mongodb://localhost:27017/test_db',
            'ADMIN_USERS': '123456789'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
    
    def test_config_loading(self):
        """Test configuration loading"""
        config = load_config()
        self.assertEqual(config['API_ID'], '12345')
        self.assertEqual(config['API_HASH'], 'abcdef1234567890')
        self.assertEqual(config['BOT_TOKEN'], '123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.assertEqual(config['MONGODB_URI'], 'mongodb://localhost:27017/test_db')
        self.assertEqual(config['ADMIN_USERS'], [123456789])
    
    @patch('pymongo.MongoClient')
    def test_mongodb_client(self, mock_mongo):
        """Test MongoDB client"""
        # Mock MongoDB client
        mock_client = MagicMock()
        mock_mongo.return_value = mock_client
        
        # Mock admin command
        mock_client.admin.command.return_value = True
        
        # Mock database
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        # Create MongoDB client
        config = {'MONGODB_URI': 'mongodb://localhost:27017/test_db'}
        db_client = MongoDBClient(config)
        
        # Check if client was created
        self.assertIsNotNone(db_client.client)
        self.assertIsNotNone(db_client.db)
        self.assertFalse(db_client.is_using_backup)
    
    def test_nlp_processing(self):
        """Test NLP processing"""
        # Test English text processing
        processed = process_text("Hello, how are you doing today?")
        self.assertIsInstance(processed, str)
        self.assertTrue(len(processed) > 0)
        
        # Test Telugu detection
        self.assertFalse(is_telugu_text("Hello, how are you?"))
        self.assertTrue(is_telugu_text("నమస్కారం, మీరు ఎలా ఉన్నారు?"))
    
    def test_conversation_model(self):
        """Test conversation model"""
        # Test English responses
        response = get_response("hello", "english")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        
        # Test Telugu responses
        response = get_response("నమస్కారం", "telugu")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
    
    def test_ipl_data_search(self):
        """Test IPL data search"""
        # Test player search
        player = search_ipl_data('player', 'virat kohli')
        self.assertIsNotNone(player)
        if player:
            self.assertEqual(player['name'], 'Virat Kohli')
        
        # Test team search
        team = search_ipl_data('team', 'csk')
        self.assertIsNotNone(team)
        if team:
            self.assertEqual(team['name'], 'CSK')

if __name__ == '__main__':
    unittest.main()
