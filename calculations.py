# calculations.py
from datetime import timedelta
import math
import pandas as pd # Mantido para a função gerar_evolucao, embora ela não retorne DataFrame diretamente

def calcular_rendimento_pos_fixado(valor_inicial, taxa_aplicacao_cdi, prazo_dias_uteis, taxa_cdi_anual, isenta_ir=False, prazo_dias_corridos_para_ir=None):
    """
    Calcula o rendimento líquido de aplicações PÓS-FIXADAS (CDI).
    """
    taxa_cdi_anual_decimal = taxa_cdi_anual / 100
    
    # Consideração: idealmente, a validação de input numérico deve ser feita na UI.
    # Mas, mantendo a função como estava por enquanto para evitar quebrar.
    if taxa_cdi_anual_decimal <= -1:
        # Se você quiser que esta função seja pura e não imprima erros de UI,
        # você deve retornar um status ou levantar uma exceção aqui.
        # Por enquanto, estou mantendo o erro direto se esta função for chamada sem validação prévia.
        # st.error("A taxa CDI anual não pode ser menor ou igual a -100%. Por favor, insira um valor válido.")
        # Retornar valores que indiquem erro para o chamador tratar.
        return 0, 0, 0, 0 # Exemplo de retorno para erro

    taxa_cdi_diaria = (1 + taxa_cdi_anual_decimal)**(1/252) - 1
    
    taxa_aplicacao_diaria = taxa_aplicacao_cdi / 100 * taxa_cdi_diaria
    
    if prazo_dias_uteis <= 0:
        return valor_inicial, 0, 0, 0
        
    valor_final_bruto = valor_inicial * (1 + taxa_aplicacao_diaria)**prazo_dias_uteis
    rendimento_bruto = valor_final_bruto - valor_inicial

    if isenta_ir:
        rendimento_liquido = rendimento_bruto
        valor_final_liquido = valor_final_bruto
        return valor_final_liquido, rendimento_liquido, 0, 0 # Retorna 0 para imposto e alíquota de IR

    else:
        # A alíquota do IR é baseada nos dias corridos
        if prazo_dias_corridos_para_ir is None:
            prazo_dias_corridos_estimado = int(prazo_dias_uteis / 0.7) if prazo_dias_uteis > 0 else 0
        else:
            prazo_dias_corridos_estimado = prazo_dias_corridos_para_ir

        if prazo_dias_corridos_estimado <= 180:
            aliquota_ir = 0.225
        elif prazo_dias_corridos_estimado <= 360:
            aliquota_ir = 0.20
        elif prazo_dias_corridos_estimado <= 720:
            aliquota_ir = 0.175
        else:
            aliquota_ir = 0.15

        imposto_renda = rendimento_bruto * aliquota_ir
        rendimento_liquido = rendimento_bruto - imposto_renda
        valor_final_liquido = valor_inicial + rendimento_liquido
        return valor_final_liquido, rendimento_liquido, aliquota_ir, imposto_renda

def calcular_rendimento_prefixado(valor_inicial, taxa_anual_prefixada, dias_corridos_totais):
    """
    Calcula o rendimento líquido de aplicações PRÉ-FIXADAS.
    """
    taxa_anual_decimal = taxa_anual_prefixada / 100
    
    if dias_corridos_totais <= 0:
        return valor_inicial, 0, 0, 0

    # Cálculo do valor bruto: (1 + taxa_anual)^(dias_corridos / 365)
    valor_final_bruto = valor_inicial * (1 + taxa_anual_decimal)**(dias_corridos_totais / 365)
    rendimento_bruto = valor_final_bruto - valor_inicial

    # Determinação da alíquota de IR (baseada em dias corridos)
    if dias_corridos_totais <= 180:
        aliquota_ir = 0.225
    elif dias_corridos_totais <= 360:
        aliquota_ir = 0.20
    elif dias_corridos_totais <= 720:
        aliquota_ir = 0.175
    else:
        aliquota_ir = 0.15

    imposto_renda = rendimento_bruto * aliquota_ir
    rendimento_liquido = rendimento_bruto - imposto_renda
    valor_final_liquido = valor_inicial + rendimento_liquido
    return valor_final_liquido, rendimento_liquido, aliquota_ir, imposto_renda

def gerar_evolucao_pos_fixada(valor_inicial, taxa_aplicacao_cdi, taxa_cdi_anual, data_inicio, data_fim, isenta_ir, nome_aplicacao):
    """
    Gera a evolução diária do patrimônio para aplicações PÓS-FIXADAS.
    Retorna uma lista de dicionários.
    """
    evolucao_dados = []
    
    delta = timedelta(days=1)
    current_date = data_inicio
    
    # Adicionar o valor inicial no dia de início
    evolucao_dados.append({
        'Data': data_inicio,
        'Aplicação': nome_aplicacao,
        'Valor Líquido': valor_inicial
    })

    # Itera dia a dia até a data de vencimento
    while current_date <= data_fim:
        dias_corridos_acumulados = (current_date - data_inicio).days
        
        dias_uteis_acumulados = math.ceil(dias_corridos_acumulados * 0.7) if dias_corridos_acumulados > 0 else 1

        valor_liquido_no_dia, _, _, _ = calcular_rendimento_pos_fixado(
            valor_inicial, 
            taxa_aplicacao_cdi, 
            dias_uteis_acumulados, 
            taxa_cdi_anual, 
            isenta_ir=isenta_ir,
            prazo_dias_corridos_para_ir=dias_corridos_acumulados
        )
        evolucao_dados.append({
            'Data': current_date,
            'Aplicação': nome_aplicacao,
            'Valor Líquido': valor_liquido_no_dia
        })
        current_date += delta
    return evolucao_dados

def gerar_evolucao_prefixada(valor_inicial, taxa_anual_prefixada, data_inicio, data_fim, nome_aplicacao):
    """
    Gera a evolução diária do patrimônio para aplicações PRÉ-FIXADAS.
    Retorna uma lista de dicionários.
    """
    evolucao_dados = []
    
    delta = timedelta(days=1)
    current_date = data_inicio
    
    # Adicionar o valor inicial no dia de início
    evolucao_dados.append({
        'Data': data_inicio,
        'Aplicação': nome_aplicacao,
        'Valor Líquido': valor_inicial
    })

    # Itera dia a dia até a data de vencimento
    while current_date <= data_fim:
        dias_corridos_acumulados = (current_date - data_inicio).days
        
        valor_liquido_no_dia, _, _, _ = calcular_rendimento_prefixado(
            valor_inicial, 
            taxa_anual_prefixada, 
            dias_corridos_acumulados
        )
        evolucao_dados.append({
            'Data': current_date,
            'Aplicação': nome_aplicacao,
            'Valor Líquido': valor_liquido_no_dia
        })
        current_date += delta
    return evolucao_dados