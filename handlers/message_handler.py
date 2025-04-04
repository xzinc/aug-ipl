import logging
import re
from telethon import events
from datetime import datetime
from ml.nlp_processor import process_text, is_telugu_text, process_telugu_text
from ml.conversation_model import get_response
from ml import gemini_ai

logger = logging.getLogger(__name__)

def setup_message_handlers(client, db_client):
    """
    Set up message handlers for the bot
    """

    @client.on(events.NewMessage(incoming=True))
    async def handle_message(event):
        """Handle incoming messages"""
        # Ignore commands
        if event.message.text.startswith('/'):
            return

        # Ignore messages from channels or other bots
        if event.is_channel or (hasattr(event.sender, 'bot') and event.sender.bot):
            return

        user = await event.get_sender()

        # Save message to database for learning
        try:
            message_data = {
                'user_id': user.id,
                'message_id': event.message.id,
                'text': event.message.text,
                'timestamp': datetime.now(),
                'chat_id': event.chat_id,
                'is_group': event.is_group
            }
            db_client.save_message(message_data)
        except Exception as e:
            logger.error(f"Error saving message: {e}")

        # Update user's last active timestamp
        try:
            user_data = {
                'user_id': user.id,
                'last_active': datetime.now()
            }
            db_client.save_user(user_data)
        except Exception as e:
            logger.error(f"Error updating user: {e}")

        # Get user preferences from database
        language_preference = 'english'
        try:
            db_user = db_client.get_user(user.id)
            if db_user:
                language_preference = db_user.get('language_preference', 'english')
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")

        # Check if message is in Telugu
        message_text = event.message.text
        is_telugu = is_telugu_text(message_text)

        # Determine language preference
        current_language = 'telugu' if is_telugu or language_preference == 'telugu' else 'english'

        # First try to get response from Gemini AI
        gemini_response = None
        if gemini_ai.is_available():
            try:
                gemini_response = await gemini_ai.chat_with_gemini(message_text, current_language)
                logger.info(f"Got response from Gemini AI: {gemini_response[:50]}...")
            except Exception as e:
                logger.error(f"Error getting response from Gemini AI: {e}")

        if gemini_response:
            # Send Gemini AI response
            response = gemini_response
        else:
            # Fallback to local model if Gemini AI is not available or fails
            # Process message based on language
            if current_language == 'telugu':
                # Process Telugu message
                if is_telugu:
                    processed_text = process_telugu_text(message_text)
                else:
                    # User has Telugu preference but sent English message
                    processed_text = process_text(message_text)
                response = get_response(processed_text, 'telugu')
            else:
                # Process English message
                processed_text = process_text(message_text)
                response = get_response(processed_text, 'english')

        # Send response
        await event.respond(response)

        # Save bot's response to database for learning
        response_data = {
            'user_id': user.id,
            'message_id': None,  # We don't have the message ID yet
            'text': response,
            'timestamp': datetime.now(),
            'chat_id': event.chat_id,
            'is_group': event.is_group,
            'is_bot_response': True,
            'in_response_to': event.message.id
        }
        db_client.save_message(response_data)

    @client.on(events.ChatAction)
    async def handle_chat_action(event):
        """Handle chat actions like user joining a group"""
        if event.user_joined:
            # Bot was added to a group
            if event.user_id == client.get_me().id:
                group_info = await event.get_chat()

                welcome_message = (
                    f"👋 Hello everyone in {group_info.title}!\n\n"
                    f"I'm the IPL Bot. I can provide information about IPL matches, "
                    f"players, teams, and statistics. I can also chat in Telugu!\n\n"
                    f"Type /help to see available commands."
                )

                await event.respond(welcome_message)

    logger.info("Message handlers have been set up")
