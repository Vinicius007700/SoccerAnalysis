import os
import matplotlib.pyplot as plt
from kloppy import metrica
import draw_game as dg




field_l = 106.0
field_w = 68.0
FPS = 25


def get_frame(timestamp):
    s = timestamp.total_seconds()
    return int(s * FPS)



# 1. CARREGAR DADOS

current_folder = os.path.dirname(os.path.abspath(__file__))
root_folder = os.path.dirname(current_folder)
metadata_path = os.path.join(root_folder, 'data', 'Sample_Game_3_metadata.xml')
tracking_path = os.path.join(root_folder, 'data', 'Sample_Game_3_tracking.txt')
event_path = os.path.join(root_folder, 'data', 'Sample_Game_3_events.json')

print("Carregando os dados.")

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

events_df = event_dataset.to_df(engine="pandas")

gols = events_df[events_df['result'] == 'GOAL'] # ou 'GOAL' dependendo do 
print(gols)
if len(gols) > 0:
    primeiro_gol = gols.iloc[0]
    time_gol = primeiro_gol['timestamp']
    time_gol = get_frame(time_gol)
    print(f'tempo do gol = {time_gol}')
    
else:
    time_gol = 500
    print('Nenhum gol encontrado')
time_gol = 500
    





home_team = dataset.metadata.teams[0]
away_team = dataset.metadata.teams[1]





df = dataset.to_df(engine="pandas")
print(df.head())



# Criar listas com os nomes das colunas de cada time para acesso rápido




#desenhar o campo


# Criar os objetos "Atores" vazios (que vão se mover)
# scatter retorna um objeto que podemos atualizar depois


ani = dg.MatchAnimator(dataset, event_dataset, home_team, away_team)

my_ani = ani.runMatch(time_gol - 1000, time_gol + 1000)






# # Salvar como MP4
# output_file = os.path.join(current_folder, 'match_animation.mp4')
# ani.save(output_file, writer='ffmpeg', fps=25)

#print(f"Vídeo salvo em: {output_file}")
# plt.show()
# plt.close() # Fecha para não mostrar janela estática

# No main.py, logo após carregar o dataset
print("Verificando atributos do primeiro jogador:")
p1 = dataset.metadata.teams[0]
print(f"Nome: {p1.name}")
print(f"Atributos (Dicionário): {p1.team_id}")