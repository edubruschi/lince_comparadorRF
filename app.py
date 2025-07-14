# app.py
import streamlit as st
from datetime import date, timedelta
import math
import pandas as pd

# Importar as funções dos novos módulos
from calculations import (
    calcular_rendimento_pos_fixado, 
    calcular_rendimento_prefixado,
    gerar_evolucao_pos_fixada,
    gerar_evolucao_prefixada
)
from ui_elements import (
    apply_custom_css,
    render_logo_and_separator,
    render_main_title_and_intro,
    render_input_forms,
    render_results_summary,
    render_conclusion,
    render_rentability_chart,
    render_evolution_chart,
    render_comparative_conclusion,
    render_detailed_sections,
    render_footer
)

# --- Configuração Inicial e CSS ---
st.set_page_config(page_title="Comparador de Renda Fixa", layout="centered")
apply_custom_css()

# --- Renderização da Interface ---
render_logo_and_separator()
render_main_title_and_intro()

# Obtém as entradas do usuário
(
    valor_aplicar, 
    taxa_aplicacao_tributada_cdi, 
    data_vencimento_tributada, 
    taxa_aplicacao_isenta_cdi, 
    data_vencimento_isenta,
    enable_prefixada,
    taxa_aplicacao_prefixada_anual,
    data_vencimento_prefixada,
    taxa_cdi_anual_atual
) = render_input_forms()


# --- Processamento e Exibição de Resultados (após o botão) ---
if st.button("Comparar Aplicações", key="comparar_button"):
    hoje = date.today()

    # Validação das datas
    datas_validas = True
    if data_vencimento_tributada <= hoje or data_vencimento_isenta <= hoje:
        st.error("Por favor, selecione datas de vencimento futuras para as aplicações pós-fixadas.")
        datas_validas = False
    if enable_prefixada and data_vencimento_prefixada <= hoje:
        st.error("Por favor, selecione uma data de vencimento futura para a aplicação pré-fixada.")
        datas_validas = False

    if datas_validas:
        # --- Cálculos para o PRAZO TOTAL ---
        # Pós-Fixada Tributada
        dias_corridos_tributada_full = (data_vencimento_tributada - hoje).days
        dias_uteis_estimados_tributada_full = math.ceil(dias_corridos_tributada_full * 0.7)
        if dias_uteis_estimados_tributada_full <= 0: dias_uteis_estimados_tributada_full = 1

        valor_final_tributada_full, rendimento_liquido_tributada_full, aliquota_ir_tributada_full, imposto_renda_tributada_full = calcular_rendimento_pos_fixado(
            valor_aplicar, taxa_aplicacao_tributada_cdi, dias_uteis_estimados_tributada_full, taxa_cdi_anual_atual, isenta_ir=False
        )

        # Pós-Fixada Isenta
        dias_corridos_isenta_full = (data_vencimento_isenta - hoje).days
        dias_uteis_estimados_isenta_full = math.ceil(dias_corridos_isenta_full * 0.7)
        if dias_uteis_estimados_isenta_full <= 0: dias_uteis_estimados_isenta_full = 1

        valor_final_isenta_full, rendimento_liquido_isenta_full, _, _ = calcular_rendimento_pos_fixado(
            valor_aplicar, taxa_aplicacao_isenta_cdi, dias_uteis_estimados_isenta_full, taxa_cdi_anual_atual, isenta_ir=True
        )

        # Pré-Fixada (se habilitada)
        valor_final_prefixada_full = 0
        rendimento_liquido_prefixada_full = 0
        aliquota_ir_prefixada_full = 0
        imposto_renda_prefixada_full = 0
        dias_corridos_prefixada_full = 0

        if enable_prefixada:
            dias_corridos_prefixada_full = (data_vencimento_prefixada - hoje).days
            valor_final_prefixada_full, rendimento_liquido_prefixada_full, aliquota_ir_prefixada_full, imposto_renda_prefixada_full = calcular_rendimento_prefixado(
                valor_aplicar, taxa_aplicacao_prefixada_anual, dias_corridos_prefixada_full
            )

        # --- Identificar a data de vencimento mais curta para comparação ---
        datas_para_comparacao = [data_vencimento_tributada, data_vencimento_isenta]
        if enable_prefixada:
            datas_para_comparacao.append(data_vencimento_prefixada)
            
        data_vencimento_comparativa = min(datas_para_comparacao)
        dias_corridos_comparativos = (data_vencimento_comparativa - hoje).days
        dias_uteis_comparativos = math.ceil(dias_corridos_comparativos * 0.7)
        if dias_uteis_comparativos <= 0: dias_uteis_comparativos = 1 

        # --- Cálculos para a COMPARAÇÃO EQUIVALENTE (até a data mais curta) ---
        valor_final_tributada_comp, rendimento_liquido_tributada_comp, aliquota_ir_tributada_comp, _ = calcular_rendimento_pos_fixado(
            valor_aplicar, taxa_aplicacao_tributada_cdi, dias_uteis_comparativos, taxa_cdi_anual_atual, 
            isenta_ir=False, prazo_dias_corridos_para_ir=dias_corridos_comparativos
        )

        valor_final_isenta_comp, rendimento_liquido_isenta_comp, _, _ = calcular_rendimento_pos_fixado(
            valor_aplicar, taxa_aplicacao_isenta_cdi, dias_uteis_comparativos, taxa_cdi_anual_atual, 
            isenta_ir=True, prazo_dias_corridos_para_ir=dias_corridos_comparativos
        )
        
        valor_final_prefixada_comp = 0
        rendimento_liquido_prefixada_comp = 0
        aliquota_ir_prefixada_comp = 0
        if enable_prefixada:
            valor_final_prefixada_comp, rendimento_liquido_prefixada_comp, aliquota_ir_prefixada_comp, _ = calcular_rendimento_prefixado(
                valor_aplicar, taxa_aplicacao_prefixada_anual, dias_corridos_comparativos
            )

        # --- Dicionários para passar para as funções de UI ---
        cores_aplicacoes = {
            'Pós-Fixada Tributada': 'lightseagreen', 
            'Pós-Fixada Isenta': 'darkorange',
            'Pré-fixada': 'cornflowerblue' 
        }

        rendimentos_full = {
            "Pós-Fixada Tributada": rendimento_liquido_tributada_full,
            "Pós-Fixada Isenta": rendimento_liquido_isenta_full
        }
        if enable_prefixada:
            rendimentos_full["Pré-fixada"] = rendimento_liquido_prefixada_full

        rendimentos_comp = {
            "Pós-Fixada Tributada": rendimento_liquido_tributada_comp,
            "Pós-Fixada Isenta": rendimento_liquido_isenta_comp
        }
        if enable_prefixada:
            rendimentos_comp["Pré-fixada"] = rendimento_liquido_prefixada_comp

        # Dados para o gráfico de evolução
        dados_evolucao_list = []
        dados_evolucao_list.extend(gerar_evolucao_pos_fixada(
            valor_aplicar, taxa_aplicacao_tributada_cdi, taxa_cdi_anual_atual, hoje, data_vencimento_tributada, False, 'Pós-Fixada Tributada'
        ))
        dados_evolucao_list.extend(gerar_evolucao_pos_fixada(
            valor_aplicar, taxa_aplicacao_isenta_cdi, taxa_cdi_anual_atual, hoje, data_vencimento_isenta, True, 'Pós-Fixada Isenta'
        ))
        if enable_prefixada:
            dados_evolucao_list.extend(gerar_evolucao_prefixada(
                valor_aplicar, taxa_aplicacao_prefixada_anual, hoje, data_vencimento_prefixada, 'Pré-fixada'
            ))
        df_evolucao = pd.DataFrame(dados_evolucao_list)

        # Dados para detalhamento
        details_tributada = {
            'taxa_aplicacao_cdi': taxa_aplicacao_tributada_cdi,
            'data_vencimento': data_vencimento_tributada,
            'dias_corridos': dias_corridos_tributada_full,
            'dias_uteis': dias_uteis_estimados_tributada_full,
            'rendimento_bruto': rendimento_liquido_tributada_full + imposto_renda_tributada_full,
            'aliquota_ir': aliquota_ir_tributada_full,
            'imposto_renda': imposto_renda_tributada_full,
            'valor_final_liquido': valor_final_tributada_full,
            'rendimento_liquido': rendimento_liquido_tributada_full
        }
        details_isenta = {
            'taxa_aplicacao_cdi': taxa_aplicacao_isenta_cdi,
            'data_vencimento': data_vencimento_isenta,
            'dias_corridos': dias_corridos_isenta_full,
            'dias_uteis': dias_uteis_estimados_isenta_full,
            'valor_final_liquido': valor_final_isenta_full,
            'rendimento_liquido': rendimento_liquido_isenta_full
        }
        details_prefixada = None
        if enable_prefixada:
            details_prefixada = {
                'taxa_anual_prefixada': taxa_aplicacao_prefixada_anual,
                'data_vencimento': data_vencimento_prefixada,
                'dias_corridos': dias_corridos_prefixada_full,
                'rendimento_bruto': rendimento_liquido_prefixada_full + imposto_renda_prefixada_full,
                'aliquota_ir': aliquota_ir_prefixada_full,
                'imposto_renda': imposto_renda_prefixada_full,
                'valor_final_liquido': valor_final_prefixada_full,
                'rendimento_liquido': rendimento_liquido_prefixada_full
            }

        # --- Exibição dos resultados (chamando funções de ui_elements) ---
        render_results_summary(valor_aplicar, taxa_cdi_anual_atual)
        render_conclusion(rendimentos_full, enable_prefixada)
        render_rentability_chart(
            {
                'Aplicação': list(rendimentos_full.keys()), 
                'Rendimento Líquido (R$)': list(rendimentos_full.values())
            }, 
            'Rendimento Líquido Comparativo (Prazos Originais)', 
            cores_aplicacoes
        )
        render_evolution_chart(df_evolucao, cores_aplicacoes)
        render_comparative_conclusion(data_vencimento_comparativa, dias_uteis_comparativos, rendimentos_comp)
        render_rentability_chart(
            {
                'Aplicação': list(rendimentos_comp.keys()), 
                'Rendimento Líquido (R$)': list(rendimentos_comp.values())
            }, 
            f'Rendimento Líquido Comparativo (até {data_vencimento_comparativa.strftime("%d/%m/%Y")})', 
            cores_aplicacoes
        )
        render_detailed_sections(details_tributada, details_isenta, details_prefixada)

# --- Rodapé ---
render_footer()