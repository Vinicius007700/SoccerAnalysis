import os
from kloppy import metrica
import assets.manipulate_data as md
import assets.Team as tm
class Match:
    def __init__(self, math_name, tracking_path, metadata_path, event_path, dimensions_field):
        self.match_name=  math_name
    
        self.dataset, self.event_dataset = self._loadMatch(tracking_path, metadata_path, event_path)
        self.home_team_id, self.away_team_id = self._setHomeVisitingTeam_id(self.dataset)
        self.tracking_df, self.events_df = self.setDf(dimensions_field, self.dataset, self.event_dataset) 
        
        md.add_realtime_score_game(self.tracking_df, self.events_df, self.home_team_id)
        
        
        
        
        self.finalhome_score, self.finalaway_score = self._getFinalResult()

        self.winner = self._setWinner()
        self.home_team = self.setTeam(self.home_team_id, 'Home')
        self.away_team = self.setTeam(self.away_team_id, 'Away')
    
    def setDf(self, dimensions_field, dataset, event_dataset):
        events_df =  event_dataset.to_df(engine = 'pandas')
        tracking_df = dataset.to_df(engine = 'pandas')
        cols_to_convert = [c for c in tracking_df.columns if c.endswith('_x') or c.endswith('_y')]
        
        for col in cols_to_convert:
            if col.endswith('_x'):
                tracking_df[col] = (tracking_df[col]) * dimensions_field[0]
            elif col.endswith('_y'):
                tracking_df[col] = (tracking_df[col]) * dimensions_field[1]
                
        return tracking_df, events_df
                

        
    def setTeam(self, team_id, side = 'Home'):
        kloppy_team_obj = None
        for team in self.dataset.metadata.teams:
            if str(team.team_id) == team_id:
                kloppy_team_obj = team
                break
        if kloppy_team_obj == None:
            raise ValueError(f"Time com ID {team_id} não encontrado")
        
        print(f"Time encontradao: {kloppy_team_obj}")
        return tm.Team(kloppy_team_obj, self.tracking_df.columns, side)
    
    
    def _getFinalResult(self):
        score = self.dataset.metadata.score
        if score:
            print(score)
            return score.home, score.away
    
        print("Não foi encontrado o placar final")
        return 0, 0
    
    def _setWinner(self):
        if self.finalhome_score > self.finalaway_score:
            return self.home_team_id
        elif self.finalaway_score > self.finalhome_score:
            return self.away_team_id

        return None
        
    def _loadMatch(self, tracking_path, metadata_path, event_path):
        
        print("Loading the data...")
        dataset = metrica.load_tracking_epts(
            meta_data=metadata_path,
            raw_data=tracking_path,
            coordinates="metrica",
            limit = 1000
        )
        event_dataset = metrica.load_event(
        event_data = event_path,
        meta_data= metadata_path,
        coordinates="metrica"
        )
        return dataset, event_dataset
    
    def _setHomeVisitingTeam_id(self, dataset):
        score_attrs = getattr(dataset.metadata.score, 'attributes', {})
    
        home_id = score_attrs.get('idLocalTeam')
        visit_id = score_attrs.get('idVisitingTeam')

        # Se achou os IDs no XML, retorna eles
        if home_id and visit_id:
            return home_id, visit_id
            
        # FALLBACK: Se não tiver os atributos (ou o XML for diferente), usa o padrão da lista
        print("Aviso: IDs não encontrados no Score. Usando ordem da lista de times.")
        return dataset.metadata.teams[0].team_id, dataset.metadata.teams[1].team_id
