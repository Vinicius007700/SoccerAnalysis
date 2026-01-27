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