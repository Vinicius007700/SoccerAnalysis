import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import assets.strategy as st
import assets.strategys.TeamStrategy as ts
from mplsoccer import Pitch

field_l = 106.0
field_w = 68.0
FPS = 25

class MatchAnimator:
    def __init__(self, match):
        self.match = match
        self.df = match.tracking_df
        self.events_df = match.events_df

        self.strategy = self.match.h_strategy
        
        self.home_cols_x = []
        self.home_cols_y = []
        self.away_cols_x = []
        self.away_cols_y = []
        
        self.player_jersey_map = {}
        self.player_color_map = {}
        
        for player in match.home_team.players: 
            self.player_color_map[player.id] = 'cyan'
            self.player_jersey_map[player.id] = player.jersey

        for player in match.away_team.players: 
            self.player_color_map[player.id] = 'red'
            self.player_jersey_map[player.id] = player.jersey
        
        for col in self.df.columns:
            if '_x' in col and 'ball' not in col:
                player_id = col.replace('_x', '')
                y_col = col.replace('_x', '_y')
                
                color = self.player_color_map.get(player_id)
                if color == 'cyan':
                    self.home_cols_x.append(col)
                    self.home_cols_y.append(y_col)
                elif color == 'red':
                    self.away_cols_x.append(col)
                    self.away_cols_y.append(y_col)
                    
                    
        self.pitch = self._plot_pitch()
        self.fig, self.ax = self.pitch.draw(figsize = (12, 8))
        
        self.scat_home = self.ax.scatter([],[], c='cyan', s=120, edgecolors='white', zorder=5, label='Casa')
        self.scat_away = self.ax.scatter([],[], c='red', s=120, edgecolors='black', zorder=5, label='Fora')
        
        self.scat_ball = self.ax.scatter([],[], c='white', s=100, edgecolors='black', linewidth=1.5, zorder=10)
        self.home_texts = [self.ax.text(0, 0, '', color='white', fontweight='bold', ha='center', va='center', fontsize=8, zorder=6) for _ in range(len(self.home_cols_x))]
        self.away_texts = [self.ax.text(0, 0, '', color='black', fontweight='bold', ha='center', va='center', fontsize=8, zorder=6) for _ in range(len(self.away_cols_x))]

        self.chain_defensor_home, = self.ax.plot([], [], color='cyan', linewidth=1, alpha=0.8)
        self.chain_defensor_away, = self.ax.plot([], [], color='red', linewidth=1, alpha=0.8)
        
        self.chain_attacker_home, = self.ax.plot([], [], color='cyan', linewidth=1, alpha=0.8)
        self.chain_attacker_away, = self.ax.plot([], [], color='red', linewidth=1, alpha=0.8)
        
        self.title_text = self.ax.text(int(field_l/2), int(field_w + 1), "", 
            color='black', 
            ha='center', 
            va='center', 
            fontsize=12, 
            fontweight='bold',
            zorder=20)
        
        self.hull_home_patch = None
        
    def update(self, frame_idx):
        def draw_hull(team_cols_x, team_cols_y, color, old_patch):
        
            if old_patch:
                old_patch.remove()
                
            hx = row[team_cols_x].values.astype(float)
            hy = row[team_cols_y].values.astype(float)
            mask = ~np.isnan(hx) & ~np.isnan(hy)
            hx_clean, hy_clean = hx[mask], hy[mask]
            
        
            new_patch = None
            if len(hx_clean) >= 3:
                # Calcula o Fecho Convexo
                hull_data = self.pitch.convexhull(hx_clean, hy_clean)
                
                # Desenha no campo
                # poly_list retorna uma lista de polígonos, pegamos o primeiro [0]
                poly_list = self.pitch.polygon(hull_data, ax=self.ax, 
                                             edgecolor=color, facecolor=color, 
                                             alpha=0.2, linestyle='--', zorder=1)
                new_patch = poly_list[0]
            
            return new_patch
        row = self.df.iloc[frame_idx]
        
        self.hull_home_patch = draw_hull(self.home_cols_x, self.home_cols_y, 'cyan', self.hull_home_patch)
        
        self._set_teams_on_board(row, self.home_cols_x, self.home_cols_y, self.scat_home, self.home_texts)
        self._set_teams_on_board(row, self.away_cols_x, self.away_cols_y, self.scat_away, self.away_texts)
        self._set_ball_on_board(row)
        
        defensor_home_x, defensor_home_y = self.strategy.getLines(row, self.home_cols_x, self.home_cols_y, 'Defense')
        self._plotDefensiveLine(defensor_home_x, defensor_home_y, self.chain_defensor_home)
        
        attacker_home_x, attacker_home_y = self.strategy.getLines(row, self.home_cols_x, self.home_cols_y, 'Attack')
        self._plotDefensiveLine(attacker_home_x, attacker_home_y, self.chain_attacker_home)
        
        defensor_away_x, defensor_away_y = self.strategy.getLines(row, self.away_cols_x, self.away_cols_y)
        self._plotDefensiveLine(defensor_away_x, defensor_away_y, self.chain_defensor_away)
        
        attacker_away_x, attacker_away_y = self.strategy.getLines(row, self.away_cols_x, self.away_cols_y, 'Attack')
        self._plotDefensiveLine(attacker_away_x, attacker_away_y, self.chain_attacker_away)
        
        
        posse_now = self.match.h_strategy.instant_possession[frame_idx] if frame_idx < len(self.match.h_strategy.instant_possession) else np.nan
        
        if frame_idx < len(self.match.h_strategy.ball_possession):
            pct_home = self.match.h_strategy.ball_possession[frame_idx]
            pct_away = self.match.a_strategy.ball_possession[frame_idx]
        else:
            pct_home, pct_away = 50.0, 50.0

       
        color_text = 'black'
        status = ""
        
        if posse_now == 1:
            color_text = 'cyan' 
            status = ">>" 
        elif posse_now == 0:
            color_text = 'red'  
            status = "<<" 
            

        text_str = f"{pct_home:.1f}%  {status}  {pct_away:.1f}%"
        
    
        self.title_text.set_text(f"Frame {frame_idx} | Posse: {text_str}")
        self.title_text.set_color(color_text)
        
        return (self.scat_home, self.scat_away, self.scat_ball, 
                self.title_text, self.chain_defensor_home, self.chain_defensor_away, 
                self.chain_attacker_home, self.chain_attacker_away, *self.home_texts,
                *self.away_texts, self.hull_home_patch)
    
    def _set_teams_on_board(self, row, team_cols_x, team_cols_y, scat_team, team_texts):
        t_x_raw = row[team_cols_x].values.astype(float)
        t_y_raw = row[team_cols_y].values.astype(float)
        scat_team.set_offsets(np.column_stack((t_x_raw, t_y_raw)))
        for text, x, y, col_name in zip(team_texts, t_x_raw, t_y_raw, team_cols_x):
            if np.isnan(x) or np.isnan(y):
                text.set_visible(False)
            else:
                text.set_visible(True)
                text.set_position((x, y))
                p_id = col_name.replace('_x', '')
                text.set_text(str(self.player_jersey_map.get(p_id, '')))

    def _set_ball_on_board(self, row):
        if 'ball_x' in self.df.columns:
            bx_val = row['ball_x']
            by_val = row['ball_y']
            if pd.isna(bx_val) or pd.isna(by_val):
                self.scat_ball.set_offsets(np.array([[-100, -100]]))
            else:
                self.scat_ball.set_offsets(np.array([[bx_val, by_val]]))

    def _plotDefensiveLine(self, line_x, line_y, chain):
        if line_x:
            points = sorted(zip(line_x, line_y), key=lambda k: k[1])
            hx_sorted, hy_sorted = zip(*points)
            chain.set_data(hx_sorted, hy_sorted)

    def _plot_pitch(self, field_dimen = (106.0,68.0), field_color ='green', linewidth=2, markersize=20):
        pitch = Pitch(pitch_type = 'custom', pitch_length = 105, pitch_width = 68,
                      pitch_color = 'grass', line_color = 'white', stripe = True, corner_arcs = True)
        return pitch
    
    def runMatch(self, start_frame = None, end_frame= None):
        if start_frame is None:
            start_frame = 0
        if end_frame is None:
            end_frame = len(self.df)
            
        return animation.FuncAnimation(self.fig, self.update, frames=range(start_frame, end_frame), interval=40, blit=True)