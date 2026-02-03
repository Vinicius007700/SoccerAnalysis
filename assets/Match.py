import os
from kloppy import metrica
import assets.manipulate_data as md
import assets.Team as tm
import numpy as np
import assets.strategys.TeamStrategy as ts

class Match:
    def __init__(self, math_name, tracking_path, metadata_path, event_path, dimensions_field):
        self.match_name = math_name
    
        # 1. Carrega o jogo TODO (Tirei o limit=1000)
        self.dataset, self.event_dataset = self._loadMatch(tracking_path, metadata_path, event_path)
        
        
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
        
        # 4. Cria a Estratégia (ÚNICA para a partida, como conversamos)
        self.strategy = ts.TeamStrategy(self.event_dataset) 
        
        # 5. Calcula a posse (Não atribua o resultado a variável nenhuma!)
        print("Calculando posse para o time da casa...")
        self._distribute_possession_to_players(self.home_team, self.tracking_df)
        
        print("Calculando posse para o time visitante...")
        self._distribute_possession_to_players(self.away_team, self.tracking_df)
        
        self._calculate_global_possession_stats()
        
    def setDf(self, dimensions_field, dataset, event_dataset):
        events_df = event_dataset.to_df(engine='pandas')
        tracking_df = dataset.to_df(engine='pandas')
        
        # Converte tudo (incluindo a bola) para Metros (0 a 105)
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

            # Calcula distância Euclidiana
            dist = ((tracking_df[player.col_x] - bx)**2 + (tracking_df[player.col_y] - by)**2) ** 0.5
            
            # DEBUG: Mostra a menor distância que esse jogador chegou da bola
            # Se der sempre > 2.0, sabemos que a escala está errada
            min_dist = dist.min()
            # print(f"Jogador {player.jersey}: Menor dist = {min_dist:.2f}m") 
            print(f"Jogador {player.jersey} chegou a {min_dist:.2f}m da bola.")
            
            is_close = dist < 2.0 
            
            # ATENÇÃO: Use 'possession' (dois S) para bater com a classe Player
            player.possession_history = is_close.tolist()  
        print(player.possession_history)
        
    def _loadMatch(self, tracking_path, metadata_path, event_path):
        print("Loading the data...")
        dataset = metrica.load_tracking_epts(
            meta_data=metadata_path,
            raw_data=tracking_path,
            coordinates="metrica",
            limit=2000  # <--- IMPORTANTE: None para carregar o jogo inteiro
        )
        event_dataset = metrica.load_event(
            event_data=event_path,
            meta_data=metadata_path,
            coordinates="metrica"
        )
        return dataset, event_dataset
    
    # ... (Mantenha os outros métodos setTeam, _getFinalResult, etc iguais) ...
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
        Calcula a porcentagem de posse acumulada frame a frame para o jogo todo.
        """
        print("Calculando estatísticas de porcentagem de posse...")
        
        # 1. Recupera distâncias mínimas de cada time para a bola
        # Vamos usar uma lógica vetorial rápida
        bx, by = self.tracking_df['ball_x'].values, self.tracking_df['ball_y'].values
        
        # Função auxiliar rápida para pegar a menor distância do time inteiro
        def get_min_dist(team):
            min_dists = np.full(len(self.tracking_df), np.inf) # Começa com infinito
            for player in team.players:
                if player.col_x and player.col_y:
                    px = self.tracking_df[player.col_x].values
                    py = self.tracking_df[player.col_y].values
                    d = ((px - bx)**2 + (py - by)**2) ** 0.5
                    min_dists = np.minimum(min_dists, d) # Mantém a menor distância encontrada
            return min_dists

        home_min_dist = get_min_dist(self.home_team)
        away_min_dist = get_min_dist(self.away_team)
        
        # 2. Determina quem tem a bola frame a frame (1=Home, 0=Away, NaN=Ninguém)
        # Regra: Distância < 2m e menor que o adversário
        raw_possession = np.full(len(self.tracking_df), np.nan)
        
        home_has = (home_min_dist < 2.0) & (home_min_dist < away_min_dist)
        away_has = (away_min_dist < 2.0) & (away_min_dist < home_min_dist)
        
        raw_possession[home_has] = 1
        raw_possession[away_has] = 0
        
        # 3. Calcula a soma acumulada (CUMSUM)
        # Onde é True vira 1, onde é False vira 0. Somamos progressivamente.
        home_counts = np.cumsum(home_has)
        away_counts = np.cumsum(away_has)
        total_valid_frames = home_counts + away_counts
        
        # Evita divisão por zero nos primeiros frames
        total_valid_frames[total_valid_frames == 0] = 1 
        
        # 4. Salva as porcentagens prontinhas (0 a 100)
        self.home_pct_history = (home_counts / total_valid_frames) * 100
        self.away_pct_history = (away_counts / total_valid_frames) * 100
        
        print("Estatísticas de posse calculadas!")

    def _setHomeVisitingTeam_id(self, dataset):
        # ... (seu código existente) ...
        return dataset.metadata.teams[0].team_id, dataset.metadata.teams[1].team_id