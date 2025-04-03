import logging
import pandas as pd
import json
from pathlib import Path
from utils.data_loader import get_ipl_data

logger = logging.getLogger(__name__)

# Path to store processed IPL data
PROCESSED_DATA_PATH = Path("data/processed_ipl_data.json")

# Sample IPL data (will be replaced with actual data when loaded)
sample_ipl_data = {
    'teams': {
        'csk': {
            'name': 'CSK',
            'full_name': 'Chennai Super Kings',
            'home_ground': 'M. A. Chidambaram Stadium',
            'captain': 'MS Dhoni',
            'coach': 'Stephen Fleming',
            'championships': 5,
            'matches_played': 218,
            'wins': 130,
            'losses': 88,
            'win_percentage': 59.63
        },
        'mi': {
            'name': 'MI',
            'full_name': 'Mumbai Indians',
            'home_ground': 'Wankhede Stadium',
            'captain': 'Rohit Sharma',
            'coach': 'Mahela Jayawardene',
            'championships': 5,
            'matches_played': 226,
            'wins': 129,
            'losses': 97,
            'win_percentage': 57.08
        },
        # Add more teams...
    },
    'players': {
        'virat kohli': {
            'name': 'Virat Kohli',
            'team': 'RCB',
            'role': 'Batsman',
            'matches': 223,
            'runs': 6624,
            'average': 36.2,
            'strike_rate': 129.15,
            'wickets': 4,
            'economy': 8.8
        },
        'ms dhoni': {
            'name': 'MS Dhoni',
            'team': 'CSK',
            'role': 'Wicket-keeper Batsman',
            'matches': 220,
            'runs': 4978,
            'average': 39.2,
            'strike_rate': 135.2,
            'wickets': 0,
            'economy': 0
        },
        # Add more players...
    },
    'matches': {
        'csk vs mi': {
            'team1': 'CSK',
            'team2': 'MI',
            'date': '2023-05-06',
            'venue': 'M. A. Chidambaram Stadium',
            'result': 'CSK won by 7 wickets'
        },
        'rcb vs kkr': {
            'team1': 'RCB',
            'team2': 'KKR',
            'date': '2023-05-10',
            'venue': 'M. Chinnaswamy Stadium',
            'result': 'KKR won by 21 runs'
        },
        # Add more matches...
    }
}

# Global variable to store processed IPL data
ipl_processed_data = None

def process_ipl_data():
    """
    Process IPL data from the loaded dataset
    """
    global ipl_processed_data
    
    try:
        # Check if processed data already exists
        if PROCESSED_DATA_PATH.exists():
            with open(PROCESSED_DATA_PATH, 'r') as f:
                ipl_processed_data = json.load(f)
            logger.info(f"Loaded processed IPL data from {PROCESSED_DATA_PATH}")
            return ipl_processed_data
        
        # Get raw IPL data
        raw_data = get_ipl_data()
        
        if raw_data is None:
            logger.warning("No IPL data available, using sample data")
            ipl_processed_data = sample_ipl_data
            return ipl_processed_data
        
        # Process the data
        # This is a placeholder for actual data processing
        # The actual implementation would depend on the structure of the raw data
        
        # For now, we'll use the sample data
        ipl_processed_data = sample_ipl_data
        
        # Save processed data
        PROCESSED_DATA_PATH.parent.mkdir(exist_ok=True)
        with open(PROCESSED_DATA_PATH, 'w') as f:
            json.dump(ipl_processed_data, f, indent=2)
        
        logger.info(f"Processed IPL data saved to {PROCESSED_DATA_PATH}")
        
        return ipl_processed_data
    
    except Exception as e:
        logger.error(f"Error processing IPL data: {e}")
        ipl_processed_data = sample_ipl_data
        return ipl_processed_data

def get_ipl_stats():
    """
    Get IPL statistics
    """
    global ipl_processed_data
    
    if ipl_processed_data is None:
        ipl_processed_data = process_ipl_data()
    
    # Calculate statistics
    stats = {
        'total_matches': sum(team['matches_played'] for team in ipl_processed_data['teams'].values()) // 2,  # Divide by 2 because each match is counted twice
        'most_wins_team': max(ipl_processed_data['teams'].values(), key=lambda x: x['wins'])['name'],
        'most_wins_count': max(ipl_processed_data['teams'].values(), key=lambda x: x['wins'])['wins'],
        'highest_score_team': 'RCB',  # Placeholder
        'highest_score': 263,  # Placeholder
        'most_runs_player': max(ipl_processed_data['players'].values(), key=lambda x: x['runs'])['name'],
        'most_runs': max(ipl_processed_data['players'].values(), key=lambda x: x['runs'])['runs'],
        'most_wickets_player': 'Lasith Malinga',  # Placeholder
        'most_wickets': 170  # Placeholder
    }
    
    return stats

def search_ipl_data(data_type, query):
    """
    Search IPL data for a specific query
    """
    global ipl_processed_data
    
    if ipl_processed_data is None:
        ipl_processed_data = process_ipl_data()
    
    query = query.lower()
    
    if data_type == 'player':
        # Search for player
        if query in ipl_processed_data['players']:
            return ipl_processed_data['players'][query]
        
        # Try partial match
        for player_id, player_data in ipl_processed_data['players'].items():
            if query in player_id:
                return player_data
        
        return None
    
    elif data_type == 'team':
        # Search for team
        for team_id, team_data in ipl_processed_data['teams'].items():
            if query == team_id or query == team_data['name'].lower() or query in team_data['full_name'].lower():
                return team_data
        
        return None
    
    elif data_type == 'match':
        # Search for match
        if query in ipl_processed_data['matches']:
            return ipl_processed_data['matches'][query]
        
        # Try different combinations
        teams = query.split(' vs ')
        if len(teams) == 2:
            team1, team2 = teams
            
            # Try both orders
            for match_id, match_data in ipl_processed_data['matches'].items():
                if ((team1.lower() in match_data['team1'].lower() and team2.lower() in match_data['team2'].lower()) or
                    (team1.lower() in match_data['team2'].lower() and team2.lower() in match_data['team1'].lower())):
                    return match_data
        
        return None
    
    return None
