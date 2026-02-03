class  Player:
    def __init__(self, kloppy_player, df_columns):
        self.name = self._setName(kloppy_player)
        self.id = self._setId(kloppy_player)
        self.jersey = self._setJersey(kloppy_player)
        
        self.position = self._setPosition(kloppy_player)
        self.specific_position = self._setSpecificPosition(self.position)
        
        self.possession_history = []
        
        
        (self.col_x, self.col_y) = self._setCols(df_columns)
        
    def hasBall(self, frame_idx):
        if frame_idx < len(self.possession_history):
            print("Tinha a bola")
            return self.possession_history[frame_idx]
        return False
    
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
            # 1. Limpa o ID para garantir que temos só o número (Ex: "3699")
            clean_id = ''.join(filter(str.isdigit, str(self.id)))
            
            # 2. Define o nome EXATO que esperamos encontrar (Baseado no seu print)
            # Ex: Se ID é 3699, procuramos "P3699_x"
            target_col_name = f"P{clean_id}_x"
            
            col_x = None
            col_y = None
            
            # 3. Procura nas colunas
            if target_col_name in df_columns:
                # ACHOU! (Formato P3699_x)
                col_x = target_col_name
                col_y = target_col_name.replace('_x', '_y')
            else:
                # Tenta o modo "desesperado" (Varredura por sufixo _3699_x)
                # Caso algum dia o formato mude
                suffix_search = f"_{clean_id}_x"
                for col in df_columns:
                    if str(col).endswith(suffix_search):
                        col_x = col
                        col_y = col.replace('_x', '_y')
                        break
            
            # --- DEBUG ---
            if col_x is None:
                # Descomente para ver quem está falhando
                # print(f"[AVISO] Colunas não encontradas para Jogador {self.id} (Busquei por: {target_col_name})")
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
        