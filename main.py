import customtkinter as ctk
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

CLIENT_ID = "lkx2wdpwaz7doyn9hglojyzetpjua9"
ACCESS_TOKEN = "0a5vw169z78cllqe6877cc0in1st0e"
datos_usuarios = {}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NextGen Play")
        self.geometry("600x400")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.current_user = None
        self.create_login_frame()

    def create_login_frame(self):
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(pady=60, padx=20, fill="both", expand=True)

        self.username_label = ctk.CTkLabel(self.login_frame, text="Nombre de Usuario:")
        self.username_label.pack(pady=12, padx=10)

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Usuario")
        self.username_entry.pack(pady=12, padx=10)

        self.submit_button = ctk.CTkButton(
            self.login_frame, text="Ingresar", command=self.handle_login
        )
        self.submit_button.pack(pady=12, padx=10)

    def create_main_frame(self):
        self.login_frame.destroy()
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.game_label = ctk.CTkLabel(self.main_frame, text="Nombre del Juego:")
        self.game_label.pack(pady=5)

        self.game_entry = ctk.CTkEntry(self.main_frame, width=300)
        self.game_entry.pack(pady=5)

        self.search_button = ctk.CTkButton(
            self.main_frame, text="Buscar", command=self.handle_search
        )
        self.search_button.pack(pady=10)

        self.results_text = ctk.CTkTextbox(self.main_frame, width=500, height=200)
        self.results_text.pack(pady=10)

    def handle_login(self):
        username = self.username_entry.get()
        if username:
            self.current_user = username
            if username not in datos_usuarios:
                datos_usuarios[username] = []
            self.create_main_frame()

    def handle_search(self):
        game_name = self.game_entry.get()
        if not game_name or not self.current_user:
            return
        
        self.results_text.delete("1.0", "end")
        juegos = self.buscar_juegos(game_name)
        
        if juegos:
            juego = juegos[0]
            self.results_text.insert("end", f"Juegos a similares a {juego['name']}\n\n")
            datos_usuarios[self.current_user].append({
                'usuario': self.current_user,
                'juego': juego['name'],
                'valoracion': 0
            })

            if 'similar_games' in juego:
                self.results_text.insert("end", "Juegos encontrados:\n")
                for similar_id in juego['similar_games']:
                    similar = self.obtener_juegos_similares(similar_id)
                    if similar:
                        self.results_text.insert("end", f"- {similar[0]['name']}\n")

    def buscar_juegos(self, nombre_juego):
        url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Accept": "application/json",
        }
        data = f'search "{nombre_juego}"; fields name, id, similar_games;'
        response = requests.post(url, headers=headers, data=data)
        return response.json() if response.status_code == 200 else None

    def obtener_juegos_similares(self, juego_id):
        url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        }
        data = f'fields name; where id = {juego_id};'
        response = requests.post(url, headers=headers, data=data)
        return response.json() if response.status_code == 200 else None

    def obtener_recomendaciones(self, usuario):
        if usuario not in datos_usuarios:
            return []
        
        df = pd.DataFrame(datos_usuarios[usuario])
        if df.empty:
            return []
            
        matriz = df.pivot_table(index='usuario', columns='juego', values='valoracion', fill_value=0)
        similitud = cosine_similarity(matriz)
        idx_usuario = matriz.index.get_loc(usuario)
        
        recomendaciones = []
        for usuario_idx, score in sorted(enumerate(similitud[idx_usuario]), key=lambda x: x[1], reverse=True)[1:]:
            juegos = matriz.iloc[usuario_idx]
            recomendaciones.extend(juegos[juegos > 0].index.tolist())
            
        return list(set(recomendaciones))

if __name__ == "__main__":
    app = App()
    app.mainloop()
