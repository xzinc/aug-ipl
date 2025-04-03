import logging
import os
from telethon import events
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def setup_admin_handlers(client, db_client):
    """
    Set up admin handlers for the bot
    """
    
    async def is_admin(event):
        """Check if the user is an admin"""
        user = await event.get_sender()
        admin_users = os.getenv('ADMIN_USERS', '').split(',')
        admin_users = [int(id) for id in admin_users if id]
        
        return user.id in admin_users
    
    @client.on(events.NewMessage(pattern='/admin'))
    async def admin_command(event):
        """Handle /admin command"""
        if not await is_admin(event):
            await event.respond("You don't have permission to use admin commands.")
            return
        
        admin_help = (
            "🔐 **Admin Commands**\n\n"
            "• /stats_admin - Get bot usage statistics\n"
            "• /broadcast <message> - Send a message to all users\n"
            "• /blacklist <user_id> - Blacklist a user\n"
            "• /whitelist <user_id> - Remove a user from blacklist\n"
            "• /db_status - Check database status\n"
            "• /set_response <trigger>:<response> - Set custom response\n"
        )
        
        await event.respond(admin_help)
    
    @client.on(events.NewMessage(pattern='/stats_admin'))
    async def stats_admin_command(event):
        """Handle /stats_admin command"""
        if not await is_admin(event):
            await event.respond("You don't have permission to use admin commands.")
            return
        
        try:
            # Get database collections
            users_collection = db_client.get_collection('users')
            messages_collection = db_client.get_collection('messages')
            
            # Count total users
            total_users = users_collection.count_documents({})
            
            # Count active users in the last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            active_users = users_collection.count_documents({
                'last_active': {'$gte': yesterday}
            })
            
            # Count total messages
            total_messages = messages_collection.count_documents({})
            
            # Count messages in the last 24 hours
            recent_messages = messages_collection.count_documents({
                'timestamp': {'$gte': yesterday}
            })
            
            # Get database size
            db_stats = db_client.db.command("dbStats")
            db_size_mb = db_stats["dataSize"] / (1024 * 1024)
            
            stats_message = (
                "📊 **Bot Statistics**\n\n"
                f"• Total Users: {total_users}\n"
                f"• Active Users (24h): {active_users}\n"
                f"• Total Messages: {total_messages}\n"
                f"• Recent Messages (24h): {recent_messages}\n"
                f"• Database Size: {db_size_mb:.2f} MB\n"
                f"• Using Backup DB: {'Yes' if db_client.is_using_backup else 'No'}\n"
            )
            
            await event.respond(stats_message)
        
        except Exception as e:
            logger.error(f"Error in stats_admin command: {e}")
            await event.respond(f"Error retrieving statistics: {str(e)}")
    
    @client.on(events.NewMessage(pattern='/broadcast (.+)'))
    async def broadcast_command(event):
        """Handle /broadcast command"""
        if not await is_admin(event):
            await event.respond("You don't have permission to use admin commands.")
            return
        
        message = event.pattern_match.group(1).strip()
        
        try:
            # Get all users
            users_collection = db_client.get_collection('users')
            users = users_collection.find({}, {'user_id': 1})
            
            sent_count = 0
            failed_count = 0
            
            await event.respond(f"Broadcasting message to {users_collection.count_documents({})} users...")
            
            for user in users:
                try:
                    await client.send_message(user['user_id'], message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send broadcast to user {user['user_id']}: {e}")
                    failed_count += 1
            
            await event.respond(f"Broadcast completed. Sent to {sent_count} users. Failed: {failed_count}")
        
        except Exception as e:
            logger.error(f"Error in broadcast command: {e}")
            await event.respond(f"Error broadcasting message: {str(e)}")
    
    @client.on(events.NewMessage(pattern='/blacklist (\d+)'))
    async def blacklist_command(event):
        """Handle /blacklist command"""
        if not await is_admin(event):
            await event.respond("You don't have permission to use admin commands.")
            return
        
        user_id = int(event.pattern_match.group(1).strip())
        
        try:
            # Add user to blacklist
            blacklist_collection = db_client.get_collection('blacklist')
            
            # Check if already blacklisted
            if blacklist_collection.find_one({'user_id': user_id}):
                await event.respond(f"User {user_id} is already blacklisted.")
                return
            
            # Add to blacklist
            blacklist_collection.insert_one({
                'user_id': user_id,
                'blacklisted_at': datetime.now(),
                'blacklisted_by': (await event.get_sender()).id
            })
            
            await event.respond(f"User {user_id} has been blacklisted.")
        
        except Exception as e:
            logger.error(f"Error in blacklist command: {e}")
            await event.respond(f"Error blacklisting user: {str(e)}")
    
    @client.on(events.NewMessage(pattern='/whitelist (\d+)'))
    async def whitelist_command(event):
        """Handle /whitelist command"""
        if not await is_admin(event):
            await event.respond("You don't have permission to use admin commands.")
            return
        
        user_id = int(event.pattern_match.group(1).strip())
        
        try:
            # Remove user from blacklist
            blacklist_collection = db_client.get_collection('blacklist')
            
            # Check if blacklisted
            if not blacklist_collection.find_one({'user_id': user_id}):
                await event.respond(f"User {user_id} is not blacklisted.")
                return
            
            # Remove from blacklist
            blacklist_collection.delete_one({'user_id': user_id})
            
            await event.respond(f"User {user_id} has been removed from the blacklist.")
        
        except Exception as e:
            logger.error(f"Error in whitelist command: {e}")
            await event.respond(f"Error whitelisting user: {str(e)}")
    
    @client.on(events.NewMessage(pattern='/db_status'))
    async def db_status_command(event):
        """Handle /db_status command"""
        if not await is_admin(event):
            await event.respond("You don't have permission to use admin commands.")
            return
        
        try:
            # Get database status
            db_stats = db_client.db.command("dbStats")
            db_size_mb = db_stats["dataSize"] / (1024 * 1024)
            storage_size_mb = db_stats["storageSize"] / (1024 * 1024)
            
            # Get collection stats
            collections = db_client.db.list_collection_names()
            collection_stats = []
            
            for collection in collections:
                coll_stats = db_client.db.command("collStats", collection)
                coll_size_mb = coll_stats["size"] / (1024 * 1024)
                collection_stats.append((collection, coll_size_mb))
            
            # Sort by size
            collection_stats.sort(key=lambda x: x[1], reverse=True)
            
            status_message = (
                "🗄️ **Database Status**\n\n"
                f"• Database: {'Backup' if db_client.is_using_backup else 'Primary'}\n"
                f"• Total Size: {db_size_mb:.2f} MB\n"
                f"• Storage Size: {storage_size_mb:.2f} MB\n"
                f"• Collections: {len(collections)}\n\n"
                "**Collection Sizes:**\n"
            )
            
            for coll, size in collection_stats:
                status_message += f"• {coll}: {size:.2f} MB\n"
            
            await event.respond(status_message)
        
        except Exception as e:
            logger.error(f"Error in db_status command: {e}")
            await event.respond(f"Error retrieving database status: {str(e)}")
    
    @client.on(events.NewMessage(pattern='/set_response (.+?):(.+)'))
    async def set_response_command(event):
        """Handle /set_response command"""
        if not await is_admin(event):
            await event.respond("You don't have permission to use admin commands.")
            return
        
        trigger = event.pattern_match.group(1).strip()
        response = event.pattern_match.group(2).strip()
        
        try:
            # Save custom response
            responses_collection = db_client.get_collection('custom_responses')
            
            # Check if trigger already exists
            existing = responses_collection.find_one({'trigger': trigger})
            
            if existing:
                # Update existing response
                responses_collection.update_one(
                    {'trigger': trigger},
                    {'$set': {'response': response, 'updated_at': datetime.now()}}
                )
                await event.respond(f"Updated response for trigger '{trigger}'.")
            else:
                # Add new response
                responses_collection.insert_one({
                    'trigger': trigger,
                    'response': response,
                    'created_at': datetime.now(),
                    'created_by': (await event.get_sender()).id
                })
                await event.respond(f"Added new response for trigger '{trigger}'.")
        
        except Exception as e:
            logger.error(f"Error in set_response command: {e}")
            await event.respond(f"Error setting custom response: {str(e)}")
    
    logger.info("Admin handlers have been set up")
