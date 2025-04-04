import logging
from telethon import events
from datetime import datetime
from utils.data_loader import get_ipl_data
from ml.ipl_stats import get_ipl_stats, search_ipl_data
from ml.nlp_processor import process_telugu_text

logger = logging.getLogger(__name__)

def setup_command_handlers(client, db_client):
    """
    Set up command handlers for the bot
    """

    @client.on(events.NewMessage(pattern='/start'))
    async def start_command(event):
        """Handle /start command"""
        try:
            user = await event.get_sender()

            # Save user to database
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'first_seen': datetime.now(),
                'last_active': datetime.now()
            }

            # Try to save user, but continue even if it fails
            try:
                db_client.save_user(user_data)
            except Exception as e:
                logger.error(f"Error saving user data: {e}")
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            user = await event.get_sender()
            # Continue with minimal user info if there was an error

        welcome_message = (
            f"👋 Hello {user.first_name}!\n\n"
            f"Welcome to the IPL Bot. I can provide you with information about IPL matches, "
            f"players, teams, and statistics. I can also chat with you in Telugu!\n\n"
            f"Here are some commands you can use:\n"
            f"• /help - Show available commands\n"
            f"• /stats - Get IPL statistics\n"
            f"• /player <name> - Get player information\n"
            f"• /team <name> - Get team information\n"
            f"• /telugu - Switch to Telugu mode\n\n"
            f"You can also just chat with me normally, and I'll try to understand and respond!"
        )

        await event.respond(welcome_message)

    @client.on(events.NewMessage(pattern='/help'))
    async def help_command(event):
        """Handle /help command"""
        help_message = (
            "🤖 **IPL Bot Commands**\n\n"
            "• /start - Start the bot\n"
            "• /help - Show this help message\n"
            "• /stats - Get IPL statistics\n"
            "• /player <name> - Get player information\n"
            "• /team <name> - Get team information\n"
            "• /match <team1> vs <team2> - Get match information\n"
            "• /telugu - Switch to Telugu mode\n"
            "• /admin - Admin commands (for admins only)\n\n"
            "You can also just chat with me normally in English or Telugu, and I'll try to understand and respond!"
        )

        await event.respond(help_message)

    @client.on(events.NewMessage(pattern='/stats'))
    async def stats_command(event):
        """Handle /stats command"""
        try:
            stats = get_ipl_stats()

            if not stats:
                await event.respond("Sorry, I couldn't retrieve IPL statistics at the moment. Please try again later.")
                return

            stats_message = (
                "📊 **IPL Statistics**\n\n"
                f"• Total Matches: {stats['total_matches']}\n"
                f"• Most Wins: {stats['most_wins_team']} ({stats['most_wins_count']} wins)\n"
                f"• Highest Score: {stats['highest_score_team']} ({stats['highest_score']} runs)\n"
                f"• Most Runs: {stats['most_runs_player']} ({stats['most_runs']} runs)\n"
                f"• Most Wickets: {stats['most_wickets_player']} ({stats['most_wickets']} wickets)\n"
            )

            await event.respond(stats_message)

        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await event.respond("Sorry, an error occurred while retrieving statistics.")

    @client.on(events.NewMessage(pattern='/player (.+)'))
    async def player_command(event):
        """Handle /player command"""
        try:
            player_name = event.pattern_match.group(1).strip()

            # Search for player in IPL data
            player_info = search_ipl_data('player', player_name)

            if not player_info:
                await event.respond(f"Sorry, I couldn't find information about player '{player_name}'.")
                return

            player_message = (
                f"🏏 **{player_info['name']}**\n\n"
                f"• Team: {player_info['team']}\n"
                f"• Role: {player_info['role']}\n"
                f"• Matches: {player_info['matches']}\n"
                f"• Runs: {player_info['runs']}\n"
                f"• Average: {player_info['average']}\n"
                f"• Strike Rate: {player_info['strike_rate']}\n"
                f"• Wickets: {player_info['wickets']}\n"
                f"• Economy: {player_info['economy']}\n"
            )

            await event.respond(player_message)

        except Exception as e:
            logger.error(f"Error in player command: {e}")
            await event.respond("Sorry, an error occurred while retrieving player information.")

    @client.on(events.NewMessage(pattern='/team (.+)'))
    async def team_command(event):
        """Handle /team command"""
        try:
            team_name = event.pattern_match.group(1).strip()

            # Search for team in IPL data
            team_info = search_ipl_data('team', team_name)

            if not team_info:
                await event.respond(f"Sorry, I couldn't find information about team '{team_name}'.")
                return

            team_message = (
                f"🏆 **{team_info['name']}**\n\n"
                f"• Full Name: {team_info['full_name']}\n"
                f"• Home Ground: {team_info['home_ground']}\n"
                f"• Captain: {team_info['captain']}\n"
                f"• Coach: {team_info['coach']}\n"
                f"• Championships: {team_info['championships']}\n"
                f"• Matches Played: {team_info['matches_played']}\n"
                f"• Wins: {team_info['wins']}\n"
                f"• Losses: {team_info['losses']}\n"
                f"• Win Percentage: {team_info['win_percentage']}%\n"
            )

            await event.respond(team_message)

        except Exception as e:
            logger.error(f"Error in team command: {e}")
            await event.respond("Sorry, an error occurred while retrieving team information.")

    @client.on(events.NewMessage(pattern='/telugu'))
    async def telugu_command(event):
        """Handle /telugu command"""
        user = await event.get_sender()

        # Update user preference in database
        user_data = {
            'user_id': user.id,
            'language_preference': 'telugu',
            'last_active': datetime.now()
        }
        db_client.save_user(user_data)

        # Respond in Telugu
        telugu_message = "తెలుగు మోడ్ ఎంచుకోబడింది. నేను ఇప్పుడు తెలుగులో సమాధానం ఇస్తాను."
        english_translation = "Telugu mode selected. I will now respond in Telugu."

        await event.respond(f"{telugu_message}\n\n{english_translation}")

    @client.on(events.NewMessage(pattern='/english'))
    async def english_command(event):
        """Handle /english command"""
        user = await event.get_sender()

        # Update user preference in database
        user_data = {
            'user_id': user.id,
            'language_preference': 'english',
            'last_active': datetime.now()
        }
        db_client.save_user(user_data)

        await event.respond("English mode selected. I will now respond in English.")

    logger.info("Command handlers have been set up")
