import assets.Player as pl
import numpy as np
class Team:
    def __init__(self, kloppy_team, df_columns, side):
        self.name = self._setName(kloppy_team)
        
        self.id = self._setTeamId(kloppy_team)
        
        self.side = side # o atributo que vai vir da Match do time visitante ou da casa 
        
        self.players = self._setPlayers(kloppy_team, df_columns)

    def _setName(self, kloppy_team):
        return str(kloppy_team.name)
    
    def _setTeamId(self, kloppy_team):
        return str(kloppy_team.team_id)
    
    def _setPlayers(self, kloppy_team, df_columns):
        players = []
        for k_player in kloppy_team.players:
            player = pl.Player(k_player, df_columns)
            players.append(player)
            
        return players
     
    def distribute_possession_to_players(self, tracking_df):
        bx, by = tracking_df['ball_x'], tracking_df['ball_y']
        print(f"Média Posição Bola X: {np.nanmean(bx):.2f}")
        for player in self.players:
            # Se o jogador não tem colunas mapeadas, pula
            if not player.col_x or not player.col_y:
                continue

            # Calcula distância Euclidiana
            dist = ((tracking_df[player.col_x] - bx)**2 + (tracking_df[player.col_y] - by)**2) ** 0.5
            
          
            min_dist = dist.min()
            # print(f"Jogador {player.jersey}: Menor dist = {min_dist:.2f}m") 
            print(f"Jogador {player.jersey} chegou a {min_dist:.2f}m da bola.")
            
            is_close = dist < 2.0 
            
            player.possession_history = is_close.tolist()  
        print(player.possession_history)
    