import logging
import re
import string

logger = logging.getLogger(__name__)

# Telugu character pattern
telugu_pattern = re.compile(r'[\u0C00-\u0C7F]')

def is_telugu_text(text):
    """
    Check if text contains Telugu characters
    """
    return bool(telugu_pattern.search(text))

def process_text(text):
    """
    Simplified text processing (ML libraries disabled)
    """
    try:
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    except Exception as e:
        logger.error(f"Error processing text: {e}")
        return text

def process_telugu_text(text):
    """
    Simplified Telugu text processing (ML libraries disabled)
    """
    try:
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    except Exception as e:
        logger.error(f"Error processing Telugu text: {e}")
        return text

def detect_intent(text):
    """
    Simplified intent detection (ML libraries disabled)
    """
    # Simple keyword-based intent detection
    text = text.lower()

    if any(word in text for word in ['score', 'result', 'match']):
        return 'match_info'

    if any(word in text for word in ['player', 'batsman', 'bowler']):
        return 'player_info'

    if any(word in text for word in ['team', 'squad', 'franchise']):
        return 'team_info'

    if any(word in text for word in ['schedule', 'fixture', 'upcoming']):
        return 'schedule_info'

    if any(word in text for word in ['stats', 'statistics', 'record']):
        return 'stats_info'

    # Default to conversation
    return 'conversation'

def extract_entities(text, intent):
    """
    Simplified entity extraction (ML libraries disabled)
    """
    entities = {}

    if intent == 'player_info':
        # Try to extract player name
        player_patterns = [
            r'(?:player|batsman|bowler)\s+(\w+(?:\s+\w+)?)',
            r'(\w+(?:\s+\w+)?)\s+(?:stats|record|performance)'
        ]

        for pattern in player_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['player_name'] = match.group(1)
                break

    elif intent == 'team_info':
        # Try to extract team name
        team_patterns = [
            r'(?:team|squad|franchise)\s+(\w+(?:\s+\w+)?)',
            r'(\w+(?:\s+\w+)?)\s+(?:team|squad|franchise)'
        ]

        for pattern in team_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['team_name'] = match.group(1)
                break

    elif intent == 'match_info':
        # Try to extract teams
        match_pattern = r'(\w+(?:\s+\w+)?)\s+(?:vs|versus|against)\s+(\w+(?:\s+\w+)?)'
        match = re.search(match_pattern, text, re.IGNORECASE)

        if match:
            entities['team1'] = match.group(1)
            entities['team2'] = match.group(2)

    return entities
