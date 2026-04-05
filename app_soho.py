import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
from datetime import datetime
import io

# --- CONFIGURAÇÕES ---
ID_PASTA_DRIVE = "1L1cpeSdaauhGlFE7e-qBzl6d4RaFWKJ7"
ID_PLANILHA = "12OAsmeEE9DcDbvLlQhI_Tw85UYTa6dk2Tn7YhN-sjs4"

# Função para conectar com as APIs do Google
def get_gcp_creds():
    creds_dict = st.secrets["gcp_service_account"]
    return service_account.Credentials.from_service_account_info(creds_dict)

# --- FUNÇÃO: UPLOAD PARA DRIVE ---
def upload_para_drive(arquivo_pdf, nome_arquivo):
    try:
        creds = get_gcp_creds()
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': nome_arquivo, 'parents': [ID_PASTA_DRIVE]}
        media = MediaIoBaseUpload(io.BytesIO(arquivo_pdf.read()), mimetype='application/pdf', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        return file.get('webViewLink') # Retorna o link direto do arquivo
    except Exception as e:
        st.error(f"Erro no Drive: {e}")
        return None

# --- FUNÇÃO: ESCREVER NA PLANILHA ---
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

# --- INTERFACE ---
st.title("🏗️ Gestão de Manutenção Soho")

# Lendo equipamentos (Modo Leitura)
url_csv = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv"
df = pd.read_csv(url_csv)
lista_tags = df.iloc[:, 0].dropna().unique().tolist() # Pega a primeira coluna da planilha

equipamento = st.selectbox("Equipamento:", lista_tags)
relato = st.text_area("O que foi feito?")
arquivo_pdf = st.file_uploader("Upload do Laudo (PDF)", type=["pdf"])

if st.button("Finalizar e Salvar"):
    if relato and arquivo_pdf:
        with st.spinner('Processando...'):
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            nome_arq = f"Laudo_{equipamento}_{datetime.now().strftime('%d%m%Y_%H%M')}.pdf"
            
            # 1. Sobe o PDF e pega o link
            link_drive = upload_para_drive(arquivo_pdf, nome_arq)
            
            if link_drive:
                # 2. Salva a linha na planilha
                dados_linha = [data_atual, equipamento, relato, link_drive]
                sucesso = salvar_na_planilha(dados_linha)
                
                if sucesso:
                    st.success("✅ Tudo salvo! Planilha e Drive atualizados.")
                    st.balloons()
    else:
        st.warning("Preencha o relato e anexe o PDF.")
    else:
        st.warning("⚠️ Por favor, preencha a descrição do serviço.")

st.divider()
st.caption("Versão 1.2 - Suporte a anexos PDF")
