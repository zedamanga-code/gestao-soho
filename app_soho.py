import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
from datetime import datetime
import io

# --- 1. CONFIGURAÇÕES (TROQUE APENAS O ID DA PASTA) ---
ID_PASTA_DRIVE = "1L1cpeSdaauhGlFE7e-qBzl6d4RaFWKJ7"
ID_PLANILHA = "12OAsmeEE9DcDbvLlQhI_Tw85UYTa6dk2Tn7YhN-sjs4"

# Função para autenticar
def get_gcp_creds():
    creds_dict = st.secrets["gcp_service_account"]
    return service_account.Credentials.from_service_account_info(creds_dict)

# --- 2. FUNÇÕES DE APOIO ---
def upload_para_drive(arquivo_pdf, nome_arquivo):
    try:
        creds = get_gcp_creds()
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': nome_arquivo, 'parents': [ID_PASTA_DRIVE]}
        media = MediaIoBaseUpload(io.BytesIO(arquivo_pdf.read()), mimetype='application/pdf', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Erro no Drive: {e}")
        return None

def salvar_na_planilha(dados):
    try:
        creds = get_gcp_creds()
        service = build('sheets', 'v4', credentials=creds)
        corpo = {'values': [dados]}
        service.spreadsheets().values().append(
            spreadsheetId=ID_PLANILHA,
            range="HISTORICO!A1",
            valueInputOption="USER_ENTERED",
            body=corpo
        ).execute()
        return True
    except Exception as e:
        st.error(f"Erro na Planilha: {e}")
        return False

# --- 3. INTERFACE ---
st.set_page_config(page_title="Soho Manutenção", page_icon="🏗️")
st.title("🏗️ Gestão Soho - Manutenção")

# Tentar carregar equipamentos da planilha
try:
    url_csv = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv"
    df_equip = pd.read_csv(url_csv)
    # Pega a coluna que contém as TAGS (ajuste se não for a primeira)
    lista_tags = df_equip.iloc[:, 0].dropna().unique().tolist()
except:
    lista_tags = ["Bomba de Recalque", "Gerador", "Piscina"]

equipamento = st.selectbox("Selecione o Equipamento:", lista_tags)
relato = st.text_area("Descreva o serviço realizado:")
arquivo_pdf = st.file_uploader("Anexe o Laudo em PDF", type=["pdf"])

if st.button("Finalizar e Registrar"):
    if relato and arquivo_pdf:
        with st.spinner('Salvando no sistema...'):
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            nome_arq = f"Laudo_{equipamento}_{datetime.now().strftime('%d%m%Y_%H%M')}.pdf"
            
            link_drive = upload_para_drive(arquivo_pdf, nome_arq)
            
            if link_drive:
                sucesso = salvar_na_planilha([data_atual, equipamento, relato, link_drive])
                if sucesso:
                    st.success("✅ Registro concluído com sucesso!")
                    st.balloons()
            else:
                st.error("Falha ao gerar link do PDF.")
    else:
        st.warning("Preencha o relato e anexe o arquivo.")
