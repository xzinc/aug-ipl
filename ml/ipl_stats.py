import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Sample IPL data (simplified for deployment without ML libraries)
sample_ipl_data = {
    'teams': {
        'csk': {
            'name': 'CSK',
            'full_name': 'Chennai Super Kings',
            'home_ground': 'M. A. Chidambaram Stadium',
            'captain': 'MS Dhoni',
            'championships': '5'
        },
        'mi': {
            'name': 'MI',
            'full_name': 'Mumbai Indians',
            'home_ground': 'Wankhede Stadium',
            'captain': 'Rohit Sharma',
            'championships': '5'
        },
        'rcb': {
            'name': 'RCB',
            'full_name': 'Royal Challengers Bangalore',
            'home_ground': 'M. Chinnaswamy Stadium',
            'captain': 'Faf du Plessis',
            'championships': '0'
        },
        'kkr': {
            'name': 'KKR',
            'full_name': 'Kolkata Knight Riders',
            'home_ground': 'Eden Gardens',
            'captain': 'Shreyas Iyer',
            'championships': '2'
        }
    },
    'players': {
        'virat kohli': {
            'name': 'Virat Kohli',
            'team': 'RCB',
            'role': 'Batsman',
            'matches': '223',
            'runs': '6624',
            'wickets': '4'
        },
        'ms dhoni': {
            'name': 'MS Dhoni',
            'team': 'CSK',
            'role': 'Wicket-keeper Batsman',
            'matches': '220',
            'runs': '4978',
            'wickets': '0'
        },
        'rohit sharma': {
            'name': 'Rohit Sharma',
            'team': 'MI',
            'role': 'Batsman',
            'matches': '218',
            'runs': '5611',
            'wickets': '15'
        },
        'jasprit bumrah': {
            'name': 'Jasprit Bumrah',
            'team': 'MI',
            'role': 'Bowler',
            'matches': '120',
            'runs': '56',
            'wickets': '145'
        }
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
        'mi vs rcb': {
            'team1': 'MI',
            'team2': 'RCB',
            'date': '2023-05-14',
            'venue': 'Wankhede Stadium',
            'result': 'RCB won by 8 wickets'
        },
        'kkr vs csk': {
            'team1': 'KKR',
            'team2': 'CSK',
            'date': '2023-05-18',
            'venue': 'Eden Gardens',
            'result': 'CSK won by 3 runs'
        }
    }
}

# Global variable to store IPL data
ipl_processed_data = sample_ipl_data

def get_ipl_stats():
    """
    Get IPL statistics (simplified version)
    """
    global ipl_processed_data

    # Calculate statistics
    stats = {
        'total_matches': 60,  # Placeholder value
        'most_wins_team': 'CSK',
        'most_wins_count': 30,
        'highest_score_team': 'RCB',
        'highest_score': 263,
        'most_runs_player': 'Virat Kohli',
        'most_runs': 6624,
        'most_wickets_player': 'Jasprit Bumrah',
        'most_wickets': 145
    }

    return stats

def search_ipl_data(data_type, query):
    """
    Search IPL data for a specific query (simplified version)
    """
    global ipl_processed_data

    query = query.lower()

    if data_type == 'player':
        # Search for player
        if query in ipl_processed_data['players']:
            return ipl_processed_data['players'][query]

        # Try partial match
        for player_id, player_data in ipl_processed_data['players'].items():
            if query in player_id:
                return player_data

        # Return a generic player if not found
        return {
            'name': query.title(),
            'team': 'Unknown Team',
            'role': 'Player',
            'matches': '0',
            'runs': '0',
            'wickets': '0'
        }

    elif data_type == 'team':
        # Search for team
        for team_id, team_data in ipl_processed_data['teams'].items():
            if query == team_id or query == team_data['name'].lower() or query in team_data['full_name'].lower():
                return team_data

        # Return a generic team if not found
        return {
            'name': query.upper(),
            'full_name': f'{query.title()} Cricket Team',
            'home_ground': 'Unknown Stadium',
            'captain': 'Unknown Captain',
            'championships': '0'
        }

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

        # Return a generic match if not found
        return {
            'team1': teams[0].upper() if len(teams) > 0 else 'Team A',
            'team2': teams[1].upper() if len(teams) > 1 else 'Team B',
            'date': '2023-04-15',
            'venue': 'IPL Stadium',
            'result': 'Match scheduled'
        }

    return None
