import assets.players as pl
import pandas as pd

field_l = 106.0
field_w = 68.0
class Strategy:
    def __init__(self, dataset):
        self.dataset = dataset
        self.gk_ids = pl.findGoalkeeper(dataset)
        print("Herança")

    
    def _getTeamPositions(self, row, team_cols_x, team_cols_y):
        players_data = []
        for col_x, col_y in zip(team_cols_x, team_cols_y):
            x_m, y_m = pl.positionOnBoard(row[col_x], row[col_y])
            
            if x_m == y_m == None: continue
            
            raw_id = col_x.replace('_x','')
            clean_id = raw_id.replace('Home_', '').replace('Away', '')
            if clean_id in self.gk_ids:
                team_defenders_right = True if x_m > 0 else False
                continue
            players_data.append({'id': clean_id, 'x': x_m, 'y': y_m})
        
        return players_data, team_defenders_right
    
            

    def getLines(self, row, team_cols_x, team_cols_y, mode = 'Defense' , tolerance = 8):        
        players_data, defenders_right = self._getTeamPositions(row, team_cols_x, team_cols_y)
                
        if not players_data: return [], []
        
        if mode == 'Defense' :
            return self._getDefenseLines(
                players_data, defenders_right, tolerance)
        elif mode == 'Attack':
            return self._getAttackLines(
                players_data, defenders_right, tolerance)
    
        
        
        return
    
    def getBreakDefenseLine(self, row, attacker_cols_x, attacker_cols_y, defender_cols_x, defender_cols_y):
        attackers_data, attackers_defender_right = self._getTeamPositions(row, attacker_cols_x, attacker_cols_y)
        defenders_data, defenders_defender_right = self._getTeamPositions(row, defender_cols_x, defender_cols_y)
        
        if not attackers_data or not defenders_data: return [], []
        
        player_ball = pl.getPlayerBall(row, attackers_data + defenders_data)
        
        if player_ball == None: return [], []
        
        
        
        
                
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
    
