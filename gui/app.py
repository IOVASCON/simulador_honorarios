import customtkinter as ctk
from tkinter import messagebox
from datetime import date, datetime
import os
import unicodedata # Para normalizar nomes de chave

# Importa a lógica de negócio, utilitários e constantes
from core import formulas, utils, constants
from reports import pdf_generator # Para gerar o PDF

# --- Função Auxiliar para Normalização de Chaves ---
def normalize_key(text):
    """Remove acentos, converte para minúsculas e substitui espaços/hífens por underscores."""
    try:
        nfkd_form = unicodedata.normalize('NFKD', text)
        text_sem_acentos = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        return text_sem_acentos.lower().replace("-", "_").replace(" ", "_")
    except TypeError: # Caso receba algo que não seja string
        return str(text).lower().replace("-", "_").replace(" ", "_")

# --- Classe Principal da Aplicação GUI ---
class App(ctk.CTk):
    def __init__(self):
        """Inicializa a janela principal e todos os seus widgets."""
        super().__init__()

        self.title("Simulador de Honorários Advocatícios")
        # Ajuste fino da geometria pode ser necessário dependendo da fonte/resolução
        self.geometry("750x700")

        # --- Definição de Fontes para consistência e compactação ---
        self.default_font = ctk.CTkFont(size=12)
        self.label_font = ctk.CTkFont(size=12)
        self.entry_font = ctk.CTkFont(size=12)
        self.title_font = ctk.CTkFont(size=13, weight="bold")

        # --- Dicionário para armazenar widgets de entrada para fácil acesso ---
        self.entries = {}
        # --- Lista para armazenar widgets de entrada das Pós-Graduações ---
        self.pos_grad_entries = []

        # --- Configuração do Layout Principal da Janela ---
        # Faz a coluna 0 (onde o scroll frame estará) expandir com a janela
        self.grid_columnconfigure(0, weight=1)
        # Faz a linha 0 (onde o scroll frame estará) expandir com a janela
        self.grid_rowconfigure(0, weight=1)

        # --- Frame Principal com Barra de Rolagem ---
        # Contém a maioria dos campos de entrada
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Dados para Simulação")
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # Configura a coluna 1 DENTRO do scroll frame (onde ficam as Entries) para expandir
        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        # Configura a coluna 3 DENTRO do scroll frame para expandir (usada na linha Valor Causa/Percentual)
        self.scrollable_frame.grid_columnconfigure(3, weight=1)

        # --- Variável para controlar a próxima linha disponível no grid do scroll_frame ---
        row_idx = 0

        # --- Seção: Dados Pessoais e Formação ---
        ctk.CTkLabel(self.scrollable_frame, text="Dados Pessoais e Formação", font=self.title_font).grid(
            row=row_idx, column=0, columnspan=4, pady=(0, 5), sticky="w") # Span 4 colunas
        row_idx += 1
        self.entries['nome_advogado'] = self._create_entry_row("Nome do Advogado:", row_idx)
        row_idx += 1
        self.entries['data_graduacao'] = self._create_entry_row("Data Graduação (DD/MM/AAAA):", row_idx)
        row_idx += 1
        self.entries['data_oab'] = self._create_entry_row("Data Inscrição OAB (DD/MM/AAAA):", row_idx)
        row_idx += 1

        # --- Seção: Pós-Graduações ---
        ctk.CTkLabel(self.scrollable_frame, text="Pós-Graduações", font=self.title_font).grid(
            row=row_idx, column=0, columnspan=3, pady=(15, 5), sticky="w") # Span 3 colunas
        # Botão para adicionar mais campos de pós
        add_pos_button = ctk.CTkButton(self.scrollable_frame, text="+ Pós", command=self._add_pos_grad_entry, width=60, font=self.default_font)
        add_pos_button.grid(row=row_idx, column=3, pady=(15,2), padx=(0,5), sticky="e") # Coluna 3
        row_idx += 1
        # Frame interno para agrupar os campos de pós adicionados dinamicamente
        self.pos_grad_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.pos_grad_frame.grid(row=row_idx, column=0, columnspan=4, sticky="ew", pady=(0, 5)) # Span 4 colunas
        self.pos_grad_frame.grid_columnconfigure(1, weight=1) # Coluna da entry dentro deste frame expande
        self.pos_grad_next_row = 0 # Contador de linha interno para o pos_grad_frame
        self._add_pos_grad_entry() # Adiciona o primeiro campo
        row_idx += 1

        # --- Seção: Experiência Prática ---
        ctk.CTkLabel(self.scrollable_frame, text="Experiência Prática", font=self.title_font).grid(
            row=row_idx, column=0, columnspan=4, pady=(15, 5), sticky="w") # Span 4 colunas
        row_idx += 1
        # Ajuste o rótulo para ser claro sobre o que o valor representa
        self.entries['total_acoes_defendidas'] = self._create_entry_row("Total Ações Atuadas (Carreira):", row_idx)
        row_idx += 1
        ctk.CTkLabel(self.scrollable_frame, text="Ações Ganhas por Área:", font=self.label_font).grid(
            row=row_idx, column=0, columnspan=4, padx=(0,5), pady=(5,2), sticky="w") # Span 4 colunas
        row_idx += 1
        # Frame interno para layout das ações ganhas (pode quebrar em linhas)
        acoes_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        acoes_frame.grid(row=row_idx, column=0, columnspan=4, sticky="ew", pady=(0, 5)) # Span 4 colunas
        # Configura colunas internas do acoes_frame para 2 pares Label/Entry por linha
        acoes_frame.grid_columnconfigure(1, weight=1) # Coluna Entry 1 expande
        acoes_frame.grid_columnconfigure(3, weight=1) # Coluna Entry 2 expande
        acoes_row = 0
        acoes_col = 0
        for area in constants.AREAS_ATUACAO: # Itera sobre as áreas definidas nas constantes
            key = f'acoes_ganhas_{normalize_key(area)}' # Gera chave normalizada
            lab = ctk.CTkLabel(acoes_frame, text=f"{area}:", font=self.label_font)
            ent = ctk.CTkEntry(acoes_frame, font=self.entry_font)
            lab.grid(row=acoes_row, column=acoes_col, padx=(5,2), pady=2, sticky="e")
            ent.grid(row=acoes_row, column=acoes_col + 1, padx=(0, 10), pady=2, sticky="ew")
            self.entries[key] = ent # Armazena a entry no dicionário
            acoes_col += 2 # Próximo par Label/Entry
            if acoes_col >= 4: # Se preencheu as 4 colunas, vai para a próxima linha
                acoes_col = 0
                acoes_row += 1
        row_idx += 1

        # --- Seção: Investimento e Dedicação ---
        ctk.CTkLabel(self.scrollable_frame, text="Investimento e Dedicação", font=self.title_font).grid(
            row=row_idx, column=0, columnspan=4, pady=(15, 5), sticky="w") # Span 4 colunas
        row_idx += 1
        self.entries['gastos_educacao'] = self._create_entry_row("Gasto Educação (Total R$):", row_idx)
        row_idx += 1
        # **IMPORTANTE**: Ajuste o rótulo para refletir o que as horas extras significam (mensal, anual, etc.)
        self.entries['horas_trabalhadas_fds_total'] = self._create_entry_row("Média Mensal Horas Extras:", row_idx)
        row_idx += 1

        # --- Seção: Dados do Serviço Específico ---
        ctk.CTkLabel(self.scrollable_frame, text="Dados do Serviço Específico", font=self.title_font).grid(
            row=row_idx, column=0, columnspan=4, pady=(15, 5), sticky="w") # Span 4 colunas
        row_idx += 1
        self.entries['area_servico_atual'] = self._create_combobox_row("Área do Serviço:", constants.AREAS_ATUACAO, row_idx)
        row_idx += 1
        self.entries['horas_estimadas_servico'] = self._create_entry_row("Horas Estimadas TOTAIS:", row_idx)
        row_idx += 1
        self.entries['nivel_complexidade_servico'] = self._create_combobox_row("Complexidade:", constants.NIVEIS_COMPLEXIDADE, row_idx)
        row_idx += 1
        self.entries['nivel_urgencia_servico'] = self._create_combobox_row("Urgência:", constants.NIVEIS_URGENCIA, row_idx)
        row_idx += 1

        # --- Linha Combinada: Valor Causa e Percentual Êxito ---
        # Label Valor Causa
        ctk.CTkLabel(self.scrollable_frame, text="Valor Causa (Cliente - R$, 0 se N/A):", font=self.label_font).grid(
            row=row_idx, column=0, padx=(0, 5), pady=2, sticky="w")
        # Entry Valor Causa
        entry_valor_causa = ctk.CTkEntry(self.scrollable_frame, font=self.entry_font)
        entry_valor_causa.grid(row=row_idx, column=1, padx=0, pady=2, sticky="ew")
        self.entries['valor_estimado_causa_ganha'] = entry_valor_causa
        # Label Percentual Êxito
        ctk.CTkLabel(self.scrollable_frame, text="Percentual Êxito (%):", font=self.label_font).grid(
            row=row_idx, column=2, padx=(10, 5), pady=2, sticky="w") # Padding à esquerda para separar
        # Entry Percentual Êxito
        entry_perc_exito = ctk.CTkEntry(self.scrollable_frame, font=self.entry_font)
        entry_perc_exito.grid(row=row_idx, column=3, padx=0, pady=2, sticky="ew")
        self.entries['percentual_exito'] = entry_perc_exito
        row_idx += 1

        # --- Seção: Parâmetros Base ---
        ctk.CTkLabel(self.scrollable_frame, text="Parâmetros Base (Cálculo Horário)", font=self.title_font).grid(
            row=row_idx, column=0, columnspan=4, pady=(15, 5), sticky="w") # Span 4 colunas
        row_idx += 1
        self.entries['taxa_horaria_base_minima'] = self._create_entry_row("Taxa Horária Mínima (R$):", row_idx)
        row_idx += 1

        # --- Botão Calcular (Fora do Scroll Frame) ---
        # Posicionado na linha 1 da janela principal (self)
        calculate_button = ctk.CTkButton(self, text="Calcular e Gerar PDF", command=self.calculate, font=self.default_font)
        calculate_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # --- Área de Resultados (Fora do Scroll Frame) ---
        # Posicionado na linha 2 da janela principal (self)
        self.results_label = ctk.CTkLabel(self, text="Resultados aparecerão aqui...", wraplength=700, anchor="w", justify="left", font=self.default_font)
        self.results_label.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")

    # --- Métodos Auxiliares para Criação de Widgets ---
    def _create_entry_row(self, label_text, row_index):
        """Cria uma linha padrão com Label na coluna 0 e Entry na coluna 1."""
        label = ctk.CTkLabel(self.scrollable_frame, text=label_text, font=self.label_font)
        # Coloca o label na coluna 0 da linha especificada
        label.grid(row=row_index, column=0, padx=(0, 5), pady=2, sticky="w")
        entry = ctk.CTkEntry(self.scrollable_frame, font=self.entry_font)
        # Coloca a entry na coluna 1 da linha especificada, fazendo-a expandir horizontalmente
        entry.grid(row=row_index, column=1, columnspan=3, padx=0, pady=2, sticky="ew") # Span 3 colunas restantes
        return entry

    def _create_combobox_row(self, label_text, values, row_index):
        """Cria uma linha padrão com Label na coluna 0 e ComboBox na coluna 1."""
        label = ctk.CTkLabel(self.scrollable_frame, text=label_text, font=self.label_font)
        label.grid(row=row_index, column=0, padx=(0, 5), pady=2, sticky="w")
        combobox = ctk.CTkComboBox(self.scrollable_frame, values=values, state="readonly", font=self.entry_font, dropdown_font=self.entry_font)
        combobox.grid(row=row_index, column=1, columnspan=3, padx=0, pady=2, sticky="ew") # Span 3 colunas restantes
        if values: # Define o primeiro valor como padrão, se houver valores
            combobox.set(values[0])
        return combobox

    def _add_pos_grad_entry(self):
        """Adiciona dinamicamente uma nova linha para data de Pós-Graduação."""
        row = self.pos_grad_next_row # Linha dentro do pos_grad_frame
        # Label curto para economizar espaço
        label = ctk.CTkLabel(self.pos_grad_frame, text=f"Pós {len(self.pos_grad_entries) + 1} (DD/MM/AAAA):", font=self.label_font)
        label.grid(row=row, column=0, padx=(0, 5), pady=1, sticky="w") # Coluna 0 do frame interno
        entry = ctk.CTkEntry(self.pos_grad_frame, font=self.entry_font)
        entry.grid(row=row, column=1, padx=0, pady=1, sticky="ew") # Coluna 1 do frame interno
        self.pos_grad_entries.append(entry) # Adiciona a entry à lista
        self.pos_grad_next_row += 1 # Incrementa o contador de linha interna

    # --- Método Principal de Cálculo e Geração de Relatório ---
    def calculate(self):
        """Coleta todos os dados da GUI, valida, chama os cálculos e exibe/salva os resultados."""
        dados_input = {} # Dicionário para armazenar os dados coletados
        self.results_label.configure(text="Calculando...", font=self.default_font) # Feedback

        try:
            # --- 1. Coleta e Validação dos Dados de Entrada ---

            # Coleta Nome (simples validação de não vazio)
            dados_input['nome_advogado'] = self.entries['nome_advogado'].get().strip()
            if not dados_input['nome_advogado']:
                raise ValueError("Nome do Advogado não pode estar vazio.")

            # Coleta e Validação de Datas
            data_graduacao_str = self.entries['data_graduacao'].get().strip()
            dados_input['data_graduacao'] = utils.parse_data(data_graduacao_str) # Usa helper de utils.py
            if not dados_input['data_graduacao'] or dados_input['data_graduacao'] > date.today():
                 raise ValueError("Data de Graduação inválida ou futura. Use DD/MM/AAAA.")

            data_oab_str = self.entries['data_oab'].get().strip()
            dados_input['data_oab'] = utils.parse_data(data_oab_str)
            if not dados_input['data_oab'] or dados_input['data_oab'] > date.today():
                 raise ValueError("Data da OAB inválida ou futura. Use DD/MM/AAAA.")
            if dados_input['data_oab'] < dados_input['data_graduacao']:
                 raise ValueError("Data da OAB não pode ser anterior à data de graduação.")

            # Coleta e Validação das Datas de Pós-Graduação (pode haver várias)
            dados_input['datas_pos_graduacao'] = []
            for i, entry in enumerate(self.pos_grad_entries):
                data_str = entry.get().strip()
                if data_str: # Processa apenas se o campo não estiver vazio
                    data_obj = utils.parse_data(data_str)
                    if not data_obj or data_obj > date.today():
                         raise ValueError(f"Data de Pós {i+1} ('{data_str}') inválida/futura.")
                    if data_obj < dados_input['data_graduacao']:
                         raise ValueError(f"Data de Pós {i+1} ('{data_str}') anterior à graduação.")
                    if data_obj not in dados_input['datas_pos_graduacao']: # Evita datas duplicadas
                         dados_input['datas_pos_graduacao'].append(data_obj)
            dados_input['datas_pos_graduacao'].sort() # Ordena as datas

            # Coleta e Validação de Campos Inteiros
            int_fields = { # Mapeia chave interna para rótulo amigável
                'total_acoes_defendidas': "Total Ações Atuadas (Carreira)",
                'horas_trabalhadas_fds_total': "Média Mensal Horas Extras", # Ajuste conforme o significado real
            }
            # Adiciona dinamicamente as chaves das ações ganhas por área
            for area in constants.AREAS_ATUACAO:
                key = f'acoes_ganhas_{normalize_key(area)}'
                int_fields[key] = f"Ações Ganhas ({area})"

            for key, label in int_fields.items():
                 if key not in self.entries: # Verificação de segurança
                      print(f"Aviso: Chave inteira '{key}' esperada não encontrada em self.entries.")
                      dados_input[key] = 0 # Assume 0 se não encontrar
                      continue
                 try:
                     value_str = self.entries[key].get().strip()
                     dados_input[key] = int(value_str) if value_str else 0 # Converte para int, 0 se vazio
                     if dados_input[key] < 0: raise ValueError() # Não permite negativos
                 except ValueError:
                     raise ValueError(f"Valor inválido para '{label}'. Insira um número inteiro >= 0.")

            # Coleta e Validação de Campos Numéricos (float)
            float_fields = {
                 'gastos_educacao': "Gasto Educação (Total R$)",
                 'horas_estimadas_servico': "Horas Estimadas TOTAIS",
                 'valor_estimado_causa_ganha': "Valor Causa Cliente",
                 'taxa_horaria_base_minima': "Taxa Horária Mínima",
                 'percentual_exito': "Percentual Êxito (%)", # Nome mantido para compatibilidade da chave
            }
            for key, label in float_fields.items():
                 if key not in self.entries: # Verificação de segurança
                      print(f"Aviso: Chave float '{key}' esperada não encontrada em self.entries.")
                      dados_input[key] = 0.0 # Assume 0.0 se não encontrar
                      continue
                 try:
                     # Trata vírgula como decimal e remove pontos de milhar
                     value_str = self.entries[key].get().strip().replace('.', '').replace(',', '.')
                     if not value_str: # Se vazio, considera 0.0
                          dados_input[key] = 0.0
                     else:
                          dados_input[key] = float(value_str) # Converte para float
                          # Validações específicas de intervalo/mínimo
                          if key == 'horas_estimadas_servico' and dados_input[key] < 0.1:
                              raise ValueError("Mínimo de 0.1 hora.")
                          elif key == 'taxa_horaria_base_minima' and dados_input[key] < 1.0:
                              raise ValueError("Mínimo de R$ 1.00.")
                          elif key == 'percentual_exito' and not (0 <= dados_input[key] <= 100):
                              raise ValueError("Percentual deve ser entre 0 e 100.") # Ajuste da mensagem
                          elif dados_input[key] < 0: # Outros campos float não podem ser negativos
                               raise ValueError("Valor não pode ser negativo.")
                 except ValueError as e: # Captura erros de conversão ou das validações acima
                     msg_base = f"Valor inválido para '{label}'. Insira número >= 0"
                     if key == 'percentual_exito': msg_base += " (entre 0 e 100)"
                     # Adiciona a mensagem específica do erro se for uma das nossas validações
                     msg_extra = str(e) if str(e).startswith(("Mínimo", "Percentual deve", "Valor não pode")) else "" # Ajuste do check
                     raise ValueError(f"{msg_base}. {msg_extra}".strip())

            # Coleta dos valores dos ComboBoxes (seleção já garante valor válido da lista)
            dados_input['area_servico_atual'] = self.entries['area_servico_atual'].get()
            dados_input['nivel_complexidade_servico'] = self.entries['nivel_complexidade_servico'].get()
            dados_input['nivel_urgencia_servico'] = self.entries['nivel_urgencia_servico'].get()

            # --- 2. Validação Lógica Cruzada e Alertas de Confirmação ---

            # Verifica se o total de ações ganhas não excede o total atuado
            total_ganhas = sum(dados_input.get(f'acoes_ganhas_{normalize_key(area)}', 0) for area in constants.AREAS_ATUACAO)
            if total_ganhas > dados_input.get('total_acoes_defendidas', 0):
                 raise ValueError(f"Total Ações Ganhas ({total_ganhas}) > Total Atuadas ({dados_input.get('total_acoes_defendidas', 0)}).")

            # Alertas opcionais para valores altos (permite ao usuário confirmar ou cancelar)
            # Utiliza limites definidos em core/constants.py
            if dados_input.get('horas_estimadas_servico', 0) > constants.HORAS_SERVICO_ALERTA_LIMITE:
                 if not messagebox.askyesno("Alerta de Esforço Alto", f"Estimativa de {dados_input['horas_estimadas_servico']:.1f} horas parece alta.\nDeseja prosseguir?"):
                     self.results_label.configure(text="Cálculo cancelado. Revise as horas estimadas.")
                     return # Interrompe se o usuário clicar "Não"

            if dados_input.get('valor_estimado_causa_ganha', 0) > constants.VALOR_CAUSA_ALERTA_LIMITE:
                 if not messagebox.askyesno("Alerta de Valor de Causa Alto", f"Valor da causa ({utils.formatar_moeda(dados_input['valor_estimado_causa_ganha'])}) parece alto.\nDeseja prosseguir?"):
                     self.results_label.configure(text="Cálculo cancelado. Revise o valor da causa.")
                     return # Interrompe se o usuário clicar "Não"

            if dados_input.get('taxa_horaria_base_minima', 0) > constants.TAXA_BASE_ALERTA_LIMITE:
                 if not messagebox.askyesno("Alerta de Taxa Base Alta", f"Taxa base ({utils.formatar_moeda(dados_input['taxa_horaria_base_minima'])}) parece alta como MÍNIMO.\nDeseja prosseguir?"):
                     self.results_label.configure(text="Cálculo cancelado. Revise a taxa base mínima.")
                     return # Interrompe se o usuário clicar "Não"

            # --- 3. Execução dos Cálculos Principais ---
            # Chama as funções do módulo 'core.formulas' para obter os resultados

            # Calcula a taxa horária sugerida com base nos fatores de experiência, etc.
            taxa_horaria_sugerida, detalhes_taxa = formulas.calcular_taxa_horaria_sugerida(dados_input)

            # Calcula o preço final do serviço com base na taxa horária e outros fatores do serviço atual
            preco_horario_sugerido, detalhes_preco_horario = formulas.calcular_preco_final_servico(
                taxa_horaria_sugerida, dados_input
            )

            # --- INÍCIO DA LÓGICA MODIFICADA ---
            # Calcula um valor de referência aplicando o percentual informado sobre o PREÇO HORÁRIO calculado
            valor_ref_percentual = None # Valor de referência calculado com o percentual
            detalhes_valor_percentual = {} # Detalhes deste cálculo para o PDF
            percentual_informado = dados_input.get('percentual_exito', 0.0) # Pega o % informado
            valor_causa_cliente = dados_input.get('valor_estimado_causa_ganha', 0.0) # Pega valor original (contexto)

            # Calcula o valor de referência se um percentual foi informado
            if percentual_informado > 0:
                percentual_decimal = percentual_informado / 100.0
                # *** AQUI A MUDANÇA PRINCIPAL: Base do cálculo é preco_horario_sugerido ***
                valor_ref_percentual = preco_horario_sugerido * percentual_decimal
                # Armazena detalhes para o relatório PDF
                detalhes_valor_percentual = {
                    "Valor Estimado Causa Cliente": valor_causa_cliente, # Para contexto no PDF
                    "Preço Base Horária (Usado p/ Cálculo %)": preco_horario_sugerido, # Indica a base usada
                    "Percentual Informado (%)": percentual_informado, # O percentual usado
                    "Valor Calculado (Ref. Percentual)": valor_ref_percentual # O resultado do cálculo
                }
            # --- FIM DA LÓGICA MODIFICADA ---

            # Agrupa todos os resultados e detalhes em um dicionário para passar ao gerador de PDF
            # Mantém as chaves originais ("preco_exito_sugerido", "detalhes_preco_exito")
            # por consistência interna e para o gerador de PDF, mas os valores são os novos.
            resultados_calculo = {
                "taxa_horaria_sugerida": taxa_horaria_sugerida,
                "preco_horario_sugerido": preco_horario_sugerido,
                "detalhes_taxa_horaria": detalhes_taxa,
                "detalhes_preco_horario": detalhes_preco_horario,
                "preco_exito_sugerido": valor_ref_percentual, # Usa o novo valor calculado (ou None)
                "detalhes_preco_exito": detalhes_valor_percentual  # Usa os novos detalhes (ou {})
            }

            # --- 4. Geração do Relatório PDF ---
            # Cria um nome de arquivo único com timestamp e nome sanitizado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_adv_sanit = "".join(c if c.isalnum() else "_" for c in dados_input.get('nome_advogado', 'Advogado'))
            nome_arquivo_pdf = f"Simulacao_Honorarios_{nome_adv_sanit}_{timestamp}.pdf"

            # Define a pasta de saída e a cria se não existir
            output_dir = "output"
            if not os.path.exists(output_dir):
                 os.makedirs(output_dir)

            # Monta o caminho completo para o arquivo PDF
            caminho_pdf = os.path.join(output_dir, nome_arquivo_pdf)

            # Chama a função do módulo 'reports.pdf_generator' para criar o PDF
            pdf_generator.gerar_pdf_simulacao(caminho_pdf, dados_input, resultados_calculo)

            # --- 5. Exibição dos Resultados na GUI ---
            # Formata o texto de resumo para mostrar na interface
            resultado_txt = f"Cálculo Concluído!\n\n"
            resultado_txt += f"Taxa Horária Sugerida: {utils.formatar_moeda(taxa_horaria_sugerida)}\n"
            resultado_txt += f"Preço Sugerido (Base Horária): {utils.formatar_moeda(preco_horario_sugerido)}\n"

            # --- INÍCIO DA EXIBIÇÃO MODIFICADA ---
            # Adiciona a linha do valor de referência percentual, se calculado
            if valor_ref_percentual is not None:
                # Atualiza o texto para refletir que o % foi sobre a Base Horária
                resultado_txt += f"Valor Ref. ({percentual_informado:.1f}% de Base Horária): {utils.formatar_moeda(valor_ref_percentual)}\n"
            # --- FIM DA EXIBIÇÃO MODIFICADA ---

            resultado_txt += f"\nRelatório PDF gerado em: {caminho_pdf}"

            # Atualiza o label na interface
            self.results_label.configure(text=resultado_txt)
            # Mostra um pop-up de sucesso
            messagebox.showinfo("Sucesso", f"Simulação concluída e PDF gerado:\n{caminho_pdf}")

        # --- Tratamento de Erros Esperados e Inesperados ---
        except ValueError as ve: # Erros de validação específicos (formato, intervalo)
            messagebox.showerror("Erro de Validação", str(ve))
            self.results_label.configure(text=f"Erro: {str(ve)}", font=self.default_font)
        except ImportError as ie: # Erros ao importar módulos (problema de setup/instalação)
             messagebox.showerror("Erro de Importação", f"Erro ao importar módulos: {ie}\nVerifique a instalação e a estrutura do projeto.")
             self.results_label.configure(text="Erro interno (importação).")
        except FileNotFoundError as fnfe: # Erro ao tentar criar/salvar o PDF (permissão, caminho inválido)
             messagebox.showerror("Erro de Arquivo", f"Erro ao tentar salvar o PDF: {fnfe}\nVerifique as permissões na pasta '{output_dir}'.")
             self.results_label.configure(text="Erro ao salvar PDF.")
        except KeyError as ke: # Erros se alguma chave esperada faltar nos dicionários (erro de programação)
             messagebox.showerror("Erro Interno (Chave)", f"Erro ao acessar dados internos: Chave '{ke}' não encontrada.\nContate o desenvolvedor.")
             self.results_label.configure(text=f"Erro interno (chave {ke}).")
             import traceback
             traceback.print_exc() # Ajuda a debugar no console
        except Exception as e: # Captura qualquer outro erro inesperado
            import traceback
            traceback.print_exc() # Imprime detalhes do erro no console para depuração
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro:\n{type(e).__name__}: {e}")
            self.results_label.configure(text="Ocorreu um erro inesperado.", font=self.default_font)

# --- Fim da classe App ---
