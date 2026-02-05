import os
import matplotlib.pyplot as plt
import assets.Match as mtch
import assets.draw_game as dg




current_folder = os.path.dirname(os.path.abspath(__file__))
metadata_path = os.path.join(current_folder, 'data', 'Sample_Game_3_metadata.xml')
tracking_path = os.path.join(current_folder, 'data', 'Sample_Game_3_tracking.txt')
event_path = os.path.join(current_folder, 'data', 'Sample_Game_3_events.json')

match = mtch.Match(math_name = 'Jogo_Teste', 
                   tracking_path = tracking_path,
                   metadata_path = metadata_path,
                   event_path = event_path,
                   dimensions_field=(105, 68),
                   limit_frames=None)




ani = dg.MatchAnimator(match)

my_ani = ani.runMatch(start_frame= None, end_frame= None)






# # Salvar como MP4
# output_file = os.path.join(current_folder, 'match_animation.mp4')
# my_ani.save(output_file, writer='ffmpeg', fps=25)

# print(f"Vídeo salvo em: {output_file}")
plt.show()
plt.close() # Fecha para não mostrar janela estática

