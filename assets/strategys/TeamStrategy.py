import pandas as pd
import numpy as np
import assets.Team as tm
import assets.strategy as st

class TeamStrategy(st.Strategy):
    def __init__(self, dataset):
        super().__init__(dataset)
        self.ball_possesion = 0
        
    def calculate_ballpossesion(self, frame_idx, team_home, team_away):
        # Chama a função interna self.teamHasBall
        if self.teamHasBall(team_home, frame_idx):
            return 1
        elif self.teamHasBall(team_away, frame_idx):
            return 0
        return 0.5
            
    # --- CORREÇÃO: Nome da função ajustado para bater com a chamada acima ---
    def teamHasBall(self, team, frame_idx):
        for player in team.players:
            if player.hasBall(frame_idx):
                return True
        return False