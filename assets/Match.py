import os
from kloppy import metrica
import assets.manipulate_data as md
import assets.Team as tm
class Match:
    def __init__(self):
        self.match_name
        self._load()

        self.dataset, self.event_dataset = self._loadMatch()
        self.home_team_id, self.away_team_id = self._setHomeVisitingTeam_id(self.dataset)
        md.add_realtime_score_game(self.dataset, self.event_dataset, self.home_team_id)
        
        self.finalhome_score, self.finalaway_score = self._getFinalResult()

        self.winner = self._setWinner()
        self.home_team = self.setTeam(self.home_team_id, 'Home')
        self.away_team = self.setTeam(self.away_team_id, 'Away')
    
    def setTeam(self, team_id, side = 'Home'):
        kloppy_team_obj = None
        for team in self.dataset.metada.teams:
            if str(team.team_id) == team_id:
                kloppy_team_obj = team
                break
        if kloppy_team_obj == None:
            raise ValueError(f"Time com ID {team_id} não encontrado")

        return tm.Team(kloppy_team_obj, self.dataset.columns, side)
    
    
    def _getFinalResult(self,dataset):
        score = dataset.metadata.score
        return score.home_score, score.away_score
    
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
        return dataset.metadata.score.get('idLocalTeam'), dataset.metadata.score.get('idVisitingTeam')
