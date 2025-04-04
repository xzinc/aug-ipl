import os
import logging
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv
from database.mongo_client import MongoDBClient
from handlers.command_handler import setup_command_handlers
from handlers.message_handler import setup_message_handlers
from handlers.admin_handler import setup_admin_handlers
from utils.config import load_config
from utils.data_loader import load_ipl_data, load_telugu_nlp_data

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set Gemini API key if available
if os.getenv('GEMINI_API_KEY'):
    logger.info("Gemini API key found in environment variables")
else:
    logger.warning("Gemini API key not found in environment variables - AI features will be limited")

async def main():
    # Load configuration
    config = load_config()

    # Initialize MongoDB client
    db_client = MongoDBClient(config)

    # Create the Telegram client
    client = TelegramClient(
        'ipl_bot_session',
        config['API_ID'],
        config['API_HASH']
    )

    # Setup handlers
    setup_command_handlers(client, db_client)
    setup_message_handlers(client, db_client)
    setup_admin_handlers(client, db_client)

    # Load datasets
    await load_ipl_data()
    await load_telugu_nlp_data()

    # Start the client
    await client.start(bot_token=config['BOT_TOKEN'])

    # Run the client until disconnected
    logger.info("Bot started successfully!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
