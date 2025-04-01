from datetime import date
# Importa utils E constants agora
from core.utils import parse_data, formatar_moeda # Importar formatar_moeda para o alerta
from core import constants # Para usar as listas de opções

# (Funções obter_input_* e obter_input_opcao permanecem as mesmas)
# ... (Inclua as funções obter_input_float, obter_input_int, etc. aqui) ...
def obter_input_float(mensagem: str, minimo: float | None = 0.0) -> float:
    """Obtém um input numérico (float) do usuário com tratamento de erro."""
    while True:
        try:
            # Use replace('.', '') para remover separador de milhar se existir
            valor_str = input(mensagem).replace('.', '').replace(',', '.')
            valor = float(valor_str)
            if minimo is None or valor >= minimo:
                return valor
            else:
                print(f"Valor inválido. O valor mínimo é {minimo}.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número válido.")

def obter_input_int(mensagem: str, minimo: int | None = 0) -> int:
    """Obtém um input numérico (int) do usuário com tratamento de erro."""
    while True:
        try:
            valor = int(input(mensagem))
            if minimo is None or valor >= minimo:
                return valor
            else:
                print(f"Valor inválido. O valor mínimo é {minimo}.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número inteiro.")

def obter_input_data(mensagem: str) -> date | None:
    """Obtém uma data do usuário no formato dd/mm/aaaa."""
    while True:
        data_str = input(mensagem + " (formato DD/MM/AAAA): ").strip()
        if not data_str:
            print("Data inválida. Não pode ser vazia.") # Mensagem mais clara
            continue
        data_obj = parse_data(data_str)
        if data_obj:
            if data_obj > date.today():
                print("Data inválida. A data não pode ser no futuro.")
            else:
                return data_obj
        else:
            # Tenta dar uma dica se o formato estiver próximo mas errado
            if len(data_str) == 8 and data_str.isdigit():
                 hint = f"{data_str[:2]}/{data_str[2:4]}/{data_str[4:]}"
                 print(f"Formato de data inválido. Use DD/MM/AAAA (ex: {hint}).")
            elif "/" not in data_str and "-" not in data_str and len(data_str) > 5:
                 print("Formato de data inválido. Use DD/MM/AAAA (separado por /).")
            else:
                 print("Formato de data inválido. Use DD/MM/AAAA.")

def obter_input_sim_nao(mensagem: str) -> bool:
    """Obtém uma resposta Sim/Não do usuário."""
    while True:
        resposta = input(mensagem + " (S/N): ").strip().upper()
        if resposta == 'S':
            return True
        elif resposta == 'N':
            return False
        else:
            print("Resposta inválida. Por favor, digite S ou N.")

def obter_input_opcao(mensagem: str, opcoes: list) -> str: # Simplificado para aceitar apenas lista agora
    """Obtém uma escolha de uma lista de opções."""
    opcoes_dict = {}
    print(mensagem)
    for i, opcao in enumerate(opcoes):
        print(f"  {i+1}. {opcao}")
        opcoes_dict[str(i+1)] = opcao
        opcoes_dict[opcao.lower()] = opcao # Para aceitar digitação do nome

    while True:
        escolha = input("Sua escolha (número ou nome): ").strip().lower()
        if escolha in opcoes_dict:
            return opcoes_dict[escolha] # Retorna o nome original da opção
        else:
             print(f"Opção inválida. Escolha um número ou um dos nomes listados.")


# --- Função Principal de Coleta ---

def coletar_dados_simulacao() -> dict:
    """Coleta todos os dados necessários para a simulação, com validações."""
    print("\n--- Simulador de Honorários Advocatícios ---")
    print("Por favor, forneça as informações abaixo.")

    dados = {}

    print("\n--- Dados Pessoais e de Formação ---")
    dados['nome_advogado'] = input("Nome do(a) Advogado(a) (Opcional, para o relatório): ").strip()
    dados['data_graduacao'] = obter_input_data("Data de Conclusão do Bacharelado em Direito")
    dados['data_oab'] = obter_input_data("Data de Aprovação na OAB (Inscrição Definitiva)")

    dados['datas_pos_graduacao'] = []
    print("\n--- Cursos de Pós-Graduação (Lato Sensu ou Stricto Sensu) ---")
    while obter_input_sim_nao("Deseja adicionar uma data de certificação de pós-graduação?"):
        data_pos = obter_input_data("  Data de Certificação da Pós-Graduação")
        if data_pos:
             if data_pos not in dados['datas_pos_graduacao']:
                dados['datas_pos_graduacao'].append(data_pos)
             else:
                print("  Data já adicionada.")

    print("\n--- Experiência Prática ---")
    # Loop de validação para ações totais vs ganhas
    while True:
        dados['total_acoes_defendidas'] = obter_input_int("Quantidade TOTAL de ações defendidas/atuadas na justiça: ")

        print("Quantidade de ações GANHAS (com êxito para o cliente):")
        dados['acoes_ganhas_previdenciaria'] = obter_input_int("  - Área Previdenciária: ")
        dados['acoes_ganhas_empresarial'] = obter_input_int("  - Área Empresarial: ")
        dados['acoes_ganhas_civil'] = obter_input_int("  - Área Civil (inclui família, consumidor, etc.): ")
        dados['acoes_ganhas_trabalhista'] = obter_input_int("  - Área Trabalhista: ")
        dados['acoes_ganhas_tributaria'] = obter_input_int("  - Área Tributária: ")
        dados['acoes_ganhas_outras'] = obter_input_int("  - Outras Áreas: ")

        total_ganhas = (
            dados['acoes_ganhas_previdenciaria'] + dados['acoes_ganhas_empresarial'] +
            dados['acoes_ganhas_civil'] + dados['acoes_ganhas_trabalhista'] +
            dados['acoes_ganhas_tributaria'] + dados['acoes_ganhas_outras']
        )

        if total_ganhas > dados['total_acoes_defendidas']:
            print("\n" + "="*25 + " ERRO DE VALIDAÇÃO " + "="*25)
            print(f"  O total de ações ganhas informado ({total_ganhas}) é MAIOR que")
            print(f"  o total de ações atuadas informado ({dados['total_acoes_defendidas']}).")
            print("  Isto é inconsistente. Por favor, revise e insira novamente os dados de experiência.")
            print("="*70 + "\n")
            # Continue no loop para pedir os dados de experiência novamente
        else:
            break # Dados consistentes, sair do loop de validação

    print("\n--- Investimento e Dedicação ---")
    dados['gastos_educacao'] = obter_input_float("Gasto TOTAL estimado com educação formal (Graduação, Pós, Cursos, Livros) (R$): ")
    dados['horas_trabalhadas_fds_total'] = obter_input_int("Estimativa de TOTAL de horas trabalhadas em Finais de Semana/Feriados ao longo da carreira: ")

    print("\n--- Dados do Serviço a Precificar ---")
    dados['area_servico_atual'] = obter_input_opcao("Área Principal do Serviço ATUAL:", constants.AREAS_ATUACAO)

    # Alerta para horas estimadas altas
    while True:
        dados['horas_estimadas_servico'] = obter_input_float("Horas Estimadas para este Serviço Específico: ", minimo=0.1)
        if dados['horas_estimadas_servico'] > constants.HORAS_SERVICO_ALERTA_LIMITE:
            horas_estimadas_fmt = dados['horas_estimadas_servico']
            limite_fmt = constants.HORAS_SERVICO_ALERTA_LIMITE
            print(f"\n--- ALERTA DE VALOR ALTO ---")
            # Mensagem mais clara:
            print(f"  A estimativa de {horas_estimadas_fmt:.1f} horas parece ALTA como o **esforço TOTAL**")
            print(f"  necessário para concluir este serviço específico.")
            print(f"  (O limite configurado para alerta é {limite_fmt:.1f} horas totais para um serviço).")
            print(f"  Valores muito altos aqui (representando todo o trabalho para este caso/serviço)")
            print(f"  podem levar a um preço final exagerado.")
            print(f"  Certifique-se de que esta estimativa cobre todo o trabalho esperado para ESTE serviço.")
            if not obter_input_sim_nao("  Deseja prosseguir com este número TOTAL de horas?"):
                continue # Volta para pedir as horas novamente
        break # Sai do loop se o valor for baixo ou se o usuário confirmar

    dados['nivel_complexidade_servico'] = obter_input_opcao("Nível de Complexidade deste Serviço:", constants.NIVEIS_COMPLEXIDADE)
    dados['nivel_urgencia_servico'] = obter_input_opcao("Nível de Urgência deste Serviço:", constants.NIVEIS_URGENCIA)

    print("\n--- Parâmetros Base ---")
    # Alerta para taxa base alta
    while True:
        dados['taxa_horaria_base_minima'] = obter_input_float("Sua Taxa Horária MÍNIMA (R$) (cobre custos básicos e retirada mínima desejada): ", minimo=1.0)
        if dados['taxa_horaria_base_minima'] > constants.TAXA_BASE_ALERTA_LIMITE:
            taxa_formatada = formatar_moeda(dados['taxa_horaria_base_minima'])
            limite_formatado = formatar_moeda(constants.TAXA_BASE_ALERTA_LIMITE)
            print(f"\n--- ALERTA DE VALOR ALTO ---")
            print(f"  A taxa horária base de {taxa_formatada} parece ALTA como valor MÍNIMO inicial.")
            print(f"  (O limite configurado para alerta é {limite_formatado}).")
            print("  Lembre-se: este valor deve cobrir custos essenciais + retirada mínima.")
            print("  A valorização pela experiência, especialização, etc., será adicionada pelos fatores.")
            print("  Uma base muito alta pode inflacionar o resultado final.")
            if not obter_input_sim_nao("  Deseja prosseguir com esta taxa base mínima?"):
                continue # Volta para pedir a taxa base novamente
        break # Sai do loop se o valor for baixo ou se o usuário confirmar

    print("\n--- Coleta de Dados Concluída ---")
    return dados