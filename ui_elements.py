# ui_elements.py
import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.express as px

# Importar as funções de cálculo necessárias
from calculations import (
    calcular_rendimento_pos_fixado, 
    calcular_rendimento_prefixado,
    gerar_evolucao_pos_fixada,
    gerar_evolucao_prefixada
)

def apply_custom_css():
    """Aplica estilos CSS personalizados para o layout do Streamlit."""
    st.markdown(
        """
        <style>
        /* Ajusta o padding do elemento principal para reduzir o espaço no topo */
        .stApp {
            padding-top: 10px; /* Reduz o padding superior. Ajuste conforme necessário */
        }
        /* Centraliza os elementos na coluna para o logo */
        .st-emotion-cache-nahz7x { /* Esta classe pode mudar com atualizações do Streamlit */
            display: flex;
            justify-content: center;
            align-items: center;
        }
        /* Estilo para a linha divisória */
        .divider {
            margin-top: 10px;
            margin-bottom: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1); /* Cor da linha mais sutil com fundo escuro */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_logo_and_separator():
    """Renderiza o logo da empresa e uma linha separadora."""
    col_left, col_center, col_right = st.columns([0.33, 0.66, 0.33])
    with col_center:
        st.image("https://linceinvest.com.br/wp-content/uploads/2024/03/Agrupar-1-1-2048x393.png", use_container_width=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)


def render_main_title_and_intro():
    """Renderiza o título principal e a introdução."""
    st.title("💰 Comparador de Renda Fixa")
    st.markdown("Compare o rendimento líquido de aplicações tributadas (IR regressivo) e isentas (LCI, LCA, CRI, CRA).")

def render_input_forms():
    """
    Renderiza os formulários de entrada de dados e retorna os valores inseridos pelo usuário.
    """
    st.header("Dados da Aplicação")

    valor_aplicar = st.number_input(
        "Valor a ser aplicado (R$)", 
        min_value=1.0, 
        value=10000.00, 
        step=100.0, 
        format="%.2f",
        key="valor_aplicar_input"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Aplicação Pós-Fixada Tributada")
        taxa_aplicacao_tributada_cdi = st.slider(
            "Taxa (% do CDI)", 
            min_value=80, 
            max_value=130, 
            value=100, 
            step=1,
            key="taxa_tributada_slider"
        )
        data_vencimento_tributada = st.date_input(
            "Data de Vencimento", 
            date.today() + timedelta(days=365),
            min_value=date.today(),
            format="DD/MM/YYYY",
            key="data_vencimento_tributada_input"
        )

    with col2:
        st.subheader("Aplicação Pós-Fixada Isenta")
        taxa_aplicacao_isenta_cdi = st.slider(
            "Taxa (% do CDI)", 
            min_value=70, 
            max_value=120, 
            value=95, 
            step=1,
            key="taxa_isenta_slider"
        )
        data_vencimento_isenta = st.date_input(
            "Data de Vencimento", 
            date.today() + timedelta(days=365),
            min_value=date.today(),
            format="DD/MM/YYYY",
            key="data_vencimento_isenta_input"
        )

    st.markdown("---")
    st.subheader("Aplicação Pré-Fixada (Opcional)")
    enable_prefixada = st.checkbox("Incluir Aplicação Pré-Fixada na Comparação", value=False)

    taxa_aplicacao_prefixada_anual = 0.0
    data_vencimento_prefixada = None

    if enable_prefixada:
        taxa_aplicacao_prefixada_anual = st.number_input(
            "Taxa Anual Acordada (% a.a.)",
            min_value=0.01,
            value=15.00,
            step=0.01,
            format="%.2f",
            key="taxa_prefixada_input"
        )
        data_vencimento_prefixada = st.date_input(
            "Data de Vencimento Pré-Fixada",
            date.today() + timedelta(days=365),
            min_value=date.today(),
            format="DD/MM/YYYY",
            key="data_vencimento_prefixada_input"
        )

    st.markdown("---")
    st.subheader("Parâmetros Gerais")
    taxa_cdi_anual_atual = st.number_input(
        "Taxa do CDI anual atual (%)", 
        min_value=0.01, 
        value=14.90,
        step=0.01, 
        format="%.2f",
        key="taxa_cdi_anual_input"
    )
    
    return (
        valor_aplicar, 
        taxa_aplicacao_tributada_cdi, 
        data_vencimento_tributada, 
        taxa_aplicacao_isenta_cdi, 
        data_vencimento_isenta,
        enable_prefixada,
        taxa_aplicacao_prefixada_anual,
        data_vencimento_prefixada,
        taxa_cdi_anual_atual
    )

def render_results_summary(valor_aplicar, taxa_cdi_anual_atual):
    """Renderiza o resumo dos dados de entrada."""
    st.subheader("Resultados da Comparação")
    st.markdown(f"**Valor a ser aplicado:** R$ {valor_aplicar:,.2f}")
    st.markdown(f"**CDI anual atual:** {taxa_cdi_anual_atual:.2f}%")
    st.markdown("---")

def render_conclusion(rendimentos_full, enable_prefixada):
    """Renderiza a conclusão principal baseada nos prazos originais."""
    st.subheader("Conclusão (Considerando Prazos Originais)")
    if rendimentos_full:
        melhor_aplicacao_full = max(rendimentos_full, key=rendimentos_full.get)
        melhor_rendimento_full = rendimentos_full[melhor_aplicacao_full]
        st.success(f"A **{melhor_aplicacao_full}** é a mais vantajosa, com um rendimento líquido de **R$ {melhor_rendimento_full:,.2f}**, considerando seus prazos originais.")
    else:
        st.info("Nenhuma aplicação selecionada para comparação.")
    st.markdown("---")

def render_rentability_chart(rendimentos_data, title, cores_aplicacoes):
    """Renderiza um gráfico de barras de rentabilidade líquida."""
    st.subheader(title)
    df_rentabilidade = pd.DataFrame(rendimentos_data)
    fig = px.bar(
        df_rentabilidade, 
        x='Aplicação', 
        y='Rendimento Líquido (R$)', 
        title=title,
        text='Rendimento Líquido (R$)',
        color='Aplicação',
        color_discrete_map=cores_aplicacoes 
    )
    fig.update_traces(texttemplate='R$ %{y:,.2f}', textposition='outside')
    fig.update_layout(yaxis_title="Rendimento Líquido (R$)", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

def render_evolution_chart(df_evolucao, cores_aplicacoes):
    """Renderiza o gráfico de evolução do patrimônio ao longo do tempo."""
    st.subheader("📈 Evolução do Patrimônio ao Longo do Tempo")
    st.info("O 'salto' nas linhas de aplicações tributadas representa a redução da alíquota de Imposto de Renda ao cruzar marcos de tempo (180, 360, 720 dias).")
    fig_evolucao = px.line(
        df_evolucao, 
        x='Data', 
        y='Valor Líquido', 
        color='Aplicação', 
        title='Evolução do Valor Líquido das Aplicações',
        labels={'Valor Líquido': 'Valor Líquido (R$)', 'Data': 'Data'},
        color_discrete_map=cores_aplicacoes 
    )
    fig_evolucao.update_layout(hovermode="x unified")
    st.plotly_chart(fig_evolucao, use_container_width=True)
    st.markdown("---")

def render_comparative_conclusion(data_vencimento_comparativa, dias_uteis_comparativos, rendimentos_comp):
    """Renderiza a conclusão comparativa até o menor prazo."""
    st.subheader("Conclusão Comparativa (até o menor prazo)")
    st.markdown(f"Para uma comparação equivalente, todas as aplicações foram simuladas até a data de **{data_vencimento_comparativa.strftime('%d/%m/%Y')}** ({dias_uteis_comparativos} dias úteis estimados).")
    if rendimentos_comp:
        melhor_aplicacao_comp = max(rendimentos_comp, key=rendimentos_comp.get)
        melhor_rendimento_comp = rendimentos_comp[melhor_aplicacao_comp]
        st.success(f"Nesta simulação comparativa, a **{melhor_aplicacao_comp}** é a mais vantajosa, com um rendimento líquido de **R$ {melhor_rendimento_comp:,.2f}**.")
    else:
        st.info("Nenhuma aplicação selecionada para comparação equivalente.")
    st.markdown("---")

def render_detailed_sections(details_tributada, details_isenta, details_prefixada=None):
    """Renderiza os detalhamentos completos das aplicações."""
    st.subheader("Detalhamento Completo das Aplicações")

    st.markdown("### 📊 Detalhamento da Aplicação Pós-Fixada Tributada (Prazo Original)")
    st.markdown(f"**Taxa:** {details_tributada['taxa_aplicacao_cdi']:.2f}% do CDI")
    st.markdown(f"**Data de Vencimento:** {details_tributada['data_vencimento'].strftime('%d/%m/%Y')}")
    st.markdown(f"**Prazo total em dias corridos:** {details_tributada['dias_corridos']} dias")
    st.markdown(f"**Prazo estimado em dias úteis:** {details_tributada['dias_uteis']} dias")
    st.markdown(f"**Rendimento Bruto:** R$ {details_tributada['rendimento_bruto']:,.2f}")
    st.markdown(f"**Alíquota de IR aplicada:** {details_tributada['aliquota_ir'] * 100:.1f}%")
    st.markdown(f"**Imposto de Renda (IR):** R$ {details_tributada['imposto_renda']:,.2f}")
    st.markdown(f"**Valor Final Líquido:** R$ {details_tributada['valor_final_liquido']:,.2f}")
    st.markdown(f"**Rendimento Líquido:** R$ {details_tributada['rendimento_liquido']:,.2f}")
    st.markdown("---")

    st.markdown("### 📈 Detalhamento da Aplicação Pós-Fixada Isenta (Prazo Original)")
    st.markdown(f"**Taxa:** {details_isenta['taxa_aplicacao_cdi']:.2f}% do CDI")
    st.markdown(f"**Data de Vencimento:** {details_isenta['data_vencimento'].strftime('%d/%m/%Y')}")
    st.markdown(f"**Prazo total em dias corridos:** {details_isenta['dias_corridos']} dias")
    st.markdown(f"**Prazo estimado em dias úteis:** {details_isenta['dias_uteis']} dias")
    st.markdown(f"**Valor Final Líquido:** R$ {details_isenta['valor_final_liquido']:,.2f}")
    st.markdown(f"**Rendimento Líquido:** R$ {details_isenta['rendimento_liquido']:,.2f}")
    st.markdown("---")

    if details_prefixada:
        st.markdown("### 📊 Detalhamento da Aplicação Pré-Fixada (Prazo Original)")
        st.markdown(f"**Taxa Anual Acordada:** {details_prefixada['taxa_anual_prefixada']:.2f}% a.a.")
        st.markdown(f"**Data de Vencimento:** {details_prefixada['data_vencimento'].strftime('%d/%m/%Y')}")
        st.markdown(f"**Prazo total em dias corridos:** {details_prefixada['dias_corridos']} dias")
        st.markdown(f"**Rendimento Bruto:** R$ {details_prefixada['rendimento_bruto']:,.2f}")
        st.markdown(f"**Alíquota de IR aplicada:** {details_prefixada['aliquota_ir'] * 100:.1f}%")
        st.markdown(f"**Imposto de Renda (IR):** R$ {details_prefixada['imposto_renda']:,.2f}")
        st.markdown(f"**Valor Final Líquido:** R$ {details_prefixada['valor_final_liquido']:,.2f}")
        st.markdown(f"**Rendimento Líquido:** R$ {details_prefixada['rendimento_liquido']:,.2f}")
        st.markdown("---")

def render_footer():
    """Renderiza o rodapé com o aviso legal."""
    st.markdown("""
    <br>
    <small>*Lembre-se que este é um cálculo simulado e não substitui uma análise detalhada com um profissional de investimentos. A estimativa de dias úteis pode não ser exata devido a feriados variáveis.*</small>
    """, unsafe_allow_html=True)