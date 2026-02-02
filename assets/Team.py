import assets.Player as pl
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

    