# landing_page.py
from datetime import datetime
import streamlit as st
import gspread

   
def save_to_google_sheets(nome, phone):
    """
    Função para salvar e-mail e telefone no Google Sheets.
    As credenciais são carregadas do `st.secrets`.
    """
    try:
        service_account_info = st.secrets["gcp_service_account"]
        gc = gspread.service_account_from_dict(service_account_info)
        
        # AQUI ESTÁ O NOME DA PLANILHA CORRIGIDO
        worksheet = gc.open("Leads_Ferramenta").sheet1
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_to_add = [nome, phone, timestamp]
        
        worksheet.append_row(row_to_add)
        
        return True
    except Exception as e:
        st.error(f"Ocorreu um erro ao salvar seus dados. Erro: {e}")
        return False

def render_landing_page():
    """
    Renderiza a landing page com o formulário de cadastro.
    """
    #st.set_page_config(page_title="Leads_Ferramenta", layout="centered")

    # Layout com colunas para centralizar a imagem e o conteúdo
    #col_left, col_center, col_right = st.columns([0.25, 0.5, 0.25])
    #with col_center:
    #    st.image("https://linceinvest.com.br/wp-content/uploads/2024/03/Agrupar-1-1-2048x393.png", use_container_width=True)

    st.title("💰 Comparador de Renda Fixa!")
    st.markdown("Informe seu nome e telefone para acessar o simulador:")
        
    with st.form(key='lead_form'):
        nome = st.text_input("Seu nome:")
        # --- AJUSTE: Adicionando um placeholder para a máscara de telefone ---
        phone = st.text_input("Seu telefone celular:", placeholder="(99) 99999-9999")
        # --------------------------------------------------------------------
        submit_button = st.form_submit_button(label='Acessar Ferramenta')

    if submit_button:
        # --- AJUSTE: Validação e mensagem de erro mais amigável ---
        if not nome or not phone:
            st.error("A ferramenta é absolutamente gratuita. Peço só seu nome e telefone para eu te conhecer melhor ;-)")
        else:
            # --- AJUSTE: Adicionando um spinner de loading ---
            with st.spinner("Salvando seus dados... Aguarde um momento."):
                if save_to_google_sheets(nome, phone):
                    st.success("Prontinho! Você será redirecionado para a ferramenta automaticamente.")
                    # A função save_to_google_sheets agora apenas retorna True/False
                    
                    # A mensagem de sucesso é mostrada aqui
                    st.session_state.is_authenticated = True
                    st.rerun() # Reinicia a aplicação para mostrar o conteúdo principal
            # ---------------------------------------------------------