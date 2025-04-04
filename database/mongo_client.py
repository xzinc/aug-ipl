import logging
import copy
import time
from datetime import datetime

# Import pymongo conditionally to allow running without it
try:
    import pymongo
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

logger = logging.getLogger(__name__)

# In-memory collection class to simulate MongoDB collections
class MemoryCollection:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data if data is not None else []

    def find(self, query=None, projection=None, **kwargs):
        """
        Simulate MongoDB find operation
        """
        if query is None:
            query = {}

        # Filter data based on query
        results = self._filter_data(query)

        # Apply projection if provided
        if projection:
            results = self._apply_projection(results, projection)

        # Apply sort if provided
        sort_params = kwargs.get('sort', [])
        if sort_params:
            results = self._apply_sort(results, sort_params)

        # Apply limit if provided
        limit = kwargs.get('limit', None)
        if limit is not None:
            results = results[:limit]

        return results

    def find_one(self, query=None, projection=None):
        """
        Simulate MongoDB find_one operation
        """
        results = self.find(query, projection, limit=1)
        return results[0] if results else None

    def insert_one(self, document):
        """
        Simulate MongoDB insert_one operation
        """
        # Make a copy to avoid modifying the original
        doc = copy.deepcopy(document)

        # Add _id if not present
        if '_id' not in doc:
            doc['_id'] = str(time.time())

        self.data.append(doc)
        return True

    def update_one(self, query, update):
        """
        Simulate MongoDB update_one operation
        """
        # Find the first matching document
        for i, doc in enumerate(self.data):
            if self._matches_query(doc, query):
                # Apply updates
                if '$set' in update:
                    for key, value in update['$set'].items():
                        doc[key] = value
                return True
        return False

    def count_documents(self, query=None):
        """
        Simulate MongoDB count_documents operation
        """
        if query is None:
            query = {}
        return len(self._filter_data(query))

    def _filter_data(self, query):
        """
        Filter data based on query
        """
        if not query:
            return copy.deepcopy(self.data)

        results = []
        for doc in self.data:
            if self._matches_query(doc, query):
                results.append(copy.deepcopy(doc))

        return results

    def _matches_query(self, doc, query):
        """
        Check if document matches query
        """
        for key, value in query.items():
            # Handle special operators
            if key.startswith('$'):
                # Not implemented for simplicity
                continue

            if key not in doc:
                return False

            # Handle nested query operators
            if isinstance(value, dict) and any(k.startswith('$') for k in value.keys()):
                for op, op_value in value.items():
                    if op == '$gte':
                        if not (doc[key] >= op_value):
                            return False
                    elif op == '$gt':
                        if not (doc[key] > op_value):
                            return False
                    elif op == '$lte':
                        if not (doc[key] <= op_value):
                            return False
                    elif op == '$lt':
                        if not (doc[key] < op_value):
                            return False
                    elif op == '$ne':
                        if doc[key] == op_value:
                            return False
            else:
                # Direct value comparison
                if doc[key] != value:
                    return False

        return True

    def _apply_projection(self, results, projection):
        """
        Apply projection to results
        """
        if not projection:
            return results

        projected_results = []
        for doc in results:
            projected_doc = {}
            for key, include in projection.items():
                if include and key in doc:
                    projected_doc[key] = doc[key]
            projected_results.append(projected_doc)

        return projected_results

    def _apply_sort(self, results, sort_params):
        """
        Apply sort to results
        """
        if not sort_params:
            return results

        for field, direction in sort_params:
            reverse = direction < 0  # -1 for descending, 1 for ascending
            results.sort(key=lambda x: x.get(field, None), reverse=reverse)

        return results

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
            'users': [],
            'messages': [],
            'blacklist': [],
            'custom_responses': []
        }

        # Add command method to the db dictionary for compatibility
        self.db.command = self._memory_db_command

        logger.info("In-memory database ready")

    def _memory_db_command(self, command_name, *args, **kwargs):
        """
        Simulate MongoDB commands for in-memory database
        """
        if command_name == "dbStats":
            # Return simulated database stats
            return {
                "dataSize": len(str(self.db)) * 2,  # Rough estimate
                "storageSize": len(str(self.db)) * 3,  # Rough estimate
                "ok": 1
            }
        elif command_name == "listCollections":
            # Return list of collections
            return [{'name': coll} for coll in self.db.keys() if not callable(getattr(self.db, coll, None))]
        elif command_name == "collStats":
            # Return collection stats
            collection = kwargs.get('collStats', '')
            if collection in self.db:
                data_size = len(str(self.db[collection])) * 2  # Rough estimate
                return {
                    "size": data_size,
                    "count": len(self.db[collection]) if isinstance(self.db[collection], (list, dict)) else 0,
                    "ok": 1
                }
            return {"size": 0, "count": 0, "ok": 0}

        # Default response for unknown commands
        return {"ok": 0}

    def get_collection(self, collection_name):
        """
        Get a collection from the database
        """
        if not self.db:
            logger.error("No database connection available")
            return None

        # Check if we're using in-memory mode
        if self.client is None:
            # Initialize collection if it doesn't exist
            if collection_name not in self.db:
                self.db[collection_name] = []

            # Return a MemoryCollection object for the collection
            return MemoryCollection(collection_name, self.db[collection_name])

        return self.db[collection_name]

    def save_user(self, user_data):
        """
        Save user data to the database
        """
        if not self.db:
            logger.error("No database connection available")
            return False

        try:
            # Get users collection
            users_collection = self.get_collection('users')

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
            # Get messages collection
            messages_collection = self.get_collection('messages')
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
            # Get users collection
            users_collection = self.get_collection('users')
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
            # Get messages collection
            messages_collection = self.get_collection('messages')

            # Get messages for the user
            sort_param = [('timestamp', -1)]
            return list(messages_collection.find(
                {'user_id': user_id},
                sort=sort_param,
                limit=limit
            ))

        except Exception as e:
            logger.error(f"Error getting user messages: {e}")
            return []
