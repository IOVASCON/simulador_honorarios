# -*- coding: utf-8 -*-

"""
Arquivo de Constantes e Parâmetros Configuráveis
-------------------------------------------------
Este arquivo centraliza todos os pesos, multiplicadores e limiares
utilizados nas fórmulas de cálculo de honorários, bem como listas
de opções usadas na GUI e validações. Ajuste estes
valores para calibrar o simulador à sua realidade e mercado.
"""

# --- Fator Experiência Temporal ---
PESO_ANO_POS_OAB: float = 0.035      # % adicional por ano de prática efetiva (pós-OAB)
PESO_ANO_POS_GRAD: float = 0.015    # % adicional por ano médio desde a conclusão das pós

# --- Fator Especialização e Pós-Graduação ---
VALOR_BASE_POS_GRAD: float = 0.08   # Bônus base por CADA pós-graduação concluída

# --- Fator Experiência Prática (Casos) ---
PESO_VOLUME_ACOES: float = 0.05    # Peso para o logaritmo do volume total de ações
PESO_TAXA_SUCESSO_GERAL: float = 0.40 # Peso da taxa de sucesso geral (0 a 1)
PESO_TAXA_SUCESSO_ESPECIFICA: float = 0.60 # Peso da taxa de sucesso na área do serviço (0 a 1) - Maior peso (usado como proxy da geral)
MIN_ACOES_PARA_SUCESSO_GERAL: int = 10 # Mínimo de ações totais para considerar a taxa de sucesso geral significativa

# --- Fator Investimento Educacional ---
PESO_GASTO_EDUCACAO_SOBRE_TAXA_MIN_ANUAL: float = 0.10 # Peso relativo ao gasto anual com taxa mínima
HORAS_NORMAIS_POR_ANO: int = 1800 # Base para cálculo da receita anual mínima

# --- Fator Dedicação (Horas Extras) ---
PESO_DEDICACAO_HORAS_FDS: float = 0.20 # Peso para a proporção de horas FDS sobre horas normais

# --- Multiplicadores do Serviço Específico (Base Horária) ---
MULTIPLICADOR_COMPLEXIDADE: dict[str, float] = {
    "Baixa": 1.0,
    "Média": 1.2,
    "Alta": 1.5,
    "Muito Alta": 1.8,
    "Excepcional": 2.2
}
MULTIPLICADOR_URGENCIA: dict[str, float] = {
    "Normal": 1.0,
    "Moderada": 1.15,
    "Alta": 1.35,
    "Imediata": 1.6
}

# --- Parâmetros para Cálculo de Êxito ---
PERCENTUAL_EXITO_PADRAO: float = 0.30 # Percentual padrão aplicado sobre o valor ganho pelo cliente (0.30 = 30%)

# --- Limites para Alertas/Validações na GUI ---
HORAS_SERVICO_ALERTA_LIMITE: float = 100.0 # Acima disso, pede confirmação na GUI
TAXA_BASE_ALERTA_LIMITE: float = 300.0 # Acima disso, pede confirmação na GUI
VALOR_CAUSA_ALERTA_LIMITE: float = 1000000.0 # Acima disso, pede confirmação na GUI

# --- Listas de Opções para GUI (ComboBoxes) ---
AREAS_ATUACAO: list[str] = ["Previdenciária", "Empresarial", "Civil", "Trabalhista", "Tributária", "Outra"]
NIVEIS_COMPLEXIDADE: list[str] = list(MULTIPLICADOR_COMPLEXIDADE.keys())
NIVEIS_URGENCIA: list[str] = list(MULTIPLICADOR_URGENCIA.keys())