import logging
import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

# Download NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK resources: {e}")

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Telugu character pattern
telugu_pattern = re.compile(r'[\u0C00-\u0C7F]')

def is_telugu_text(text):
    """
    Check if text contains Telugu characters
    """
    return bool(telugu_pattern.search(text))

def process_text(text):
    """
    Process English text for NLP
    """
    try:
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        
        # Lemmatize
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        
        # Join tokens back into text
        processed_text = ' '.join(tokens)
        
        return processed_text
    
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        return text

def process_telugu_text(text):
    """
    Process Telugu text for NLP
    """
    try:
        # For Telugu, we'll do minimal processing for now
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
    Detect the intent of the message
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
    Extract entities from text based on intent
    """
    entities = {}
    
    if intent == 'player_info':
        # Try to extract player name
        # This is a simple implementation and can be improved
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
