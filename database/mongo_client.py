import logging

# Import pymongo conditionally to allow running without it
try:
    import pymongo
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

logger = logging.getLogger(__name__)

class MongoDBClient:
    """
    MongoDB client for handling database operations
    """

    def __init__(self, config):
        """
        Initialize MongoDB client with configuration
        """
        # Get MongoDB URI and ensure it has the correct format
        self.primary_uri = self._validate_uri(config.get('MONGODB_URI'))
        self.backup_uri = self._validate_uri(config.get('MONGODB_URI_BACKUP'))
        self.client = None
        self.db = None
        self.is_using_backup = False

        # Connect to MongoDB
        self._connect()

    def _validate_uri(self, uri):
        """
        Validate and format MongoDB URI
        """
        if not uri:
            logger.warning("No MongoDB URI provided, using in-memory mode")
            return None

        # Check if URI has the correct format
        if not uri.startswith('mongodb://') and not uri.startswith('mongodb+srv://'):
            logger.warning(f"Invalid MongoDB URI format: {uri[:10]}..., adding prefix")
            uri = f"mongodb://{uri}"

        return uri

    def _connect(self):
        """
        Connect to MongoDB using primary or backup URI
        """
        # Check if pymongo is available
        if not PYMONGO_AVAILABLE:
            logger.warning("PyMongo is not available, using in-memory mode")
            self._setup_memory_db()
            return

        # If no MongoDB URI is provided, use in-memory mode
        if not self.primary_uri:
            logger.warning("No MongoDB URI provided, using in-memory mode")
            self._setup_memory_db()
            return

        try:
            # Try primary connection
            logger.info("Connecting to primary MongoDB...")
            self.client = pymongo.MongoClient(self.primary_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')  # Check connection
            self.db = self.client['ipl_bot_db']
            self.is_using_backup = False
            logger.info("Connected to primary MongoDB successfully")

        except Exception as e:
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

                except Exception as e:
                    logger.error(f"Failed to connect to backup MongoDB: {e}")
                    self._setup_memory_db()
            else:
                logger.warning("No backup MongoDB URI provided, using in-memory mode")
                self._setup_memory_db()

    def _setup_memory_db(self):
        """
        Set up an in-memory database for development/testing
        """
        logger.info("Setting up in-memory database")
        self.client = None
        # Create a simple in-memory database using dictionaries
        self.db = {
            'users': {},
            'messages': []
        }
        logger.info("In-memory database ready")

    def get_collection(self, collection_name):
        """
        Get a collection from the database
        """
        if not self.db:
            logger.error("No database connection available")
            return None

        # Check if we're using in-memory mode
        if self.client is None:
            return self.db.get(collection_name, {})

        return self.db[collection_name]

    def save_user(self, user_data):
        """
        Save user data to the database
        """
        if not self.db:
            logger.error("No database connection available")
            return False

        try:
            # Check if we're using in-memory mode
            if self.client is None:
                # In-memory mode
                user_id = user_data['user_id']
                self.db['users'][user_id] = user_data
                return True

            # MongoDB mode
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
            # Check if we're using in-memory mode
            if self.client is None:
                # In-memory mode
                self.db['messages'].append(message_data)
                return True

            # MongoDB mode
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
        # If using in-memory mode, no need to check size
        if self.client is None:
            return False

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
        # Check if pymongo is available
        if not PYMONGO_AVAILABLE:
            logger.warning("PyMongo is not available, using in-memory mode")
            self._setup_memory_db()
            return False

        if not self.backup_uri:
            logger.warning("No backup MongoDB URI provided, using in-memory mode")
            self._setup_memory_db()
            return False

        try:
            logger.info("Connecting to backup MongoDB...")
            self.client = pymongo.MongoClient(self.backup_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')  # Check connection
            self.db = self.client['ipl_bot_db']
            self.is_using_backup = True
            logger.info("Connected to backup MongoDB successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to backup MongoDB: {e}")
            self._setup_memory_db()
            return False

    def get_user(self, user_id):
        """
        Get user data from the database
        """
        if not self.db:
            logger.error("No database connection available")
            return None

        try:
            # Check if we're using in-memory mode
            if self.client is None:
                # In-memory mode
                return self.db['users'].get(user_id)

            # MongoDB mode
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
            # Check if we're using in-memory mode
            if self.client is None:
                # In-memory mode
                user_messages = [msg for msg in self.db['messages'] if msg.get('user_id') == user_id]
                # Sort by timestamp (descending)
                user_messages.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
                # Apply limit
                return user_messages[:limit]

            # MongoDB mode
            messages_collection = self.db['messages']
            if PYMONGO_AVAILABLE:
                return list(messages_collection.find(
                    {'user_id': user_id},
                    sort=[('timestamp', pymongo.DESCENDING)],
                    limit=limit
                ))
            else:
                # Fallback if pymongo is not available
                return []

        except Exception as e:
            logger.error(f"Error getting user messages: {e}")
            return []
