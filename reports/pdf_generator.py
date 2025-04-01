# -*- coding: utf-8 -*-

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import cm
from reportlab.lib.colors import navy, gray, black, darkblue
from datetime import datetime, date

# Importa utils e constants do core
from core.utils import formatar_moeda, formatar_numero
from core import constants # Necessário para exibir o percentual padrão de êxito

def gerar_pdf_simulacao(nome_arquivo: str, dados_input: dict, calculos: dict):
    """Gera um PDF com os resultados da simulação."""

    try:
        doc = SimpleDocTemplate(nome_arquivo, pagesize=(21*cm, 29.7*cm), # A4
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm,
                                title=f"Simulação Honorários - {dados_input.get('nome_advogado', 'Advogado')}",
                                author="Simulador de Honorários")
        styles = getSampleStyleSheet()
        story = []

        # --- Estilos Customizados ---
        style_titulo = ParagraphStyle(name='TituloPrincipal', parent=styles['h1'], alignment=TA_CENTER, textColor=darkblue, fontSize=18, spaceAfter=0.6*cm)
        style_subtitulo = ParagraphStyle(name='Subtitulo', parent=styles['h2'], textColor=navy, fontSize=14, spaceBefore=0.8*cm, spaceAfter=0.4*cm)
        style_normal = ParagraphStyle(name='NormalPDF', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_JUSTIFY)
        style_label_valor = ParagraphStyle(name='LabelValor', parent=styles['Normal'], fontSize=10, leading=14) # Para Label: Valor
        style_destaque = ParagraphStyle(name='Destaque', parent=styles['h3'], fontSize=11, textColor=black, spaceBefore=0.4*cm, spaceAfter=0.2*cm, alignment=TA_LEFT, fontName='Helvetica-Bold')
        style_final_preco = ParagraphStyle(name='PrecoFinal', parent=styles['h2'], alignment=TA_CENTER, fontSize=15, textColor=darkblue, spaceBefore=0.8*cm, spaceAfter=0.5*cm, fontName='Helvetica-Bold')
        style_obs = ParagraphStyle(name='Observacoes', parent=styles['Italic'], fontSize=9, textColor=gray, spaceBefore=1.5*cm, alignment=TA_JUSTIFY, leading=12)

        # --- Conteúdo do PDF ---
        story.append(Paragraph("Simulador de Honorários Advocatícios", style_titulo))
        story.append(Paragraph(f"Relatório Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        nome_adv = dados_input.get('nome_advogado')
        if nome_adv:
            story.append(Paragraph(f"Advogado(a): {nome_adv}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # --- Função Auxiliar para adicionar linhas Label: Valor ---
        def add_info(label, valor, format_func=None, unit=""):
             valor_str = "N/A"
             if isinstance(valor, date):
                 valor_str = valor.strftime('%d/%m/%Y')
             elif isinstance(valor, list) and all(isinstance(item, date) for item in valor):
                 valor_str = ", ".join([d.strftime('%d/%m/%Y') for d in valor]) if valor else "Nenhuma"
             elif format_func:
                 valor_str = format_func(valor)
             elif valor is not None:
                  valor_str = str(valor)

             story.append(Paragraph(f"<b>{label}:</b> {valor_str}{unit}", style_label_valor))


        # --- Dados de Entrada Consolidados ---
        story.append(Paragraph("Dados Informados na Simulação", style_subtitulo))
        # Usar KeepTogether para tentar manter seções juntas na página
        entrada_section = []
        entrada_section.append(Paragraph("<u>Formação e Experiência:</u>", style_destaque))
        add_info("Data Graduação Direito", dados_input.get('data_graduacao'))
        add_info("Data Inscrição OAB", dados_input.get('data_oab'))
        add_info("Datas Pós-Graduações", dados_input.get('datas_pos_graduacao', []))
        entrada_section.append(Spacer(1, 0.2*cm))
        add_info("Total Ações Atuadas", dados_input.get('total_acoes_defendidas'), lambda v: formatar_numero(v, 0))
        total_ganhas = sum(dados_input.get(key, 0) for key in dados_input if key.startswith('acoes_ganhas_'))
        add_info("Total Ações Ganhas (Informado)", total_ganhas, lambda v: formatar_numero(v, 0))
        # Opcional: Detalhar ações ganhas por área
        # for area in constants.AREAS_ATUACAO:
        #    key = f'acoes_ganhas_{area.lower().replace("-","").replace(" ","_")}'
        #    if key in dados_input and dados_input[key] > 0:
        #         add_info(f"  - Ganhas {area}", dados_input[key], lambda v: formatar_numero(v, 0))
        entrada_section.append(Spacer(1, 0.2*cm))
        add_info("Gasto Estimado Educação", dados_input.get('gastos_educacao'), formatar_moeda)
        add_info("Horas Estimadas FDS/Feriados (Carreira)", dados_input.get('horas_trabalhadas_fds_total'), lambda v: formatar_numero(v, 0))
        entrada_section.append(Spacer(1, 0.4*cm))

        entrada_section.append(Paragraph("<u>Dados do Serviço Específico:</u>", style_destaque))
        add_info("Área Serviço Atual", dados_input.get('area_servico_atual'))
        add_info("Horas Estimadas Totais (Esforço)", dados_input.get('horas_estimadas_servico'), lambda v: formatar_numero(v, 1), unit=" h")
        add_info("Complexidade Serviço", dados_input.get('nivel_complexidade_servico'))
        add_info("Urgência Serviço", dados_input.get('nivel_urgencia_servico'))
        entrada_section.append(Spacer(1, 0.2*cm))
        add_info("Valor Estimado da Causa (Recebimento Cliente)", dados_input.get('valor_estimado_causa_ganha', 0.0), formatar_moeda)
        add_info("Taxa Horária Base Mínima (p/ Cálculo Horário)", dados_input.get('taxa_horaria_base_minima'), formatar_moeda)

        story.append(KeepTogether(entrada_section))

        # --- Detalhes do Cálculo da Taxa Horária (Modelo Horário) ---
        story.append(PageBreak())
        story.append(Paragraph("Cálculo da Taxa Horária Sugerida (Base Horária)", style_subtitulo))
        detalhes_taxa = calculos.get('detalhes_taxa_horaria', {})
        taxa_section = []
        taxa_section.append(Paragraph("<u>Componentes do Cálculo:</u>", style_destaque))
        add_info("Taxa Horária Base Informada", detalhes_taxa.get('Taxa Horária Base Informada'), formatar_moeda)
        taxa_section.append(Spacer(1, 0.3*cm))
        taxa_section.append(Paragraph("Fatores Multiplicadores Aplicados:", style_label_valor))
        fatores = detalhes_taxa.get('Fatores Multiplicadores', {})
        for nome, valor in fatores.items():
            # Indentar os fatores
            p = Paragraph(f"    - {nome}: {formatar_numero(valor, 3)}x", style_label_valor)
            taxa_section.append(p)

        taxa_section.append(Spacer(1, 0.6*cm))
        taxa_horaria_final_fmt = formatar_moeda(calculos.get('taxa_horaria_sugerida'))
        taxa_section.append(Paragraph(f"<b>Taxa Horária Sugerida Calculada: {taxa_horaria_final_fmt}</b>", style_destaque))
        story.append(KeepTogether(taxa_section))

        # --- Cálculo do Preço Final (Modelo Horário) ---
        story.append(Paragraph("Cálculo do Preço Final (Base Horária)", style_subtitulo))
        detalhes_preco_horario = calculos.get('detalhes_preco_horario', {})
        preco_h_section = []
        preco_h_section.append(Paragraph("<u>Componentes do Cálculo:</u>", style_destaque))
        add_info("Taxa Horária Utilizada", detalhes_preco_horario.get('Taxa Horária Utilizada'), formatar_moeda)
        add_info("Horas Estimadas (Esforço)", detalhes_preco_horario.get('Horas Estimadas'), lambda v: formatar_numero(v, 1), unit=" h")
        add_info("Fator Complexidade", f"{detalhes_preco_horario.get('Nível de Complexidade')} ({formatar_numero(detalhes_preco_horario.get('Fator Complexidade'),2)}x)")
        add_info("Fator Urgência", f"{detalhes_preco_horario.get('Nível de Urgência')} ({formatar_numero(detalhes_preco_horario.get('Fator Urgência'),2)}x)")
        preco_h_section.append(Spacer(1, 0.3*cm))
        add_info("Preço Base (Taxa * Horas)", detalhes_preco_horario.get('Preço Base (Taxa * Horas)'), formatar_moeda)

        preco_h_section.append(Spacer(1, 0.5*cm))
        preco_final_horario_fmt = formatar_moeda(calculos.get('preco_horario_sugerido'))
        preco_h_section.append(Paragraph(f"Preço Final Sugerido (Base Horária): {preco_final_horario_fmt}", style_final_preco))
        story.append(KeepTogether(preco_h_section))


        # --- Cálculo por Êxito (Se aplicável) ---
        detalhes_preco_exito = calculos.get('detalhes_preco_exito', {})
        preco_exito_sugerido = calculos.get('preco_exito_sugerido')

        if preco_exito_sugerido is not None and preco_exito_sugerido > 0:
            story.append(PageBreak())
            story.append(Paragraph("Cálculo do Preço (Base Êxito - Estimativa)", style_subtitulo))
            preco_e_section = []
            preco_e_section.append(Paragraph("<u>Componentes do Cálculo:</u>", style_destaque))

            valor_causa_fmt = formatar_moeda(detalhes_preco_exito.get('Valor Estimado Causa Cliente'))
            percentual_aplicado = detalhes_preco_exito.get('Percentual Êxito Aplicado', constants.PERCENTUAL_EXITO_PADRAO) # Pega o aplicado ou o padrão
            percentual_fmt = f"{percentual_aplicado:.1%}"
            percentual_const_fmt = f"{constants.PERCENTUAL_EXITO_PADRAO:.0%}" # Para mostrar o padrão usado

            add_info("Valor Estimado da Causa (Recebimento Cliente)", valor_causa_fmt)
            add_info(f"Percentual de Êxito Aplicado ({percentual_const_fmt} padrão)", percentual_fmt)

            preco_e_section.append(Spacer(1, 0.5*cm))
            preco_final_exito_fmt = formatar_moeda(preco_exito_sugerido)
            preco_e_section.append(Paragraph(f"Preço Sugerido (Base Êxito): {preco_final_exito_fmt}", style_final_preco))
            story.append(KeepTogether(preco_e_section))


        # --- Observações Finais ---
        # Adiciona espaço antes das observações, a menos que seja a última coisa na página anterior
        if preco_exito_sugerido is None or preco_exito_sugerido <= 0:
             story.append(Spacer(1, 3*cm)) # Mais espaço se não houve cálculo de êxito
        else:
             story.append(Spacer(1, 1*cm))

        story.append(Paragraph("Observações Importantes:", style_obs))
        obs_text = """
        - Os valores apresentados são <b>SUGESTÕES</b> calculadas com base nos dados fornecidos e nos parâmetros definidos em <i>core/constants.py</i>.
        - O modelo de 'Base Horária' reflete o esforço estimado (horas) multiplicado por uma taxa horária valorizada pela experiência, especialização e outros fatores.
        - O modelo de 'Base Êxito' (se aplicável) reflete um percentual padrão sobre o ganho estimado do cliente, comum em certas áreas (ex: previdenciária, trabalhista, cível).
        - A escolha final do modelo de cobrança (horário, êxito, misto, fixo) e o valor dependem da análise de mercado, do tipo de serviço, do valor percebido pelo cliente, do acordo contratual e da estratégia do escritório.
        - A valoração de fatores intangíveis (experiência, sucesso) é inerentemente subjetiva. Ajuste os pesos e parâmetros no código para refletir sua realidade.
        - Este simulador é uma ferramenta de apoio à decisão e não substitui o julgamento profissional, a análise de risco e a negociação com o cliente.
        """
        story.append(Paragraph(obs_text, style_obs))

        # --- Construção do PDF ---
        doc.build(story)
        print(f"\nPDF gerado com sucesso: {nome_arquivo}")

    except ImportError as ie:
         print(f"\nErro de Importação ao gerar PDF: {ie}. Verifique as dependências (reportlab) e a estrutura do projeto.")
         # Poderia lançar a exceção para ser pega pela GUI, ou retornar False
         raise # Re-lança a exceção para a GUI tratar

    except Exception as e:
        print(f"\nErro inesperado ao gerar PDF: {type(e).__name__}: {e}")
        # Re-lança a exceção para a GUI tratar
        raise