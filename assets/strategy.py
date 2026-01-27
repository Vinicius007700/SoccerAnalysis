import players as pl
import pandas as pd

field_l = 106.0
field_w = 68.0
class Strategy:
    def __init__(self, dataset):
        self.dataset = dataset
        self.gk_ids = pl.findGoalkeeper(dataset)
        
    def getLines(self, row, team_cols_x, team_cols_y, mode = 'Defense' , tolerance = 8):
        players_data = []
        
        for col_x, col_y in zip(team_cols_x, team_cols_y):
            val_x = row[col_x]
            val_y = row[col_y]
            
            if pd.isna(val_x) or pd.isna(val_y): continue

            raw_id = col_x.replace('_x','')
            clean_id = raw_id.replace('Home_', '').replace('Away', '')
                   
            x_m = (val_x - 0.5) * field_l
            y_m = (val_y - 0.5) * field_w
            if clean_id in self.gk_ids:
                # se o goleiro está negativo, a nossa linha defensiva é na esquerda
                defenders_right = True if x_m > 0 else False
                               
                continue
            players_data.append({id: clean_id, 'x': x_m, 'y': y_m})
            
        if not players_data: return [], []
        
        if mode == 'Defense' :
            return self._getDefenseLines(
                players_data, defenders_right, tolerance)
        elif mode == 'Attack':
            return self._getAttackLines(
                players_data, defenders_right, tolerance)
    
        
        
        return 
                
    def _getDefenseLines(self, players_data, defenders_right, tolerance):
        #nós vamos organizar os jogadores do time
        #em ordem crescente se eles tiverem atacando para a esquerda
        players_data.sort(key=lambda p: p['x'], reverse = defenders_right)
        #este é o último homem da defesa
        last_player = players_data[0]
        
        defensive_line = []
        for p in players_data:
            if(abs(p['x'] - last_player['x']) <= tolerance):
                defensive_line.append(p)
            #como já está ordenado se passou da linha, acabou
            else:
                break
                
        line_x = [p['x'] for p in defensive_line]
        line_y = [p['y'] for p in defensive_line]

        
        return line_x, line_y
    
    def _getAttackLines(self, players_data, defenders_right, tolerance):
        #nós vamos organizar os jogadores do time
        #em ordem crescente se eles tiverem atacando para a esquerda
        players_data.sort(key=lambda p: p['x'], reverse = not defenders_right)
        #este é o último homem da defesa
        last_player = players_data[0]
        
        defensive_line = []
        for p in players_data:
            if(abs(p['x'] - last_player['x']) <= tolerance):
                defensive_line.append(p)
            #como já está ordenado se passou da linha, acabou
            else:
                break
                
        line_x = [p['x'] for p in defensive_line]
        line_y = [p['y'] for p in defensive_line]

        
        return line_x, line_y
    
