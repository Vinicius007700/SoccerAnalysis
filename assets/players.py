import pandas as pd

field_l = 106.0
field_w = 68.0

def findGoalkeeper(dataset):
    gk_ids = []
    for team in dataset.metadata.teams:
        for player in team.players:
            if isGoalkeeper(player):
                gk_ids.append(player.player_id)
                
    return gk_ids

def getLastDefensor():
    return

def isGoalkeeper(player):
    if(str(player.starting_position) == "Goalkeeper"):
        return True
    return False

def getPlayerBall(row, players_data, possesion_radius = 2.0):
    ball_x = row['ball_x']
    ball_y = row['ball_y']
    
    if pd.isna(ball_x) or pd.isna(ball_y):
        return
    bx, by = ball_x, ball_y
    
    dist_min = possesion_radius
    closest_player = None
    for p in players_data:
        if p['x'] == None or p['y'] == None: continue
        dist_actual = (bx - p['x']) ** 2 + (by - p['y']) ** 2
        if dist_min > dist_actual:
            dist_min = dist_actual
            closest_player = p
    
    return closest_player
        
    
    

        
    
    
    
    
def positionOnBoard(pos_x, pos_y):
    
    if pd.isna(pos_x) or pd.isna(pos_y):
        return None, None
    
    new_pos_x = (pos_x - 0.5) * field_l
    new_pos_y = (pos_y - 0.5) * field_w   
    
    return new_pos_x, new_pos_y
 
    