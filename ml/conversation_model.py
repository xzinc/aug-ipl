import logging
import random
import json
import os
from pathlib import Path
from ml.nlp_processor import detect_intent, extract_entities

logger = logging.getLogger(__name__)

# Load conversation data
conversation_data = {
    'english': {
        'greetings': [
            "Hello! How can I help you with IPL information today?",
            "Hi there! I'm your IPL assistant. What would you like to know?",
            "Greetings! Ask me anything about IPL!",
            "Hello! Ready to talk about cricket and IPL?"
        ],
        'farewells': [
            "Goodbye! Feel free to come back for more IPL info!",
            "See you later! Enjoy the IPL matches!",
            "Bye! Have a great day!",
            "Until next time! Keep supporting your favorite IPL team!"
        ],
        'thanks': [
            "You're welcome! Anything else you'd like to know about IPL?",
            "Happy to help! Any other IPL questions?",
            "My pleasure! I'm here for all your IPL needs!",
            "No problem at all! Feel free to ask more about IPL!"
        ],
        'fallbacks': [
            "I'm not sure I understand. Could you ask about IPL in a different way?",
            "I'm still learning. Can you rephrase your question about IPL?",
            "I didn't quite catch that. Try asking something specific about IPL teams, players, or matches.",
            "Sorry, I'm not sure how to answer that. I'm best at answering questions about IPL!"
        ]
    },
    'telugu': {
        'greetings': [
            "నమస్కారం! నేను మీకు IPL సమాచారంతో ఎలా సహాయపడగలను?",
            "హలో! నేను మీ IPL సహాయకుడిని. మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?",
            "శుభోదయం! IPL గురించి నన్ను ఏదైనా అడగండి!",
            "నమస్తే! క్రికెట్ మరియు IPL గురించి మాట్లాడటానికి సిద్ధంగా ఉన్నాను!"
        ],
        'farewells': [
            "వీడ్కోలు! మరింత IPL సమాచారం కోసం తిరిగి రావడానికి సంకోచించకండి!",
            "తరువాత కలుద్దాం! IPL మ్యాచ్‌లను ఆస్వాదించండి!",
            "బై! శుభదినం కలగాలని కోరుకుంటున్నాను!",
            "మళ్ళీ కలుద్దాం! మీ అభిమాన IPL జట్టుకు మద్దతు ఇవ్వడం కొనసాగించండి!"
        ],
        'thanks': [
            "స్వాగతం! IPL గురించి మరేమైనా తెలుసుకోవాలనుకుంటున్నారా?",
            "సహాయం చేయడం సంతోషం! ఇతర IPL ప్రశ్నలు ఏమైనా ఉన్నాయా?",
            "నా ఆనందం! నేను మీ అన్ని IPL అవసరాల కోసం ఇక్కడ ఉన్నాను!",
            "అస్సలు సమస్య లేదు! IPL గురించి మరింత అడగడానికి సంకోచించకండి!"
        ],
        'fallbacks': [
            "నేను అర్థం చేసుకోలేకపోతున్నాను. మీరు IPL గురించి వేరే విధంగా అడగగలరా?",
            "నేను ఇంకా నేర్చుకుంటున్నాను. మీరు మీ IPL ప్రశ్నను మరోలా అడగగలరా?",
            "నేను దానిని పట్టుకోలేదు. IPL జట్లు, ఆటగాళ్లు లేదా మ్యాచ్‌ల గురించి నిర్దిష్టంగా ఏదైనా అడగడానికి ప్రయత్నించండి.",
            "క్షమించండి, నేను ఎలా సమాధానం ఇవ్వాలో నాకు తెలియదు. నేను IPL గురించి ప్రశ్నలకు సమాధానం ఇవ్వడంలో మంచివాడిని!"
        ]
    }
}

# Path to store learned responses
LEARNED_RESPONSES_PATH = Path("data/learned_responses.json")

# Initialize learned responses
learned_responses = {'english': {}, 'telugu': {}}

# Load learned responses if file exists
def load_learned_responses():
    """
    Load learned responses from file
    """
    global learned_responses

    try:
        if LEARNED_RESPONSES_PATH.exists():
            with open(LEARNED_RESPONSES_PATH, 'r', encoding='utf-8') as f:
                learned_responses = json.load(f)
            logger.info(f"Loaded {sum(len(v) for v in learned_responses.values())} learned responses")
    except Exception as e:
        logger.error(f"Error loading learned responses: {e}")

# Save learned responses to file
def save_learned_responses():
    """
    Save learned responses to file
    """
    try:
        # Create directory if it doesn't exist
        LEARNED_RESPONSES_PATH.parent.mkdir(exist_ok=True)

        with open(LEARNED_RESPONSES_PATH, 'w', encoding='utf-8') as f:
            json.dump(learned_responses, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {sum(len(v) for v in learned_responses.values())} learned responses")
    except Exception as e:
        logger.error(f"Error saving learned responses: {e}")

# Load learned responses at module import
load_learned_responses()

# Mock function for search_ipl_data (since we removed the actual implementation)
def search_ipl_data(data_type, query):
    """
    Simplified mock function for searching IPL data
    """
    if data_type == 'player':
        return {
            'name': query,
            'team': 'Sample Team',
            'role': 'Batsman',
            'matches': '50',
            'runs': '1500',
            'wickets': '10'
        }
    elif data_type == 'team':
        return {
            'name': query,
            'full_name': f'{query} Cricket Team',
            'home_ground': 'Sample Stadium',
            'captain': 'Sample Captain',
            'championships': '2'
        }
    elif data_type == 'match':
        teams = query.split(' vs ')
        return {
            'team1': teams[0],
            'team2': teams[1] if len(teams) > 1 else 'Unknown Team',
            'date': '2023-04-15',
            'venue': 'Sample Stadium',
            'result': 'Team 1 won by 5 wickets'
        }
    return None

def get_response(text, language='english'):
    """
    Get a response based on the input text
    """
    # Check for greetings
    if any(greeting in text.lower() for greeting in ['hello', 'hi', 'hey', 'namaste', 'నమస్కారం', 'హలో']):
        return random.choice(conversation_data[language]['greetings'])

    # Check for farewells
    if any(farewell in text.lower() for farewell in ['bye', 'goodbye', 'see you', 'వీడ్కోలు', 'బై']):
        return random.choice(conversation_data[language]['farewells'])

    # Check for thanks
    if any(thanks in text.lower() for thanks in ['thanks', 'thank you', 'ధన్యవాదాలు', 'థాంక్స్']):
        return random.choice(conversation_data[language]['thanks'])

    # Check learned responses
    for pattern, response in learned_responses[language].items():
        if pattern.lower() in text.lower():
            return response

    # Detect intent
    intent = detect_intent(text)

    # Handle intent-based responses
    if intent != 'conversation':
        entities = extract_entities(text, intent)

        if intent == 'player_info' and 'player_name' in entities:
            player_info = search_ipl_data('player', entities['player_name'])
            if player_info:
                if language == 'english':
                    return (
                        f"Here's information about {player_info['name']}:\n"
                        f"Team: {player_info['team']}\n"
                        f"Role: {player_info['role']}\n"
                        f"Matches: {player_info['matches']}\n"
                        f"Runs: {player_info['runs']}\n"
                        f"Wickets: {player_info['wickets']}"
                    )
                else:  # Telugu
                    return (
                        f"{player_info['name']} గురించి సమాచారం ఇక్కడ ఉంది:\n"
                        f"జట్టు: {player_info['team']}\n"
                        f"పాత్ర: {player_info['role']}\n"
                        f"మ్యాచ్‌లు: {player_info['matches']}\n"
                        f"పరుగులు: {player_info['runs']}\n"
                        f"వికెట్లు: {player_info['wickets']}"
                    )

        elif intent == 'team_info' and 'team_name' in entities:
            team_info = search_ipl_data('team', entities['team_name'])
            if team_info:
                if language == 'english':
                    return (
                        f"Here's information about {team_info['name']}:\n"
                        f"Full Name: {team_info['full_name']}\n"
                        f"Home Ground: {team_info['home_ground']}\n"
                        f"Captain: {team_info['captain']}\n"
                        f"Championships: {team_info['championships']}"
                    )
                else:  # Telugu
                    return (
                        f"{team_info['name']} గురించి సమాచారం ఇక్కడ ఉంది:\n"
                        f"పూర్తి పేరు: {team_info['full_name']}\n"
                        f"హోమ్ గ్రౌండ్: {team_info['home_ground']}\n"
                        f"కెప్టెన్: {team_info['captain']}\n"
                        f"ఛాంపియన్‌షిప్‌లు: {team_info['championships']}"
                    )

        elif intent == 'match_info' and 'team1' in entities and 'team2' in entities:
            match_info = search_ipl_data('match', f"{entities['team1']} vs {entities['team2']}")
            if match_info:
                if language == 'english':
                    return (
                        f"Here's information about {match_info['team1']} vs {match_info['team2']}:\n"
                        f"Date: {match_info['date']}\n"
                        f"Venue: {match_info['venue']}\n"
                        f"Result: {match_info['result']}"
                    )
                else:  # Telugu
                    return (
                        f"{match_info['team1']} vs {match_info['team2']} గురించి సమాచారం ఇక్కడ ఉంది:\n"
                        f"తేదీ: {match_info['date']}\n"
                        f"వేదిక: {match_info['venue']}\n"
                        f"ఫలితం: {match_info['result']}"
                    )

    # Fallback response
    return random.choice(conversation_data[language]['fallbacks'])

def learn_response(text, response, language='english'):
    """
    Learn a new response for a given text
    """
    # Extract key phrases from text (simple implementation)
    words = text.lower().split()
    key_phrase = ' '.join(words[:min(5, len(words))])

    # Store the response
    learned_responses[language][key_phrase] = response

    # Save learned responses
    save_learned_responses()

    return True
