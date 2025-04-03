import logging
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

class MongoDBClient:
    """
    MongoDB client for handling database operations
    """
    
    def __init__(self, config):
        """
        Initialize MongoDB client with configuration
        """
        self.primary_uri = config['MONGODB_URI']
        self.backup_uri = config.get('MONGODB_URI_BACKUP')
        self.client = None
        self.db = None
        self.is_using_backup = False
        
        # Connect to MongoDB
        self._connect()
    
    def _connect(self):
        """
        Connect to MongoDB using primary or backup URI
        """
        try:
            # Try primary connection
            logger.info("Connecting to primary MongoDB...")
            self.client = pymongo.MongoClient(self.primary_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')  # Check connection
            self.db = self.client['ipl_bot_db']
            self.is_using_backup = False
            logger.info("Connected to primary MongoDB successfully")
        
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to primary MongoDB: {e}")
            
            # Try backup connection if available
            if self.backup_uri:
                try:
                    logger.info("Connecting to backup MongoDB...")
                    self.client = pymongo.MongoClient(self.backup_uri, serverSelectionTimeoutMS=5000)
                    self.client.admin.command('ping')  # Check connection
                    self.db = self.client['ipl_bot_db']
                    self.is_using_backup = True
                    logger.info("Connected to backup MongoDB successfully")
                
                except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                    logger.error(f"Failed to connect to backup MongoDB: {e}")
                    self.client = None
                    self.db = None
            else:
                logger.warning("No backup MongoDB URI provided")
                self.client = None
                self.db = None
    
    def get_collection(self, collection_name):
        """
        Get a collection from the database
        """
        if not self.db:
            logger.error("No database connection available")
            return None
        
        return self.db[collection_name]
    
    def save_user(self, user_data):
        """
        Save user data to the database
        """
        if not self.db:
            logger.error("No database connection available")
            return False
        
        try:
            users_collection = self.db['users']
            
            # Check if user already exists
            existing_user = users_collection.find_one({'user_id': user_data['user_id']})
            
            if existing_user:
                # Update existing user
                users_collection.update_one(
                    {'user_id': user_data['user_id']},
                    {'$set': user_data}
                )
            else:
                # Insert new user
                users_collection.insert_one(user_data)
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return False
    
    def save_message(self, message_data):
        """
        Save message data to the database
        """
        if not self.db:
            logger.error("No database connection available")
            return False
        
        try:
            messages_collection = self.db['messages']
            messages_collection.insert_one(message_data)
            
            # Check if we need to switch to backup database due to size constraints
            if self._check_database_size() and self.backup_uri and not self.is_using_backup:
                logger.warning("Primary database size limit reached, switching to backup")
                self._connect_to_backup()
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving message data: {e}")
            return False
    
    def _check_database_size(self):
        """
        Check if the database size is approaching limits
        """
        try:
            stats = self.db.command("dbStats")
            size_mb = stats["dataSize"] / (1024 * 1024)
            
            # MongoDB Atlas free tier has a 512MB limit
            # We'll switch when we reach 80% of that
            if size_mb > 400:  # 80% of 512MB
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking database size: {e}")
            return False
    
    def _connect_to_backup(self):
        """
        Connect to the backup database
        """
        if not self.backup_uri:
            logger.error("No backup MongoDB URI provided")
            return False
        
        try:
            logger.info("Connecting to backup MongoDB...")
            self.client = pymongo.MongoClient(self.backup_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')  # Check connection
            self.db = self.client['ipl_bot_db']
            self.is_using_backup = True
            logger.info("Connected to backup MongoDB successfully")
            return True
        
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to backup MongoDB: {e}")
            return False
    
    def get_user(self, user_id):
        """
        Get user data from the database
        """
        if not self.db:
            logger.error("No database connection available")
            return None
        
        try:
            users_collection = self.db['users']
            return users_collection.find_one({'user_id': user_id})
        
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return None
    
    def get_user_messages(self, user_id, limit=50):
        """
        Get messages for a specific user
        """
        if not self.db:
            logger.error("No database connection available")
            return []
        
        try:
            messages_collection = self.db['messages']
            return list(messages_collection.find(
                {'user_id': user_id},
                sort=[('timestamp', pymongo.DESCENDING)],
                limit=limit
            ))
        
        except Exception as e:
            logger.error(f"Error getting user messages: {e}")
            return []
