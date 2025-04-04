import os
import logging
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize Gemini AI with API key from environment variable
try:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
        logger.info("Gemini AI initialized successfully")
    else:
        GEMINI_AVAILABLE = False
        logger.warning("GEMINI_API_KEY not found in environment variables")
except Exception as e:
    GEMINI_AVAILABLE = False
    logger.error(f"Error initializing Gemini AI: {e}")

# Configure the model
GEMINI_MODEL = "gemini-1.5-pro"

def is_available():
    """
    Check if Gemini AI is available
    """
    return GEMINI_AVAILABLE

async def get_ipl_team_info(team_name):
    """
    Get up-to-date information about an IPL team using Gemini AI
    """
    if not GEMINI_AVAILABLE:
        logger.warning("Gemini AI not available for team info")
        return None
    
    try:
        current_year = datetime.now().year
        
        prompt = f"""
        Provide detailed information about the IPL cricket team {team_name} for the {current_year} season.
        Include the following information:
        - Full team name
        - Home ground
        - Current captain
        - Current coach
        - Number of IPL championships won
        - Current squad key players
        - Recent performance in IPL {current_year}
        
        Format the response as a structured JSON object with the following fields:
        name, full_name, home_ground, captain, coach, championships, key_players, recent_performance
        
        Do not include any explanatory text outside the JSON structure.
        """
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        import json
        import re
        
        # Try to extract JSON from the response
        response_text = response.text
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no JSON code block, try to parse the whole response
            json_str = response_text
        
        # Clean up the string and parse JSON
        json_str = json_str.strip()
        if json_str.startswith('{') and json_str.endswith('}'):
            team_data = json.loads(json_str)
            return team_data
        else:
            logger.error(f"Invalid JSON response from Gemini AI: {json_str}")
            return None
    
    except Exception as e:
        logger.error(f"Error getting team info from Gemini AI: {e}")
        return None

async def get_ipl_player_info(player_name):
    """
    Get up-to-date information about an IPL player using Gemini AI
    """
    if not GEMINI_AVAILABLE:
        logger.warning("Gemini AI not available for player info")
        return None
    
    try:
        current_year = datetime.now().year
        
        prompt = f"""
        Provide detailed information about the IPL cricket player {player_name} for the {current_year} season.
        Include the following information:
        - Full name
        - Current IPL team
        - Playing role (batsman, bowler, all-rounder, etc.)
        - Number of IPL matches played
        - Total IPL runs scored
        - Total IPL wickets taken
        - Recent performance in IPL {current_year}
        
        Format the response as a structured JSON object with the following fields:
        name, team, role, matches, runs, wickets, recent_performance
        
        Do not include any explanatory text outside the JSON structure.
        """
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        import json
        import re
        
        # Try to extract JSON from the response
        response_text = response.text
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no JSON code block, try to parse the whole response
            json_str = response_text
        
        # Clean up the string and parse JSON
        json_str = json_str.strip()
        if json_str.startswith('{') and json_str.endswith('}'):
            player_data = json.loads(json_str)
            return player_data
        else:
            logger.error(f"Invalid JSON response from Gemini AI: {json_str}")
            return None
    
    except Exception as e:
        logger.error(f"Error getting player info from Gemini AI: {e}")
        return None

async def get_ipl_match_info(team1, team2):
    """
    Get up-to-date information about an IPL match using Gemini AI
    """
    if not GEMINI_AVAILABLE:
        logger.warning("Gemini AI not available for match info")
        return None
    
    try:
        current_year = datetime.now().year
        
        prompt = f"""
        Provide information about the most recent or upcoming IPL {current_year} match between {team1} and {team2}.
        Include the following information:
        - Match date
        - Venue
        - Result (if played) or scheduled time (if upcoming)
        - Key highlights or predictions
        
        Format the response as a structured JSON object with the following fields:
        team1, team2, date, venue, result, highlights
        
        Do not include any explanatory text outside the JSON structure.
        """
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        import json
        import re
        
        # Try to extract JSON from the response
        response_text = response.text
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no JSON code block, try to parse the whole response
            json_str = response_text
        
        # Clean up the string and parse JSON
        json_str = json_str.strip()
        if json_str.startswith('{') and json_str.endswith('}'):
            match_data = json.loads(json_str)
            return match_data
        else:
            logger.error(f"Invalid JSON response from Gemini AI: {json_str}")
            return None
    
    except Exception as e:
        logger.error(f"Error getting match info from Gemini AI: {e}")
        return None

async def get_ipl_stats():
    """
    Get up-to-date IPL statistics using Gemini AI
    """
    if not GEMINI_AVAILABLE:
        logger.warning("Gemini AI not available for IPL stats")
        return None
    
    try:
        current_year = datetime.now().year
        
        prompt = f"""
        Provide current statistics for the IPL {current_year} season.
        Include the following information:
        - Total matches played so far
        - Team with most wins
        - Number of wins for that team
        - Team with highest score
        - Highest score value
        - Player with most runs
        - Number of runs for that player
        - Player with most wickets
        - Number of wickets for that player
        
        Format the response as a structured JSON object with the following fields:
        total_matches, most_wins_team, most_wins_count, highest_score_team, highest_score, 
        most_runs_player, most_runs, most_wickets_player, most_wickets
        
        Do not include any explanatory text outside the JSON structure.
        """
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        import json
        import re
        
        # Try to extract JSON from the response
        response_text = response.text
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no JSON code block, try to parse the whole response
            json_str = response_text
        
        # Clean up the string and parse JSON
        json_str = json_str.strip()
        if json_str.startswith('{') and json_str.endswith('}'):
            stats_data = json.loads(json_str)
            return stats_data
        else:
            logger.error(f"Invalid JSON response from Gemini AI: {json_str}")
            return None
    
    except Exception as e:
        logger.error(f"Error getting IPL stats from Gemini AI: {e}")
        return None

async def chat_with_gemini(message, language='english'):
    """
    Chat with Gemini AI
    """
    if not GEMINI_AVAILABLE:
        logger.warning("Gemini AI not available for chat")
        return None
    
    try:
        is_telugu = language == 'telugu'
        
        prompt = f"""
        You are an IPL cricket expert assistant who is knowledgeable about all IPL seasons including the current {datetime.now().year} season.
        
        User message: {message}
        
        Respond in a friendly, conversational manner with accurate and up-to-date information about IPL cricket.
        Keep your response concise (under 200 words).
        
        {f"Please respond in Telugu language." if is_telugu else ""}
        """
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        return response.text.strip()
    
    except Exception as e:
        logger.error(f"Error chatting with Gemini AI: {e}")
        return None
