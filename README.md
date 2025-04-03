# IPL Telegram Bot

A Telegram bot that provides information about IPL (Indian Premier League) cricket matches, teams, and players. The bot uses AI and machine learning to enable human-like conversations and learns from user interactions over time. It also supports Telugu language for conversations.

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Features

- **IPL Data**: Access to extensive IPL datasets for insights, stats, and updates
- **AI Conversations**: Human-like conversations that improve over time
- **Telugu Language Support**: Interact with the bot in Telugu
- **Admin Privileges**: Manage user interactions, customize responses, and moderate content
- **Scalable Architecture**: Optimized for real-time performance with multiple database support
- **Group Chat Support**: Works in both private chats and group conversations

## Requirements

- Python 3.8+
- Telegram API credentials (API ID, API Hash, Bot Token)
- MongoDB database
- Kaggle account for dataset access

## Installation

### Local Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Tg-ipl.git
   cd Tg-ipl
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials:
   ```
   # Telegram API credentials
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token

   # MongoDB connection
   MONGODB_URI=your_mongodb_uri
   MONGODB_URI_BACKUP=your_backup_mongodb_uri  # Optional

   # Kaggle credentials
   KAGGLE_USERNAME=your_kaggle_username
   KAGGLE_KEY=your_kaggle_key

   # Admin users (comma-separated Telegram user IDs)
   ADMIN_USERS=123456789,987654321
   ```

5. Run the bot:
   ```
   python bot.py
   ```

### Heroku Deployment

1. Click the "Deploy to Heroku" button above
2. Fill in the required environment variables:
   - `API_ID`: Your Telegram API ID from [my.telegram.org](https://my.telegram.org)
   - `API_HASH`: Your Telegram API Hash from [my.telegram.org](https://my.telegram.org)
   - `BOT_TOKEN`: Your Telegram Bot Token from [@BotFather](https://t.me/BotFather)
   - `MONGODB_URI`: Your MongoDB connection URI
   - `KAGGLE_USERNAME`: Your Kaggle username
   - `KAGGLE_KEY`: Your Kaggle API key

3. Deploy the app

## MongoDB Setup

The bot requires a MongoDB database for storing user data and conversations. You can use MongoDB Atlas for a free cloud-hosted database:

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (the free tier is sufficient)
3. Create a database user with read/write permissions
4. Get your connection string from the "Connect" button
5. Add your connection string to the `.env` file or Heroku environment variables

**Important**: The free tier of MongoDB Atlas has a 512MB storage limit. The bot is designed to switch to a backup database when the primary database approaches this limit. You can set up a second MongoDB database and provide its connection string as `MONGODB_URI_BACKUP`.

## Kaggle API Setup

To access the IPL and Telugu NLP datasets, you need Kaggle API credentials:

1. Create a Kaggle account at [kaggle.com](https://www.kaggle.com/)
2. Go to your account settings
3. Scroll down to the API section and click "Create New API Token"
4. This will download a `kaggle.json` file with your credentials
5. Add your Kaggle username and key to the `.env` file or Heroku environment variables

## Bot Commands

- `/start` - Start the bot
- `/help` - Show available commands
- `/stats` - Get IPL statistics
- `/player <name>` - Get player information
- `/team <name>` - Get team information
- `/match <team1> vs <team2>` - Get match information
- `/telugu` - Switch to Telugu mode
- `/english` - Switch to English mode
- `/admin` - Admin commands (for admins only)

### Admin Commands

- `/stats_admin` - Get bot usage statistics
- `/broadcast <message>` - Send a message to all users
- `/blacklist <user_id>` - Blacklist a user
- `/whitelist <user_id>` - Remove a user from blacklist
- `/db_status` - Check database status
- `/set_response <trigger>:<response>` - Set custom response

## Project Structure

- `bot.py` - Main bot file
- `app.py` - Web server for Heroku
- `utils/` - Utility functions
  - `config.py` - Configuration loader
  - `data_loader.py` - Dataset loader
- `database/` - Database handlers
  - `mongo_client.py` - MongoDB client
- `handlers/` - Message handlers
  - `command_handler.py` - Command handlers
  - `message_handler.py` - Message handlers
  - `admin_handler.py` - Admin command handlers
- `ml/` - Machine learning components
  - `nlp_processor.py` - NLP processing
  - `conversation_model.py` - Conversation model
  - `ipl_stats.py` - IPL statistics
- `data/` - Data storage
- `templates/` - Web templates

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Telethon](https://github.com/LonamiWebs/Telethon) - Python MTProto library for Telegram
- [IPL Dataset](https://github.com/12345k/IPL-Dataset) - IPL cricket data
- [Telugu NLP Dataset](https://www.kaggle.com/sudalairajkumar/telugu-nlp) - Telugu language processing data
