import logging
from telethon import events
from datetime import datetime
from utils.data_loader import get_ipl_data
from ml.ipl_stats import get_ipl_stats, search_ipl_data
from ml.nlp_processor import process_telugu_text
from ml import gemini_ai

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
            # First, try to get stats from Gemini AI
            gemini_stats = None
            if gemini_ai.is_available():
                # Let the user know we're fetching data
                await event.respond(f"Fetching latest IPL statistics...")
                gemini_stats = await gemini_ai.get_ipl_stats()

            if gemini_stats:
                # Format the response from Gemini AI
                stats_message = (
                    "📊 **IPL Statistics**\n\n"
                    f"• Total Matches: {gemini_stats.get('total_matches', 'N/A')}\n"
                    f"• Most Wins: {gemini_stats.get('most_wins_team', 'N/A')} ({gemini_stats.get('most_wins_count', 'N/A')} wins)\n"
                    f"• Highest Score: {gemini_stats.get('highest_score_team', 'N/A')} ({gemini_stats.get('highest_score', 'N/A')} runs)\n"
                    f"• Most Runs: {gemini_stats.get('most_runs_player', 'N/A')} ({gemini_stats.get('most_runs', 'N/A')} runs)\n"
                    f"• Most Wickets: {gemini_stats.get('most_wickets_player', 'N/A')} ({gemini_stats.get('most_wickets', 'N/A')} wickets)\n"
                )

                # Add data source
                stats_message += f"\n_Data provided by Gemini AI - {datetime.now().strftime('%Y-%m-%d')}_"

                await event.respond(stats_message)
                return

            # Fallback to local data if Gemini AI is not available or fails
            stats = get_ipl_stats()

            if not stats:
                await event.respond(f"Sorry, I couldn't retrieve IPL statistics at the moment.")
                return

            # Format the response from local data
            stats_message = (
                "📊 **IPL Statistics**\n\n"
                f"• Total Matches: {stats.get('total_matches', 'N/A')}\n"
                f"• Most Wins: {stats.get('most_wins_team', 'N/A')} ({stats.get('most_wins_count', 'N/A')} wins)\n"
                f"• Highest Score: {stats.get('highest_score_team', 'N/A')} ({stats.get('highest_score', 'N/A')} runs)\n"
                f"• Most Runs: {stats.get('most_runs_player', 'N/A')} ({stats.get('most_runs', 'N/A')} runs)\n"
                f"• Most Wickets: {stats.get('most_wickets_player', 'N/A')} ({stats.get('most_wickets', 'N/A')} wickets)\n"
            )

            # Add data source
            stats_message += f"\n_Data from local database - may not be current_"

            await event.respond(stats_message)

        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await event.respond("Sorry, an error occurred while retrieving statistics.\nPlease try again later.")

            # Try to provide some helpful information even if there's an error
            try:
                await event.respond(f"You can also try other commands like /team CSK or /player Virat Kohli.")
            except:
                pass

    @client.on(events.NewMessage(pattern='/player (.+)'))
    async def player_command(event):
        """Handle /player command"""
        try:
            player_name = event.pattern_match.group(1).strip()

            # First, try to get player info from Gemini AI
            gemini_player_info = None
            if gemini_ai.is_available():
                # Let the user know we're fetching data
                await event.respond(f"Fetching latest information about {player_name}...")
                gemini_player_info = await gemini_ai.get_ipl_player_info(player_name)

            if gemini_player_info:
                # Format the response from Gemini AI
                player_message = (
                    f"🏏 **{gemini_player_info.get('name', player_name)}**\n\n"
                    f"• Team: {gemini_player_info.get('team', 'N/A')}\n"
                    f"• Role: {gemini_player_info.get('role', 'N/A')}\n"
                    f"• Matches: {gemini_player_info.get('matches', 'N/A')}\n"
                    f"• Runs: {gemini_player_info.get('runs', 'N/A')}\n"
                    f"• Wickets: {gemini_player_info.get('wickets', 'N/A')}\n"
                )

                # Add recent performance if available
                if 'recent_performance' in gemini_player_info:
                    player_message += f"\n**Recent Performance:**\n{gemini_player_info['recent_performance']}\n"

                # Add data source
                player_message += f"\n_Data provided by Gemini AI - {datetime.now().strftime('%Y-%m-%d')}_"

                await event.respond(player_message)
                return

            # Fallback to local data if Gemini AI is not available or fails
            player_info = search_ipl_data('player', player_name)

            if not player_info:
                await event.respond(f"Sorry, I couldn't find information about player '{player_name}'.")
                return

            # Format the response from local data
            player_message = (
                f"🏏 **{player_info['name']}**\n\n"
                f"• Team: {player_info['team']}\n"
                f"• Role: {player_info['role']}\n"
                f"• Matches: {player_info['matches']}\n"
                f"• Runs: {player_info['runs']}\n"
                f"• Wickets: {player_info['wickets']}\n"
            )

            # Add additional fields if they exist
            if 'average' in player_info:
                player_message += f"• Average: {player_info['average']}\n"

            if 'strike_rate' in player_info:
                player_message += f"• Strike Rate: {player_info['strike_rate']}\n"

            if 'economy' in player_info:
                player_message += f"• Economy: {player_info['economy']}\n"

            # Add data source
            player_message += f"\n_Data from local database - may not be current_"

            await event.respond(player_message)

        except Exception as e:
            logger.error(f"Error in player command: {e}")
            await event.respond("Sorry, an error occurred while retrieving player information.\nPlease try again later or try with a different player name.")

            # Try to provide some helpful information even if there's an error
            try:
                await event.respond(f"You can try searching for popular players like Virat Kohli, MS Dhoni, or Rohit Sharma.")
            except:
                pass

    @client.on(events.NewMessage(pattern='/team (.+)'))
    async def team_command(event):
        """Handle /team command"""
        try:
            team_name = event.pattern_match.group(1).strip()

            # First, try to get team info from Gemini AI
            gemini_team_info = None
            if gemini_ai.is_available():
                # Let the user know we're fetching data
                await event.respond(f"Fetching latest information about {team_name}...")
                gemini_team_info = await gemini_ai.get_ipl_team_info(team_name)

            if gemini_team_info:
                # Format the response from Gemini AI
                team_message = (
                    f"🏆 **{gemini_team_info.get('name', team_name)}**\n\n"
                    f"• Full Name: {gemini_team_info.get('full_name', 'N/A')}\n"
                    f"• Home Ground: {gemini_team_info.get('home_ground', 'N/A')}\n"
                    f"• Captain: {gemini_team_info.get('captain', 'N/A')}\n"
                )

                # Add coach if available
                if 'coach' in gemini_team_info:
                    team_message += f"• Coach: {gemini_team_info['coach']}\n"

                # Add championships if available
                team_message += f"• Championships: {gemini_team_info.get('championships', 'N/A')}\n"

                # Add key players if available
                if 'key_players' in gemini_team_info:
                    team_message += f"• Key Players: {gemini_team_info['key_players']}\n"

                # Add recent performance if available
                if 'recent_performance' in gemini_team_info:
                    team_message += f"\n**Recent Performance:**\n{gemini_team_info['recent_performance']}\n"

                # Add data source
                team_message += f"\n_Data provided by Gemini AI - {datetime.now().strftime('%Y-%m-%d')}_"

                await event.respond(team_message)
                return

            # Fallback to local data if Gemini AI is not available or fails
            team_info = search_ipl_data('team', team_name)

            if not team_info:
                await event.respond(f"Sorry, I couldn't find information about team '{team_name}'.")
                return

            # Format the response from local data
            team_message = (
                f"🏆 **{team_info['name']}**\n\n"
                f"• Full Name: {team_info['full_name']}\n"
                f"• Home Ground: {team_info['home_ground']}\n"
                f"• Captain: {team_info['captain']}\n"
            )

            # Add additional fields if they exist
            if 'coach' in team_info:
                team_message += f"• Coach: {team_info['coach']}\n"

            team_message += f"• Championships: {team_info['championships']}\n"

            if 'matches_played' in team_info:
                team_message += f"• Matches Played: {team_info['matches_played']}\n"

            if 'wins' in team_info:
                team_message += f"• Wins: {team_info['wins']}\n"

            if 'losses' in team_info:
                team_message += f"• Losses: {team_info['losses']}\n"

            if 'win_percentage' in team_info:
                team_message += f"• Win Percentage: {team_info['win_percentage']}%\n"

            # Add data source
            team_message += f"\n_Data from local database - may not be current_"

            await event.respond(team_message)

        except Exception as e:
            logger.error(f"Error in team command: {e}")
            await event.respond("Sorry, an error occurred while retrieving team information.\nPlease try again later or try with a different team name.")

            # Try to provide some helpful information even if there's an error
            try:
                await event.respond(f"You can try searching for popular teams like CSK, MI, RCB, or KKR.")
            except:
                pass

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
