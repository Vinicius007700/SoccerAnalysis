import pandas as pd
import numpy as np
import assets.Team as tm
import assets.strategy as st

class TeamStrategy(st.Strategy):
    def __init__(self, dataset):
        super().__init__(dataset)
        self.ball_possession = []
        
    def calculate_ballpossesion(self, frame_idx, team_home, team_away):
        if self.teamHasBall(team_home, frame_idx):
            return 1
        elif self.teamHasBall(team_away, frame_idx):
            return 0
        return 0.5
            
            
    def teamHasBall(self, team, frame_idx):
        for player in team.players:
            if player.hasBall(frame_idx):
                return True
        return False