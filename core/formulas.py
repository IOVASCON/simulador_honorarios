import math
from datetime import date
# Importa o módulo de constantes e as funções utilitárias
import core.constants as constants 
from core.utils import calcular_anos_desde, formatar_numero, formatar_moeda

# (As definições de constantes foram MOVIDAS para constants.py)

# --- Funções de Cálculo dos Fatores (agora usam constants.) ---

def calcular_fator_tempo_experiencia(data_graduacao: date, data_oab: date, datas_pos: list[date]) -> tuple[float, dict]:
    """Calcula o fator baseado no tempo de formado, prática (OAB) e pós-graduações."""
    anos_desde_grad = calcular_anos_desde(data_graduacao)
    anos_desde_oab = calcular_anos_desde(data_oab) # Prática efetiva

    anos_desde_pos_lista = [calcular_anos_desde(dt) for dt in datas_pos if dt]
    anos_desde_pos_media = sum(anos_desde_pos_lista) / len(anos_desde_pos_lista) if anos_desde_pos_lista else 0

    # Fórmula: Base 1 + Bônus por ano de OAB + Bônus por ano médio de pós
    fator = 1.0 + (constants.PESO_ANO_POS_OAB * anos_desde_oab) \
                + (constants.PESO_ANO_POS_GRAD * anos_desde_pos_media)

    detalhes = {
        "Anos desde Graduação": formatar_numero(anos_desde_grad, 1),
        "Anos desde Inscrição OAB": formatar_numero(anos_desde_oab, 1),
        "Anos Médios desde Pós-Graduações": formatar_numero(anos_desde_pos_media, 1) if anos_desde_pos_lista else "N/A",
        "Peso Ano Pós-OAB (const)": constants.PESO_ANO_POS_OAB,
        "Peso Ano Médio Pós (const)": constants.PESO_ANO_POS_GRAD
    }
    return max(1.0, fator), detalhes

def calcular_fator_especializacao_pos(datas_pos: list[date]) -> tuple[float, dict]:
    """Calcula o fator baseado na quantidade de pós-graduações."""
    num_pos = len(datas_pos)
    # Fórmula: Base 1 + Bônus por cada pós
    fator = 1.0 + (constants.VALOR_BASE_POS_GRAD * num_pos)

    detalhes = {
        "Número de Pós-Graduações": num_pos,
        "Bônus por Pós-Graduação (const)": constants.VALOR_BASE_POS_GRAD
    }
    return max(1.0, fator), detalhes

def calcular_fator_experiencia_pratica(
    total_acoes: int,
    ganhas_prev: int, ganhas_emp: int, ganhas_civil: int, ganhas_trab: int, ganhas_trib: int, ganhas_outras: int, # Adicionado Trab e Trib
    area_servico_atual: str
) -> tuple[float, dict]:
    """Calcula o fator baseado no volume e sucesso em ações judiciais."""
    total_ganhas = ganhas_prev + ganhas_emp + ganhas_civil + ganhas_trab + ganhas_trib + ganhas_outras
    taxa_sucesso_geral = (total_ganhas / total_acoes) if total_acoes >= constants.MIN_ACOES_PARA_SUCESSO_GERAL else 0.0

    # --- Taxa de sucesso específica ---
    # Idealmente, o input coletaria o TOTAL de ações atuadas POR ÁREA.
    # Sem isso, a taxa específica fica prejudicada.
    # Simplificação: Usaremos a taxa geral, mas o peso dela será maior.
    # (Mantendo a lógica anterior para simplificar, mas ciente da limitação)
    taxa_sucesso_especifica_proxy = taxa_sucesso_geral # Usando a geral como proxy
    ganhas_na_area_atual = 0
    if area_servico_atual == "Previdenciária": ganhas_na_area_atual = ganhas_prev
    elif area_servico_atual == "Empresarial": ganhas_na_area_atual = ganhas_emp
    elif area_servico_atual == "Civil": ganhas_na_area_atual = ganhas_civil
    elif area_servico_atual == "Trabalhista": ganhas_na_area_atual = ganhas_trab
    elif area_servico_atual == "Tributária": ganhas_na_area_atual = ganhas_trib
    elif area_servico_atual == "Outra": ganhas_na_area_atual = ganhas_outras
    # Nota: Uma taxa específica real seria:
    # total_acoes_na_area = obter_input_int(f"Total de ações atuadas na área {area_servico_atual}:")
    # taxa_sucesso_especifica = (ganhas_na_area_atual / total_acoes_na_area) if total_acoes_na_area >= constants.MIN_ACOES_PARA_SUCESSO_ESPECIFICO else 0.0

    # Usar logaritmo natural + 1 para o volume, suaviza o impacto de números muito grandes
    log_volume = math.log(total_acoes + 1) if total_acoes > 0 else 0

    # Fórmula: Base 1 + Bônus Volume (Log) + Bônus Sucesso Geral + Bônus Sucesso Específico (Proxy)
    fator = 1.0 + (constants.PESO_VOLUME_ACOES * log_volume) \
                + (constants.PESO_TAXA_SUCESSO_GERAL * taxa_sucesso_geral) \
                + (constants.PESO_TAXA_SUCESSO_ESPECIFICA * taxa_sucesso_especifica_proxy)

    detalhes = {
        "Total de Ações Atuadas": total_acoes,
        "Total de Ações Ganhas": total_ganhas,
        f"Ações Ganhas em {area_servico_atual}": ganhas_na_area_atual,
        "Taxa de Sucesso Geral Estimada": f"{taxa_sucesso_geral:.1%}" if total_acoes >= constants.MIN_ACOES_PARA_SUCESSO_GERAL else f"< {constants.MIN_ACOES_PARA_SUCESSO_GERAL} ações",
        "Taxa Sucesso Específica Usada (Proxy)": f"{taxa_sucesso_especifica_proxy:.1%}",
        "Log(Volume + 1)": formatar_numero(log_volume, 3),
        "Peso Volume (const)": constants.PESO_VOLUME_ACOES,
        "Peso Sucesso Geral (const)": constants.PESO_TAXA_SUCESSO_GERAL,
        "Peso Sucesso Específico (const)": constants.PESO_TAXA_SUCESSO_ESPECIFICA,
        "Mínimo Ações Sucesso Geral (const)": constants.MIN_ACOES_PARA_SUCESSO_GERAL,
    }
    return max(1.0, fator), detalhes


def calcular_fator_investimento_educacional(gastos_educacao: float, taxa_horaria_minima: float) -> tuple[float, dict]:
    """Calcula o fator baseado no investimento em educação."""
    if taxa_horaria_minima <= 0: return 1.0, {"Detalhe": "Taxa horária mínima inválida."}

    # Estimativa de receita anual baseada na taxa mínima
    receita_anual_minima_estimada = taxa_horaria_minima * constants.HORAS_NORMAIS_POR_ANO

    if receita_anual_minima_estimada <= 0: return 1.0, {"Detalhe": "Receita anual mínima estimada inválida."}

    # Proporção do gasto educacional sobre a receita anual mínima
    proporcao_gasto_receita = gastos_educacao / receita_anual_minima_estimada

    # Fórmula: Base 1 + Peso * Proporção
    fator = 1.0 + (constants.PESO_GASTO_EDUCACAO_SOBRE_TAXA_MIN_ANUAL * proporcao_gasto_receita)

    detalhes = {
        "Gasto Total com Educação": formatar_moeda(gastos_educacao),
        "Taxa Horária Mínima Informada": formatar_moeda(taxa_horaria_minima),
        "Receita Anual Mínima Estimada": formatar_moeda(receita_anual_minima_estimada),
        "Proporção Gasto/Receita Anual Min.": f"{proporcao_gasto_receita:.2%}",
        "Peso Gasto Educação (const)": constants.PESO_GASTO_EDUCACAO_SOBRE_TAXA_MIN_ANUAL,
        "Horas Normais/Ano (const)": constants.HORAS_NORMAIS_POR_ANO,
    }
    return max(1.0, fator), detalhes


def calcular_fator_dedicacao(horas_fds: int, data_oab: date) -> tuple[float, dict]:
    """Calcula o fator baseado nas horas trabalhadas em fins de semana/feriados."""
    anos_desde_oab = calcular_anos_desde(data_oab)
    if anos_desde_oab <= 0:
        return 1.0, {"Detalhe": "Menos de um ano de prática (OAB)."}

    total_horas_normais_estimadas_carreira = anos_desde_oab * constants.HORAS_NORMAIS_POR_ANO
    if total_horas_normais_estimadas_carreira <= 0:
         return 1.0, {"Detalhe": "Horas normais estimadas inválidas."}

    proporcao_horas_fds = horas_fds / total_horas_normais_estimadas_carreira if total_horas_normais_estimadas_carreira > 0 else 0

    # Fórmula: Base 1 + Peso * Proporção
    fator = 1.0 + (constants.PESO_DEDICACAO_HORAS_FDS * proporcao_horas_fds)

    detalhes = {
        "Total Horas Estimadas FDS/Feriados": horas_fds,
        "Anos de Prática (OAB)": formatar_numero(anos_desde_oab, 1),
        "Total Horas Normais Estimadas (Carreira)": formatar_numero(total_horas_normais_estimadas_carreira, 0),
        "Proporção Horas FDS / Normais": f"{proporcao_horas_fds:.2%}",
        "Peso Dedicação (Horas FDS) (const)": constants.PESO_DEDICACAO_HORAS_FDS,
        "Horas Normais/Ano (const)": constants.HORAS_NORMAIS_POR_ANO,
    }
    return max(1.0, fator), detalhes


# --- Funções Principais de Cálculo ---

def calcular_taxa_horaria_sugerida(dados: dict) -> tuple[float, dict]:
    """Calcula a taxa horária final combinando todos os fatores."""
    taxa_base = dados['taxa_horaria_base_minima']
    fatores_aplicados = {}
    detalhes_fatores = {}

    fator_tempo, det_tempo = calcular_fator_tempo_experiencia(
        dados['data_graduacao'], dados['data_oab'], dados['datas_pos_graduacao']
    )
    fatores_aplicados['Tempo Experiência'] = fator_tempo
    detalhes_fatores['Tempo Experiência'] = det_tempo

    fator_pos, det_pos = calcular_fator_especializacao_pos(dados['datas_pos_graduacao'])
    fatores_aplicados['Especialização (Pós)'] = fator_pos
    detalhes_fatores['Especialização (Pós)'] = det_pos

    fator_pratica, det_pratica = calcular_fator_experiencia_pratica(
        dados['total_acoes_defendidas'],
        dados['acoes_ganhas_previdenciaria'], dados['acoes_ganhas_empresarial'],
        dados['acoes_ganhas_civil'], dados['acoes_ganhas_trabalhista'], # Adicionado
        dados['acoes_ganhas_tributaria'], dados['acoes_ganhas_outra'], # Adicionado 'acoes_ganhas_outra' 'outra' no sigular
        dados['area_servico_atual']
    )
    fatores_aplicados['Experiência Prática (Casos)'] = fator_pratica
    detalhes_fatores['Experiência Prática (Casos)'] = det_pratica

    fator_invest_edu, det_invest = calcular_fator_investimento_educacional(
        dados['gastos_educacao'], dados['taxa_horaria_base_minima']
    )
    fatores_aplicados['Investimento Educacional'] = fator_invest_edu
    detalhes_fatores['Investimento Educacional'] = det_invest

    fator_dedic, det_dedic = calcular_fator_dedicacao(
        dados['horas_trabalhadas_fds_total'], dados['data_oab']
    )
    fatores_aplicados['Dedicação (Horas Extras)'] = fator_dedic
    detalhes_fatores['Dedicação (Horas Extras)'] = det_dedic

    taxa_calculada = taxa_base
    print("\nAplicando Fatores à Taxa Base:")
    print(f"- Taxa Base Informada: {formatar_moeda(taxa_base)}")
    for nome, fator in fatores_aplicados.items():
        taxa_calculada *= fator
        print(f"- Fator {nome}: {formatar_numero(fator, 3)}x")

    detalhes_calculo_taxa = {
        "Taxa Horária Base Informada": taxa_base,
        "Fatores Multiplicadores": fatores_aplicados,
        "Detalhes dos Fatores": detalhes_fatores,
        "Taxa Horária Calculada Bruta": taxa_calculada
    }

    # Aplica um arredondamento ou ajuste final se desejado
    # taxa_final_ajustada = round(taxa_calculada / 5) * 5 # Ex: Múltiplo de 5
    taxa_final_ajustada = taxa_calculada # Sem ajuste por enquanto

    detalhes_calculo_taxa["Taxa Horária Sugerida Final"] = taxa_final_ajustada

    print(f"\n=> Taxa Horária Sugerida: {formatar_moeda(taxa_final_ajustada)}")

    return taxa_final_ajustada, detalhes_calculo_taxa


def calcular_preco_final_servico(taxa_horaria_sugerida: float, dados_servico: dict) -> tuple[float, dict]:
    """Calcula o preço final do serviço aplicando complexidade e urgência."""
    horas = dados_servico['horas_estimadas_servico']
    complexidade_str = dados_servico['nivel_complexidade_servico']
    urgencia_str = dados_servico['nivel_urgencia_servico']

    fator_complexidade = constants.MULTIPLICADOR_COMPLEXIDADE.get(complexidade_str, 1.0)
    fator_urgencia = constants.MULTIPLICADOR_URGENCIA.get(urgencia_str, 1.0)

    preco_base = taxa_horaria_sugerida * horas
    preco_final = preco_base * fator_complexidade * fator_urgencia

    print(f"\nCalculando Preço do Serviço Específico:")
    print(f"- Horas Estimadas: {formatar_numero(horas, 1)} h")
    print(f"- Nível Complexidade: {complexidade_str} ({fator_complexidade:.2f}x)")
    print(f"- Nível Urgência: {urgencia_str} ({fator_urgencia:.2f}x)")
    print(f"- Preço Base (Taxa * Horas): {formatar_moeda(preco_base)}")
    print(f"=> Preço Final Sugerido (Base * Complexidade * Urgência): {formatar_moeda(preco_final)}")

    detalhes = {
        "Taxa Horária Utilizada": taxa_horaria_sugerida,
        "Horas Estimadas": horas,
        "Nível de Complexidade": complexidade_str,
        "Fator Complexidade": fator_complexidade,
        "Nível de Urgência": urgencia_str,
        "Fator Urgência": fator_urgencia,
        "Preço Base (Taxa * Horas)": preco_base,
        "Preço Final Sugerido": preco_final
    }
    return preco_final, detalhes