import customtkinter as ctk
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

CLIENT_ID = "lkx2wdpwaz7doyn9hglojyzetpjua9"
ACCESS_TOKEN = "0a5vw169z78cllqe6877cc0in1st0e"
datos_usuarios = {}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NextGen Play")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color="#1a1a1a")
        
        self.current_user = None
        self.create_login_frame()

    def create_login_frame(self):
        self.login_frame = ctk.CTkFrame(self,fg_color="transparent")
        self.login_frame.pack(pady=60, padx=20, fill="both", expand=True)

        self.username_label = ctk.CTkLabel(self.login_frame, text="¡Bienvenido a NextGen Play!",font=("false",20))
        self.username_label.pack(pady=12, padx=10)
        self.sub_label = ctk.CTkLabel(self.login_frame, text="¡Prepárate para descubrir tus próximos títulos favoritos!",font=("false",14))
        self.sub_label.pack(pady=12, padx=10)

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Usuario",font=("Arial Rounded MT", 14),width=200)
        self.username_entry.pack(pady=12, padx=10)
        
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Contraseña",font=("Arial Rounded MT", 14),show="*",width=200)
        self.password_entry.pack(pady=12, padx=10)        
        
        self.submit_button = ctk.CTkButton(
            self.login_frame, command=self.handle_login,
            text="Ingresar", fg_color="#005b96", hover_color="#03396c", font=("false", 16), text_color="#ffffff", width=225).pack(pady=(12), padx=(10)
        )

    def create_main_frame(self):
        self.login_frame.destroy()
        
        self.main_frame = ctk.CTkScrollableFrame(self,fg_color="transparent")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.game_label = ctk.CTkLabel(self.main_frame, text="Nombre del juego:",font=("false",20))
        self.game_label.pack(pady=5)

        self.game_entry = ctk.CTkEntry(self.main_frame, width=300,font=("Arial Rounded MT", 14))
        self.game_entry.pack(pady=5)

        self.search_button = ctk.CTkButton(
            self.main_frame, text="Buscar", fg_color="#005b96", hover_color="#03396c", font=("false", 16), text_color="#ffffff", width=225,command=self.handle_search
        ).pack(pady=(12), padx=(10))

        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.results_frame.pack(pady=10, fill="both", expand=True)
        for i in range(5):
         self.results_frame.grid_columnconfigure(i, weight=1)

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
        
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        juegos = self.buscar_juegos(game_name)
        
        if juegos:
            juego = juegos[0]
            title_label = ctk.CTkLabel(self.results_frame, 
                                     text=f"Juegos similares a {juego['name']}",
                                     font=("false", 16))
            title_label.grid(row=0, column=0, columnspan=5, pady=10)

            datos_usuarios[self.current_user].append({
                'usuario': self.current_user,
                'juego': juego['name'],
                'valoracion': 0
            })

            if 'similar_games' in juego:
                row = 2
                col = 0
                for i, similar_id in enumerate(juego['similar_games']):
                    similar = self.obtener_juegos_similares(similar_id)
                    if similar and 'cover' in similar[0]:
                        col = i % 5
                        self.mostrar_imagen(similar[0]['cover'], similar[0]['name'], row=row, col=col)
                        if col == 4:
                            row += 1

    def mostrar_imagen(self, cover_data, nombre_juego, row, col):
        image_id = cover_data['image_id']
        url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"
        
        response = requests.get(url)
        img_data = Image.open(BytesIO(response.content))
        
        ct_image = ctk.CTkImage(light_image=img_data,
                              dark_image=img_data,
                              size=(150, 200))
        
        card_frame = ctk.CTkFrame(self.results_frame, 
                                fg_color="transparent", 
                                corner_radius=10,
                                width=200,
                                height=250)
        card_frame.grid(row=row, column=col, padx=10, pady=10)

        label_image = ctk.CTkLabel(card_frame, image=ct_image, text="",font=("false", 16))
        label_image.pack(pady=5)

        label_text = ctk.CTkLabel(card_frame, 
                                text=nombre_juego, 
                                wraplength=180,
                                justify="center",
                                font=("false",16))
        label_text.pack(pady=5)
    
    def buscar_juegos(self, nombre_juego):
        url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Accept": "application/json",
        }
        data = f'search "{nombre_juego}"; fields name, id, similar_games, cover.image_id;;'
        response = requests.post(url, headers=headers, data=data)
        return response.json() if response.status_code == 200 else None

    def obtener_juegos_similares(self, juego_id):
        url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        }
        data = f'fields name, cover.image_id; where id = {juego_id};'
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
