class  Player:
    def __init__(self, kloppy_player, df_columns):
        self.name = self._setName(kloppy_player)
        self.id = self._setId(kloppy_player)
        self.jersey = self._setJersey(kloppy_player)
        
        self.position = self._setPosition(kloppy_player)
        self.specific_position = self._setSpecificPosition(self.position)
        
        (self.col_x, self.col_y) = self._setCols(df_columns, self.id)
        
    
    def _setName(self, kloppy_player):
        return str(kloppy_player.name)
    
    def _setId(self, kloppy_player):
        return str(kloppy_player.name_id)
    
    def _setJersey(self, kloppy_player):
        return int(kloppy_player.jersey_no)
    def _setCols(self, df_columns, id):
        return (df_columns.get(f'{id}_x'), 
                df_columns.get(f'{id}_y'))
        
    def _setPosition(self, kloppy_player):
        position = kloppy_player.attributes.get('position_type', 'Unknown')
        if position == 'Unknown':
            print("Posição definida de maneira errada! Classe Player")
            
        return position
    
    def _setSpecificPosition(self, position):
        position = position.lower()
        
        if 'goalkeeper' in position:
            return 'Goalkeeper'
        
        if 'midfielder' in position:
            return 'Midfielder'
        
        if 'forward' in position:
            return 'Attacker'
        
        if 'defensive' in position or 'back' in position:
            return 'Defender'
        
        print(f'Não encontrada a posição correta. OBS: {position}')
        return 'Desconhecida'
        