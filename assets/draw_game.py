import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import assets.strategy as st

field_l = 106.0
field_w = 68.0
FPS = 25

class MatchAnimator:
    def __init__(self, dataset, events, home_team, away_team):
        self.df = dataset.to_df(engine="pandas")
        self.events_df = events.to_df(engine="pandas")
        self.strategy = st.Strategy(dataset)
        
        self.home_cols_x = []
        self.home_cols_y = []
        self.away_cols_x = []
        self.away_cols_y = []
        
        self.player_jersey_map = {}
        self.player_color_map = {}
        
        for player in home_team.players: 
            self.player_color_map[player.id] = 'cyan'
            self.player_jersey_map[player.id] = player.jersey

        for player in away_team.players: 
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
                    
                    
        self.fig, self.ax = self._plot_pitch()
        
        self.scat_home = self.ax.scatter([],[], c='cyan', s=120, edgecolors='white', zorder=5, label='Casa')
        self.scat_away = self.ax.scatter([],[], c='red', s=120, edgecolors='black', zorder=5, label='Fora')
        
        self.scat_ball = self.ax.scatter([],[], c='white', s=100, edgecolors='black', linewidth=1.5, zorder=10)
        self.home_texts = [self.ax.text(0, 0, '', color='white', fontweight='bold', ha='center', va='center', fontsize=8, zorder=6) for _ in range(len(self.home_cols_x))]
        self.away_texts = [self.ax.text(0, 0, '', color='black', fontweight='bold', ha='center', va='center', fontsize=8, zorder=6) for _ in range(len(self.away_cols_x))]

        self.chain_defensor_home, = self.ax.plot([], [], color='cyan', linewidth=1, alpha=0.8)
        self.chain_defensor_away, = self.ax.plot([], [], color='red', linewidth=1, alpha=0.8)
        
        self.chain_attacker_home, = self.ax.plot([], [], color='cyan', linewidth=1, alpha=0.8)
        self.chain_attacker_away, = self.ax.plot([], [], color='red', linewidth=1, alpha=0.8)
        
        self.title_text = self.ax.text(0.5, 1.02, "", transform=self.ax.transAxes, color='white', ha='center', fontsize=12)
        
    def update(self, frame_idx):
        #Lê as coordenadas de todos para o determinado frame 
        row = self.df.iloc[frame_idx]
        
        self._set_teams_on_board(row, self.home_cols_x, self.home_cols_y, self.scat_home, 
                           self.home_texts)
    
        # Time Visitante
        self._set_teams_on_board(row, self.away_cols_x, self.away_cols_y, self.scat_away, 
                           self.away_texts)
            
        # Bola 
        self._set_ball_on_board(row)
        
        
        #linha de defesa do time da casa
        defensor_home_x, defensor_home_y = self.strategy.getLines(row, self.home_cols_x, self.home_cols_y, 'Defense')
        self._plotDefensiveLine(defensor_home_x, defensor_home_y, self.chain_defensor_home)
        
        #linha de ataque do time da casa
        attacker_home_x, attacker_home_y = self.strategy.getLines(row, self.home_cols_x, self.home_cols_y, 'Attack')
        self._plotDefensiveLine(attacker_home_x, attacker_home_y, self.chain_attacker_home)
        

        
        #linha de defesa do time visitante
        defensor_away_x, defensor_away_y = self.strategy.getLines(row, self.away_cols_x, self.away_cols_y)
        self._plotDefensiveLine(defensor_away_x, defensor_away_y, self.chain_defensor_away)
        
        attacker_away_x, attacker_away_y = self.strategy.getLines(row, self.away_cols_x, self.away_cols_y, 'Attack')
        self._plotDefensiveLine(attacker_away_x, attacker_away_y, self.chain_attacker_away)
        
        self.title_text.set_text(f"Frame {frame_idx}")
        
        
        
        return (self.scat_home, self.scat_away, self.scat_ball, 
                self.title_text, self.chain_defensor_home, self.chain_defensor_away, 
                self.chain_attacker_home, self.chain_attacker_away,*self.home_texts,
                *self.away_texts)
    
    
    
    def _set_teams_on_board(self, row, team_cols_x, team_cols_y, scat_team, team_texts):
        t_x_raw = row[team_cols_x].values.astype(float)
        t_y_raw = row[team_cols_y].values.astype(float)
        
        #os valores das pos do campo vem de 0 a 1, 
        # sendo que o (0,0) é o meio para facilitar nossas contas
        t_x = (t_x_raw - 0.5) * field_l
        t_y = (t_y_raw - 0.5) * field_w
        
        scat_team.set_offsets(np.column_stack((t_x, t_y)))
        
        for text, x, y, col_name in zip(team_texts, t_x, t_y, team_cols_x):
            if np.isnan(x) or np.isnan(y):
                text.set_visible(False)
                
            else:
                text.set_visible(True)
                text.set_position((x, y))
                p_id = col_name.replace('_x', '')
                text.set_text(str(self.player_jersey_map.get(p_id, '')))
                
                
            
    def _set_ball_on_board(self, row):
        if 'ball_x' in self.df.columns:
            # Pega valor escalar, converte se for None
            bx_val = row['ball_x']
            by_val = row['ball_y']
            
            # Se for NaN (bola fora de jogo/tracking perdido), joga pra longe
            if pd.isna(bx_val) or pd.isna(by_val):
                self.scat_ball.set_offsets(np.array([[-100, -100]]))
            else:
                b_x = (float(bx_val) - 0.5) * field_l
                b_y = (float(by_val) - 0.5) * field_w
                self.scat_ball.set_offsets(np.array([[b_x, b_y]]))
                
    def _plotDefensiveLine(self, line_x, line_y, chain):
        if line_x:
            points = sorted(zip(line_x, line_y), key=lambda k: k[1])
            hx_sorted, hy_sorted = zip(*points)
            chain.set_data(hx_sorted, hy_sorted)
    
    def _plotAttackLine(self, line_x, line_y, chain):
        if line_x:
            points = sorted(zip(line_x, line_y), key=lambda k: k[1])
            hx_sorted, hy_sorted = zip(*points)
            chain.set_data(hx_sorted, hy_sorted)
               

    def _plot_pitch(self, field_dimen = (106.0,68.0), field_color ='green', linewidth=2, markersize=20):
        """ plot_pitch
        
        Plots a soccer pitch. All distance units converted to meters.
        
        Parameters
        -----------
            field_dimen: (length, width) of field in meters. Default is (106,68)
            field_color: color of field. options are {'green','white'}
            linewidth  : width of lines. default = 2
            markersize : size of markers (e.g. penalty spot, centre spot, posts). default = 20
            
        Returrns
        -----------
        fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)

        """
        fig,ax = plt.subplots(figsize=(12,8)) # create a figure 
        # decide what color we want the field to be. Default is green, but can also choose white
        if field_color=='green':
            ax.set_facecolor('mediumseagreen')
            lc = 'whitesmoke' # line color
            pc = 'w' # 'spot' colors
        elif field_color=='white':
            lc = 'k'
            pc = 'k'
        # ALL DIMENSIONS IN m
        border_dimen = (3,3) # include a border arround of the field of width 3m
        #meters_per_yard = 0.9144 # unit conversion from yards to meters
        half_pitch_length = field_dimen[0]/2. # length of half pitch
        half_pitch_width = field_dimen[1]/2. # width of half pitch
        signs = [-1,1] 
        # Soccer field dimensions typically defined in yards, so we need to convert to meters
        goal_line_width = 8 #*meters_per_yard
        box_width = 20 #*meters_per_yard
        box_length = 6 #*meters_per_yard
        area_width = 44 #*meters_per_yard
        area_length = 18 #*meters_per_yard
        penalty_spot = 12 #*meters_per_yard
        corner_radius = 1 #*meters_per_yard
        D_length = 8 #*meters_per_yard
        D_radius = 10 #*meters_per_yard
        D_pos = 12 #*meters_per_yard
        centre_circle_radius = 10 #*meters_per_yard
        # plot half way line # center circle
        ax.plot([0,0],[-half_pitch_width,half_pitch_width],lc,linewidth=linewidth)
        ax.scatter(0.0,0.0,marker='o',facecolor=lc,linewidth=0,s=markersize)
        y = np.linspace(-1,1,50)*centre_circle_radius
        x = np.sqrt(centre_circle_radius**2-y**2)
        ax.plot(x,y,lc,linewidth=linewidth)
        ax.plot(-x,y,lc,linewidth=linewidth)
        for s in signs: # plots each line seperately
            # plot pitch boundary
            ax.plot([-half_pitch_length,half_pitch_length],[s*half_pitch_width,s*half_pitch_width],lc,linewidth=linewidth)
            ax.plot([s*half_pitch_length,s*half_pitch_length],[-half_pitch_width,half_pitch_width],lc,linewidth=linewidth)
            # goal posts & line
            ax.plot( [s*half_pitch_length,s*half_pitch_length],[-goal_line_width/2.,goal_line_width/2.],pc+'s',markersize=6*markersize/20.,linewidth=linewidth)
            # 6 yard box
            ax.plot([s*half_pitch_length,s*half_pitch_length-s*box_length],[box_width/2.,box_width/2.],lc,linewidth=linewidth)
            ax.plot([s*half_pitch_length,s*half_pitch_length-s*box_length],[-box_width/2.,-box_width/2.],lc,linewidth=linewidth)
            ax.plot([s*half_pitch_length-s*box_length,s*half_pitch_length-s*box_length],[-box_width/2.,box_width/2.],lc,linewidth=linewidth)
            # penalty area
            ax.plot([s*half_pitch_length,s*half_pitch_length-s*area_length],[area_width/2.,area_width/2.],lc,linewidth=linewidth)
            ax.plot([s*half_pitch_length,s*half_pitch_length-s*area_length],[-area_width/2.,-area_width/2.],lc,linewidth=linewidth)
            ax.plot([s*half_pitch_length-s*area_length,s*half_pitch_length-s*area_length],[-area_width/2.,area_width/2.],lc,linewidth=linewidth)
            # penalty spot
            ax.scatter(s*half_pitch_length-s*penalty_spot,0.0,marker='o',facecolor=lc,linewidth=0,s=markersize)
            # corner flags
            y = np.linspace(0,1,50)*corner_radius
            x = np.sqrt(corner_radius**2-y**2)
            ax.plot(s*half_pitch_length-s*x,-half_pitch_width+y,lc,linewidth=linewidth)
            ax.plot(s*half_pitch_length-s*x,half_pitch_width-y,lc,linewidth=linewidth)
            # draw the D
            y = np.linspace(-1,1,50)*D_length # D_length is the chord of the circle that defines the D
            x = np.sqrt(D_radius**2-y**2)+D_pos
            ax.plot(s*half_pitch_length-s*x,y,lc,linewidth=linewidth)
            
        # remove axis labels and ticks
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])
        # set axis limits
        xmax = field_dimen[0]/2. + border_dimen[0]
        ymax = field_dimen[1]/2. + border_dimen[1]
        ax.set_xlim([-xmax,xmax])
        ax.set_ylim([-ymax,ymax])
        ax.set_axisbelow(True)
        return fig,ax
    
    def runMatch(self, start_frame, end_frame):
        return animation.FuncAnimation(
            self.fig, 
            self.update,
            frames=range(start_frame, end_frame), 
            interval=40, 
            blit=True
        )


        
    



