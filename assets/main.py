import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from kloppy import metrica
import numpy as np
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



dataset = metrica.load_tracking_epts(
    meta_data=metadata_path,
    raw_data=tracking_path,
    coordinates="metrica"
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




home_team = dataset.metadata.teams[0]
away_team = dataset.metadata.teams[1]

player_jersey_map = {}
player_color_map = {}


for player in home_team.players: 
    player_color_map[player.player_id] = 'cyan'
    player_jersey_map[player.player_id] = player.jersey_no

for player in away_team.players: 
    player_color_map[player.player_id] = 'red'
    player_jersey_map[player.player_id] = player.jersey_no


df = dataset.to_df(engine="pandas")
print(df.head())

# Criar listas com os nomes das colunas de cada time para acesso rápido
home_cols_x = []
home_cols_y = []
away_cols_x = []
away_cols_y = []

for col in df.columns:
    if '_x' in col and 'ball' not in col:
        player_id = col.replace('_x', '')
        y_col = col.replace('_x', '_y')
        
        color = player_color_map.get(player_id)
        if color == 'red':
            home_cols_x.append(col)
            home_cols_y.append(y_col)
        elif color == 'cyan':
            away_cols_x.append(col)
            away_cols_y.append(y_col)

#desenhar o campo
fig, ax = dg.plot_pitch()

# Criar os objetos "Atores" vazios (que vão se mover)
# scatter retorna um objeto que podemos atualizar depois
scat_home = ax.scatter([],[], c='red', s=120, edgecolors='white', zorder=5, label='Casa')
scat_away = ax.scatter([],[], c='cyan', s=120, edgecolors='black', zorder=5, label='Fora')
scat_ball = ax.scatter([],[], c='white', s=100, edgecolors='black', linewidth=1.5, zorder=10)

home_texts = [ax.text(0, 0, '', color='white', fontweight='bold', ha='center', va='center', fontsize=8, zorder=6) for _ in range(len(home_cols_x))]
away_texts = [ax.text(0, 0, '', color='black', fontweight='bold', ha='center', va='center', fontsize=8, zorder=6) for _ in range(len(away_cols_x))]

title_text = ax.text(0.5, 1.02, "", transform=ax.transAxes, color='white', ha='center', fontsize=12)






update_arguments = (
    df, 
    home_cols_x, home_cols_y, 
    away_cols_x, away_cols_y, 
    scat_home, scat_away, scat_ball, 
    home_texts, away_texts, 
    player_jersey_map, 
    title_text
)
ani = animation.FuncAnimation(
    fig, 
    dg.update, 
    frames=range(time_gol - 100, time_gol + 100), 
    fargs=update_arguments, 
    interval=40, 
    blit=True
)

# # Salvar como MP4
# output_file = os.path.join(current_folder, 'match_animation.mp4')
# ani.save(output_file, writer='ffmpeg', fps=25)

#print(f"Vídeo salvo em: {output_file}")
plt.show()
plt.close() # Fecha para não mostrar janela estática