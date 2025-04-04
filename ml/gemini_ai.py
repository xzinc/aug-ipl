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
        You are an IPL cricket expert with access to the most current information about the {current_year} IPL season.

        Provide detailed and ACCURATE information about the IPL cricket team {team_name} for the {current_year} season.
        Make sure all information is CURRENT and UP-TO-DATE for the {current_year} IPL season.

        Include the following information:
        - Full team name (with correct spelling and capitalization)
        - Home ground (current for {current_year})
        - Current captain (for {current_year} season)
        - Current coach (for {current_year} season)
        - Number of IPL championships won (including any recent wins)
        - Current squad key players (star players in {current_year})
        - Recent performance in IPL {current_year} (current standing, recent match results)
        - Team owner (current ownership)

        Format the response as a structured JSON object with the following fields:
        name, full_name, home_ground, captain, coach, championships, key_players, recent_performance, owner

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
            logger.info(f"Successfully retrieved current {current_year} data for {team_name}")
            return team_data
        else:
            logger.error(f"Invalid JSON response from Gemini AI: {json_str}")
            # Try to extract JSON from unstructured text as a fallback
            try:
                # Find anything that looks like a JSON object
                potential_json = re.search(r'\{.*\}', response_text, re.DOTALL)
                if potential_json:
                    team_data = json.loads(potential_json.group(0))
                    logger.info(f"Extracted JSON from unstructured response for {team_name}")
                    return team_data
            except:
                pass
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
        You are an IPL cricket expert with access to the most current information about the {current_year} IPL season.

        Provide detailed and ACCURATE information about the IPL cricket player {player_name} for the {current_year} season.
        Make sure all information is CURRENT and UP-TO-DATE for the {current_year} IPL season.

        Include the following information:
        - Full name (with correct spelling)
        - Current IPL team in {current_year} season
        - Playing role (batsman, bowler, all-rounder, wicket-keeper, etc.)
        - Number of IPL matches played (total career)
        - Total IPL runs scored (career total)
        - Total IPL wickets taken (career total)
        - Batting average and strike rate
        - Recent performance in IPL {current_year} (include specific stats from recent matches)
        - Country of origin
        - Current form (is the player in good form this season?)

        Format the response as a structured JSON object with the following fields:
        name, team, role, matches, runs, wickets, batting_avg, strike_rate, recent_performance, country, current_form

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
            logger.info(f"Successfully retrieved current {current_year} data for player {player_name}")
            return player_data
        else:
            logger.error(f"Invalid JSON response from Gemini AI: {json_str}")
            # Try to extract JSON from unstructured text as a fallback
            try:
                # Find anything that looks like a JSON object
                potential_json = re.search(r'\{.*\}', response_text, re.DOTALL)
                if potential_json:
                    player_data = json.loads(potential_json.group(0))
                    logger.info(f"Extracted JSON from unstructured response for player {player_name}")
                    return player_data
            except:
                pass
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
        You are an IPL cricket expert with access to the most current information about the {current_year} IPL season.

        Provide ACCURATE and UP-TO-DATE statistics for the IPL {current_year} season.
        Make sure all information is CURRENT for the {current_year} season.

        Include the following information:
        - Total matches played so far in the {current_year} season
        - Current points table standings (top 4 teams)
        - Team with most wins in {current_year}
        - Number of wins for that team
        - Team with highest score in {current_year}
        - Highest score value and against which team
        - Player with most runs in {current_year}
        - Number of runs for that player
        - Player with most wickets in {current_year}
        - Number of wickets for that player
        - Highest individual score in {current_year}
        - Player who scored highest individual score
        - Best bowling figures in {current_year}
        - Player with best bowling figures

        Format the response as a structured JSON object with the following fields:
        total_matches, points_table, most_wins_team, most_wins_count, highest_score_team, highest_score,
        most_runs_player, most_runs, most_wickets_player, most_wickets, highest_individual_score,
        highest_individual_score_player, best_bowling_figures, best_bowling_player

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
            logger.info(f"Successfully retrieved current {current_year} IPL statistics")
            return stats_data
        else:
            logger.error(f"Invalid JSON response from Gemini AI: {json_str}")
            # Try to extract JSON from unstructured text as a fallback
            try:
                # Find anything that looks like a JSON object
                potential_json = re.search(r'\{.*\}', response_text, re.DOTALL)
                if potential_json:
                    stats_data = json.loads(potential_json.group(0))
                    logger.info(f"Extracted JSON from unstructured response for IPL stats")
                    return stats_data
            except:
                pass
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
        current_year = datetime.now().year

        if is_telugu:
            prompt = f"""
            You are an IPL cricket expert assistant who is knowledgeable about all IPL seasons including the current {current_year} season.

            User message: {message}

            Respond in a friendly, conversational manner with accurate and up-to-date information about IPL cricket.
            Keep your response concise (under 200 words).

            IMPORTANT INSTRUCTIONS:
            1. First, compose your response in Telugu language.
            2. Then TRANSLITERATE your Telugu response into English letters (Roman script).
            3. DO NOT translate to English - keep the Telugu language but write it using English letters.
            4. For example, instead of "నమస్కారం" write "Namaskaram".
            5. Make sure your entire response is in Telugu language but written with English letters.
            6. Add the English transliteration, not the actual Telugu script.

            Example format:
            "Namaskaram! IPL gurinchi meeru adagina prashnaku samadhanam..." (NOT "నమస్కారం! IPL గురించి మీరు అడిగిన ప్రశ్నకు సమాధానం...")
            """
        else:
            prompt = f"""
            You are an IPL cricket expert assistant who is knowledgeable about all IPL seasons including the current {current_year} season.

            User message: {message}

            Respond in a friendly, conversational manner with accurate and up-to-date information about IPL cricket.
            Keep your response concise (under 200 words).

            IMPORTANT INSTRUCTIONS:
            1. Be slightly flirtatious and charming in your response, but still professional.
            2. Use playful language and occasional compliments.
            3. Include cricket-related flirty metaphors or puns when appropriate.
            4. Keep the flirting subtle and tasteful - focus primarily on answering the cricket question.
            5. Make sure your information about IPL {current_year} is accurate and up-to-date.

            Example tone: "Hey there cricket fan! Your cricket knowledge is as impressive as a Virat Kohli cover drive! Here's what you wanted to know about..."
            """

        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)

        response_text = response.text.strip()
        logger.info(f"Generated {language} response: {response_text[:50]}...")
        return response_text

    except Exception as e:
        logger.error(f"Error chatting with Gemini AI: {e}")
        return None
