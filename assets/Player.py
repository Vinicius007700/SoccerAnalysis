class  Player:
    def __init__(self, kloppy_player, df_columns):
        self.name = self._setName(kloppy_player)
        self.id = self._setId(kloppy_player)
        self.jersey = self._setJersey(kloppy_player)
        
        self.position = self._setPosition(kloppy_player)
        self.specific_position = self._setSpecificPosition(self.position)
        
        (self.col_x, self.col_y) = self._setCols(df_columns)
        
    
    def _setName(self, kloppy_player):
        return str(kloppy_player.name)
    
    def _setId(self, kloppy_player):
        return str(kloppy_player.player_id)
    
    def _setJersey(self, kloppy_player):
        return int(kloppy_player.jersey_no)
    
    def _setCols(self, df_columns):
        """
        Procura nas colunas do DataFrame onde estão os dados deste jogador.
        """
        # O padrão do Metrica/Kloppy geralmente é: "Home_11_x" ou "home_11_x"
        # O self.id geralmente é apenas "11"
        
        # 1. Cria o padrão de busca seguro (Ex: "_11_x")
        # O underline (_) antes do ID é importante para não confundir ID 1 com 11
        search_pattern_x = f"_{self.id}_x" 
        
        # 2. Varre as colunas para encontrar a correspondência
        col_x = None
        col_y = None
        
        for col in df_columns:
            # Se a coluna termina com "_11_x" (Ex: "Home_11_x" ou "player_11_x")
            if str(col).endswith(search_pattern_x):
                col_x = col
                # Assume que a coluna Y tem o mesmo nome, só trocando final x por y
                col_y = col.replace('_x', '_y')
                break # Achamos, pode parar de procurar
        
        # Se não achou (pode acontecer com goleiros ou reservas que não jogaram), retorna None
        if col_x is None:
            # Descomente a linha abaixo se quiser ver avisos no console
            # print(f"Aviso: Colunas não encontradas para o Jogador {self.id}")
            return None, None
            
        return col_x, col_y
        
    def _setPosition(self, kloppy_player):
        position = kloppy_player.attributes.get('position_type', 'Unknown')
        if position == 'Unknown':
            print("Posição definida de maneira errada! Classe Player")
            
        return position
    
    def _setSpecificPosition(self, position):
        position = str(position).lower()
        
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
        