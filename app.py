# app.py
import streamlit as st
import math
import pandas as pd
from datetime import date, timedelta

# Importar as funções dos módulos
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
from landing_page import render_landing_page # A função da landing page

# --- FUNÇÃO PARA SEO E ANALYTICS ---
def add_seo_tags():
    """Adiciona meta tags de SEO e script do Google Analytics."""
    # Defina as tags que você quer injetar
    meta_tags = """
        <meta name="keywords" content="renda fixa, cdb, lca, lci, poupança, cdi, comparação de investimentos, lince safra">
        <meta name="description" content="Ferramenta de comparação de rendimentos de aplicações de Renda Fixa Pós-fixadas e Pré-fixadas.">
    """
    
    # Injeta o código do Google Analytics se o ID for encontrado
    if "GA_MEASUREMENT_ID" in st.secrets:
        ga_id = st.secrets["GA_MEASUREMENT_ID"]
        ga_script = f"""
            <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
            <script>
              window.dataLayer = window.dataLayer || [];
              function gtag(){{dataLayer.push(arguments);}}
              gtag('js', new Date());
              gtag('config', '{ga_id}');
            </script>
        """
        st.markdown(ga_script, unsafe_allow_html=True)
    
    # Injeta as meta tags de SEO no HTML da página
    st.markdown(meta_tags, unsafe_allow_html=True)

# --- CONFIGURAÇÕES INICIAIS (DEVE SER SEMPRE O PRIMEIRO CÓDIGO STREAMLIT) ---
st.set_page_config(
    page_title="Comparador de Renda Fixa",
    page_icon="💰", 
    layout="centered"
)

# --- Lógica de Controle: Exibir Landing Page ou o Aplicativo ---
if 'is_authenticated' not in st.session_state or not st.session_state.is_authenticated:
    # Chama a função para adicionar as tags de SEO na landing page
    add_seo_tags()
    render_landing_page()
else:
    # A partir daqui, a aplicação principal é renderizada
    
    # Chama a função para adicionar as tags de SEO (também na página principal)
    add_seo_tags()
    
    # --- Restante do código da aplicação principal ---
    apply_custom_css()
    
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

        datas_validas = True
        if data_vencimento_tributada <= hoje or data_vencimento_isenta <= hoje:
            st.error("Por favor, selecione datas de vencimento futuras para as aplicações pós-fixadas.")
            datas_validas = False
        if enable_prefixada and data_vencimento_prefixada <= hoje:
            st.error("Por favor, selecione uma data de vencimento futura para a aplicação pré-fixada.")
            datas_validas = False

        if datas_validas:
            # --- Cálculos e lógicas (mantido do seu código original) ---
            # ...
            # --- Cálculos para o PRAZO TOTAL ---
            dias_corridos_tributada_full = (data_vencimento_tributada - hoje).days
            dias_uteis_estimados_tributada_full = math.ceil(dias_corridos_tributada_full * 0.7)
            if dias_uteis_estimados_tributada_full <= 0: dias_uteis_estimados_tributada_full = 1

            valor_final_tributada_full, rendimento_liquido_tributada_full, aliquota_ir_tributada_full, imposto_renda_tributada_full = calcular_rendimento_pos_fixado(
                valor_aplicar, taxa_aplicacao_tributada_cdi, dias_uteis_estimados_tributada_full, taxa_cdi_anual_atual, isenta_ir=False
            )

            dias_corridos_isenta_full = (data_vencimento_isenta - hoje).days
            dias_uteis_estimados_isenta_full = math.ceil(dias_corridos_isenta_full * 0.7)
            if dias_uteis_estimados_isenta_full <= 0: dias_uteis_estimados_isenta_full = 1

            valor_final_isenta_full, rendimento_liquido_isenta_full, _, _ = calcular_rendimento_pos_fixado(
                valor_aplicar, taxa_aplicacao_isenta_cdi, dias_uteis_estimados_isenta_full, taxa_cdi_anual_atual, isenta_ir=True
            )

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