import os
from kloppy import metrica
import assets.manipulate_data as md
import assets.Team as tm
import numpy as np
import assets.strategys.TeamStrategy as ts

class Match:
    def __init__(self, math_name, tracking_path, metadata_path, event_path, dimensions_field, limit_frames = None):
        self.match_name = math_name
    

        self.dataset, self.event_dataset = self._loadMatch(tracking_path, metadata_path, event_path, limit_frames)
        
        
        self.home_team_id, self.away_team_id = self._setHomeVisitingTeam_id(self.dataset)
        
        # 2. Configura DF e converte para Metros
        self.tracking_df, self.events_df = self.setDf(dimensions_field, self.dataset, self.event_dataset) 
        print(self.tracking_df.head())
        md.add_realtime_score_game(self.tracking_df, self.events_df, self.home_team_id)
        
        self.finalhome_score, self.finalaway_score = self._getFinalResult()
        self.winner = self._setWinner()
        
        # 3. Cria os Times
        self.home_team = self.setTeam(self.home_team_id, 'Home')
        self.away_team = self.setTeam(self.away_team_id, 'Away')
        
        self.h_strategy = ts.TeamStrategy(self.event_dataset) 
        
        self.a_strategy = ts.TeamStrategy(self.event_dataset)
        
        # 5. Calcula a posse (Não atribua o resultado a variável nenhuma!)
        print("Calculando posse para o time da casa...")
        self.home_team.distribute_possession_to_players(self.tracking_df)
        print("Calculando posse para o time visitante...")
        self.away_team.distribute_possession_to_players(self.tracking_df)
        
        self._calculate_global_possession_stats()
        
    def setDf(self, dimensions_field, dataset, event_dataset):
        events_df = event_dataset.to_df(engine='pandas')
        tracking_df = dataset.to_df(engine='pandas')
        
        #Converte tudo (incluindo a bola) para Metros (0 a 105)
        cols_to_convert = [c for c in tracking_df.columns if c.endswith('_x') or c.endswith('_y')]
        
        for col in cols_to_convert:
            if col.endswith('_x'):
                tracking_df[col] = tracking_df[col] * dimensions_field[0]
            elif col.endswith('_y'):
                tracking_df[col] = tracking_df[col] * dimensions_field[1]
                
        return tracking_df, events_df
    
    def _distribute_possession_to_players(self, team, tracking_df):
        bx, by = tracking_df['ball_x'], tracking_df['ball_y']
        print(f"Média Posição Bola X: {np.nanmean(bx):.2f}")
        for player in team.players:
            # Se o jogador não tem colunas mapeadas, pula
            if not player.col_x or not player.col_y:
                continue

       
            dist = ((tracking_df[player.col_x] - bx)**2 + (tracking_df[player.col_y] - by)**2) ** 0.5
            
          
            min_dist = dist.min()
        
            print(f"Jogador {player.jersey} chegou a {min_dist:.2f}m da bola.")
            
            is_close = dist < 2.0 
            
            player.possession_history = is_close.tolist()  
        print(player.possession_history)
        
    def _loadMatch(self, tracking_path, metadata_path, event_path, limit_frames=None):
        print("Loading the data...")
        dataset = metrica.load_tracking_epts(
            meta_data=metadata_path,
            raw_data=tracking_path,
            coordinates="metrica",
            limit = limit_frames
        )
        event_dataset = metrica.load_event(
            event_data=event_path,
            meta_data=metadata_path,
            coordinates="metrica"
        )
        return dataset, event_dataset
    
    def setTeam(self, team_id, side='Home'):
        kloppy_team_obj = None
        for team in self.dataset.metadata.teams:
            if str(team.team_id) == str(team_id):
                kloppy_team_obj = team
                break
        if kloppy_team_obj == None:
            raise ValueError(f"Time com ID {team_id} não encontrado")
        
        return tm.Team(kloppy_team_obj, self.tracking_df.columns, side)

    def _getFinalResult(self):
        score = self.dataset.metadata.score
        if score:
            return score.home, score.away
        return 0, 0
    
    def _setWinner(self):
        if self.finalhome_score > self.finalaway_score:
            return self.home_team_id
        elif self.finalaway_score > self.finalhome_score:
            return self.away_team_id
        return None
    
    def _calculate_global_possession_stats(self):
        """
        Calcula a posse de bola acumulada do jogo INTEIRO de uma vez só.
        Usa NumPy Vectorizado (Instantâneo).
        """
        
       
        bx = self.tracking_df['ball_x'].values
        by = self.tracking_df['ball_y'].values
        

        valid_frames_mask = ~np.isnan(bx) & ~np.isnan(by)
        
       
        def get_team_min_distances_vectorized(team):
            dists_list = []
            
            for player in team.players:
                if not player.col_x or not player.col_y:
                    continue
                
                px = self.tracking_df[player.col_x].values
                py = self.tracking_df[player.col_y].values
                
                # CÁLCULO MÁGICO: Processa 100% dos frames em 1 linha
                d = ((px - bx)**2 + (py - by)**2)**0.5
                dists_list.append(d)
            
            if not dists_list:
                return np.full(len(bx), np.inf)
            
            # Empilha e acha o mínimo por frame
            all_dists = np.vstack(dists_list)
            return np.nanmin(all_dists, axis=0)

        # 2. Calcula as menores distâncias
        dist_home = get_team_min_distances_vectorized(self.home_team)
        dist_away = get_team_min_distances_vectorized(self.away_team)
        
        # 3. Quem tem a bola? (Boolean Arrays)
        home_has = (dist_home < 2.0) & (dist_home < dist_away) & valid_frames_mask
        away_has = (dist_away < 2.0) & (dist_away < dist_home) & valid_frames_mask
        
        # 4. ACUMULA (CUMSUM) - AQUI GERA O HISTÓRICO
        home_counts = np.cumsum(home_has.astype(int))
        away_counts = np.cumsum(away_has.astype(int))
        total_valid = home_counts + away_counts
        
        # Evita divisão por zero
        total_valid[total_valid == 0] = 1
        
        # 5. Salva nas Estratégias
        n_frames = len(self.tracking_df)
        
        # Porcentagem Acumulada
        self.h_strategy.ball_possession = (home_counts / total_valid) * 100
        self.a_strategy.ball_possession = (away_counts / total_valid) * 100
        
        # Posse Instantânea (0, 1 ou NaN)
        raw_poss = np.full(n_frames, np.nan)
        raw_poss[home_has] = 1
        raw_poss[away_has] = 0
        self.h_strategy.instant_possession = raw_poss
        
        print(f"Cálculo pronto! Final do jogo: Casa {self.h_strategy.ball_possession[-1]:.1f}%")

    def _setHomeVisitingTeam_id(self, dataset):
        return dataset.metadata.teams[0].team_id, dataset.metadata.teams[1].team_id