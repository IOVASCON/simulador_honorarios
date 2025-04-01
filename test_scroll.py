# test_scroll.py
import customtkinter as ctk

class MinimalApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Minimal Scroll Test")
        self.geometry("400x300")

        try:
            print("Tentando criar CTkScrollableFrame...")
            # Tente PRIMEIRO sem corner_radius
            scroll_frame = ctk.CTkScrollableFrame(self, label_text="Scroll Test")

            # Se o de cima falhar, comente ele e descomente uma das linhas abaixo para testar:
            # scroll_frame = ctk.CTkScrollableFrame(self, label_text="Scroll Test", corner_radius=None)
            # scroll_frame = ctk.CTkScrollableFrame(self, label_text="Scroll Test", corner_radius=1) # Testar com um inteiro > 0

            scroll_frame.pack(padx=20, pady=20, fill="both", expand=True)
            print("CTkScrollableFrame criado com sucesso.")
            label = ctk.CTkLabel(scroll_frame, text="Conteúdo dentro do ScrollFrame")
            label.pack(pady=10)

        except Exception as e:
            print(f"\n--- ERRO AO CRIAR CTkScrollableFrame ---")
            print(f"Erro: {type(e).__name__}: {e}")
            print("Traceback:")
            import traceback
            traceback.print_exc()
            print("----------------------------------------\n")

            # Se o ScrollFrame falhar, vamos tentar um Frame simples para comparar
            try:
                print("Tentando criar um CTkFrame simples...")
                simple_frame = ctk.CTkFrame(self) # Usando padrão
                simple_frame.pack(padx=20, pady=40, fill="both", expand=True)
                label_simple = ctk.CTkLabel(simple_frame, text="CTkFrame Simples Funcionou")
                label_simple.pack(pady=10)
                print("CTkFrame simples criado com sucesso.")
            except Exception as e_frame:
                 print(f"\n--- ERRO AO CRIAR CTkFrame SIMPLES ---")
                 print(f"Erro: {type(e_frame).__name__}: {e_frame}")
                 print("Traceback:")
                 import traceback
                 traceback.print_exc()
                 print("----------------------------------------\n")


if __name__ == "__main__":
    print("Iniciando MinimalApp...")
    app = MinimalApp()
    app.mainloop()
    print("MinimalApp finalizada.")