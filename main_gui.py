import customtkinter
from gui.app import App # Importa a classe principal da GUI
# import locale # Mantido comentado, pois não era a causa e pode ser adicionado se necessário

# --- DESATIVAR DPI AUTOMÁTICO (CORREÇÃO NECESSÁRIA) ---
# Esta linha é crucial para evitar o erro 'bad screen distance' no seu ambiente.
customtkinter.deactivate_automatic_dpi_awareness()
# -----------------------------------------------------

if __name__ == "__main__":
    # Configurações iniciais do CustomTkinter (Aparência e Tema)
    customtkinter.set_appearance_mode("Light") # Modes: "System" (default), "Dark", "Light"
    customtkinter.set_default_color_theme("blue") # Themes: "blue" (default), "green", "dark-blue"

    # Cria e executa a aplicação GUI
    app = App()
    app.mainloop()