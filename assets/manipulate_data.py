FRAME = 25
def add_realtime_score_game(tracking, events, home_team_id):
    tracking['home_score'] = 0
    tracking['away_score'] = 0
    
    goals = events[events['result'] == 'GOAL']
    for index, goal in goals.iterrows():
        goal_frame = get_frame(goal['timestamp'])
        team_gol = 'home_score' if goal['team_id'] == home_team_id else 'away_score'
        tracking.loc[goal_frame:, team_gol] += 1 
    
    tracking['goal_diff'] = tracking['home_score'] - tracking['away_score']  # saldo de gols  
        
        
        

def get_frame(timestamp):
    s = timestamp.total_seconds()
    return int(FRAME * s)