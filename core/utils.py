# -*- coding: utf-8 -*-

import locale
from datetime import datetime, date

# Flag para garantir que o locale seja configurado apenas uma vez
_locale_configurado = False

def configurar_locale_brasileiro():
    """Tenta configurar o locale para pt_BR.UTF-8 ou similar."""
    global _locale_configurado
    if _locale_configurado:
        return

    locales_tentativa = ['pt_BR.UTF-8', 'pt_BR.utf8', 'Portuguese_Brazil.1252', 'pt_BR', '']
    for loc in locales_tentativa:
        try:
            locale.setlocale(locale.LC_ALL, loc)
            print(f"Locale configurado para '{locale.getlocale(locale.LC_ALL)[0]}'.")
            _locale_configurado = True
            return # Sucesso, sair da função
        except locale.Error:
            continue # Tentar próximo locale
    print(f"Aviso: Não foi possível configurar um locale pt_BR. Usando locale padrão do sistema: '{locale.getlocale(locale.LC_ALL)[0]}'. A formatação de moeda pode variar.")
    _locale_configurado = True # Marcar como configurado mesmo com fallback

def formatar_moeda(valor: float | int | None) -> str:
    """Formata um valor numérico como moeda brasileira (R$)."""
    if valor is None:
        return "N/A"
    configurar_locale_brasileiro() # Garante que o locale está configurado
    try:
        # Usa a formatação do locale se possível
        return locale.currency(valor, grouping=True, symbol=True)
    except (ValueError, locale.Error):
        # Fallback manual simples se o locale falhar
        try:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (TypeError, ValueError):
            return "Inválido" # Se o valor não for numérico

def formatar_numero(valor: float | int | None, casas_decimais: int = 2) -> str:
    """Formata um número com separador de milhar brasileiro."""
    if valor is None:
        return "N/A"
    configurar_locale_brasileiro() # Garante que o locale está configurado
    try:
        # Usa a formatação do locale se possível
        return locale.format_string(f"%.{casas_decimais}f", valor, grouping=True)
    except (ValueError, locale.Error, OverflowError):
         # Fallback manual simples
        try:
            return f"{valor:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (TypeError, ValueError):
            return "Inválido"

def calcular_anos_desde(data_evento: date | None) -> float:
    """Calcula a diferença em anos fracionados entre uma data e hoje."""
    if not data_evento or not isinstance(data_evento, date):
        return 0.0
    hoje = date.today()
    if data_evento > hoje: # Não calcula para datas futuras
        return 0.0
    delta = hoje - data_evento
    # Usar 365.2425 para média mais precisa (ano tropical médio)
    return delta.days / 365.2425

def parse_data(data_str: str | None) -> date | None:
    """
    Converte string (DD/MM/AAAA, DD-MM-AAAA, YYYY-MM-DD, etc.) para objeto date.
    Retorna None se a string for vazia, None ou o formato for inválido.
    """
    if not data_str:
        return None

    # Formatos comuns a tentar
    formatos_tentativa = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d%m%Y"]

    for fmt in formatos_tentativa:
        try:
            # Tenta fazer o parse
            dt_obj = datetime.strptime(data_str.strip(), fmt)
            # Validação extra: verifica se a data é razoável (ex: não ano 10000)
            if dt_obj.year > date.today().year + 1 or dt_obj.year < 1900:
                 continue # Ignora datas muito no futuro ou muito antigas
            return dt_obj.date()
        except (ValueError, TypeError):
            continue # Tenta o próximo formato

    # Se nenhum formato funcionou
    return None

# Chama a configuração do locale na primeira importação deste módulo
configurar_locale_brasileiro()