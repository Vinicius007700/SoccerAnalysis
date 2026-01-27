import players as pl
class Strategy:
    def __init__(self, dataset):
        self.dataset = dataset
        self.gk_ids = pl.findGoalkeeper(dataset)
        
    def get_defensive_line(self, row, team_cols_x):
        